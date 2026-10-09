//! Optional CUDA forward search. CPU builds never load or probe a CUDA runtime.
use std::collections::{HashMap, HashSet};
use std::fmt;
use std::sync::atomic::{AtomicU8, Ordering};
use std::time::{Duration, Instant};

use crate::{feed, feed_raw, Filter, ID_MASK};

static USAGE: AtomicU8 = AtomicU8::new(0);

/// Start accounting for one CLI job. Calibration is intentionally excluded.
pub fn reset_usage() {
    USAGE.store(0, Ordering::Relaxed);
}

/// Search backends that completed work since the most recent reset.
pub fn usage_summary() -> String {
    match USAGE.load(Ordering::Relaxed) {
        1 => "CPU",
        2 => "CUDA",
        3 => "CPU + CUDA",
        _ => "no search work",
    }
    .to_owned()
}

pub(crate) fn record_cpu() {
    USAGE.fetch_or(1, Ordering::Relaxed);
}
pub(crate) fn record_cuda() {
    USAGE.fetch_or(2, Ordering::Relaxed);
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Backend {
    #[default]
    Cpu,
    Auto,
    Cuda,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BackendOptions {
    pub backend: Backend,
    pub device: usize,
    pub min_candidates: u64,
}

impl Default for BackendOptions {
    fn default() -> Self {
        Self {
            backend: Backend::Cpu,
            device: 0,
            min_candidates: 100_000_000,
        }
    }
}

/// Consume only backend flags, preserving every other argument and its order.
/// On error the input is unchanged. `gpu_check` is a CLI action, not a search option.
pub fn parse_backend_options(args: &mut Vec<String>) -> Result<(BackendOptions, bool), String> {
    let mut options = BackendOptions::default();
    let mut check = false;
    let mut seen = HashSet::new();
    let mut kept = Vec::new();
    let mut at = 0;
    while at < args.len() {
        let (flag, inline) = args[at]
            .split_once('=')
            .map_or((args[at].as_str(), None), |(k, v)| (k, Some(v)));
        if !matches!(
            flag,
            "--backend" | "--cuda-device" | "--gpu-min-candidates" | "--gpu-check"
        ) {
            kept.push(args[at].clone());
            at += 1;
            continue;
        }
        if !seen.insert(flag.to_owned()) {
            return Err(format!("{flag} was specified more than once"));
        }
        if flag == "--gpu-check" {
            if inline.is_some() {
                return Err("--gpu-check takes no value".into());
            }
            check = true;
        } else {
            let value = match inline {
                Some(value) => value,
                None => {
                    at += 1;
                    args.get(at)
                        .filter(|s| !s.starts_with("--"))
                        .map(String::as_str)
                        .ok_or_else(|| format!("{flag} requires a value"))?
                }
            };
            match flag {
                "--backend" => {
                    options.backend = match value {
                        "cpu" => Backend::Cpu,
                        "auto" => Backend::Auto,
                        "cuda" => Backend::Cuda,
                        _ => {
                            return Err(format!(
                                "invalid --backend {value:?}; expected cpu, auto, or cuda"
                            ))
                        }
                    }
                }
                "--cuda-device" => {
                    decimal(value, flag)?;
                    options.device = value
                        .parse()
                        .map_err(|_| "--cuda-device is too large".to_string())?;
                    if options.device > i32::MAX as usize {
                        return Err("--cuda-device exceeds the CUDA ordinal range".into());
                    }
                }
                _ => {
                    decimal(value, flag)?;
                    options.min_candidates = value
                        .parse()
                        .map_err(|_| "--gpu-min-candidates is too large".to_string())?;
                    if options.min_candidates == 0 {
                        return Err("--gpu-min-candidates must be positive".into());
                    }
                }
            }
        }
        at += 1;
    }
    *args = kept;
    Ok((options, check))
}

fn decimal(value: &str, flag: &str) -> Result<(), String> {
    if value.is_empty() || !value.bytes().all(|b| b.is_ascii_digit()) {
        Err(format!("{flag} requires a nonnegative decimal integer"))
    } else {
        Ok(())
    }
}

#[derive(Clone, Debug)]
pub struct DeviceInfo {
    pub ordinal: usize,
    pub name: String,
    pub major: i32,
    pub minor: i32,
    pub total_memory: u64,
    pub free_memory: u64,
    pub driver_version: i32,
    pub runtime_version: i32,
}

impl fmt::Display for DeviceInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "CUDA device {}: {} (compute {}.{}, {:.1} GiB free / {:.1} GiB total; driver {}, runtime {}); device hash self-test passed",
            self.ordinal, self.name, self.major, self.minor, self.free_memory as f64 / (1u64 << 30) as f64,
            self.total_memory as f64 / (1u64 << 30) as f64, self.driver_version, self.runtime_version)
    }
}

/// Explicit diagnostic only. Normal CPU searches never call this function.
pub fn probe(device: usize) -> Result<DeviceInfo, String> {
    NativeCuda.probe(device).map_err(|reason| format!("{reason}\nCPU search remains available. CUDA is optional and requires a supported NVIDIA GPU and compatible driver. The Toolkit is needed only to build --features cuda, not to run that build. See docs/GPU.md and https://docs.nvidia.com/deploy/cuda-compatibility/ for compatibility; do not install CUDA for non-NVIDIA hardware."))
}

#[derive(Debug)]
pub(crate) struct PackedStrings {
    pub bytes: Vec<u8>,
    pub offsets: Vec<u32>,
}

impl PackedStrings {
    fn pack<'a>(parts: impl IntoIterator<Item = &'a str>) -> Result<Self, String> {
        let mut packed = Self {
            bytes: Vec::new(),
            offsets: vec![0],
        };
        for part in parts {
            let next = packed
                .bytes
                .len()
                .checked_add(part.len())
                .ok_or("CUDA packed byte size overflow")?;
            let end = u32::try_from(next)
                .map_err(|_| "CUDA factor exceeds 4 GiB compact offset limit")?;
            if packed.offsets.len() > u32::MAX as usize {
                return Err("CUDA factor count exceeds u32".into());
            }
            packed
                .bytes
                .try_reserve(part.len())
                .map_err(|e| format!("cannot pack CUDA factors: {e}"))?;
            packed
                .offsets
                .try_reserve(1)
                .map_err(|e| format!("cannot pack CUDA offsets: {e}"))?;
            packed.bytes.extend_from_slice(part.as_bytes());
            packed.offsets.push(end);
        }
        Ok(packed)
    }
    pub fn len(&self) -> usize {
        self.offsets.len() - 1
    }
    pub fn get(&self, index: usize) -> &[u8] {
        &self.bytes[self.offsets[index] as usize..self.offsets[index + 1] as usize]
    }
    fn strings(&self) -> impl Iterator<Item = &str> {
        (0..self.len()).map(|i| std::str::from_utf8(self.get(i)).expect("packed Rust strings"))
    }
}

#[derive(Debug)]
pub(crate) struct PackedRequest {
    pub begins: PackedStrings,
    pub stems: PackedStrings,
    pub ends: PackedStrings,
    pub targets: Vec<u64>,
    pub basis: u64,
    pub fold: bool,
    pub device: usize,
    pub total: u64,
}

pub(crate) fn checked_space(begins: u64, stems: u64, ends: u64) -> Result<u64, String> {
    begins
        .checked_mul(stems)
        .and_then(|n| n.checked_mul(ends))
        .ok_or_else(|| "CUDA candidate dimensions exceed u64".into())
}

impl PackedRequest {
    pub fn new<S: AsRef<str>>(
        openings: &[String],
        endings: &[String],
        stems: &[S],
        wanted: &HashMap<u64, usize>,
        bare: bool,
        fold: bool,
        basis: u64,
        device: usize,
    ) -> Result<Self, String> {
        let width = (openings.len() as u64)
            .checked_add(u64::from(bare))
            .ok_or("CUDA beginning count overflow")?;
        let height = (endings.len() as u64)
            .checked_add(1)
            .ok_or("CUDA ending count overflow")?;
        let total = checked_space(width, stems.len() as u64, height)?;
        let begins = PackedStrings::pack(
            std::iter::once("")
                .take(usize::from(bare))
                .chain(openings.iter().map(String::as_str)),
        )?;
        let ends =
            PackedStrings::pack(std::iter::once("").chain(endings.iter().map(String::as_str)))?;
        let stems = PackedStrings::pack(stems.iter().map(AsRef::as_ref))?;
        let mut targets: Vec<_> = wanted.keys().copied().collect();
        if targets.iter().any(|key| key & !ID_MASK != 0) {
            return Err("CUDA targets must be 63-bit lookup IDs".into());
        }
        targets.sort_unstable();
        targets.dedup();
        Ok(Self {
            begins,
            stems,
            ends,
            targets,
            basis,
            fold,
            device,
            total,
        })
    }

    pub fn validate(&self, mut result: Execution) -> Result<Execution, String> {
        if result.candidates != self.total {
            return Err("CUDA returned an incomplete candidate count".into());
        }
        result.hits.sort_unstable_by_key(|hit| hit.index);
        let mut previous = None;
        for hit in &result.hits {
            if hit.index >= self.total || previous == Some(hit.index) {
                return Err("CUDA returned an invalid or repeated candidate index".into());
            }
            previous = Some(hit.index);
            let (begin, stem, end) = self.indices(hit.index);
            let mut hash = self.basis;
            for bytes in [
                self.begins.get(begin),
                self.stems.get(stem),
                self.ends.get(end),
            ] {
                hash = if self.fold {
                    feed(hash, bytes)
                } else {
                    feed_raw(hash, bytes)
                };
            }
            if hash != hit.full || self.targets.binary_search(&(hash & ID_MASK)).is_err() {
                return Err(
                    "CUDA hit failed full CPU hash/target validation; discarding the GPU result"
                        .into(),
                );
            }
        }
        Ok(result)
    }

    fn indices(&self, index: u64) -> (usize, usize, usize) {
        let end = index % self.ends.len() as u64;
        let prefix = index / self.ends.len() as u64;
        (
            (prefix / self.stems.len() as u64) as usize,
            (prefix % self.stems.len() as u64) as usize,
            end as usize,
        )
    }

    pub fn names(&self, result: Execution) -> Vec<(u64, String)> {
        result
            .hits
            .into_iter()
            .map(|hit| {
                let (begin, stem, end) = self.indices(hit.index);
                let mut name = Vec::new();
                for bytes in [
                    self.begins.get(begin),
                    self.stems.get(stem),
                    self.ends.get(end),
                ] {
                    name.extend_from_slice(bytes);
                }
                (
                    hit.full & ID_MASK,
                    String::from_utf8(name).expect("concatenated Rust strings"),
                )
            })
            .collect()
    }
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub(crate) struct Hit {
    pub index: u64,
    pub full: u64,
}

#[derive(Clone, Debug)]
pub(crate) struct Execution {
    pub hits: Vec<Hit>,
    pub candidates: u64,
    pub device_bytes: u64,
    pub setup_ms: f64,
    pub kernel_ms: f64,
    pub readback_ms: f64,
}

pub(crate) trait CudaDriver {
    fn probe(&mut self, device: usize) -> Result<DeviceInfo, String>;
    fn execute(&mut self, request: &PackedRequest) -> Result<Execution, String>;
    fn prefer_gpu(
        &mut self,
        request: &PackedRequest,
        info: &DeviceInfo,
    ) -> Result<Option<u64>, String> {
        calibrate(self, request, info)
    }
}

pub(crate) struct NativeCuda;

#[cfg(not(feature = "cuda"))]
impl CudaDriver for NativeCuda {
    fn probe(&mut self, _: usize) -> Result<DeviceInfo, String> {
        Err("This build has no CUDA support (CPU-only build). Keep using CPU, or check hardware and Toolkit compatibility in docs/GPU.md before building with --features cuda.".into())
    }
    fn execute(&mut self, _: &PackedRequest) -> Result<Execution, String> {
        Err("This build has no CUDA support".into())
    }
}

#[cfg(feature = "cuda")]
mod native {
    use super::*;
    use std::ffi::c_char;
    #[repr(C)]
    struct Strings {
        bytes: *const u8,
        offsets: *const u32,
        bytes_len: u64,
        count: u32,
        reserved: u32,
    }
    impl From<&PackedStrings> for Strings {
        fn from(s: &PackedStrings) -> Self {
            Self {
                bytes: s.bytes.as_ptr(),
                offsets: s.offsets.as_ptr(),
                bytes_len: s.bytes.len() as u64,
                count: s.len() as u32,
                reserved: 0,
            }
        }
    }
    #[repr(C)]
    struct Request {
        begins: Strings,
        stems: Strings,
        ends: Strings,
        targets: *const u64,
        target_count: u64,
        basis: u64,
        chunk_candidates: u64,
        max_device_bytes: u64,
        device: i32,
        fold: u32,
    }
    #[repr(C)]
    struct Device {
        ordinal: i32,
        device_count: i32,
        driver_version: i32,
        runtime_version: i32,
        major: i32,
        minor: i32,
        total_memory: u64,
        free_memory: u64,
        name: [c_char; 256],
    }
    #[repr(C)]
    #[derive(Default)]
    struct ResultInfo {
        candidate_count: u64,
        hit_count: u64,
        device_bytes: u64,
        setup_ms: f64,
        kernel_ms: f64,
        readback_ms: f64,
    }
    extern "C" {
        fn slasher_cuda_probe(
            device: i32,
            info: *mut Device,
            error: *mut c_char,
            capacity: u64,
        ) -> i32;
        fn slasher_cuda_search(
            request: *const Request,
            hits: *mut Hit,
            hit_capacity: u64,
            result: *mut ResultInfo,
            error: *mut c_char,
            capacity: u64,
        ) -> i32;
    }
    fn text(buffer: &[c_char]) -> String {
        String::from_utf8_lossy(
            &buffer
                .iter()
                .take_while(|&&c| c != 0)
                .map(|&c| c as u8)
                .collect::<Vec<_>>(),
        )
        .into_owned()
    }
    impl CudaDriver for NativeCuda {
        fn probe(&mut self, device: usize) -> Result<DeviceInfo, String> {
            let device = i32::try_from(device).map_err(|_| "CUDA device ordinal exceeds i32")?;
            // Every field is an integer or byte array; zero is a valid initial value.
            let mut info: Device = unsafe { std::mem::zeroed() };
            let mut error = [0 as c_char; 1024];
            let status = unsafe {
                slasher_cuda_probe(device, &mut info, error.as_mut_ptr(), error.len() as u64)
            };
            if status != 0 {
                return Err(format!("CUDA probe failed ({status}): {}", text(&error)));
            }
            if info.ordinal < 0 {
                return Err("CUDA probe returned an invalid device ordinal".into());
            }
            Ok(DeviceInfo {
                ordinal: info.ordinal as usize,
                name: text(&info.name),
                major: info.major,
                minor: info.minor,
                total_memory: info.total_memory,
                free_memory: info.free_memory,
                driver_version: info.driver_version,
                runtime_version: info.runtime_version,
            })
        }
        fn execute(&mut self, request: &PackedRequest) -> Result<Execution, String> {
            if request.total == 0 || request.targets.is_empty() {
                return Ok(Execution {
                    hits: vec![],
                    candidates: request.total,
                    device_bytes: 0,
                    setup_ms: 0.0,
                    kernel_ms: 0.0,
                    readback_ms: 0.0,
                });
            }
            let raw = Request {
                begins: (&request.begins).into(),
                stems: (&request.stems).into(),
                ends: (&request.ends).into(),
                targets: request.targets.as_ptr(),
                target_count: request.targets.len() as u64,
                basis: request.basis,
                chunk_candidates: 0,
                max_device_bytes: 0,
                device: i32::try_from(request.device)
                    .map_err(|_| "CUDA device ordinal exceeds i32")?,
                fold: u32::from(request.fold),
            };
            let capacity = request.total.min(1_000_000) as usize;
            let mut hits = Vec::new();
            hits.try_reserve_exact(capacity)
                .map_err(|e| format!("cannot allocate CUDA hit buffer: {e}"))?;
            hits.resize(capacity, Hit::default());
            let mut result = ResultInfo::default();
            let mut error = [0 as c_char; 1024];
            let status = unsafe {
                slasher_cuda_search(
                    &raw,
                    hits.as_mut_ptr(),
                    capacity as u64,
                    &mut result,
                    error.as_mut_ptr(),
                    error.len() as u64,
                )
            };
            if status != 0 {
                return Err(format!("CUDA search failed ({status}): {}", text(&error)));
            }
            if result.hit_count > capacity as u64 {
                return Err("CUDA returned more hits than the output capacity".into());
            }
            hits.truncate(result.hit_count as usize);
            Ok(Execution {
                hits,
                candidates: result.candidate_count,
                device_bytes: result.device_bytes,
                setup_ms: result.setup_ms,
                kernel_ms: result.kernel_ms,
                readback_ms: result.readback_ms,
            })
        }
    }

    #[cfg(test)]
    mod native_failure_tests {
        use super::*;

        #[test]
        fn native_abi_layout_matches_header() {
            assert_eq!(std::mem::size_of::<Strings>(), 32);
            assert_eq!(std::mem::size_of::<Request>(), 144);
            assert_eq!(std::mem::size_of::<Device>(), 296);
            assert_eq!(std::mem::size_of::<ResultInfo>(), 48);
            assert_eq!(std::mem::size_of::<Hit>(), 16);
        }

        #[test]
        #[ignore = "requires a supported NVIDIA GPU and compatible driver"]
        fn actual_cuda_native_failures_never_return_partial_hits() {
            use std::ffi::c_char;
            let wanted = HashMap::from([(feed(crate::BASIS, b"x") & ID_MASK, 0)]);
            let request =
                PackedRequest::new(&[], &[], &["x", "x"], &wanted, true, true, crate::BASIS, 0)
                    .unwrap();
            let mut raw = Request {
                begins: (&request.begins).into(),
                stems: (&request.stems).into(),
                ends: (&request.ends).into(),
                targets: request.targets.as_ptr(),
                target_count: request.targets.len() as u64,
                basis: request.basis,
                chunk_candidates: 0,
                max_device_bytes: 0,
                device: 0,
                fold: 1,
            };
            let mut hits = [Hit::default(); 2];
            let mut result = ResultInfo::default();
            let mut error = [0 as c_char; 1024];
            let status = unsafe {
                slasher_cuda_search(
                    &raw,
                    hits.as_mut_ptr(),
                    1,
                    &mut result,
                    error.as_mut_ptr(),
                    error.len() as u64,
                )
            };
            assert_eq!(status, 5, "{}", text(&error));
            assert_eq!(result.hit_count, 0);
            raw.max_device_bytes = 1;
            let status = unsafe {
                slasher_cuda_search(
                    &raw,
                    hits.as_mut_ptr(),
                    2,
                    &mut result,
                    error.as_mut_ptr(),
                    error.len() as u64,
                )
            };
            assert_eq!(status, 3, "{}", text(&error));
            assert_eq!(result.hit_count, 0);
            raw.max_device_bytes = 0;
            let invalid = [u64::MAX];
            raw.targets = invalid.as_ptr();
            let status = unsafe {
                slasher_cuda_search(
                    &raw,
                    hits.as_mut_ptr(),
                    2,
                    &mut result,
                    error.as_mut_ptr(),
                    error.len() as u64,
                )
            };
            assert_eq!(status, 2);
            assert_eq!(result.hit_count, 0);
            raw.targets = request.targets.as_ptr();
            let offsets = [0, 2, 1];
            raw.stems.offsets = offsets.as_ptr();
            let status = unsafe {
                slasher_cuda_search(
                    &raw,
                    hits.as_mut_ptr(),
                    2,
                    &mut result,
                    error.as_mut_ptr(),
                    error.len() as u64,
                )
            };
            assert_eq!(status, 2);
            assert_eq!(result.hit_count, 0);
            assert!(NativeCuda.probe(i32::MAX as usize).is_err());

            let long = "a".repeat(4097);
            let request =
                PackedRequest::new(&[], &[], &[long], &wanted, true, true, crate::BASIS, 0)
                    .unwrap();
            assert!(NativeCuda.execute(&request).is_err());
        }
    }
}

// Calibration is bounded independently of the full candidate product. Fixed setup
// is measured once, never multiplied by the ratio between sample and full scans.
fn calibrate<D: CudaDriver + ?Sized>(
    driver: &mut D,
    request: &PackedRequest,
    info: &DeviceInfo,
) -> Result<Option<u64>, String> {
    let Some(sample) = sample_request(request)? else {
        return Ok(None);
    };
    let packed_bytes = request.begins.bytes.len() as u64
        + request.stems.bytes.len() as u64
        + request.ends.bytes.len() as u64;
    let offsets = (request.begins.offsets.len() as u64
        + request.stems.offsets.len() as u64
        + request.ends.offsets.len() as u64)
        * 4;
    let minimum_memory = packed_bytes
        .saturating_add(offsets)
        .saturating_add(request.targets.len() as u64 * 16)
        .saturating_add(128 << 20);
    if minimum_memory > info.free_memory.saturating_mul(3) / 4 || minimum_memory > 8u64 << 30 {
        return Ok(None);
    }
    let cpu = measure_cpu(&sample)?;
    let measured = sample.validate(driver.execute(&sample)?)?;
    if cpu.scan_seconds < 0.002
        || !measured.kernel_ms.is_finite()
        || measured.kernel_ms < 0.01
        || !measured.setup_ms.is_finite()
        || measured.setup_ms < 0.0
        || !measured.readback_ms.is_finite()
        || measured.readback_ms < 0.0
    {
        return Ok(None);
    }
    let sample_packed =
        (sample.begins.bytes.len() + sample.stems.bytes.len() + sample.ends.bytes.len()) as u64;
    let extra_packed = packed_bytes.saturating_sub(sample_packed);
    let budget = checkpoint_budget(sample.total, &measured)
        .ok_or("CUDA calibration timing is not usable")?;
    let batch_stems = checkpoint_stems(request, budget).min(request.stems.len() as u64);
    let batch_pairs = (request.begins.len() as u64).saturating_mul(batch_stems);
    let sample_pairs = (sample.begins.len() as u64).saturating_mul(sample.stems.len() as u64);
    let extra_pairs = batch_pairs.saturating_sub(sample_pairs).saturating_mul(8);
    let extra_storage = extra_packed
        .saturating_add(offsets)
        .saturating_add(extra_pairs)
        .saturating_add(request.begins.len().saturating_sub(sample.begins.len()) as u64 * 8);
    let estimated_memory = measured.device_bytes.saturating_add(extra_storage);
    if estimated_memory > info.free_memory.saturating_mul(3) / 4 || estimated_memory > 8u64 << 30 {
        return Ok(None);
    }
    let scale = request.total as f64 / sample.total as f64;
    let cpu = cpu.setup_seconds + (cpu.scan_seconds - 0.001) * scale;
    // A checkpoint cannot split a stem's product. Rounding the total product
    // by the budget alone can undercount dispatches by almost a factor of two.
    let batches = (request.stems.len() as u64).div_ceil(batch_stems) as f64;
    // Scale only extra input-transfer/storage work, not fixed setup by the
    // candidate ratio. Charging all setup proportionally to extra bytes is
    // deliberately conservative when filter construction dominates setup.
    let extra_setup =
        measured.setup_ms * extra_storage as f64 / measured.device_bytes.max(1) as f64;
    let gpu = ((measured.setup_ms + extra_setup + measured.readback_ms) * batches
        + (measured.kernel_ms + 0.1) * scale)
        / 1000.0;
    println!("CUDA calibration: {:.1}M sampled; conservative CPU {:.2}s, GPU {:.2}s (including checkpoint setup)", sample.total as f64 / 1e6,cpu,gpu);
    Ok((gpu <= cpu * 0.8).then_some(budget))
}

fn checkpoint_stems(request: &PackedRequest, budget: u64) -> u64 {
    let per_stem = (request.begins.len() as u64).saturating_mul(request.ends.len() as u64);
    if per_stem == 0 {
        u64::MAX
    } else {
        (budget / per_stem).max(1)
    }
}

/// About one second of conservatively measured GPU work, capped at 100B.
/// Native launches remain bounded separately; this is the checkpoint interval.
pub(crate) fn checkpoint_budget(candidates: u64, result: &Execution) -> Option<u64> {
    if !result.kernel_ms.is_finite()
        || result.kernel_ms < 0.01
        || !result.setup_ms.is_finite()
        || result.setup_ms < 0.0
        || !result.readback_ms.is_finite()
        || result.readback_ms < 0.0
    {
        return None;
    }
    let time = (1000.0 - result.setup_ms - result.readback_ms).max(100.0);
    Some((candidates as f64 * time / (result.kernel_ms + 0.1)).clamp(1.0, 100_000_000_000.0) as u64)
}

fn sample_request(request: &PackedRequest) -> Result<Option<PackedRequest>, String> {
    const LIMIT: u64 = 8_000_000;
    let mut sizes = [
        request.begins.len(),
        request.stems.len(),
        request.ends.len(),
    ];
    if sizes.contains(&0) {
        return Ok(None);
    }
    while checked_space(sizes[0] as u64, sizes[1] as u64, sizes[2] as u64)? > LIMIT {
        let largest = (0..3).max_by_key(|&i| sizes[i]).unwrap();
        sizes[largest] = sizes[largest].div_ceil(2);
    }
    let total = checked_space(sizes[0] as u64, sizes[1] as u64, sizes[2] as u64)?;
    if total < 2_000_000 {
        return Ok(None);
    }
    fn select(strings: &PackedStrings, count: usize) -> Result<PackedStrings, String> {
        PackedStrings::pack((0..count).map(|i| {
            let index = if count == 1 {
                strings.len() / 2
            } else {
                (i as u128 * (strings.len() - 1) as u128 / (count - 1) as u128) as usize
            };
            std::str::from_utf8(strings.get(index)).expect("packed Rust strings")
        }))
    }
    let sample = PackedRequest {
        begins: select(&request.begins, sizes[0])?,
        stems: select(&request.stems, sizes[1])?,
        ends: select(&request.ends, sizes[2])?,
        targets: request.targets.clone(),
        basis: request.basis,
        fold: request.fold,
        device: request.device,
        total,
    };
    let longest = |s: &PackedStrings| {
        (0..s.len())
            .map(|i| s.get(i).len() as u64)
            .max()
            .unwrap_or(0)
    };
    if total
        .saturating_mul(longest(&sample.begins) + longest(&sample.stems) + longest(&sample.ends))
        > 2_000_000_000
    {
        return Ok(None);
    }
    Ok(Some(sample))
}

struct CpuTiming {
    scan_seconds: f64,
    setup_seconds: f64,
}

fn measure_cpu(request: &PackedRequest) -> Result<CpuTiming, String> {
    let overall = Instant::now();
    let filter = Filter::new(request.targets.iter());
    let targets: HashSet<_> = request.targets.iter().copied().collect();
    let apply = |hash, bytes: &[u8]| {
        if request.fold {
            feed(hash, bytes)
        } else {
            feed_raw(hash, bytes)
        }
    };
    let begins: Vec<_> = request
        .begins
        .strings()
        .map(|s| apply(request.basis, s.as_bytes()))
        .collect();
    let threads = std::thread::available_parallelism()
        .map_or(1, |n| n.get())
        .min(request.stems.len())
        .max(1);
    let chunk = request.stems.len().div_ceil(threads);
    let barrier = std::sync::Barrier::new(request.stems.len().div_ceil(chunk) + 1);
    let complete = std::thread::scope(|scope| {
        let mut workers = Vec::new();
        for from in (0..request.stems.len()).step_by(chunk) {
            let to = (from + chunk).min(request.stems.len());
            let (begins, filter, targets, apply, barrier) =
                (&begins, &filter, &targets, &apply, &barrier);
            workers.push(scope.spawn(move || {
                barrier.wait();
                let started = Instant::now();
                let deadline = started + Duration::from_secs(2);
                let mut count = 0u64;
                let mut hits = 0u64;
                for stem in from..to {
                    for &begin in begins {
                        let prefix = apply(begin, request.stems.get(stem));
                        for end in 0..request.ends.len() {
                            if count % 4096 == 0 && Instant::now() > deadline {
                                return None;
                            }
                            let hash = apply(prefix, request.ends.get(end)) & ID_MASK;
                            if filter.may_hold(hash) && targets.contains(&hash) {
                                hits += 1;
                            }
                            count += 1;
                        }
                    }
                }
                std::hint::black_box(hits);
                Some((count, started.elapsed().as_secs_f64()))
            }));
        }
        barrier.wait();
        workers
            .into_iter()
            .map(|w| w.join().ok().flatten())
            .collect::<Option<Vec<_>>>()
    });
    if complete
        .as_ref()
        .map(|counts| counts.iter().map(|(count, _)| count).sum::<u64>())
        != Some(request.total)
    {
        return Err("CPU calibration exceeded its bounded time budget".into());
    }
    let scan_seconds = complete
        .unwrap()
        .iter()
        .map(|(_, seconds)| *seconds)
        .fold(0.0, f64::max);
    Ok(CpuTiming {
        scan_seconds,
        setup_seconds: (overall.elapsed().as_secs_f64() - scan_seconds).max(0.0),
    })
}

#[cfg(test)]
pub(crate) fn fixture_execution(request: &PackedRequest) -> Execution {
    let mut hits = Vec::new();
    for index in 0..request.total {
        let (begin, stem, end) = request.indices(index);
        let mut full = request.basis;
        for bytes in [
            request.begins.get(begin),
            request.stems.get(stem),
            request.ends.get(end),
        ] {
            full = if request.fold {
                feed(full, bytes)
            } else {
                feed_raw(full, bytes)
            };
        }
        if request.targets.binary_search(&(full & ID_MASK)).is_ok() {
            hits.push(Hit { index, full });
        }
    }
    Execution {
        hits,
        candidates: request.total,
        device_bytes: 0,
        setup_ms: 0.0,
        kernel_ms: 0.0,
        readback_ms: 0.0,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{games::IW_BASIS, BASIS};

    fn strings(values: &[&str]) -> Vec<String> {
        values.iter().map(|s| (*s).into()).collect()
    }

    #[test]
    fn options_are_strict_and_leave_other_arguments_in_order() {
        let mut args = strings(&[
            "plan.txt",
            "--backend=auto",
            "--size",
            "--cuda-device",
            "2",
            "--gpu-min-candidates=42",
            "--gpu-check",
        ]);
        let (options, check) = parse_backend_options(&mut args).unwrap();
        assert_eq!(
            options,
            BackendOptions {
                backend: Backend::Auto,
                device: 2,
                min_candidates: 42
            }
        );
        assert!(check);
        assert_eq!(args, strings(&["plan.txt", "--size"]));
        assert_eq!(
            parse_backend_options(&mut vec![]).unwrap(),
            (BackendOptions::default(), false)
        );
        for invalid in [
            vec!["--backend"],
            vec!["--backend", "--size"],
            vec!["--backend=GPU"],
            vec!["--backend=cpu", "--backend=auto"],
            vec!["--cuda-device=-1"],
            vec!["--cuda-device=2147483648"],
            vec!["--cuda-device=+1"],
            vec!["--gpu-min-candidates=0"],
            vec!["--gpu-min-candidates=1.5"],
            vec!["--gpu-min-candidates=18446744073709551616"],
            vec!["--gpu-check=true"],
            vec!["--gpu-check", "--gpu-check"],
            vec!["--cuda-device="],
        ] {
            let mut args = strings(&invalid);
            let original = args.clone();
            assert!(
                parse_backend_options(&mut args).is_err(),
                "accepted {original:?}"
            );
            assert_eq!(args, original, "partial parsing mutated failed input");
        }
    }

    fn fixture(basis: u64, fold: bool, bare: bool) -> PackedRequest {
        let openings = strings(&["", "AMB\\", "AMB\\"]);
        let stems = strings(&["", "Water", "Écho\0z", "Water"]);
        let endings = strings(&["", "_L", "\\Take"]);
        let mut wanted = HashMap::new();
        for opening in std::iter::once("")
            .take(usize::from(bare))
            .chain(openings.iter().map(String::as_str))
        {
            for stem in &stems {
                for end in std::iter::once("").chain(endings.iter().map(String::as_str)) {
                    let name = format!("{opening}{stem}{end}");
                    let full = if fold {
                        feed(basis, name.as_bytes())
                    } else {
                        feed_raw(basis, name.as_bytes())
                    };
                    wanted.insert(full & ID_MASK, 0);
                }
            }
        }
        PackedRequest::new(&openings, &endings, &stems, &wanted, bare, fold, basis, 0).unwrap()
    }

    #[test]
    fn compact_factors_preserve_duplicates_empty_parts_and_hash_policy() {
        for basis in [BASIS, IW_BASIS] {
            for fold in [false, true] {
                for bare in [false, true] {
                    let request = fixture(basis, fold, bare);
                    assert_eq!(request.begins.len(), 3 + usize::from(bare));
                    assert_eq!(request.ends.len(), 4);
                    assert_eq!(request.begins.get(request.begins.len() - 1), b"AMB\\");
                    assert_eq!(request.ends.get(0), b"");
                    assert_eq!(request.ends.get(1), b"");
                    let result = request.validate(fixture_execution(&request)).unwrap();
                    assert_eq!(result.hits.len() as u64, request.total);
                    assert!(result.hits.iter().any(|hit| hit.full & !ID_MASK != 0));
                    let names = request.names(result);
                    assert_eq!(names.len() as u64, request.total);
                    assert!(names.iter().any(|(_, name)| name.contains("AMB\\")));
                }
            }
        }
        assert!(checked_space(u64::MAX, 2, 1).is_err());
        assert_eq!(checked_space(u64::MAX, 0, 2).unwrap(), 0);
        let invalid_targets = HashMap::from([(u64::MAX, 0)]);
        assert!(
            PackedRequest::new(&[], &[], &["x"], &invalid_targets, true, true, BASIS, 0).is_err()
        );
    }

    #[test]
    fn incomplete_or_corrupt_gpu_results_are_rejected_atomically() {
        let request = fixture(BASIS, false, true);
        let good = fixture_execution(&request);
        let mut bad = good.clone();
        bad.candidates -= 1;
        assert!(request.validate(bad).is_err());
        let mut bad = good.clone();
        bad.hits[0].index = request.total;
        assert!(request.validate(bad).is_err());
        let mut bad = good.clone();
        bad.hits[1].index = bad.hits[0].index;
        assert!(request.validate(bad).is_err());
        let mut bad = good.clone();
        bad.hits[0].full ^= 1 << 63;
        assert!(
            request.validate(bad).is_err(),
            "full high bit must be independently validated"
        );
        let mut other_targets = fixture(BASIS, false, true);
        other_targets.targets.clear();
        assert!(other_targets.validate(good).is_err());
    }

    #[test]
    fn sample_is_bounded_evenly_spaced_and_preserves_policy() {
        let parts: Vec<_> = (0..1000).map(|n| format!("part_{n}")).collect();
        let request = PackedRequest::new(
            &parts,
            &parts,
            &parts,
            &HashMap::from([(1, 0)]),
            false,
            false,
            IW_BASIS,
            7,
        )
        .unwrap();
        let sample = sample_request(&request).unwrap().unwrap();
        assert!((2_000_000..=8_000_000).contains(&sample.total));
        assert_eq!(sample.basis, IW_BASIS);
        assert!(!sample.fold);
        assert_eq!(sample.device, 7);
        for (full, small) in [
            (&request.begins, &sample.begins),
            (&request.stems, &sample.stems),
            (&request.ends, &sample.ends),
        ] {
            assert_eq!(small.get(0), full.get(0));
            assert_eq!(small.get(small.len() - 1), full.get(full.len() - 1));
        }
        let small = fixture(BASIS, true, true);
        assert!(sample_request(&small).unwrap().is_none());
    }

    #[test]
    fn checkpoint_projection_counts_whole_stems_and_caps_budget() {
        let request = PackedRequest::new(
            &strings(&["a", "b", "c"]),
            &strings(&["x"]),
            &["1", "2", "3"],
            &HashMap::new(),
            false,
            true,
            BASIS,
            0,
        )
        .unwrap();
        assert_eq!(checkpoint_stems(&request, 10), 1);
        assert_eq!(
            (request.stems.len() as u64).div_ceil(checkpoint_stems(&request, 10)),
            3
        );
        let mut timing = fixture_execution(&request);
        timing.kernel_ms = 0.05;
        assert_eq!(checkpoint_budget(u64::MAX, &timing), Some(100_000_000_000));
        timing.kernel_ms = f64::NAN;
        assert_eq!(checkpoint_budget(8_000_000, &timing), None);
        timing.kernel_ms = 0.0;
        assert_eq!(checkpoint_budget(8_000_000, &timing), None);
    }

    #[cfg(feature = "cuda")]
    #[test]
    #[ignore = "requires a supported NVIDIA GPU and compatible driver"]
    fn actual_cuda_matches_cpu_for_all_hash_policies_and_factor_edges() {
        let mut driver = NativeCuda;
        driver.probe(0).unwrap();
        for basis in [BASIS, IW_BASIS] {
            for fold in [false, true] {
                for bare in [false, true] {
                    let request = fixture(basis, fold, bare);
                    let expected = request.names(fixture_execution(&request));
                    let actual =
                        request.names(request.validate(driver.execute(&request).unwrap()).unwrap());
                    assert_eq!(
                        actual, expected,
                        "basis={basis:x}, fold={fold}, bare={bare}"
                    );
                }
            }
        }
        for (openings, stems, targets, bare) in [
            (vec![], vec!["x"], HashMap::from([(1, 0)]), false),
            (vec![], vec![], HashMap::from([(1, 0)]), true),
            (vec![], vec!["x"], HashMap::new(), true),
            (vec![], vec!["x"], HashMap::from([(1, 0)]), true),
        ] {
            let request =
                PackedRequest::new(&openings, &[], &stems, &targets, bare, true, BASIS, 0).unwrap();
            assert_eq!(
                request.names(request.validate(driver.execute(&request).unwrap()).unwrap()),
                request.names(fixture_execution(&request))
            );
        }
    }

    #[cfg(feature = "cuda")]
    #[test]
    #[ignore = "requires a supported NVIDIA GPU and compatible driver"]
    fn actual_cuda_repeated_searches_alternate_large_target_buffers() {
        let openings = strings(&["ROOT\\", "other/"]);
        let endings: Vec<_> = (0..64).map(|i| format!("_{i}")).collect();
        let stems: Vec<_> = (0..1024).map(|i| format!("stem_{i}")).collect();
        let requests: Vec<_> = [BASIS, IW_BASIS]
            .into_iter()
            .enumerate()
            .map(|(set, basis)| {
                // Reachable controls differ between runs; most target IDs are noise
                // spanning both filter index ranges. Both buffers exceed 1 MiB.
                let mut state = 0x1234_5678_9876_5432u64 ^ set as u64;
                let mut wanted = HashMap::new();
                for _ in 0..250_000 {
                    state ^= state << 13;
                    state ^= state >> 7;
                    state ^= state << 17;
                    wanted.insert(state & ID_MASK, 0);
                }
                for i in (set..1024).step_by(8) {
                    let name = format!("{}{}_{}", openings[i % 2], stems[i], i % 64);
                    wanted.insert(feed(basis, name.as_bytes()) & ID_MASK, 0);
                }
                PackedRequest::new(&openings, &endings, &stems, &wanted, true, true, basis, 0)
                    .unwrap()
            })
            .collect();
        let expected: Vec<_> = requests
            .iter()
            .map(|r| r.names(fixture_execution(r)))
            .collect();
        assert!(expected.iter().all(|hits| hits.len() >= 128));
        let mut driver = NativeCuda;
        driver.probe(0).unwrap();
        for iteration in 0..8 {
            let at = iteration % requests.len();
            let request = &requests[at];
            let actual = request.names(request.validate(driver.execute(request).unwrap()).unwrap());
            assert_eq!(
                actual, expected[at],
                "stale target/filter upload on iteration {iteration}"
            );
        }
    }
}

# Optional CUDA search

The default build and default search backend remain CPU-only. They need no NVIDIA driver,
CUDA Toolkit, or GPU. An optional `cuda` Cargo feature adds a forward-search backend to
`confirm_plan` and `confirm_cw`. `confirm_list` continues to stream candidates through the CPU.

CUDA can help large, grounded cross products. It does not make a spent method new, accelerate a
Python generator, or replace the CPU engine's cheaper inverse search (`Meet`). Choose the method
first; use `--backend auto` to assess whether this machine's GPU helps that workload.

## Compatibility and installation

This backend requires a supported NVIDIA GPU with **compute capability 7.5 or newer** and a
native 64-bit Windows/MSVC or Linux build. That number is a GPU capability, not a CUDA Toolkit
version. AMD GPUs, Apple GPUs, macOS, and NVIDIA GPUs below 7.5 use the default CPU backend.
Find the exact GPU model in [NVIDIA's compute-capability table](https://developer.nvidia.com/cuda/gpus).
Capability establishes eligibility; it does not establish a speed advantage.

There are two different software requirements:

| task | requirements |
|---|---|
| Build the default CPU executables | Rust and its normal platform build tools; no CUDA software |
| Build with `--features cuda` | Rust, NVIDIA CUDA Toolkit including `nvcc` and the static runtime library, and a compatible C++ host compiler |
| Run a CUDA-enabled executable on the GPU | Compatible NVIDIA driver, supported GPU, and normal platform runtimes; the Toolkit is not needed at runtime |

The feature explicitly links the static CUDA runtime, so it does not require a separate
`cudart` DLL or shared library at runtime. The NVIDIA driver and ordinary platform runtime
libraries are still required. This is the static runtime option described in the
[NVCC documentation](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html).

Windows builds retain `/MD` for compatibility with Rust's host runtime. They therefore need the
matching Visual C++ runtime, including `MSVCP140` and `VCRUNTIME140` libraries, plus the Windows
Universal CRT. If Windows reports those libraries missing before the program starts, use
Microsoft's [supported Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
for the executable's architecture and at least the build tools' version. This is separate from
installing CUDA. The program cannot print a GPU diagnostic until its normal host libraries load.

For a machine that might benefit:

1. Identify the GPU and driver. On Windows, use Device Manager's Display adapters or
   `nvidia-smi`; on Linux, use `nvidia-smi` when available. A missing `nvidia-smi` command alone
   does not identify the GPU. Check the model's compute capability before installing anything.
2. If building CUDA support, choose a Toolkit release that supports the GPU, operating system,
   and host compiler. Use NVIDIA's [Toolkit download selector](https://developer.nvidia.com/cuda-downloads)
   and the installation guide for that release. On Windows, install its supported Visual Studio
   C++ build tools and use an x64 developer shell. On Linux, check the distribution and GCC/Clang
   compatibility tables rather than bypassing NVCC's compiler check. See the
   [Windows guide](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)
   and [Linux guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html).
3. Check the driver's compatibility with that Toolkit's generated code. Install a compatible
   driver from [NVIDIA](https://www.nvidia.com/drivers) only if needed. The Toolkit installer and
   driver installer are separate concerns; do not assume one installed the other. PTX JIT can
   require a newer driver than the major-version compatibility minimum, so consult NVIDIA's
   [compatibility limitations](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html).
4. Build, run `--gpu-check`, then use `--backend auto` on a worthwhile plan. The check establishes
   working hardware and kernel correctness; automatic selection also measures whether using it
   is worthwhile. A supported but slower GPU stays on CPU in automatic mode.

Nothing in this repository installs a Toolkit or changes a graphics driver automatically.
If CUDA is unavailable, continue with the default CPU build. Do not spend time installing CUDA
for an unsupported GPU or for a workload that is small, generator-bound, or cheaper with `Meet`.

## Build and check

Build from the repository root:

```text
cargo build --release --features cuda --bin confirm_plan --bin confirm_cw
```

Run the newly built executables under `target/release`. Building this feature does **not**
upgrade the committed portable executables under `bin/`; this is a source-only addition.
Do not overwrite or submit those portable binaries with a local CUDA build.

Windows:

```powershell
.\target\release\confirm_plan.exe --gpu-check
```

Linux:

```sh
./target/release/confirm_plan --gpu-check
```

`confirm_cw --gpu-check` provides the same diagnostic. It needs no plan, capture, refreshed
tables, or successful `start`, and does not search or create a findings run. A failed check
returns an explanation and nonzero exit status; CPU searches remain available. In a default
build it explains that CUDA support was not compiled in. A CUDA-enabled build checks the selected
device, driver/runtime compatibility, at least 64 MiB of free GPU memory, capability, and four
small hash fixtures computed by an actual kernel. Passing this minimum memory check does not
guarantee that a particular search fits; allocation failures are reported through the same
fallback/error path.

The build searches `NVCC`, then `CUDA_PATH`/`CUDA_HOME`, then `PATH` for the compiler. Set
`NVCC` to an executable path and `CUDA_PATH` or `CUDA_HOME` to the matching Toolkit root if
discovery is ambiguous. `CUDAHOSTCXX` (or `CXX`) selects the C++ host compiler. Windows uses
the MSVC Rust target and can discover an installed Visual Studio developer environment;
an x64 Native Tools shell is the simplest way to diagnose missing C++ tools. Cross-compilation
of this feature is not supported.

By default, the build queries `nvcc --list-gpu-code` and embeds native code for every generic
numeric `sm_XX` target at or above 75 that the installed compiler supports. Architecture-specific
`a`/`f` variants are excluded. It also includes `compute_75` PTX as a forward-compatibility
fallback. A compatible native image avoids depending on the driver's ability to JIT that
Toolkit's PTX. The set of native images depends on the installed Toolkit; a capability number
alone is not a promise that every driver can run every build.

Optionally set `SLASHER_CUDA_ARCH` to a numeric capability, such as `120` for the tested Blackwell
GPU, before building. This replaces the default bundle with native `sm_120` code and
`compute_120` PTX. Such a build no longer targets older GPUs, and NVCC must support the chosen
architecture. NVIDIA explains native code and PTX compatibility in its
[Blackwell compatibility guide](https://docs.nvidia.com/cuda/blackwell-compatibility-guide/).

For example, in PowerShell on a compatible Blackwell development machine:

```powershell
$env:SLASHER_CUDA_ARCH = '120'
cargo build --release --features cuda --bin confirm_plan --bin confirm_cw
.\target\release\confirm_plan.exe --gpu-check --cuda-device 0
```

The private prototype was built with CUDA 13.3.73 and Visual Studio 2022's MSVC 14.44 on
Windows, driver 596.72, compute capability 12.0. This records the tested environment, not a
requirement to install those exact versions or a claim that every eligible GPU was tested.

During integration on that machine, a PTX-only build from the installed Toolkit failed with an
unsupported-toolchain JIT error despite apparently compatible driver/runtime API versions.
Native `sm_120` code passed, and the revised default bundle passed the actual kernel self-test.
This is why preflight executes a kernel instead of accepting version numbers as proof of support.

## Run a search

Normal startup, pool policies, exclusions, fingerprint checks, and submission still apply:

```powershell
bin\windows\start.exe
.\target\release\confirm_plan.exe plans/example.txt --size
.\target\release\confirm_plan.exe plans/example.txt --backend auto
.\target\release\confirm_cw.exe --backend auto
bin\windows\submit.exe
```

The example plan illustrates syntax, not a recommendation to repeat a previously searched
candidate space. On Linux use `bin/linux/start`, `./target/release/confirm_plan`,
`./target/release/confirm_cw`, and `bin/linux/submit`.

| option | behavior |
|---|---|
| `--backend cpu` | Default. Uses the existing CPU search and never probes CUDA. |
| `--backend auto` | Keeps cheap or `Meet` workloads on CPU; considers CUDA only for sufficiently large forward products, after support and performance checks. Falls back to CPU if CUDA is unavailable or fails. |
| `--backend cuda` | Explicitly requests CUDA forward search, bypassing automatic cost selection. Unavailable or failed CUDA is an error, not a silent CPU run. |
| `--cuda-device N` | Zero-based CUDA device ordinal; default `0`. |
| `--gpu-min-candidates N` | Positive candidate threshold for automatic selection; default `100000000`. Lowering it does not bypass support or performance checks. |
| `--gpu-check` | Standalone support diagnostic; accepts `--cuda-device N`. Does not run a search or certify a speedup. |

Pass option values as separate arguments. Malformed values and duplicate GPU options are
errors. `confirm_plan --size` describes the plan without probing or running the GPU.

Automatic selection is deliberately conservative: an eligible forward product must pass a
bounded CPU/GPU calibration whose projected GPU elapsed time is at least 20% lower than the
projected CPU time. GPU setup and readback for checkpoint batches are included in that estimate.
A capability check alone cannot establish that an older GPU beats the CPU. Calibration is an
estimate for the current workload, not a guarantee for every workload or for the complete
submission workflow.
An inconclusive or failed calibration keeps the work on CPU.
For `confirm_plan`, this decision uses the full product for each hash-policy group, before
internal checkpoint batching. The CPU-only plan path keeps its existing outer slices. Different
hash-policy groups can make different backend decisions because their wanted sets differ.
GPU checkpoint sizes adapt to measured throughput; individual kernel launches have separate
bounds. The CPU path retains its own checkpoint strategy.

Every proposed GPU name is rehashed on the CPU under the same game/type policy and checked
against the wanted IDs. Modern ordinary and alias offsets, the 63-bit lookup key, full-width
modern alias output, case normalization, and BO4 sound backslash handling remain unchanged.
Buffer overflow or a device error cannot be accepted as a successful partial search.

Current implementation bounds apply even on a large GPU: each dispatch uses at most 8 GiB of
device memory and reserves the larger of 64 MiB or 10% of free VRAM. Individual beginning,
stem, and ending strings are limited to 4,096 bytes, and the Rust adapter accepts at most one
million raw matches per batch. Exceeding a memory, string, or hit-capacity bound causes CPU
fallback in `auto` or an error in forced `cuda`; results are never silently truncated.

Backend, device, and performance threshold do not change candidate reach or the fingerprint.
Switching hardware therefore cannot bypass a spent-method refusal. Findings and submission use
the existing paths and checks; run notes record which backend actually performed the search,
including mixed CPU/GPU runs. GPU support is not a new recovery method.

## Troubleshooting

| symptom | next step |
|---|---|
| Unknown GPU option in an old portable binary | Run the feature build under `target/release`; installing a Toolkit does not change an existing executable. |
| Check says CUDA support was not compiled in | Rebuild with `--features cuda` only if the hardware and workload warrant it, or keep using CPU. |
| Build cannot find `nvcc` or the static runtime | Check the installed Toolkit and `NVCC`/`CUDA_PATH`/`CUDA_HOME`. Omit the feature to build CPU executables immediately. |
| NVCC rejects the host compiler | Use a compiler supported by that Toolkit release; on Windows check the x64 C++ tools/developer shell. |
| Windows reports a missing MSVCP/VCRUNTIME library before launch | Install the supported Microsoft Visual C++ Redistributable linked above. These are host runtime libraries, not CUDA Toolkit files. |
| Missing/insufficient driver, incompatible PTX, or failed kernel check | Check the GPU, driver, Toolkit, and architecture bundle. Rebuild with the default native-code bundle if the old binary contained only PTX or a restrictive architecture. Use the official guidance above if a driver update is needed. `auto` can continue on CPU; forced `cuda` reports the failure. |
| Invalid device ordinal, unsupported capability, or insufficient memory | Select an available eligible device or use CPU. Adding a Toolkit cannot change a GPU's capability or memory. |
| `auto` selects CPU on a working NVIDIA GPU | The workload or measured GPU advantage did not meet the selection rules. This is expected for small or `Meet` searches and can occur on older GPUs. |

## Validation commands

Run the default suite without CUDA software:

```text
cargo test --release
python -m unittest discover -s scripts -p "test_*.py"
python scripts/check_docs.py
```

On a machine with the CUDA build prerequisites, also compile and run the feature suite:

```text
cargo test --release --features cuda
```

The three tests that execute real GPU searches are ignored by the ordinary test run. After a
successful `--gpu-check`, run them serially on supported hardware:

```text
cargo test --release --features cuda --lib actual_cuda -- --ignored --test-threads=1
```

These tests cover hash policies and factor edge cases, native error/overflow handling, and
repeated searches alternating large target buffers. CPU/mock tests separately check automatic
selection, unavailable devices, corrupted output, checkpointing, and CPU fallback. Hardware
tests should pass before timing a new CUDA build. Large private comparison inputs and hit files
are not required for this test suite and do not belong in a source pull request.

## Integrated backend measurements: 2026-10-09

The integrated Rust/CUDA backend was measured separately from the prototype below, on the same
Windows machine: Intel Core i9-13900KS with 16 logical threads available, NVIDIA RTX PRO 6000
Blackwell, driver 596.72, CUDA Toolkit 13.3.73, and MSVC 14.44. These prepared-input API
benchmarks used identical frozen factors and 839,489 BO7 image target IDs across CPU, automatic,
and forced CUDA modes. The targets include already-known assets; matches are not new recoveries.

| forward candidates | CPU first-process seconds | Auto first-process seconds | Forced CUDA first-process seconds | distinct matched names |
|---|---:|---:|---:|---:|
| 459,883,392 | 0.6736 | 0.3428 | 0.2580 | 109 |
| 5,374,887,144 | 5.8375 | 0.3485 | 0.3476 | 2,545 |
| 222,486,555,075 | 223.8618 | 2.9344 | 2.8840 | 60,261 |

The interval includes prepared input loading, calibration when automatic selection requires it,
backend setup and transfers, search, per-hit CPU validation, and hit-file output. It excludes
shell process creation and the complete confirmer workflow: capture/table loading, exclusion
preparation, normal `start`/Git refresh, and submission. These are individual first-process
observations, not medians or promises about a complete grinding session.

Each CUDA mode was searched three times at each size. CPU search was repeated three times for
the first two sizes and once for the largest. All 18 retained Auto/forced-CUDA outputs and all
seven new CPU outputs passed independent exact-set comparison against the frozen CPU reference.
Independent verification was performed separately from the timed search. Initial diagnostic
runs that exposed an upload-ordering race are excluded from this table; the reported results
are from the corrected build with ordered transfers. All three explicit hardware tests passed,
including the large-buffer repetition regression test.

The integrated measurements establish agreement and performance for these three forward
products on this machine. They do not establish a speedup for `Meet`, generator-bound streams,
other GPUs, or the complete startup-to-submission workflow. No private names, capture data, or
hit files are published with these aggregate figures.

## Private prototype measurements: 2026-10-09

These measurements justified implementing the optional backend. They compare a **private CUDA
prototype** with the repository's CPU `search::run_best`; they are not integrated-backend or
whole-workflow speed guarantees.

Hardware: Intel Core i9-13900KS with 16 logical threads available to the process; NVIDIA RTX
PRO 6000 Blackwell with 96 GB marketed VRAM (97,887 MiB reported), Windows, driver 596.72.
The CUDA build environment is recorded above. Each case used identical frozen factors and
839,489 BO7 image target IDs, including already-known IDs, with the modern ordinary hash policy.
No target data, private source names, or hit files are included here.

| forward candidates | CPU first-process seconds | CUDA prototype first-process seconds | distinct matched names |
|---|---:|---:|---:|
| 459,883,392 | 0.9135 | 0.2516 | 109 |
| 5,374,887,144 | 5.5454 | 0.2875 | 2,545 |
| 222,486,555,075 | 216.9418 | 2.7096 | 60,261 |

The elapsed interval starts at prepared factor/target file input and ends after verified hit
output. It includes input loading, device setup, search, verification, and serialization;
it excludes shell process creation, factor generation, capture/table loading, Git/startup
refresh, exclusions, and submission. Each first-process total is one observation. Search was
also repeated three times per size, and all nine retained GPU outputs exactly matched the CPU
outputs. Repeated GPU timings reused resident allocations and must not be compared as if they
included fresh setup.

The prototype used a 10 MiB target bitmap and about 6.4 MiB of exact target IDs. Its host loader
had already replaced quadratic factor deduplication with order-preserving set membership.
The largest search exercised indexes above 2^32. Separate ordinary/alias fixtures covered empty
fragments, uppercase, backslash policy, and alias outputs with bit 63 set; overflow was checked
as a failure. These are correctness controls, not new recoveries.

The measurements do not establish GPU performance for the CPU engine's much larger peeled
target sets, the previously discussed 128 MiB bitmap regime, or other GPUs. A selective
16-target `Meet` countercase was also checked, but its tiny CPU timing was dominated by the
reporter's sleep; it is not used to claim a GPU advantage over inverse search. None of these
results implies that 96 GB of VRAM is required.

## Historical measurements: 2026-08-19

The original GPU investigation used a Ryzen 7 7800X3D (8 cores, 16 threads), 32 GB RAM,
Radeon RX 7900 XT, Windows 11, and the Cold War snapshot. These remain useful evidence about
different workloads; the earlier blanket recommendation against CUDA is superseded by the
optional, measured selection described above.

| workload | measured rate | what the rate counts |
|---|---|---|
| General CPU search, `Meet` | 3.94 × 10^10 equivalent candidates/s | 41.72 trillion candidate combinations in 1,058 s |
| Same run, actual forward work | 1.81 × 10^8 hashes/s | 191.2 billion forward hashes in 1,058 s |
| `confirm_list` from a file | 6.43 × 10^7 candidates/s | Recorded file-input throughput |
| `confirm_list` from a Python pipe | 7.7 × 10^5 candidates/s | Generator-limited throughput |

`Meet` peels endings from wanted IDs and avoids hashing the whole product. Its equivalent
candidate rate cannot be compared directly with a GPU's actual forward hashes per second.
The recorded `confirm_list` change from allocated lines to byte slices improved identical-input
CPU throughput from 5.2 million to 64.3 million candidates/s, about 12 times. A faster hashing
device cannot remove the Python pipe's generation bottleneck.

That investigation also inspected two external tools, without reproducing their GPU benchmarks:

| historical reference | evidence recorded at the time |
|---|---|
| `atian-cod-tools` / `acts hashbrutedictgpu` | OpenCL source wrote one 64-bit result per candidate into 64/128 MiB buffers, copied them to the host, and scanned every slot. This was a source audit, not a local benchmark. |
| `codehash`, author's RTX 3090 results | Flat depth-two search: 12.8 billion candidates/s; tuned bitmap: 17.5 billion/s; prefix-table backward mode: 1.11 million stems/s. |
| `codehash`, author's word-length comparison | Mean lengths 3.5, 7.5, and 15.5 characters yielded 16.7, 16.4, and 15.5 billion candidates/s respectively. |

The CPU's large peeled-set regime uses random bitmap probes and sorted-target lookup. The
old estimate of a 128 MiB bitmap and roughly 400 cycles per candidate motivated a memory-access
experiment; it did not measure this CUDA implementation. Likewise, an inferred memory
bottleneck in an external tool is not a universal limit on GPU forward search. Keep algorithm,
target-set size, setup costs, and hardware attached to every performance claim.

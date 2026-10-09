#include "backend.h"
#include <cuda_runtime.h>
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using U64 = unsigned long long;
using U32 = unsigned int;
using Clock = std::chrono::steady_clock;
constexpr U64 PRIME = 0x100000001b3ULL, MASK = 0x7fffffffffffffffULL;
constexpr U64 MAX_CHUNK = 8ULL * 1024 * 1024;
constexpr U64 MAX_HITS = 16ULL * 1024 * 1024;
constexpr U64 DEFAULT_BUDGET = 8ULL * 1024 * 1024 * 1024;
constexpr U64 MAX_STRING = 4096, HASH_BYTES_PER_LAUNCH = 64ULL * 1024 * 1024;
static_assert(sizeof(SlasherCudaStrings) == 32 && sizeof(SlasherCudaRequest) == 144);
static_assert(sizeof(SlasherCudaDevice) == 296 && sizeof(SlasherCudaResult) == 48);
static_assert(sizeof(SlasherCudaHit) == 16 && sizeof(uint64_t) == sizeof(U64));

struct Failure : std::runtime_error {
    int32_t status;
    Failure(int32_t code, const std::string& text) : std::runtime_error(text), status(code) {}
};
void require(bool condition, const char* text) {
    if (!condition) throw Failure(SLASHER_CUDA_INVALID, text);
}
void check(cudaError_t code, const char* operation) {
    if (code == cudaSuccess) return;
    int32_t status = code == cudaErrorMemoryAllocation ? SLASHER_CUDA_MEMORY : SLASHER_CUDA_RUNTIME;
    std::string message = std::string(operation) + ": " + cudaGetErrorString(code);
    if (code == cudaErrorNoDevice) {
        status = SLASHER_CUDA_UNAVAILABLE;
        message += ". Use CPU; first check for supported NVIDIA hardware and whether CUDA_VISIBLE_DEVICES hides it. Do not install CUDA for non-NVIDIA hardware.";
    } else if (code == cudaErrorInsufficientDriver || code == cudaErrorInitializationError) {
        status = SLASHER_CUDA_UNAVAILABLE;
        message += ". Use CPU. Verify supported NVIDIA hardware before installing/updating its driver: https://www.nvidia.com/Download/index.aspx (the CUDA Toolkit is not required to run this binary).";
    } else if (code == cudaErrorUnsupportedPtxVersion) {
        message += ". The driver cannot JIT this Toolkit's PTX. Use CPU or update to a compatible NVIDIA driver: https://www.nvidia.com/Download/index.aspx.";
    } else if (code == cudaErrorNoKernelImageForDevice || code == cudaErrorInvalidDeviceFunction) {
        message += ". This binary's CUDA architecture does not match the selected GPU. Use CPU or rebuild without a restrictive SLASHER_CUDA_ARCH override.";
    }
    throw Failure(status, message);
}
#define CUDA(call) check((call), #call)
U64 multiply(U64 a, U64 b) {
    if (b && a > std::numeric_limits<U64>::max() / b) throw Failure(SLASHER_CUDA_INVALID, "CUDA dimensions overflow 64 bits");
    return a * b;
}
void add_bytes(U64& total, U64 count, U64 width) {
    U64 bytes = multiply(count, width);
    if (total > std::numeric_limits<U64>::max() - bytes) throw Failure(SLASHER_CUDA_INVALID, "CUDA allocation size overflow");
    total += bytes;
}
double elapsed(Clock::time_point a, Clock::time_point b) {
    return std::chrono::duration<double, std::milli>(b - a).count();
}
struct DeviceScope {
    int previous = -1;
    explicit DeviceScope(int ordinal) { CUDA(cudaGetDevice(&previous)); if (previous != ordinal) CUDA(cudaSetDevice(ordinal)); }
    ~DeviceScope() noexcept { if (previous >= 0) (void)cudaSetDevice(previous); }
};
template<class T> struct Buffer {
    T* value = nullptr;
    explicit Buffer(U64 count) {
        U64 bytes = multiply(std::max<U64>(1, count), sizeof(T));
        require(bytes <= std::numeric_limits<size_t>::max(), "CUDA allocation exceeds host address space");
        CUDA(cudaMalloc(reinterpret_cast<void**>(&value), static_cast<size_t>(bytes)));
    }
    ~Buffer() noexcept { if (value) (void)cudaFree(value); }
    Buffer(const Buffer&) = delete;
    Buffer& operator=(const Buffer&) = delete;
};
struct Stream {
    cudaStream_t value = nullptr;
    Stream() { CUDA(cudaStreamCreateWithFlags(&value, cudaStreamNonBlocking)); }
    ~Stream() noexcept { if (value) (void)cudaStreamDestroy(value); }
};
struct Event {
    cudaEvent_t value = nullptr;
    Event() { CUDA(cudaEventCreate(&value)); }
    ~Event() noexcept { if (value) (void)cudaEventDestroy(value); }
};
struct DeviceStrings { const uint8_t* bytes; const U32* offsets; U32 count; };
struct Strings {
    Buffer<uint8_t> bytes;
    Buffer<U32> offsets;
    DeviceStrings view;
    explicit Strings(const SlasherCudaStrings& source, cudaStream_t stream) : bytes(source.bytes_len), offsets(U64(source.count) + 1),
        view{bytes.value, offsets.value, source.count} {
        if (source.bytes_len) CUDA(cudaMemcpyAsync(bytes.value, source.bytes, static_cast<size_t>(source.bytes_len), cudaMemcpyHostToDevice, stream));
        CUDA(cudaMemcpyAsync(offsets.value, source.offsets, (size_t(source.count) + 1) * sizeof(U32), cudaMemcpyHostToDevice, stream));
    }
};

template<bool Fold> __device__ U64 feed(U64 hash, const uint8_t* bytes, U32 start, U32 end) {
    for (U32 i = start; i < end; ++i) {
        uint8_t c = bytes[i];
        if (c >= 'A' && c <= 'Z') c += 32;
        if (Fold && c == '\\') c = '/';
        hash = (hash ^ c) * PRIME;
    }
    return hash;
}
template<bool Fold> __global__ void prefixes(DeviceStrings p, U64 basis, U64 start, U64 count, U64* output) {
    U64 offset = U64(blockIdx.x) * blockDim.x + threadIdx.x;
    if (offset >= count) return;
    U64 i = start + offset;
    output[i] = feed<Fold>(basis, p.bytes, p.offsets[i], p.offsets[i + 1]);
}
template<bool Fold> __global__ void pairs(const U64* p, DeviceStrings s, U64 start, U64 count, U64* output) {
    U64 offset = U64(blockIdx.x) * blockDim.x + threadIdx.x;
    if (offset >= count) return;
    U64 i = start + offset;
    U32 stem = U32(i % s.count);
    output[i] = feed<Fold>(p[i / s.count], s.bytes, s.offsets[stem], s.offsets[stem + 1]);
}
template<bool Fold> __global__ void scan(const U64* states, DeviceStrings ends,
    const U64* coarse, const U64* fine, const uint64_t* targets, U64 target_count,
    U64 start, U64 count, SlasherCudaHit* hits, U64* found, U32* overflow, U64 capacity) {
    U64 offset = U64(blockIdx.x) * blockDim.x + threadIdx.x;
    if (offset >= count) return;
    U64 i = start + offset;
    U32 ending = U32(i % ends.count);
    U64 full = feed<Fold>(states[i / ends.count], ends.bytes, ends.offsets[ending], ends.offsets[ending + 1]);
    U64 id = full & MASK;
    U32 c = U32(id & ((1ULL << 24) - 1));
    if (!(coarse[c >> 6] & (1ULL << (c & 63)))) return;
    U32 f = U32((id >> 24) & ((1ULL << 26) - 1));
    if (!(fine[f >> 6] & (1ULL << (f & 63)))) return;
    U64 lo = 0, hi = target_count;
    while (lo < hi) { U64 mid = lo + (hi - lo) / 2; if (targets[mid] < id) lo = mid + 1; else hi = mid; }
    if (lo == target_count || targets[lo] != id) return;
    U64 slot = atomicAdd(found, 1ULL);
    if (slot < capacity) hits[slot] = {i, full}; else atomicExch(overflow, 1U);
}

__global__ void self_test_kernel(U64* output) {
    const uint8_t text[] = {'M','i','X','e','D','\\','P','a','t','h'};
    if (threadIdx.x == 0) {
        output[0] = feed<false>(0x47f5817a5ef961baULL, text, 0, 10);
        output[1] = feed<true>(0x47f5817a5ef961baULL, text, 0, 10);
        output[2] = feed<false>(0xcbf29ce484222325ULL, text, 0, 10);
        output[3] = feed<true>(0xcbf29ce484222325ULL, text, 0, 10);
    }
}
void inspect_device(int ordinal, int count, SlasherCudaDevice& info) {
    cudaDeviceProp property{};
    CUDA(cudaGetDeviceProperties(&property, ordinal));
    if (property.major < 7 || (property.major == 7 && property.minor < 5))
        throw Failure(SLASHER_CUDA_UNAVAILABLE, "This CUDA backend requires compute capability 7.5 or newer; keep the CPU backend for this GPU.");
    int compute_mode = 0;
    CUDA(cudaDeviceGetAttribute(&compute_mode, cudaDevAttrComputeMode, ordinal));
    if (compute_mode == cudaComputeModeProhibited || property.maxThreadsPerBlock < 256)
        throw Failure(SLASHER_CUDA_UNAVAILABLE, "CUDA compute is unavailable on the selected device; use the CPU backend.");
    DeviceScope device(ordinal);
    size_t free = 0, total = 0;
    CUDA(cudaMemGetInfo(&free, &total));
    if (free < 64ULL * 1024 * 1024) throw Failure(SLASHER_CUDA_MEMORY, "Selected CUDA device has less than 64 MiB free; use CPU or free GPU memory.");
    Buffer<U64> output(4);
    Stream stream;
    self_test_kernel<<<1, 32, 0, stream.value>>>(output.value);
    CUDA(cudaGetLastError());
    CUDA(cudaStreamSynchronize(stream.value));
    U64 actual[4]{};
    CUDA(cudaMemcpy(actual, output.value, sizeof(actual), cudaMemcpyDeviceToHost));
    // Independently computed golden FNV values: modern ordinary/standard basis,
    // literal/folded slash, lowercase, and retained high-bit output coverage.
    const U64 expected[] = {0x87b2b6bf6f5550fcULL, 0x33123280c9ed5485ULL,
                            0xc21c092b8845b90bULL, 0xb71ac04f03947386ULL};
    if (!std::equal(std::begin(actual), std::end(actual), std::begin(expected)))
        throw Failure(SLASHER_CUDA_RUNTIME, "CUDA hashing self-test failed; results are unsafe, so use the CPU backend.");
    info.ordinal = ordinal; info.device_count = count;
    CUDA(cudaDriverGetVersion(&info.driver_version));
    CUDA(cudaRuntimeGetVersion(&info.runtime_version));
    info.major = property.major; info.minor = property.minor;
    info.total_memory = total; info.free_memory = free;
    std::strncpy(info.name, property.name, sizeof(info.name) - 1);
}
SlasherCudaDevice probe(int requested) {
    require(requested >= -1, "CUDA device ordinal must be -1 or nonnegative");
    int count = 0;
    CUDA(cudaGetDeviceCount(&count));
    if (count == 0) throw Failure(SLASHER_CUDA_UNAVAILABLE, "No NVIDIA CUDA device was found. Use CPU; install a driver only after checking GPU compatibility.");
    if (requested >= count) throw Failure(SLASHER_CUDA_UNAVAILABLE, "Requested CUDA device ordinal does not exist; check --gpu-check or use CPU.");
    SlasherCudaDevice info{};
    if (requested >= 0) { inspect_device(requested, count, info); return info; }
    std::string last;
    for (int ordinal = 0; ordinal < count; ++ordinal) {
        try { inspect_device(ordinal, count, info); return info; }
        catch (const Failure& error) { last = error.what(); }
    }
    throw Failure(SLASHER_CUDA_UNAVAILABLE, "No compatible self-tested CUDA device: " + last);
}
U64 validate_strings(const SlasherCudaStrings& strings) {
    require(strings.count > 0 && strings.offsets && (!strings.bytes_len || strings.bytes), "CUDA packed factors are empty or have null storage");
    require(strings.reserved == 0 && strings.bytes_len <= UINT32_MAX, "CUDA packed factor bytes exceed 32-bit offsets");
    require(strings.offsets[0] == 0 && strings.offsets[strings.count] == strings.bytes_len, "CUDA factor offsets must span the complete byte buffer");
    U64 maximum = 0;
    for (U64 i = 0; i < strings.count; ++i) {
        require(strings.offsets[i] <= strings.offsets[i + 1], "CUDA factor offsets are not monotonic");
        U64 length = U64(strings.offsets[i + 1]) - strings.offsets[i];
        require(length <= MAX_STRING, "CUDA factors longer than 4096 bytes require CPU search");
        maximum = std::max(maximum, length);
    }
    return maximum;
}
U64 bounded_chunk(U64 requested, U64 maximum_length) {
    return std::max<U64>(1, std::min(requested, HASH_BYTES_PER_LAUNCH / std::max<U64>(1, maximum_length)));
}
template<bool Fold> void launch(const SlasherCudaRequest& request, const Strings& p, const Strings& s, const Strings& e,
    Buffer<U64>& prefix, Buffer<U64>& pair, Buffer<U64>& coarse, Buffer<U64>& fine,
    Buffer<uint64_t>& targets, Buffer<SlasherCudaHit>& hits, Buffer<U64>& found, Buffer<U32>& overflow,
    U64 capacity, U64 total, const U64 lengths[3], cudaStream_t stream) {
    U64 prefix_chunk = bounded_chunk(262144, lengths[0]);
    U64 pair_chunk = bounded_chunk(262144, lengths[1]);
    U64 scan_chunk = bounded_chunk(request.chunk_candidates ? request.chunk_candidates : MAX_CHUNK, lengths[2]);
    U64 pair_count = U64(p.view.count) * s.view.count;
    for (U64 start = 0; start < p.view.count;) {
        U64 n = std::min<U64>(p.view.count - start, prefix_chunk);
        prefixes<Fold><<<unsigned((n + 255) / 256), 256, 0, stream>>>(p.view, request.basis, start, n, prefix.value);
        CUDA(cudaGetLastError()); start += n;
    }
    for (U64 start = 0; start < pair_count;) {
        U64 n = std::min(pair_count - start, pair_chunk);
        pairs<Fold><<<unsigned((n + 255) / 256), 256, 0, stream>>>(prefix.value, s.view, start, n, pair.value);
        CUDA(cudaGetLastError()); start += n;
    }
    for (U64 start = 0; start < total;) {
        U64 n = std::min(total - start, scan_chunk);
        scan<Fold><<<unsigned((n + 255) / 256), 256, 0, stream>>>(pair.value, e.view, coarse.value, fine.value,
            targets.value, request.target_count, start, n, hits.value, found.value, overflow.value, capacity);
        CUDA(cudaGetLastError()); start += n;
    }
}
void search(const SlasherCudaRequest& request, SlasherCudaHit* output, U64 capacity, SlasherCudaResult& result) {
    auto started = Clock::now();
    require(output && capacity > 0 && capacity <= MAX_HITS, "CUDA hit capacity must be 1..16777216");
    require(request.fold <= 1 && request.chunk_candidates <= MAX_CHUNK, "Invalid CUDA fold flag or chunk size (maximum 8388608)");
    U64 lengths[] = {validate_strings(request.begins), validate_strings(request.stems), validate_strings(request.ends)};
    U64 pair_count = multiply(request.begins.count, request.stems.count);
    U64 total = multiply(pair_count, request.ends.count);
    require(request.target_count > 0 && request.targets, "CUDA target array is empty or null");
    require(multiply(request.target_count, sizeof(uint64_t)) <= std::numeric_limits<size_t>::max(), "CUDA target array exceeds host address space");
    for (U64 i = 0; i < request.target_count; ++i)
        require(request.targets[i] <= MASK && (!i || request.targets[i - 1] < request.targets[i]), "CUDA targets must be strictly increasing unique 63-bit IDs");
    U64 bytes = 0;
    for (const SlasherCudaStrings* strings : {&request.begins, &request.stems, &request.ends}) {
        add_bytes(bytes, std::max<U64>(1, strings->bytes_len), 1); add_bytes(bytes, U64(strings->count) + 1, sizeof(U32));
    }
    add_bytes(bytes, request.target_count, 8); add_bytes(bytes, (1ULL << 18) + (1ULL << 20), 8);
    add_bytes(bytes, request.begins.count, 8); add_bytes(bytes, pair_count, 8);
    add_bytes(bytes, capacity, sizeof(SlasherCudaHit)); add_bytes(bytes, 1, 12);
    SlasherCudaDevice info = probe(request.device);
    DeviceScope device(info.ordinal);
    U64 reserve = std::max<U64>(64ULL * 1024 * 1024, info.free_memory / 10);
    U64 available = info.free_memory > reserve ? info.free_memory - reserve : 0;
    U64 budget = request.max_device_bytes ? request.max_device_bytes : DEFAULT_BUDGET;
    if (bytes > std::min(budget, available)) throw Failure(SLASHER_CUDA_MEMORY, "CUDA working set exceeds its configured/free-memory budget; use CPU or smaller factors");
    std::vector<U64> coarse(1ULL << 18), fine(1ULL << 20);
    for (U64 i = 0; i < request.target_count; ++i) {
        U64 id = request.targets[i], c = id & ((1ULL << 24) - 1), f = (id >> 24) & ((1ULL << 26) - 1);
        coarse[c >> 6] |= 1ULL << (c & 63); fine[f >> 6] |= 1ULL << (f & 63);
    }
    // A nonblocking stream does not wait for default-stream uploads. Keep every
    // transfer and dependent kernel on this stream, including repeated searches
    // whose allocations may reuse storage from the preceding invocation.
    Stream stream;
    Strings p(request.begins, stream.value), s(request.stems, stream.value), e(request.ends, stream.value);
    Buffer<uint64_t> targets(request.target_count);
    Buffer<U64> dc(coarse.size()), df(fine.size()), prefix(request.begins.count), pair(pair_count), found(1);
    Buffer<U32> overflow(1); Buffer<SlasherCudaHit> hits(capacity);
    CUDA(cudaMemcpyAsync(targets.value, request.targets, static_cast<size_t>(request.target_count * 8), cudaMemcpyHostToDevice, stream.value));
    CUDA(cudaMemcpyAsync(dc.value, coarse.data(), coarse.size() * 8, cudaMemcpyHostToDevice, stream.value));
    CUDA(cudaMemcpyAsync(df.value, fine.data(), fine.size() * 8, cudaMemcpyHostToDevice, stream.value));
    Event begin, end;
    CUDA(cudaMemsetAsync(found.value, 0, sizeof(U64), stream.value));
    CUDA(cudaMemsetAsync(overflow.value, 0, sizeof(U32), stream.value));
    CUDA(cudaStreamSynchronize(stream.value));
    auto ready = Clock::now();
    CUDA(cudaEventRecord(begin.value, stream.value));
    if (request.fold) launch<true>(request, p, s, e, prefix, pair, dc, df, targets, hits, found, overflow, capacity, total, lengths, stream.value);
    else launch<false>(request, p, s, e, prefix, pair, dc, df, targets, hits, found, overflow, capacity, total, lengths, stream.value);
    CUDA(cudaEventRecord(end.value, stream.value)); CUDA(cudaEventSynchronize(end.value));
    float kernel_ms = 0; CUDA(cudaEventElapsedTime(&kernel_ms, begin.value, end.value));
    auto read_started = Clock::now();
    U64 count = 0; U32 overflowed = 0;
    CUDA(cudaMemcpy(&count, found.value, sizeof(count), cudaMemcpyDeviceToHost));
    CUDA(cudaMemcpy(&overflowed, overflow.value, sizeof(overflowed), cudaMemcpyDeviceToHost));
    if (overflowed || count > capacity) throw Failure(SLASHER_CUDA_OVERFLOW, "CUDA hit buffer overflowed; no partial results are accepted. Use CPU or a smaller candidate product.");
    if (count) CUDA(cudaMemcpy(output, hits.value, static_cast<size_t>(count * sizeof(SlasherCudaHit)), cudaMemcpyDeviceToHost));
    result = {total, count, bytes, elapsed(started, ready), kernel_ms, elapsed(read_started, Clock::now())};
}
void error_text(char* output, uint64_t capacity, const char* message) noexcept {
    if (!output || !capacity) return;
    size_t n = static_cast<size_t>(std::min<uint64_t>(capacity - 1, std::strlen(message)));
    std::memcpy(output, message, n); output[n] = '\0';
}
template<class Fn> int32_t boundary(Fn function, char* error, uint64_t capacity) noexcept {
    if (error && capacity) error[0] = '\0';
    try { function(); return SLASHER_CUDA_OK; }
    catch (const Failure& failure) { error_text(error, capacity, failure.what()); return failure.status; }
    catch (const std::bad_alloc&) { error_text(error, capacity, "CUDA host allocation failed; use CPU or smaller factors"); return SLASHER_CUDA_MEMORY; }
    catch (const std::exception& failure) { error_text(error, capacity, failure.what()); return SLASHER_CUDA_RUNTIME; }
    catch (...) { error_text(error, capacity, "Unexpected CUDA backend failure; use CPU"); return SLASHER_CUDA_RUNTIME; }
}
} // namespace

extern "C" int32_t slasher_cuda_probe(int32_t device, SlasherCudaDevice* info, char* error, uint64_t capacity) {
    if (info) *info = {};
    return boundary([&] { require(info, "CUDA device output pointer is null"); *info = probe(device); }, error, capacity);
}
extern "C" int32_t slasher_cuda_search(const SlasherCudaRequest* request, SlasherCudaHit* hits,
    uint64_t hit_capacity, SlasherCudaResult* result, char* error, uint64_t capacity) {
    if (result) *result = {};
    return boundary([&] { require(request && result, "CUDA request/result pointer is null"); search(*request, hits, hit_capacity, *result); }, error, capacity);
}

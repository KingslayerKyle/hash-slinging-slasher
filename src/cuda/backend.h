#ifndef SLASHER_CUDA_BACKEND_H
#define SLASHER_CUDA_BACKEND_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Internal ABI: all pointers remain owned by the caller for the duration of a call.
 * Offsets has count+1 entries, beginning at zero and ending at bytes_len. Empty
 * strings are equal adjacent offsets. Preserve duplicates and original ordering.
 * The caller explicitly supplies any bare beginning and empty ending. */
typedef struct SlasherCudaStrings {
    const uint8_t *bytes;
    const uint32_t *offsets;
    uint64_t bytes_len;
    uint32_t count;
    uint32_t reserved;
} SlasherCudaStrings;

typedef struct SlasherCudaRequest {
    SlasherCudaStrings begins, stems, ends;
    const uint64_t *targets;
    uint64_t target_count;
    uint64_t basis;
    uint64_t chunk_candidates; /* 0 = bounded native default; otherwise <= 8M. */
    uint64_t max_device_bytes; /* 0 = native 8 GiB budget, also bounded by free VRAM. */
    int32_t device;            /* -1 = first supported device; >=0 = exact ordinal. */
    uint32_t fold;             /* Always ASCII lowercase; fold=1 also maps backslash. */
} SlasherCudaRequest;

typedef struct SlasherCudaHit {
    uint64_t index; /* ((begin * stem_count) + stem) * end_count + end */
    uint64_t full;
} SlasherCudaHit;

typedef struct SlasherCudaDevice {
    int32_t ordinal, device_count, driver_version, runtime_version, major, minor;
    uint64_t total_memory, free_memory;
    char name[256];
} SlasherCudaDevice;

typedef struct SlasherCudaResult {
    uint64_t candidate_count, hit_count, device_bytes;
    double setup_ms, kernel_ms, readback_ms;
} SlasherCudaResult;

enum SlasherCudaStatus {
    SLASHER_CUDA_OK = 0,
    SLASHER_CUDA_UNAVAILABLE = 1,
    SLASHER_CUDA_INVALID = 2,
    SLASHER_CUDA_MEMORY = 3,
    SLASHER_CUDA_RUNTIME = 4,
    SLASHER_CUDA_OVERFLOW = 5
};

/* Zero success; all failures include a NUL-terminated diagnostic when capacity>0.
 * Probe executes actual device hashing fixtures, not just a presence check.
 * Search either returns every hit or fails: hit_count is zero on every failure,
 * and output hits must not be consumed unless status is SLASHER_CUDA_OK.
 * No callback, allocation ownership transfer, device reset, or C++ exception crosses ABI. */
int32_t slasher_cuda_probe(int32_t device, SlasherCudaDevice *info,
                          char *error, uint64_t error_capacity);
int32_t slasher_cuda_search(const SlasherCudaRequest *request,
                           SlasherCudaHit *hits, uint64_t hit_capacity,
                           SlasherCudaResult *result, char *error, uint64_t error_capacity);

#ifdef __cplusplus
}
#endif
#endif

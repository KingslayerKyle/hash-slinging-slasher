"""Measure the two halves of the meet engine on an OpenCL device, against bench/cpu_peel.rs.

    python bench/gpu_probe.py            both halves
    python bench/gpu_probe.py peel       the multiply chain over (id, ending) pairs
    python bench/gpu_probe.py probe      random binary search into a sorted peeled set
    TABLE_MB=128 python bench/gpu_probe.py probe

Same arithmetic as `src/lib.rs:449` (`peel`), same ending vocabulary as a real pass
(`data/suffixes.txt`), so the figures are comparable with the CPU baseline in this folder and with
the rates `docs/GPU.md` already records.

Nothing here is part of the build: `numpy` and `pyopencl` only, no Cargo dependency. It measures
whether a GPU would help before anybody writes a backend.

Each half carries a positive control, because a sweep that never built a valid candidate reports a
beautiful rate. `peel` re-solves sampled pairs on the host and refuses if the GPU disagrees; `probe`
searches for keys that are really in the table and refuses unless every one of them was found.

## Measured on 2026-10-12, and what it says

| device | half | rate |
|---|---|---|
| Ryzen 7 9850X3D, 16 threads | peel | 1.44 G peels/s |
| Ryzen 7 9850X3D, 1 thread | peel | 0.22 G peels/s |
| RTX 5090, OpenCL 3.0 | peel | 145 G peels/s |
| RTX 5090, OpenCL 3.0 | probe | 5.4 G searches/s (see the caveat) |

The GPU is worth ~100x on the **peel** side, which is sequential and arithmetic-bound, and it is
the side `run_best` picks for a plan-shaped search. The probe number is flattered by cache: a
binary search's top levels touch so few distinct lines that they stay resident, so treat 5.4 G/s
as a ceiling for the search and not a rate for the filter. See `docs/GPU.md` for what follows.
"""
import os
import sys
import time

import numpy as np
import pyopencl as cl

PRIME_INVERSE = 0xCE965057AFF6957B
ID_MASK = 0x7FFFFFFFFFFFFFFF
MAX_ENDING = 32

PEEL_KERNEL = r"""
#define MAX_ENDING 32

__kernel void peel(__global const ulong *ids,
                   __global const uchar *endings,
                   __global const uchar *lengths,
                   const uint n_ids,
                   const uint n_endings,
                   __global ulong *out)
{
    uint ending = get_global_id(1);
    uint id = get_global_id(0);
    if (id >= n_ids || ending >= n_endings) return;
    ulong work = (ulong)ending * n_ids + id;

    ulong h = ids[id];
    uint base = ending * MAX_ENDING;
    uint len = lengths[ending];
    for (int step = (int)len - 1; step >= 0; step--) {
        uchar byte = endings[base + step];
        if (byte >= 'A' && byte <= 'Z') byte += 32;
        else if (byte == '\\') byte = '/';
        h = h * 0xCE965057AFF6957Bul ^ (ulong)byte;
    }
    out[work] = h;
}
"""

PROBE_KERNEL = r"""
__kernel void probe(__global const ulong *table,
                    const ulong entries,
                    __global const ulong *keys,
                    const ulong probes,
                    __global uint *hits,
                    __global ulong *ran)
{
    ulong work = (ulong)get_global_id(1) * get_global_size(0) + get_global_id(0);
    if (work >= probes) return;

    ulong key = keys[work];
    long low = 0, high = (long)entries - 1;
    while (low <= high) {
        long mid = (low + high) >> 1;
        ulong value = table[mid];
        if (value < key) low = mid + 1;
        else if (value > key) high = mid - 1;
        else { atomic_inc(hits); break; }
    }
    atomic_add(ran, 1ul);
}
"""


def endings_packed():
    """The committed ending list, one fixed row each, so the kernel can index it."""
    rows, lengths = [], []
    with open(os.path.join("data", "suffixes.txt"), encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                raw = line.encode("utf-8")
                if len(raw) > MAX_ENDING:
                    continue
                rows.append(raw + b"\0" * (MAX_ENDING - len(raw)))
                lengths.append(len(raw))
    return np.frombuffer(b"".join(rows), dtype=np.uint8), np.array(lengths, dtype=np.uint8)


def xorshift_ids(count):
    state = np.uint64(0x2545F4914F6CDD1)
    return (np.arange(count, dtype=np.uint64) * state) & ID_MASK


def host_peel(value, ending, endings_bytes, lengths):
    for step in reversed(range(int(lengths[ending]))):
        byte = int(endings_bytes[ending * MAX_ENDING + step])
        if 65 <= byte <= 90:
            byte += 32
        elif byte == 92:
            byte = 47
        value = ((value * PRIME_INVERSE) & 0xFFFFFFFFFFFFFFFF) ^ byte
    return value


def peel_bench(queue, device):
    ids_count = int(os.environ.get("IDS", "100000"))
    if ids_count < 2 or ids_count > np.iinfo(np.uint32).max:
        raise SystemExit("IDS must be between 2 and the uint32 limit")
    endings_bytes, lengths = endings_packed()
    n_endings = len(lengths)
    if not n_endings:
        raise SystemExit("No supported endings in data/suffixes.txt")
    ids = xorshift_ids(ids_count)

    mf = cl.mem_flags
    id_buf = cl.Buffer(queue.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=ids)
    end_buf = cl.Buffer(queue.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=endings_bytes)
    len_buf = cl.Buffer(queue.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=lengths)
    total = ids_count * n_endings
    if total * 8 > min(device.max_mem_alloc_size, device.global_mem_size * 3 // 4):
        raise SystemExit("Peel output exceeds this device's memory budget; reduce IDS")
    out = cl.Buffer(queue.context, mf.WRITE_ONLY, total * 8)

    kernel = cl.Kernel(cl.Program(queue.context, PEEL_KERNEL).build(), "peel")
    args = (id_buf, end_buf, len_buf, np.uint32(ids_count), np.uint32(n_endings), out)
    grid = (ids_count, n_endings)
    kernel(queue, grid, None, *args).wait()

    started = time.perf_counter()
    kernel(queue, grid, None, *args).wait()
    queue.finish()
    seconds = time.perf_counter() - started

    got = np.empty(total, dtype=np.uint64)
    cl.enqueue_copy(queue, got, out).wait()
    checked = 0
    for ending in sorted({0, min(1, n_endings - 1), min(7, n_endings - 1), n_endings // 3, n_endings - 1}):
        for index in (0, 1, ids_count // 2, ids_count - 1):
            want = host_peel(int(ids[index]), ending, endings_bytes, lengths)
            if int(got[ending * ids_count + index]) != want:
                raise SystemExit(
                    f"peel control failed at ending={ending} id={index}: "
                    f"{int(got[ending * ids_count + index]):#x} != {want:#x}"
                )
            checked += 1

    print(f"peel   backend=OpenCL device={device.name} ids={ids_count} endings={n_endings} "
          f"peels={total/1e9:.2f}B runtime={seconds*1000:.0f}ms rate={total/seconds/1e9:.1f}G/s "
          f"control={checked} pairs re-solved on host and matched")
    print(f"       store cost included: {total*8/2**30:.1f} GB written, which is part of what "
          f"this half of the engine actually does")


def probe_bench(queue, device):
    table_mb = int(os.environ.get("TABLE_MB", "480"))
    if table_mb < 1:
        raise SystemExit("TABLE_MB must be positive")
    entries = table_mb * 1024 * 1024 // 8
    if entries * 8 > min(device.max_mem_alloc_size, device.global_mem_size // 2):
        raise SystemExit("Probe table exceeds this device's memory budget; reduce TABLE_MB")
    table = np.sort(xorshift_ids(entries))
    probes = min(20_000_000, entries)
    keys = np.random.default_rng(4).permutation(table[:probes])

    mf = cl.mem_flags
    table_buf = cl.Buffer(queue.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=table)
    key_buf = cl.Buffer(queue.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=keys)
    hits = np.zeros(1, dtype=np.uint32)
    ran = np.zeros(1, dtype=np.uint64)
    hits_buf = cl.Buffer(queue.context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=hits)
    ran_buf = cl.Buffer(queue.context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=ran)

    kernel = cl.Kernel(cl.Program(queue.context, PROBE_KERNEL).build(), "probe")
    args = (table_buf, np.uint64(entries), key_buf, np.uint64(probes), hits_buf, ran_buf)
    grid = (256, (probes + 255) // 256)
    kernel(queue, grid, None, *args).wait()

    # The warm-up filled both accumulators; without this the control counts two launches as one.
    hits[...] = 0
    ran[...] = 0
    cl.enqueue_copy(queue, hits_buf, hits)
    cl.enqueue_copy(queue, ran_buf, ran)
    queue.finish()

    started = time.perf_counter()
    kernel(queue, grid, None, *args).wait()
    queue.finish()
    seconds = time.perf_counter() - started

    cl.enqueue_copy(queue, hits, hits_buf).wait()
    cl.enqueue_copy(queue, ran, ran_buf).wait()
    if int(hits[0]) != probes or int(ran[0]) != probes:
        raise SystemExit(f"probe control failed: hits={int(hits[0])} ran={int(ran[0])} "
                         f"of {probes} -- the rate below would be meaningless")

    print(f"probe  backend=OpenCL device={device.name} table={table_mb}MB "
          f"({entries:,} sorted u64) probes={probes/1e6:.0f}M runtime={seconds*1000:.0f}ms "
          f"rate={probes/seconds/1e6:.0f}M searches/s control=all {probes/1e6:.0f}M found the key")
    print(f"       the keys are the table's own {probes/1e6:.0f}M lowest entries, so the upper "
          f"levels of every search read the same few lines and stay resident. That is a ceiling "
          f"for the search, not a rate for the filter.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    device = cl.get_platforms()[0].get_devices()[0]
    queue = cl.CommandQueue(cl.Context([device]))
    print(f"platform={cl.get_platforms()[0].name} device={device.name} "
          f"units={device.max_compute_units} local_mem={device.local_mem_size/1024:.0f}KB "
          f"L2={device.global_mem_cache_size/2**20:.1f}MB "
          f"global={device.global_mem_size/2**30:.1f}GB")
    if mode in ("peel", "both"):
        peel_bench(queue, device)
    if mode in ("probe", "both"):
        probe_bench(queue, device)

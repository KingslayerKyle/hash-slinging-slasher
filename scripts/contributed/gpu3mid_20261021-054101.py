# GPU (CuPy) three-word middles for BO4 models (or any pool/game via pool= and a hwt_load.py pickle):  H _w1 _w2 _w3 [_E]
#   H = top-NH known >=2-token model prefixes, w = top-NV model tokens, E = top-NE known 1-3 token model suffixes (or none).
#   "_E" is peeled off every unnamed id (both values of the masked top bit) into one GPU hash table; every H_w1_w2_w3
#   state is looked up. Forward work NH x NV^3, table 2 x ids x (NE+1). Chance = NH x NV^3 x 2 x ids x (NE+1) / 2^64.
#   NV1/skipV1, NV2/skipV2, NV3/skipV3 = rank windows of the three middle slots (default NV/skipV). K=2: H _w2 _w3.
# usage: py gpu3mid.py <bo4.pkl> OUT.txt [NH=3000] [NV=1000] [NE=1500] [K=3] [skipH=0] [skipV=0] [skipE=0] [hold=GLOB]
#   prints  name,id_hex  for every hit (global hits: eyeball / audit before confirm_list)
import sys, pickle, collections, time
import numpy as np, cupy as cp

args = dict(a.split("=") for a in sys.argv[3:])
NH = int(args.get("NH", 3000)); NV = int(args.get("NV", 1000)); NE = int(args.get("NE", 1500))
K = int(args.get("K", 3)); SKH = int(args.get("skipH", 0)); SKV = int(args.get("skipV", 0)); SKE = int(args.get("skipE", 0))
OFF, PR, M64 = 0xCBF29CE484222325, 0x100000001B3, (1 << 64) - 1
PINV = pow(PR, -1, 1 << 64)
def st(h, s):
    for c in s.encode(): h = ((h ^ c) * PR) & M64
    return h
def un(h, s):
    for c in reversed(s.encode()): h = ((h * PINV) & M64) ^ c
    return h

d = pickle.load(open(sys.argv[1], "rb"))
POOL = args.get("pool", "xmodel")  # any pool of a bo4load.py / hwt_load.py pickle
if "offs" in d and POOL in d["offs"]: OFF = d["offs"][POOL][0]
named = set(d["named"][POOL].values())
un_ids = sorted(d["pools"][POOL] - set(d["named"][POOL]))
if "hold" in args:  # validation: names in the hold file (name per line or id,name) act as the unnamed set
    import glob
    hold = set()
    for f in glob.glob(args["hold"]):
        for l in open(f): hold.add(l.strip().split(",")[-1])
    named -= hold; un_ids = sorted(st(OFF, n) & ((1 << 63) - 1) for n in hold)
heads = collections.Counter(); tails = collections.Counter(); mid = collections.Counter()
for n in named:
    t = n.split("_")
    for i in range(2, len(t)): heads["_".join(t[:i])] += 1
    for i in range(1, min(4, len(t))): tails["_".join(t[-i:])] += 1
    for x in t[1:]:
        if x: mid[x] += 1
H = [k for k, _ in heads.most_common(SKH + NH)][SKH:]
V = [k for k, _ in mid.most_common(SKV + NV)][SKV:]
# first middle slot may use its own rank window (NV1/skipV1), the kernel slots w2,w3 use V
SKV1 = int(args.get("skipV1", SKV)); NV1 = int(args.get("NV1", NV))
V1 = [k for k, _ in mid.most_common(SKV1 + NV1)][SKV1:]
E = ([""] if SKE == 0 else []) + [k for k, _ in tails.most_common(SKE + NE)][SKE:]
nent = 2 * len(un_ids) * len(E)
print(f"ids {len(un_ids)} H {len(H)} V {len(V)} E {len(E)} K {K} V1 {len(V1)} work {len(H)*len(V1)*len(V)**(K-1):.2e} "
      f"chance {len(H)*len(V1)*len(V)**(K-1)*nent/2**64:.2f}", flush=True)

# peeled table
TB = 1 << max(20, (nent * 2 - 1).bit_length()); TM = TB - 1
keys = np.zeros(TB, dtype=np.uint64)
ids_np = np.array(un_ids, dtype=np.uint64); ids_np = np.concatenate([ids_np, ids_np | np.uint64(1 << 63)])
PINV_np = np.uint64(PINV); ent = []
with np.errstate(over="ignore"):
    for e in E:
        h = ids_np.copy()
        for c in reversed(("_" + e).encode() if e else b""): h = (h * PINV_np) ^ np.uint64(c)
        ent.append(h)
ent = np.concatenate(ent)
# host insertion (vectorised linear probing)
slot = ((ent * np.uint64(0x9E3779B97F4A7C15)) >> np.uint64(64 - TB.bit_length() + 1)).astype(np.int64)
pend = np.arange(len(ent))
while len(pend):
    s = slot[pend]
    order = np.argsort(s, kind="stable"); s = s[order]; p = pend[order]
    first = np.ones(len(s), bool); first[1:] = s[1:] != s[:-1]
    free = keys[s] == 0
    ok = first & free
    keys[s[ok]] = ent[p[ok]]
    rest = p[~ok]; slot[rest] = (slot[rest] + 1) & TM
    pend = rest
print("table", TB, "built", flush=True)

def pack(words):
    b = bytearray(); offs = []
    for w in words: offs.append(len(b)); b += ("_" + w).encode()
    offs.append(len(b)); return np.frombuffer(bytes(b), np.uint8).copy(), np.array(offs, np.int32)
# slot vocabularies: S = H_w1 (CPU, V1), thread slot w2 (V2, global memory), inner loop w3 (V3, shared memory)
SKV2 = int(args.get("skipV2", SKV)); NV2 = int(args.get("NV2", NV)); SKV3 = int(args.get("skipV3", SKV)); NV3 = int(args.get("NV3", NV))
ranked = [k for k, _ in mid.most_common(max(SKV2 + NV2, SKV3 + NV3))]
V2 = ranked[SKV2:SKV2 + NV2]; V3 = ranked[SKV3:SKV3 + NV3]
print(f"V2 {len(V2)} V3 {len(V3)}  work now {len(H)*(len(V1) if K == 3 else 1)*len(V2)*len(V3):.2e} chance "
      f"{len(H)*(len(V1) if K == 3 else 1)*len(V2)*len(V3)*nent/2**64:.2f}", flush=True)
vb2, vo2 = pack(V2); vb3, vo3 = pack(V3)

src = r"""
extern "C" __global__ void k(const unsigned long long* S, int nS, const unsigned char* vb2, const int* vo2, int nV2,
    const unsigned char* vb3, const int* vo3, int nV3,
    const unsigned long long* T, unsigned long long TM, int SH, unsigned long long* out, int* nout, int maxout) {
  extern __shared__ unsigned char sh[];
  int* so = (int*)sh; unsigned char* sb = sh + (nV3 + 1) * 4;
  for (int i = threadIdx.x; i <= nV3; i += blockDim.x) so[i] = vo3[i];
  __syncthreads();
  int tot = so[nV3];
  for (int i = threadIdx.x; i < tot; i += blockDim.x) sb[i] = vb3[i];
  __syncthreads();
  long long g = (long long)blockIdx.x * blockDim.x + threadIdx.x;
  long long si = g / nV2; int w2 = (int)(g % nV2);
  if (si >= nS) return;
  unsigned long long h = S[si];
  for (int c = vo2[w2]; c < vo2[w2 + 1]; c++) h = (h ^ vb2[c]) * 0x100000001B3ULL;
  for (int w3 = 0; w3 < nV3; w3++) {
    unsigned long long x = h;
    for (int c = so[w3]; c < so[w3 + 1]; c++) x = (x ^ sb[c]) * 0x100000001B3ULL;
    unsigned long long s = (x * 0x9E3779B97F4A7C15ULL) >> SH;
    while (true) {
      unsigned long long t = T[s];
      if (t == 0) break;
      if (t == x) { int o = atomicAdd(nout, 1); if (o < maxout) { out[o*2] = si; out[o*2+1] = ((unsigned long long)w2 << 32) | (unsigned long long)w3; } break; }
      s = (s + 1) & TM;
    }
  }
}"""
kern = cp.RawKernel(src, "k")
shmem = (len(V3) + 1) * 4 + len(vb3)
if shmem > 48 * 1024: kern.max_dynamic_shared_size_bytes = shmem
T = cp.asarray(keys); dvb2 = cp.asarray(vb2); dvo2 = cp.asarray(vo2); dvb3 = cp.asarray(vb3); dvo3 = cp.asarray(vo3)
SH = 64 - TB.bit_length() + 1
MAXO = 1 << 16
out = cp.zeros(MAXO * 2, dtype=cp.uint64); nout = cp.zeros(1, dtype=cp.int32)
# K=3: S = H_w1 ; K=2: S = H (names H_w2_w3)
Snames = [(h,) for h in H] if K == 2 else [(h, w) for h in H for w in V1]
idset = set(un_ids)
fo = open(sys.argv[2], "w"); found = 0; t0 = time.time()
CH = max(1, min(200000, (1 << 31) // len(V2)))  # states per launch
for c0 in range(0, len(Snames), CH):
    part = Snames[c0:c0 + CH]
    Sh = np.array([st(OFF, "_".join(p)) for p in part], dtype=np.uint64)
    dS = cp.asarray(Sh); nout[0] = 0
    nthreads = len(part) * len(V2); bs = 256
    kern(((nthreads + bs - 1) // bs,), (bs,), (dS, np.int32(len(part)), dvb2, dvo2, np.int32(len(V2)), dvb3, dvo3,
         np.int32(len(V3)), T, np.uint64(TM), np.int32(SH), out, nout, np.int32(MAXO)), shared_mem=shmem)
    cp.cuda.Device().synchronize()
    n = int(nout[0])
    if n > MAXO: print("WARN overflow", n, flush=True); n = MAXO
    o = cp.asnumpy(out[:2 * n]).reshape(-1, 2) if n else []
    for si, code in o:
        w2, w3 = int(code >> 32), int(code & 0xFFFFFFFF)
        base = "_".join(part[int(si)]) + "_" + V2[w2] + "_" + V3[w3]
        for e in E:
            nm = base + ("_" + e if e else "")
            x = st(OFF, nm) & ((1 << 63) - 1)
            if x in idset: fo.write(f"{nm},{x:x}\n"); found += 1
    fo.flush()
    el = time.time() - t0; frac = (c0 + len(part)) / len(Snames)
    print(f"{frac*100:5.1f}%  hits {found}  {el:.0f}s  eta {el/frac-el:.0f}s", flush=True)
print("done hits", found, flush=True)

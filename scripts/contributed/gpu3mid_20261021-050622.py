# GPU (CuPy) three-word middles for BO4 models:  H _w1 _w2 _w3 [_E]
#   H = top-NH known >=2-token model prefixes, w = top-NV model tokens, E = top-NE known 1-3 token model suffixes (or none).
#   "_E" is peeled off every unnamed id (both values of the masked top bit) into one GPU hash table; every H_w1_w2_w3
#   state is looked up. Forward work NH x NV^3, table 2 x ids x (NE+1). Chance = NH x NV^3 x 2 x ids x (NE+1) / 2^64.
# usage: py gpu3mid.py <bo4.pkl> OUT.txt [NH=3000] [NV=1000] [NE=1500] [K=3] [skipH=0] [skipV=0]
#   prints  name,id_hex  for every hit (global hits: eyeball / audit before confirm_list)
import sys, pickle, collections, time
import numpy as np, cupy as cp

args = dict(a.split("=") for a in sys.argv[3:])
NH = int(args.get("NH", 3000)); NV = int(args.get("NV", 1000)); NE = int(args.get("NE", 1500))
K = int(args.get("K", 3)); SKH = int(args.get("skipH", 0)); SKV = int(args.get("skipV", 0))
OFF, PR, M64 = 0xCBF29CE484222325, 0x100000001B3, (1 << 64) - 1
PINV = pow(PR, -1, 1 << 64)
def st(h, s):
    for c in s.encode(): h = ((h ^ c) * PR) & M64
    return h
def un(h, s):
    for c in reversed(s.encode()): h = ((h * PINV) & M64) ^ c
    return h

d = pickle.load(open(sys.argv[1], "rb"))
named = set(d["named"]["xmodel"].values())
un_ids = sorted(d["pools"]["xmodel"] - set(d["named"]["xmodel"]))
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
E = [""] + [k for k, _ in tails.most_common(NE)]
nent = 2 * len(un_ids) * len(E)
print(f"ids {len(un_ids)} H {len(H)} V {len(V)} E {len(E)} K {K} work {len(H)*len(V)**K:.2e} "
      f"chance {len(H)*len(V)**K*nent/2**64:.2f}", flush=True)

# peeled table
TB = 1 << max(20, (nent * 2 - 1).bit_length()); TM = TB - 1
keys = np.zeros(TB, dtype=np.uint64)
ent = []
for x in un_ids:
    for top in (0, 1 << 63):
        hh = x | top
        for e in E: ent.append(un(hh, "_" + e) if e else hh)
ent = np.array(ent, dtype=np.uint64)
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
    b = bytearray(); offs = [];
    for w in words: offs.append(len(b)); b += ("_" + w).encode()
    offs.append(len(b)); return np.frombuffer(bytes(b), np.uint8).copy(), np.array(offs, np.int32)
vb, vo = pack(V)

src = r'''
extern "C" __global__ void k(const unsigned long long* S, int nS, const unsigned char* vb, const int* vo, int nV,
    const unsigned long long* T, unsigned long long TM, int SH, unsigned long long* out, int* nout, int maxout, int depth) {
  extern __shared__ unsigned char sh[];
  int* so = (int*)sh; unsigned char* sb = sh + (nV + 1) * 4;
  for (int i = threadIdx.x; i <= nV; i += blockDim.x) so[i] = vo[i];
  __syncthreads();
  int tot = so[nV];
  for (int i = threadIdx.x; i < tot; i += blockDim.x) sb[i] = vb[i];
  __syncthreads();
  long long g = (long long)blockIdx.x * blockDim.x + threadIdx.x;
  // thread = (state index, w2) ; loops w3 (depth 1) or w3,w4 (depth 2)
  long long si = g / nV; int w2 = (int)(g % nV);
  if (si >= nS) return;
  unsigned long long h = S[si];
  for (int c = so[w2]; c < so[w2 + 1]; c++) h = (h ^ sb[c]) * 0x100000001B3ULL;
  int n4 = depth == 2 ? nV : 1;
  for (int w3 = 0; w3 < nV; w3++) {
    unsigned long long h3 = h;
    for (int c = so[w3]; c < so[w3 + 1]; c++) h3 = (h3 ^ sb[c]) * 0x100000001B3ULL;
    for (int w4 = 0; w4 < n4; w4++) {
      unsigned long long x = h3;
      if (depth == 2) for (int c = so[w4]; c < so[w4 + 1]; c++) x = (x ^ sb[c]) * 0x100000001B3ULL;
      unsigned long long s = (x * 0x9E3779B97F4A7C15ULL) >> SH;
      while (true) {
        unsigned long long t = T[s];
        if (t == 0) break;
        if (t == x) { int o = atomicAdd(nout, 1); if (o < maxout) { out[o*2] = si; out[o*2+1] = ((unsigned long long)w2 << 40) | ((unsigned long long)w3 << 20) | w4; } break; }
        s = (s + 1) & TM;
      }
    }
  }
}'''
kern = cp.RawKernel(src, "k")
T = cp.asarray(keys); dvb = cp.asarray(vb); dvo = cp.asarray(vo)
SH = 64 - TB.bit_length() + 1
MAXO = 1 << 16
out = cp.zeros(MAXO * 2, dtype=cp.uint64); nout = cp.zeros(1, dtype=cp.int32)
shmem = (len(V) + 1) * 4 + len(vb)
depth = K - 2  # K=3: S = H_w1 ; K=4: S = H_w1, loops w2,w3,w4
# S states: H x w1 (K=3) ; K=2 -> S = H, thread w2 = w... (use depth 1 with S=H and w3 loop -> H_w2_w3)
if K == 2:
    Snames = [(h,) for h in H]
else:
    Snames = [(h, w) for h in H for w in V]
idset = set(un_ids)
fo = open(sys.argv[2], "w"); found = 0; t0 = time.time()
CH = max(1, (1 << 31) // len(V) // 1)  # states per launch
CH = min(CH, 200000 if K < 4 else 2000)
for c0 in range(0, len(Snames), CH):
    part = Snames[c0:c0 + CH]
    Sh = np.array([st(OFF, "_".join(p)) for p in part], dtype=np.uint64)
    dS = cp.asarray(Sh); nout[0] = 0
    nthreads = len(part) * len(V); bs = 256
    kern(((nthreads + bs - 1) // bs,), (bs,), (dS, np.int32(len(part)), dvb, dvo, np.int32(len(V)), T, np.uint64(TM),
         np.int32(SH), out, nout, np.int32(MAXO), np.int32(1 if K < 4 else 2)), shared_mem=shmem)
    cp.cuda.Device().synchronize()
    n = int(nout[0])
    if n > MAXO: print("WARN overflow", n, flush=True); n = MAXO
    o = cp.asnumpy(out[:2 * n]).reshape(-1, 2) if n else []
    for si, code in o:
        w2, w3, w4 = int(code >> 40), int((code >> 20) & 0xFFFFF), int(code & 0xFFFFF)
        base = "_".join(part[int(si)]) + "_" + V[w2] + "_" + V[w3] + ("_" + V[w4] if K >= 4 else "")
        hb = st(OFF, base)
        for e in E:
            nm = base + ("_" + e if e else "")
            x = st(OFF, nm) & ((1 << 63) - 1) if e else hb & ((1 << 63) - 1)
            if x in idset: fo.write(f"{nm},{x:x}\n"); found += 1
    fo.flush()
    el = time.time() - t0; frac = (c0 + len(part)) / len(Snames)
    print(f"{frac*100:5.1f}%  hits {found}  {el:.0f}s  eta {el/frac-el:.0f}s", flush=True)
print("done hits", found, flush=True)

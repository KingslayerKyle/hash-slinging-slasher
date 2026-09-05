"""Solve printable final-two-byte variants for sound_asset names (BO4 no-fold or CW)."""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import snapshot

MASK=(1<<64)-1; TOP=1<<63; PRIME=0x100000001B3; INV=pow(PRIME,-1,1<<64)
PRINTABLE=range(0x20,0x7f)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--game",required=True); ap.add_argument("--no-fold",action="store_true"); a=ap.parse_args()
    snap=next(snapshot.read(p) for p in snapshot.snapshots() if a.game.lower() in os.path.basename(p).lower())
    hasher=snapshot.fnv1a_nofold if a.no_fold else snapshot.fnv1a
    known=set(snapshot.table_names("fnv1a_xsounds")); known.update(snapshot.confirmed_names("sound_asset"))
    prefixes={}
    for seed in known:
        seed=seed.strip().lower()
        if len(seed)<3: continue
        pre=seed[:-2]; h=hasher(pre); prefixes.setdefault(h>>8,[]).append((h&0xff,pre))
    wanted=[i for i,p in snap.records if snap.pool_name(p)=="sound_asset"]
    found=set()
    for target in wanted:
        scaled=(target*INV)&MASK
        for last in PRINTABLE:
            v=((scaled^last)*INV)&MASK
            for low,pre in prefixes.get(v>>8,()):
                first=low^(v&0xff)
                if first not in PRINTABLE: continue
                c=pre+chr(first)+chr(last)
                if hasher(c)==target: found.add(c)
    print(f"{a.game}: {len(known):,} seeds, {len(wanted):,} targets, {len(found):,} exact candidates",file=sys.stderr)
    print("\n".join(sorted(found)))
if __name__=="__main__": main()

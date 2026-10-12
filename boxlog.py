#!/usr/bin/env python3
"""boxlog.py "<opener>" — the interval narrowing as a log a solver-free script can check: one line per round,
'round | lo a..я | hi a..я'. Round 0 is 1..99 everywhere. Check: each round r+1 equals
lo_t = max(lo_t, base_t + sum_l min P[v][t] over v in [lo_l, hi_l]) and hi_t the same with max, from round r alone.
base_t = letters t in (opener + " и") + 1. P = enc.P, written out as table99.txt (sha256 5067ecd3...)."""
import sys, enc
op = sys.argv[1]; P = enc.P; base = [b + 1 for b in enc.vec(op + " и")]; lo, hi = [1] * 33, [99] * 33; r = 0
print(f"# opener: {op}\n# base: {' '.join(map(str, base))}")
while True:
    print(f"{r}|{' '.join(map(str, lo))}|{' '.join(map(str, hi))}")
    nlo = [max(lo[t], base[t] + sum(min(P[v][t] for v in range(lo[l], hi[l] + 1)) for l in range(33))) for t in range(33)]
    nhi = [min(hi[t], base[t] + sum(max(P[v][t] for v in range(lo[l], hi[l] + 1)) for l in range(33))) for t in range(33)]
    if (nlo, nhi) == (lo, hi): break
    lo, hi = nlo, nhi; r += 1
assert (lo, hi) == enc.box(op), "log disagrees with enc.box"
print(f"# fixed point after {r} rounds; equals enc.box()")

#!/usr/bin/env python3
"""ablate.py <letter> — rosenrot #85103: fix с=1, drop one letter's floor (its count need not cover its phrases), solve.
Narrowing and CNF as celld.py; the dropped letter gets no narrowing rule and no running sum."""
import sys, subprocess, cell, cellbox, celld
A = cell.A; x = A.index(sys.argv[1])
real = cellbox.narrow
def narrow(fix, log=print):
    keep = cell.FLOOR[x]; cellbox.FLOOR[x] = -10**6
    try: return real(fix, log)
    finally: cellbox.FLOOR[x] = keep
D, r = narrow([(A.index("с"), 1)], log=lambda s: None)
cell.FLOOR[x] = -10**6; celld.FLOOR[x] = -10**6
D[x] = {v for v in D[x] if v <= 39 and "с" not in cell.enc.num(v) + cell.enc.noun(v)} or D[x]
n, cl, b = celld.encode([d if i != x else d for i, d in enumerate(D)])
open("/tmp/ag/ab.cnf", "w").write(f"p cnf {n} {len(cl)}\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in cl))
rc = subprocess.run(["timeout", "100", "kissat", "-q", "/tmp/ag/ab.cnf"], capture_output=True).returncode
print(sys.argv[1], {10: "SAT", 20: "UNSAT", 124: "timeout"}.get(rc, rc))

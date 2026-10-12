#!/usr/bin/env python3
"""cyc.py — zenith's full-coverage control (#84960): 99 vectors by cyclic shift, letter i of vector k = ((i + k) mod 99) + 1,
so each of the 33x99 = 3267 (letter, value) cells of the CNF's table is fixed exactly once. Synthetic base as in synth.py
(base_t = c_t - letters t in c's phrases), so each fixed vector must be SAT. Also logs min(base): rosenrot (#84961) points out
negative bases take a different branch of the encoder than real openers (base >= 1)."""
import subprocess, enc
P = enc.P
def s(c): return [sum(P[c[l]][t] for l in range(33)) for t in range(33)]
log = open("cyc.log", "a"); cells = set(); bad = []; negs = 0
for k in range(99):
    c = [((i + k) % 99) + 1 for i in range(33)]; cells |= {(i, c[i]) for i in range(33)}
    base = [c[t] - s(c)[t] for t in range(33)]; negs += min(base) < 1
    n, cl, ge = enc.encode("", base=base)
    u = [ge[l][c[l]] for l in range(33) if c[l] >= 2] + [-ge[l][c[l] + 1] for l in range(33) if c[l] < 99]
    with open("tmp/cyc.cnf", "w") as f:
        f.write(f"p cnf {n} {len(cl) + len(u)}\n"); f.writelines(" ".join(map(str, x)) + " 0\n" for x in cl + [[x] for x in u])
    rc = subprocess.run(["kissat", "-q", "tmp/cyc.cnf"], capture_output=True).returncode
    if rc != 10: bad.append((k, rc))
    line = f"vec{k} min_base={min(base)} max_base={max(base)} rc={rc}"; print(line, flush=True); log.write(line + "\n"); log.flush()
end = f"cells covered {len(cells)}/3267, vectors 99, SAT {99 - len(bad)}, not SAT {bad}, vectors with some base<1: {negs}"
print(end); log.write(end + "\n")

#!/usr/bin/env python3
"""pos.py — rosenrot's caveat (#84961): synthetic controls with base < 1 take a different branch of the encoder than real
openers (base >= 1: every GE(t, k + base) is a variable, never the constant TRUE). Here every vector has base_t >= 1 for all
33 letters, the real-opener branch. Seeded repair search (c_t <- phrases_t + 1 + r until c_t - phrases_t >= 1 everywhere),
then a greedy subset covering as many (letter, value) cells as the 400 candidates reach. Fixed: must be SAT (all chosen
vectors); every +-1 neighbour: SAT exactly when a direct recount says so (first NB_VECS vectors only: one CPU)."""
import random, subprocess, enc
A, P = enc.A, enc.P
def s(c): return [sum(P[c[l]][t] for l in range(33)) for t in range(33)]
cand = []
for seed in range(400):
    rng = random.Random(seed); c = [rng.randint(1, 99) for _ in range(33)]
    for _ in range(200):
        sc = s(c); bad = [t for t in range(33) if c[t] - sc[t] < 1]
        if not bad: break
        for t in bad: c[t] = min(99, sc[t] + 1 + rng.randint(0, 40))
    if all(c[t] - s(c)[t] >= 1 for t in range(33)): cand.append(c)
reach = set((i, c[i]) for c in cand for i in range(33)); chosen, cov = [], set()
while cov != reach:
    c = max(cand, key=lambda c: len({(i, c[i]) for i in range(33)} - cov)); chosen.append(c); cov |= {(i, c[i]) for i in range(33)}
log = open("pos.log", "a"); log.write(f"candidates {len(cand)}, cells reachable {len(reach)}/3267, chosen vectors {len(chosen)}\n"); log.flush()
mism = runs = 0; NB_VECS = 10
for k, c in enumerate(chosen):
    base = [c[t] - s(c)[t] for t in range(33)]
    n, cl, ge = enc.encode("", base=base); body = "".join(" ".join(map(str, x)) + " 0\n" for x in cl)
    def run(v):
        u = [ge[l][v[l]] for l in range(33) if v[l] >= 2] + [-ge[l][v[l] + 1] for l in range(33) if v[l] < 99]
        open("tmp/pos.cnf", "w").write(f"p cnf {n} {len(cl) + len(u)}\n" + body + "".join(f"{x} 0\n" for x in u))
        return subprocess.run(["kissat", "-q", "tmp/pos.cnf"], capture_output=True).returncode
    bad = [] if run(c) == 10 else ["fixed"]; nb = 0
    for l in (range(33) if k < NB_VECS else []):
        for d in (-1, 1):
            v = c[:l] + [c[l] + d] + c[l + 1:]
            if not 1 <= v[l] <= 99: continue
            want = 10 if all(v[t] == base[t] + s(v)[t] for t in range(33)) else 20; nb += 1
            if run(v) != want: bad.append((A[l], v[l], want))
    runs += nb + 1; mism += len(bad)
    line = f"vec{k} min_base={min(base)} neighbours={nb} mismatches={bad}"; print(line, flush=True); log.write(line + "\n"); log.flush()
end = f"cells {len(cov)}/3267 on the base>=1 branch, runs {runs}, mismatches {mism}"; print(end); log.write(end + "\n")

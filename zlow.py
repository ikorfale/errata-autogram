#!/usr/bin/env python3
"""zlow.py — zenith #85001: three base>=1 vectors with low в/е/т that pos.py's upward repair never reached.
(1) fix each as units: must be SAT; every +-1 neighbour SAT exactly when a direct recount says so.
(2) downward repair (zenith's idea): for each of the 529 cells pos.py missed, repair the other letters choosing,
among admissible values, those with the fewest target letters; keep vectors with base>=1 on all 33; fix them in SAT."""
import random, subprocess, enc
A, P = enc.A, enc.P
def s(c): return [sum(P[c[l]][t] for l in range(33)) for t in range(33)]
Z = {"в=34": "50 35 34 1 37 16 1 1 1 15 1 36 1 7 30 33 14 16 16 44 45 1 1 15 10 5 1 1 10 30 1 1 11",
     "е=3": "59 41 40 1 43 3 1 1 1 21 1 40 1 1 33 33 11 20 11 33 35 1 1 13 1 1 1 1 11 21 1 1 11",
     "т=7": "62 41 48 1 42 18 1 1 1 8 1 41 1 17 41 42 1 8 22 7 40 1 1 8 1 7 1 1 8 21 1 1 2"}
log = open("zlow.log", "a")
def out(x): print(x, flush=True); log.write(x + "\n"); log.flush()
def check(c, nbrs):
    base = [c[t] - s(c)[t] for t in range(33)]
    n, cl, ge = enc.encode("", base=base); body = "".join(" ".join(map(str, x)) + " 0\n" for x in cl)
    def run(v):
        u = [ge[l][v[l]] for l in range(33) if v[l] >= 2] + [-ge[l][v[l] + 1] for l in range(33) if v[l] < 99]
        open("tmp/zlow.cnf", "w").write(f"p cnf {n} {len(cl) + len(u)}\n" + body + "".join(f"{x} 0\n" for x in u))
        return subprocess.run(["kissat", "-q", "tmp/zlow.cnf"], capture_output=True).returncode
    bad = [] if run(c) == 10 else ["fixed"]; nb = 0
    for l in (range(33) if nbrs else []):
        for d in (-1, 1):
            v = c[:l] + [c[l] + d] + c[l + 1:]
            if not 1 <= v[l] <= 99: continue
            want = 10 if all(v[t] == base[t] + s(v)[t] for t in range(33)) else 20; nb += 1
            if run(v) != want: bad.append((A[l], v[l], want))
    return min(base), nb, bad
tot = mism = 0
for name, z in Z.items():
    c = list(map(int, z.split())); mb, nb, bad = check(c, True); tot += nb + 1; mism += len(bad)
    out(f"zenith {name} min_base={mb} neighbours={nb} mismatches={bad}")
# (2) the cells pos.py's 400 candidates did not reach (same seeds as pos.py)
cand = []
for seed in range(400):
    rng = random.Random(seed); c = [rng.randint(1, 99) for _ in range(33)]
    for _ in range(200):
        sc = s(c); bad = [t for t in range(33) if c[t] - sc[t] < 1]
        if not bad: break
        for t in bad: c[t] = min(99, sc[t] + 1 + rng.randint(0, 40))
    if all(c[t] - s(c)[t] >= 1 for t in range(33)): cand.append(c)
reach = set((i, c[i]) for c in cand for i in range(33)); miss = sorted(set((i, v) for i in range(33) for v in range(1, 100)) - reach)
out(f"pos.py reach {len(reach)}, missed {len(miss)}")
found = {}
for (t, v) in miss:
    if (t, v) in found: continue
    for seed in range(60):
        rng = random.Random(1000 * t + v + 7919 * seed); c = [rng.randint(1, 99) for _ in range(33)]; c[t] = v
        for _ in range(200):
            sc = s(c); bad = [l for l in range(33) if l != t and c[l] - sc[l] < 1]
            if not bad: break
            for l in bad:
                ok = list(range(sc[l] + 1, 100))
                if not ok: break
                m = min(P[x][t] for x in ok); c[l] = rng.choice([x for x in ok if P[x][t] == m])
        sc = s(c)
        if all(c[l] - sc[l] >= 1 for l in range(33)):
            for i in range(33): found.setdefault((i, c[i]), c[:])
            break
newc = {k for k in found if k in set(miss)}
out(f"downward repair: {len(newc)}/{len(miss)} missed cells now have a base>=1 vector")
still = sorted(set(miss) - newc); per = {}
for i, v in still: per.setdefault(A[i], []).append(v)
out("still unreached: " + "; ".join(f"{k} {min(vs)}..{max(vs)} ({len(vs)})" for k, vs in per.items()))
chosen, cov = [], set()
pool = list({tuple(c) for c in found.values()})
while cov != newc:
    c = max(pool, key=lambda c: len({(i, c[i]) for i in range(33)} & newc - cov)); chosen.append(list(c)); cov |= {(i, c[i]) for i in range(33)} & newc
out(f"chosen {len(chosen)} vectors to fix")
for k, c in enumerate(chosen):
    mb, nb, bad = check(c, k < 5); tot += nb + 1; mism += len(bad)
    out(f"low{k} min_base={mb} neighbours={nb} mismatches={bad}")
out(f"zlow total runs {tot}, mismatches {mism}, base>=1 cells now {len(reach) + len(newc)}/3267")

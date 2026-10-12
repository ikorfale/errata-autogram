#!/usr/bin/env python3
"""synth.py — test the CNF's numeral table on every value 1..99, which the nine known autograms do not reach (they use 1..49).
For a vector c, set a synthetic opener base_t = c_t - (letters t in the 33 number phrases of c). Then c is by construction
a solution of the CNF with that base, whatever c is. Fix c as units: must be SAT. Move one letter by +-1: SAT exactly when
Python's direct recount says the moved vector also satisfies count = base + phrases (computed here, no solver).
9 vectors, each a slice of 3 shuffled permutations of 1..99, so every value sits at 3 different letters. Seeded."""
import random, subprocess, enc
A, P = enc.A, enc.P
def s(c): return [sum(P[c[l]][t] for l in range(33)) for t in range(33)]
def ok(c, base): return all(1 <= x <= 99 for x in c) and all(c[t] == base[t] + s(c)[t] for t in range(33))
rng = random.Random(20261012); vals = []
for _ in range(3): p = list(range(1, 100)); rng.shuffle(p); vals += p
log = open("synth.log", "a"); seen = set(); total = mism = 0
for i in range(9):
    c = vals[33 * i: 33 * i + 33]; base = [c[t] - s(c)[t] for t in range(33)]; seen |= set(c)
    n, cl, ge = enc.encode("", base=base); body = "".join(" ".join(map(str, x)) + " 0\n" for x in cl)
    def run(v):
        u = [ge[l][v[l]] for l in range(33) if v[l] >= 2] + [-ge[l][v[l] + 1] for l in range(33) if v[l] < 99]
        open("tmp/s.cnf", "w").write(f"p cnf {n} {len(cl) + len(u)}\n" + body + "".join(f"{x} 0\n" for x in u))
        return subprocess.run(["kissat", "-q", "tmp/s.cnf"], capture_output=True).returncode
    rc0 = run(c); bad = [] if rc0 == 10 else [("fixed", rc0)]; nb = 0
    for l in range(33):
        for d in (-1, 1):
            v = c[:l] + [c[l] + d] + c[l + 1:]
            if not 1 <= v[l] <= 99: continue
            nb += 1; want = 10 if ok(v, base) else 20; got = run(v)
            if got != want: bad.append((A[l], v[l], want, got))
    total += nb + 1; mism += len(bad)
    line = f"vec{i} min_base={min(base)} fixed_rc={rc0} neighbours={nb} mismatches={bad}"; print(line, flush=True); log.write(line + "\n")
end = f"values covered {len(seen)}/99, runs {total}, mismatches {mism}"; print(end); log.write(end + "\n")

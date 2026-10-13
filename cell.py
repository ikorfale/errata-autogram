#!/usr/bin/env python3
"""cell.py — rosenrot #85082 / zenith #85090: is a single (letter, value) cell reachable at all, with no opener?
Template without the opener: "<num> <noun> «a», ..., и <num> <noun> «я»." Each letter needs count_t - phrases_t >= 1
(its quote), и >= 2 (quote + conjunction); the rest is slack an opener would have to fill. Same order encoding and exact
running sums as enc.py, but the link is one-way: phrases_t <= count_t - floor_t. One cell fixed as unit clauses.

  cell.py <letter> <value> out.cnf      writes the CNF (+ .map); kissat 10 = SAT, 20 = UNSAT
  cell.py --decode out.cnf model.txt    vector from a SAT model, recounted directly against the floors
"""
import sys, json, enc
A, P, MAX = enc.A, enc.P, enc.MAX
FLOOR = [2 if a == "и" else 1 for a in A]
def phrases(c): return [sum(P[c[l]][t] for l in range(33)) for t in range(33)]
def ok(c): ph = phrases(c); return all(c[t] - ph[t] >= FLOOR[t] for t in range(33))

def encode(fix):
    nv = [0]; cl = []
    def new(): nv[0] += 1; return nv[0]
    T, F = "T", "F"
    def add(*lits):
        out = []
        for x in lits:
            if x == T: return
            if x == F: continue
            out.append(x)
        if not out: raise SystemExit("empty clause during encoding")
        cl.append(out)
    def neg(x): return F if x == T else T if x == F else -x
    ge = [[None] * (MAX + 2) for _ in A]
    for l in range(33):
        for m in range(2, MAX + 1): ge[l][m] = new()
        for m in range(2, MAX): add(-ge[l][m + 1], ge[l][m])
    def GE(l, m): return T if m <= 1 else F if m > MAX else ge[l][m]
    b = [[None] * (MAX + 1) for _ in A]
    for l in range(33):
        for v in range(1, MAX + 1):
            x = new(); b[l][v] = x; p, q = GE(l, v), GE(l, v + 1)
            add(-x, p); add(-x, neg(q)); add(x, neg(p), q)
    for t in range(33):
        add(GE(t, FLOOR[t]))
        if all(P[v][t] == 0 for v in P): continue
        CAP = MAX - FLOOR[t]
        prev = lambda k: T if k <= 0 else F
        for l in range(33):
            ds = sorted({P[v][t] for v in P})
            g = {}
            for d in ds:
                vs = [v for v in P if P[v][t] == d]; g[d] = new()
                for v in vs: add(-b[l][v], g[d])
                add(-g[d], *[b[l][v] for v in vs])
            S = [None] + [new() for _ in range(CAP)]
            cur = (lambda S: (lambda k: T if k <= 0 else F if k > CAP else S[k]))(S)
            for d in ds:
                for k in range(1, CAP + 2):
                    if k <= CAP:
                        add(-g[d], neg(prev(k - d)), cur(k)); add(-g[d], prev(k - d), neg(cur(k)))
                    else:
                        add(-g[d], neg(prev(k - d)))
            for k in range(1, CAP): add(-S[k + 1], S[k])
            prev = cur
        for k in range(1, CAP + 1): add(neg(prev(k)), GE(t, k + FLOOR[t]))   # phrases_t >= k  ->  count_t >= k + floor
    for (l, v) in fix:
        add(GE(l, v)); add(neg(GE(l, v + 1)))
    return nv[0], cl, ge

if __name__ == "__main__":
    if sys.argv[1] == "--decode":
        cnf, model = sys.argv[2:4]; ge = json.load(open(cnf + ".map")); lits = set()
        for line in open(model):
            if line.startswith("v"): lits |= {int(x) for x in line.split()[1:] if int(x) > 0}
        c = [max([1] + [m for m in range(2, MAX + 1) if ge[l][m] in lits]) for l in range(33)]
        print(" ".join(map(str, c))); print("floors hold on direct recount:", ok(c))
    else:
        fix = [(A.index(sys.argv[i]), int(sys.argv[i + 1])) for i in range(1, len(sys.argv) - 1, 2)]
        out = sys.argv[-1]; n, cl, ge = encode(fix)
        with open(out, "w") as f:
            f.write(f"p cnf {n} {len(cl)}\n"); f.writelines(" ".join(map(str, c)) + " 0\n" for c in cl)
        json.dump(ge, open(out + ".map", "w")); print(out, n, "vars", len(cl), "clauses")

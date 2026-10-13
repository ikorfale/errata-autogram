#!/usr/bin/env python3
"""celld.py — cell.py's CNF built directly over the narrowed domains from cellbox.py (values outside D_l do not exist).
Sound only together with cellbox.py's rounds, which are printed and checkable. One-hot per letter over D_l, order
literals ge[l][m] for m in D_l, exact running sums capped at max(D_t) - floor_t, one-way link phrases_t <= count_t - floor_t.
  celld.py <letter> <value> out.cnf"""
import sys, json, cell, cellbox
A, P, FLOOR = cell.A, cell.P, cell.FLOOR
def encode(D):
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
    Ds = [sorted(d) for d in D]
    b = [{v: new() for v in Ds[l]} for l in range(33)]
    for l in range(33):
        add(*b[l].values())
        vs = Ds[l]
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)): add(-b[l][vs[i]], -b[l][vs[j]])
    for t in range(33):
        if FLOOR[t] < -1000: continue                 # ablate.py: letter with no floor
        cap = Ds[t][-1] - FLOOR[t]
        if all(P[v][t] == 0 for l in range(33) for v in Ds[l]): continue
        prev = lambda k: T if k <= 0 else F
        for l in range(33):
            ds = sorted({P[v][t] for v in Ds[l]})
            if ds == [0]: continue
            g = {}
            for d in ds:
                vs = [v for v in Ds[l] if P[v][t] == d]; g[d] = new()
                for v in vs: add(-b[l][v], g[d])
                add(-g[d], *[b[l][v] for v in vs])
            S = [None] + [new() for _ in range(cap)]
            cur = (lambda S, cap: (lambda k: T if k <= 0 else F if k > cap else S[k]))(S, cap)
            for d in ds:
                for k in range(1, cap + 2):
                    if k <= cap:
                        add(-g[d], neg(prev(k - d)), cur(k)); add(-g[d], prev(k - d), neg(cur(k)))
                    else:
                        add(-g[d], neg(prev(k - d)))
            for k in range(1, cap): add(-S[k + 1], S[k])
            prev = cur
        for k in range(1, cap + 1):                   # phrases_t >= k  ->  count_t >= k + floor_t
            add(neg(prev(k)), *[b[t][v] for v in Ds[t] if v >= k + FLOOR[t]])
    return nv[0], cl, b
if __name__ == "__main__":
    L, V, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    D, r = cellbox.narrow([(A.index(L), V)], log=lambda s: None)
    n, cl, b = encode(D)
    with open(out, "w") as f:
        f.write(f"p cnf {n} {len(cl)}\n"); f.writelines(" ".join(map(str, c)) + " 0\n" for c in cl)
    json.dump([{str(v): x for v, x in d.items()} for d in b], open(out + ".map", "w")); print(out, n, "vars", len(cl), "clauses, narrowing rounds", r)

def decode(mapf, model):
    b = json.load(open(mapf)); lits = set()
    for line in open(model):
        if line.startswith("v"): lits |= {int(x) for x in line.split()[1:] if int(x) > 0}
    return [next(int(v) for v, x in b[l].items() if x in lits) for l in range(33)]

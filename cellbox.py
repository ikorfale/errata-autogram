#!/usr/bin/env python3
"""cellbox.py — domain narrowing for one fixed cell, printed round by round so anyone can recheck it by hand or code.
Rule (zenith #85090, on sets, not intervals): value v of letter l is dropped when
  v - P[v][l] - sum over m != l of min_{u in D_m} P[u][l] < floor_l.
Also: with с fixed at value 1, the quote alone uses it, so no number phrase may contain с.
  cellbox.py <letter> <value> in.cnf out.cnf   appends the dropped values as unit clauses (-b[l][v]) to a copy."""
import sys, json, cell
A, P, MAX, FLOOR = cell.A, cell.P, cell.MAX, cell.FLOOR
def narrow(fix, log=print):
    D = [set(range(1, MAX + 1)) for _ in A]
    for l, v in fix: D[l] = {v}
    r = 0
    while True:
        r += 1; drop = []
        mins = [[min(P[u][t] for u in D[m]) for t in range(33)] for m in range(33)]
        for l in range(33):
            rest = sum(mins[m][l] for m in range(33) if m != l)
            for v in sorted(D[l]):
                if v - P[v][l] - rest < FLOOR[l]: drop.append((l, v))
        for t in range(33):                       # letter t's total floor: count_t >= floor_t + sum of mins, count_t fixed
            if len(D[t]) == 1:
                cap = next(iter(D[t])) - FLOOR[t]
                for m in range(33):
                    other = sum(mins[k][t] for k in range(33) if k != m)
                    for u in sorted(D[m]):
                        if (m, u) not in drop and P[u][t] + other > cap and m != t: drop.append((m, u))
        if not drop: return D, r - 1
        for l, v in drop: D[l].discard(v)
        log(f"round {r}: dropped {len(drop)}: " + " ".join(f"{A[l]}{v}" for l, v in drop[:400]))
        if any(not d for d in D): log("empty domain"); return D, r
if __name__ == "__main__":
    L, V, src, dst = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    D, r = narrow([(A.index(L), V)])
    for l in range(33):
        d = sorted(D[l]); print(A[l], len(d), d if len(d) < 30 else f"{d[0]}..{d[-1]}")
    ge = json.load(open(src + ".map"))
    # b[l][v] variables are not in the map; express "count_l != v" through ge: -(ge>=v and not ge>=v+1)
    def GE(l, m): return None if m <= 1 or m > MAX else ge[l][m]
    units = []
    for l in range(33):
        for v in range(1, MAX + 1):
            if v in D[l]: continue
            p, q = GE(l, v), GE(l, v + 1)
            units.append([x for x in ((-p) if p else None, q) if x is not None])
    head, body = open(src).read().split("\n", 1); n, m = head.split()[2:]
    with open(dst, "w") as f:
        f.write(f"p cnf {n} {int(m) + len(units)}\n"); f.write(body); f.writelines(" ".join(map(str, u)) + " 0\n" for u in units)
    print("added", len(units), "clauses")

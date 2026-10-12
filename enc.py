#!/usr/bin/env python3
"""Russian 33-letter autogram as CNF, written independently of the CP-SAT models in board thread 84683.
No narrowing box: every count ranges over 1..99. Order encoding for each count (ge[l][m] = count of letter l >= m)
and, per target letter, an exact running sum of the letters contributed by the 33 number phrases.

  enc.py "<opener>" out.cnf        writes CNF + out.cnf.map (variable numbers for decoding)
  enc.py --decode "<opener>" out.cnf model.txt   builds the sentence from a SAT model and recounts it
"""
import sys, json
A = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
U = ["", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять", "одиннадцать",
     "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"]
T = {2: "двадцать", 3: "тридцать", 4: "сорок", 5: "пятьдесят", 6: "шестьдесят", 7: "семьдесят", 8: "восемьдесят", 9: "девяносто"}
def num(n): return U[n] if n < 20 else T[n // 10] + ("" if n % 10 == 0 else " " + U[n % 10])
def noun(n):
    if 11 <= n % 100 <= 14: return "букв"
    return "буква" if n % 10 == 1 else "буквы" if 2 <= n % 10 <= 4 else "букв"
def vec(s): s = s.lower(); return [s.count(a) for a in A]
def sentence(opener, c):
    parts = [f"{num(c[i])} {noun(c[i])} «{a}»" for i, a in enumerate(A)]
    return f"{opener} " + ", ".join(parts[:-1]) + " и " + parts[-1] + "."
MAX = 99
P = {v: vec(f"{num(v)} {noun(v)}") for v in range(1, MAX + 1)}

def box(opener):
    """Interval narrowing, my own code: count_t lies in base_t + sum over letters l of [min, max] of P[v][t], v in D_l."""
    base = [b + 1 for b in vec(opener + " и")]
    lo, hi = [1] * 33, [MAX] * 33
    while True:
        nlo = [max(lo[t], base[t] + sum(min(P[v][t] for v in range(lo[l], hi[l] + 1)) for l in range(33))) for t in range(33)]
        nhi = [min(hi[t], base[t] + sum(max(P[v][t] for v in range(lo[l], hi[l] + 1)) for l in range(33))) for t in range(33)]
        if any(a > b for a, b in zip(nlo, nhi)): return None
        if (nlo, nhi) == (lo, hi): return lo, hi
        lo, hi = nlo, nhi

def encode(opener, use_box=False):
    base = [b + 1 for b in vec(opener + " и")]           # opener, the final "и", and each quoted letter once
    nv = [0]; cl = []
    def new(): nv[0] += 1; return nv[0]
    TRUE, FALSE = "T", "F"
    def add(*lits):                                      # drop clause if a literal is TRUE, drop FALSE literals
        out = []
        for x in lits:
            if x == TRUE: return
            if x == FALSE: continue
            if x == "-T": continue
            if x == "-F": return
            out.append(x)
        if not out: raise SystemExit("empty clause during encoding: trivially UNSAT, check the encoder")
        cl.append(out)
    def neg(x): return {TRUE: FALSE, FALSE: TRUE}.get(x, -x) if not isinstance(x, str) else ("F" if x == "T" else "T")
    ge = [[None] * (MAX + 2) for _ in A]
    for l in range(33):
        for m in range(2, MAX + 1): ge[l][m] = new()
        for m in range(2, MAX): add(-ge[l][m + 1], ge[l][m])
    def GE(l, m): return TRUE if m <= 1 else FALSE if m > MAX else ge[l][m]
    b = [[None] * (MAX + 1) for _ in A]
    for l in range(33):
        for v in range(1, MAX + 1):
            x = new(); b[l][v] = x; p, q = GE(l, v), GE(l, v + 1)
            add(-x, p); add(-x, neg(q)); add(x, neg(p), q)
    for t in range(33):
        if all(P[v][t] == 0 for v in P):                 # letter never in a number phrase: count fixed by the opener
            add(GE(t, base[t])); add(neg(GE(t, base[t] + 1))); continue
        CAP = MAX - base[t]
        prev = lambda k: TRUE if k <= 0 else FALSE       # running sum before letter 0
        for l in range(33):
            ds = sorted({P[v][t] for v in P})
            if ds == [0]: continue
            g = {}
            for d in ds:
                vs = [v for v in P if P[v][t] == d]; g[d] = new()
                for v in vs: add(-b[l][v], g[d])
                add(-g[d], *[b[l][v] for v in vs])
            S = [None] + [new() for _ in range(CAP)]
            cur = (lambda S: (lambda k: TRUE if k <= 0 else FALSE if k > CAP else S[k]))(S)
            for d in ds:
                for k in range(1, CAP + 2):
                    if k <= CAP:
                        add(-g[d], neg(prev(k - d)), cur(k)); add(-g[d], prev(k - d), neg(cur(k)))
                    else:
                        add(-g[d], neg(prev(k - d)))     # overflow past 99 is impossible
            for k in range(1, CAP): add(-S[k + 1], S[k])
            prev = cur
        for k in range(1, CAP + 1):                      # total contributed == count - base
            add(neg(prev(k)), GE(t, k + base[t])); add(prev(k), neg(GE(t, k + base[t])))
        add(GE(t, base[t]))
    if use_box:                                          # box as unit clauses: the proof is relative to it
        lo, hi = box(opener)
        for l in range(33): add(GE(l, lo[l])); add(neg(GE(l, hi[l] + 1)))
    return nv[0], cl, ge

if __name__ == "__main__":
    if sys.argv[1] == "--decode":
        opener, cnf, model = sys.argv[2:5]
        ge = json.load(open(cnf + ".map")); lits = set()
        for line in open(model):
            if line.startswith("v"): lits |= {int(x) for x in line.split()[1:] if int(x) > 0}
        c = [max([1] + [m for m in range(2, MAX + 1) if ge[l][m] in lits]) for l in range(33)]
        s = sentence(opener, c); real = vec(s)
        print(" ".join(map(str, c))); print(s); print("recount equal:", real == c, "letters:", sum(real))
    else:
        use_box = "--box" in sys.argv; args = [a for a in sys.argv[1:] if a != "--box"]
        opener, out = args[:2]; n, cl, ge = encode(opener, use_box)
        with open(out, "w") as f:
            f.write(f"p cnf {n} {len(cl)}\n"); f.writelines(" ".join(map(str, c)) + " 0\n" for c in cl)
        json.dump(ge, open(out + ".map", "w")); print(out, n, "vars", len(cl), "clauses")

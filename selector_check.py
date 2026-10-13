#!/usr/bin/env python3
"""selector_check.py — rosenrot #85456: rebuild the ordered 3129 witness labels and the 137 impossible labels from
my own table rule (cover2.py), compare sha256 with his, then redo his draw sha256("85287:"+i) mod 3129."""
import hashlib, re, cell
A = cell.A; P = cell.P
imp = {(t, v) for t in range(33) for v in range(1, 100)
       if v - P[v][t] - 32 * min(P[x][t] for x in range(1, 100)) < cell.FLOOR[t]}
c1 = (A.index("с"), 1)
allc = [(t, v) for t in range(33) for v in range(1, 100)]
lab = lambda c: f"{A[c[0]]}{c[1]}"
wit = [lab(c) for c in allc if c not in imp and c != c1]
bad = [lab(c) for c in allc if c in imp]
h = lambda xs: hashlib.sha256(("\n".join(xs) + "\n").encode()).hexdigest()
print("impossible", len(bad), h(bad)); print("witness", len(wit), h(wit))
print("match 773f..:", h(bad).startswith("773fb9ef"), " match d9ba..:", h(wit).startswith("d9ba7c8a"))
# published labels in #85184/#85194: rosenrot19 + earlier lists; I use rosenrot's skip report to cross-check instead
taken, out, skips = set(), [], []
pub = {"л59", "г31"}  # the two skips he reports as published; any other published hit would show as a mismatch below
i = 0
while len(out) < 60:
    k = int(hashlib.sha256(f"85287:{i}".encode()).hexdigest(), 16) % len(wit)
    if k in taken or wit[k] in pub: skips.append((i, k, wit[k]))
    else: taken.add(k); out.append(wit[k])
    i += 1
print("draws", i, "skips", skips)
his = "э91 а18 щ63 х15 б50 д80 п11 я88 ф1 р6 з54 н50 г94 ь25 й78 в71 п59 е37 п47 э35 ч8 ф95 р52 п40 г33 и65 п70 ш73 и9 т91 ч60 ш86 ч1 и17 и2 ё37 с39 э21 а6 ш33 щ38 ь30 ь58 п77 ч50 е25 ю72 м63 ц85 ю56 ы3 ф96 й99 ж68 ъ88 ю37 к93 ё74 у56 я76".split()
print("draw order equals his list:", out == his)
mine60 = [l.split()[0] for l in open("rosenrot60.txt", encoding="utf-8") if l.strip()]
print("same set as the 60 lines in #85311:", set(mine60) == set(his), "| same order:", mine60 == his)

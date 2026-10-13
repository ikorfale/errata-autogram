#!/usr/bin/env python3
"""cover2.py — coverage after #85059 (zenith: 15 vectors, 5 more table cells), #85082 (rosenrot: 19 vectors), с=1 (cell1.log).
Every incoming vector is rechecked here against the floors (cell.ok) before it counts."""
import json, cell
A = cell.A; src = open("coverage.py").read().split("fl = [")[0]; g = {}; exec(src.split("\n", 3)[3].replace("import json, matplotlib; matplotlib.use(\"Agg\"); import matplotlib.pyplot as plt, numpy as np", ""), g)
P = cell.P; old = g["cov"]
imp = {(t, v) for t in range(33) for v in range(1, 100)
       if v - P[v][t] - 32 * min(P[x][t] for x in range(1, 100)) < cell.FLOOR[t]}   # zenith #85059 exact table rule
print("table-impossible", len(imp))
op = {(t, v) for t in range(33) for v in range(1, 100)} - old - imp
Z = """в35: 50 34 35 1 30 17 1 1 1 14 1 36 1 6 30 16 5 14 14 40 36 1 1 15 7 7 1 1 13 24 1 1 7
в36: 45 34 36 1 36 15 1 1 1 10 1 36 1 6 20 17 7 11 13 35 34 1 1 15 5 7 1 1 5 27 1 1 10
в37: 55 35 37 1 34 16 1 1 1 13 1 35 1 5 24 15 9 15 10 40 34 1 1 16 5 3 1 1 10 27 1 1 13
в38: 57 34 38 1 36 17 1 1 1 13 1 36 1 9 24 21 10 14 13 41 35 1 1 16 5 5 1 1 13 30 1 1 11
в40: 62 34 40 1 37 23 1 1 1 12 1 35 1 4 20 34 6 16 11 36 34 1 1 15 7 5 1 1 15 23 1 1 7
в42: 46 34 42 1 35 20 1 1 1 12 1 36 1 3 20 19 7 15 8 35 34 1 1 14 5 4 1 1 15 22 1 1 10
в44: 49 34 44 1 35 25 1 1 1 12 1 36 1 6 23 32 6 18 13 36 34 1 1 15 8 7 1 1 17 26 1 1 6
д4: 8 45 47 7 4 40 6 4 4 8 8 43 8 18 8 40 5 18 40 46 46 7 8 8 8 7 3 7 17 40 3 4 7
е3: 50 35 35 1 35 3 1 1 1 15 1 35 1 3 30 31 11 15 10 41 35 1 1 15 1 3 1 1 5 23 1 1 13
о2: 60 34 50 2 35 30 2 2 2 13 2 35 2 4 30 2 7 15 9 37 34 2 2 14 7 2 2 2 23 23 2 1 10
с3: 54 34 43 1 39 15 1 1 1 12 1 39 1 1 25 25 9 15 3 39 34 1 1 15 5 1 1 1 12 25 1 1 14
т7: 42 40 49 1 40 20 1 1 1 8 1 42 1 10 21 40 8 8 21 7 40 1 1 8 1 1 1 1 8 20 1 1 8
ы1: 65 36 45 1 36 15 1 1 1 9 1 36 1 7 20 27 5 9 13 31 36 1 1 12 1 8 1 1 1 28 1 1 8
ь9: 44 40 44 1 41 30 1 1 1 4 1 44 1 4 40 40 4 24 13 20 41 1 1 8 10 4 1 1 19 9 1 1 4
я1: 48 36 44 1 40 23 1 1 1 12 1 38 1 6 32 33 4 17 14 34 34 1 1 16 6 7 1 1 16 22 1 1 1"""
R = open("rosenrot19.txt").read()
vecs = [list(map(int, l.split(":")[1].split())) for l in Z.splitlines()] + [list(map(int, l.split()[1:])) for l in R.splitlines() if l.strip()]
bad = [v for v in vecs if not cell.ok(v)]
print("incoming vectors", len(vecs), "fail the floors:", len(bad))
newsat = {(i, v[i]) for v in vecs if cell.ok(v) for i in range(33)}
table5 = set()
s1 = {(A.index("с"), 1)}
print("open before", len(op))
left = op - newsat - table5 - s1
print("closed by vectors", len(op & newsat), "by table (5 cells)", len(op & table5), "by DRAT (с1)", len(op & s1))
print("open now", len(left), ":", " ".join(f"{A[l]}{v}" for l, v in sorted(left)))
print("old 'run' cells the exact table rule calls impossible:", sorted((A[t], v) for t, v in old & imp), "| old run cells", len(old))

#!/usr/bin/env python3
"""coverage.py — the 33x99 (letter, value) grid on the base>=1 branch: run with a fixed vector (SAT), impossible by the
template floor, open. Recomputes the pos.py and zlow.py searches (no SAT) and draws coverage.png."""
import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
src = open("zlow.py").read()
pre = src.split("tot = mism = 0")[0]; mid = "cand = []" + src.split("cand = []", 1)[1].split("chosen, cov = [], set()")[0]
g = {}; exec(pre.replace('log = open("zlow.log", "a")', 'log = open("/dev/null", "w")').replace("print(x, flush=True); ", "") + "\n" + mid, g)
A, P = g["A"], g["P"]; cov = g["reach"] | g["newc"]
for z in g["Z"].values(): c = list(map(int, z.split())); cov |= {(i, c[i]) for i in range(33)}
fl = [33 * min(P[x][t] for x in range(1, 100)) + 1 for t in range(33)]
M = np.zeros((33, 99))
for t in range(33):
    for v in range(1, 100): M[t, v - 1] = 0 if (t, v) in cov else (1 if v < fl[t] else 2)
counts = {k: int((M == i).sum()) for i, k in enumerate(["fixed_sat", "impossible", "open"])}
json.dump(counts, open("coverage.json", "w")); print(counts)
from matplotlib.colors import ListedColormap
fig, ax = plt.subplots(figsize=(12, 5.2), dpi=150)
ax.imshow(M, cmap=ListedColormap(["#d9dde3", "#3a3f47", "#e0702b"]), aspect="auto", interpolation="nearest",
          extent=(0.5, 99.5, 32.5, -0.5), vmin=0, vmax=2)
ax.set_yticks(range(33)); ax.set_yticklabels(A, fontsize=7); ax.set_xticks([1, 10, 20, 30, 34, 40, 50, 60, 70, 80, 90, 99])
ax.tick_params(length=0, labelsize=8); ax.set_xlabel("letter count in the autogram vector", fontsize=9)
for s in ax.spines.values(): s.set_visible(False)
ax.set_title("Encoder controls on the real-opener branch (base ≥ 1): which (letter, count) cells were run", loc="left", fontsize=11)
import matplotlib.patches as mp
ax.legend(handles=[mp.Patch(color="#d9dde3", label=f"run with a fixed vector, SAT ({counts['fixed_sat']})"),
                   mp.Patch(color="#3a3f47", label=f"impossible: «буква/буквы/букв» puts б, в, к, у in every clause ({counts['impossible']})"),
                   mp.Patch(color="#e0702b", label=f"open: no vector found yet ({counts['open']})")],
          loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8, frameon=False)
plt.tight_layout(); plt.savefig("coverage.png")

#!/usr/bin/env python3
"""check60.py — rosenrot #85311: 60 more witness lines chosen by sha256("85287:"+k) mod 3129.
Each line: cell label (letter+value) then 33 counts. Checks with my own counter (cell.ok, enc.P tables):
33 fields, label value == count at that letter, every letter's floor holds (count - phrases >= floor)."""
import hashlib, cell
A = cell.A; raw = open("rosenrot60.txt", "rb").read()
for tail in (raw, raw.rstrip(b"\n")):
    print("sha256", len(tail), "B", hashlib.sha256(tail).hexdigest())
lines = [l for l in raw.decode().splitlines() if l.strip()]
fails = []
for l in lines:
    lab, *xs = l.split(); c = list(map(int, xs)); letter, val = lab[0], int(lab[1:])
    why = []
    if len(c) != 33: why.append(f"{len(c)} fields")
    elif c[A.index(letter)] != val: why.append(f"label {val} != count {c[A.index(letter)]}")
    elif not cell.ok(c):
        ph = cell.phrases(c); why += [f"{A[t]}: {c[t]}-{ph[t]}<{cell.FLOOR[t]}" for t in range(33) if c[t] - ph[t] < cell.FLOOR[t]]
    if why: fails.append((lab, why))
cells = {l.split()[0] for l in lines}
print(f"lines {len(lines)}, distinct cells {len(cells)}, pass {len(lines)-len(fails)}, fail {len(fails)}")
for f in fails: print("FAIL", *f)
# control: the counter must be able to say no. Drop each line's largest count to 1 (number words still spell the
# other letters), expect a floor failure on most lines.
neg = 0
for l in lines:
    c = list(map(int, l.split()[1:])); i = max(range(33), key=lambda t: c[t]); c[i] = 1; neg += not cell.ok(c)
print(f"control: largest count -> 1, rejected {neg}/{len(lines)}")

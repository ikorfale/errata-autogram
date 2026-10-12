#!/usr/bin/env python3
"""nine.py — encoding controls on the nine published level-2 autograms (rosenrot #84902, sha256 edd8c3a0...da93).
(b) per opener, CNF without box: the vector fixed as units must be SAT; each neighbour (one letter +-1, >=1) must be UNSAT.
(a) per opener, CNF with box, nothing fixed: must be SAT, and the decoded vector must recount exactly.
One line per run in nine.log."""
import subprocess, sys, json, time, hashlib, enc
NINE = [l.split("|") for l in open("nine.txt", encoding="utf-8").read().splitlines()]
def solve(path, extra, t=600):
    head, body = open(path).read().split("\n", 1); n, m = head.split()[2:]
    open("tmp/n.cnf", "w").write(f"p cnf {n} {int(m) + len(extra)}\n" + body + "".join(f"{x} 0\n" for x in extra))
    t0 = time.time(); r = subprocess.run(["kissat", "-q", f"--time={t}", "tmp/n.cnf"], capture_output=True, text=True)
    return r.returncode, time.time() - t0, r.stdout
def units(ge, c): return [ge[l][c[l]] for l in range(33) if c[l] >= 2] + [-ge[l][c[l] + 1] for l in range(33) if c[l] < 99]
log = open("nine.log", "a"); mode = sys.argv[1]
def out(s): print(s, flush=True); log.write(s + "\n"); log.flush()
for op, s in NINE:
    c = [int(x) for x in s.split()]
    if mode == "b":
        n, cl, ge = enc.encode(op); open("tmp/o.cnf", "w").write(f"p cnf {n} {len(cl)}\n" + "".join(" ".join(map(str, x)) + " 0\n" for x in cl))
        rc, dt, _ = solve("tmp/o.cnf", units(ge, c)); bad = []
        nb = 0
        for l in range(33):
            for d in (-1, 1):
                v = c[l] + d
                if v < 1: continue
                nb += 1; r2, _, _ = solve("tmp/o.cnf", units(ge, c[:l] + [v] + c[l + 1:]))
                if r2 != 20: bad.append((enc.A[l], v, r2))
        out(f"b {op}|fixed_rc={rc} neighbours={nb} non_unsat={bad}")
    else:
        subprocess.run(["python3", "enc.py", "--box", op, "tmp/a.cnf"], check=True, capture_output=True)
        rc, dt, model = solve("tmp/a.cnf", [], 1800); res = ""
        if rc == 10:
            open("tmp/a.model", "w").write(model)
            r = subprocess.run(["python3", "enc.py", "--decode", op, "tmp/a.cnf", "tmp/a.model"], capture_output=True, text=True).stdout.splitlines()
            res = f"vec_equal_published={r[0].split() == s.split()} {r[2]}"
        out(f"a {op}|rc={rc} solve_s={dt:.0f} {res}")

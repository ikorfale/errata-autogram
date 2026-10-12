#!/bin/bash
# controls.sh — is the encoding right? Fix a known autogram's vector (bazooqa/rosenrot, board thread 84683, #84725/#84812)
# as unit clauses: must be SAT. Raise one count by one: must be UNSAT. Also rebuilds both known sentences from their vectors.
set -eu; cd "$(dirname "$0")"
python3 enc.py --box "В этой фразе" ctlbox.cnf >/dev/null
python3 - <<'PY'
import json, enc
known = {"В этой фразе": "38 34 45 1 30 20 1 1 2 9 2 35 1 5 14 14 7 15 7 35 34 2 1 14 6 2 1 1 13 25 2 1 8",
         "В данной строке": "45 34 43 1 34 20 1 1 1 11 2 37 1 4 20 20 2 17 9 32 34 1 1 14 6 3 1 1 16 18 1 1 3"}
for op, s in known.items():
    c = [int(x) for x in s.split()]; print(f"recount {op!r}: {enc.vec(enc.sentence(op, c)) == c}")
ge = json.load(open("ctlbox.cnf.map")); head, body = open("ctlbox.cnf").read().split("\n", 1); n, m = head.split()[2:]
c = [int(x) for x in known["В этой фразе"].split()]
for name, vec in (("fixed", c), ("bad", c[:14] + [c[14] + 1] + c[15:])):
    u = [ge[l][vec[l]] for l in range(33) if vec[l] >= 2] + [-ge[l][vec[l] + 1] for l in range(33) if vec[l] < 99]
    open(f"tmp/{name}.cnf", "w").write(f"p cnf {n} {int(m) + len(u)}\n" + body + "".join(f"{x} 0\n" for x in u))
PY
for f in fixed bad; do set +e; kissat -q tmp/$f.cnf > /dev/null; rc=$?; set -e; echo "control $f: kissat rc=$rc (10 = SAT, 20 = UNSAT)"; done
rm -f tmp/fixed.cnf tmp/bad.cnf

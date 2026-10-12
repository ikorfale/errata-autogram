#!/bin/bash
# cube.sh <base> <letter_index> <v1> [v2 ...] — for each value v: CNF + units "count[letter] == v", kissat with a binary
# DRAT proof, drat-trim check, then delete the proof (disk is small). One line per cube in <base>.cubes.log.
set -u; base=$1; L=$2; shift 2; W=$PWD/tmp
for v in "$@"; do
  python3 - "$base" "$L" "$v" "$W" <<'PY'
import json, sys
base, L, v = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); ge = json.load(open(base + ".cnf.map"))
head, body = open(base + ".cnf").read().split("\n", 1); n, m = head.split()[2:]
u = ([ge[L][v]] if v >= 2 else []) + ([-ge[L][v + 1]] if v + 1 <= 99 else [])
open(sys.argv[4] + "/cube.cnf", "w").write(f"p cnf {n} {int(m) + len(u)}\n" + body + "".join(f"{x} 0\n" for x in u))
PY
  t0=$(date +%s); ( ulimit -f 1400000; exec kissat -q --time=${CUBE_TIME:-2400} $W/cube.cnf $W/cube.drat > $W/cube.out ); rc=$?; t1=$(date +%s)
  sz=$(stat -c %s $W/cube.drat 2>/dev/null || echo 0); chk="-"
  if [ $rc = 20 ]; then chk=$(drat-trim $W/cube.cnf $W/cube.drat 2>&1 | tr "\r" "\n" | grep -aE "^s (VERIFIED|NOT)" | head -1); fi
  t2=$(date +%s)
  echo "$(date -u +%FT%TZ) letter=$L value=$v kissat_rc=$rc solve_s=$((t1-t0)) proof_bytes=$sz check='$chk' check_s=$((t2-t1)) cnf_sha=$(sha256sum $W/cube.cnf | cut -c1-16)" >> $base.cubes.log
  [ $rc = 10 ] && cp $W/cube.out $base.L$L.v$v.model
  rm -f $W/cube.drat
done

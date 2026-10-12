#!/bin/bash
# first batch: the cubes CP-SAT found easiest first, to learn timing; then the control opener without a proof
cd "$(dirname "$0")"
CUBE_TIME=2400 ./cube.sh rovnobox 11 43 41 40 39 38 37 36 35 34
( kissat --time=3600 ctlbox.cnf > ctlbox.out 2>&1; echo rc=$? >> ctlbox.out )

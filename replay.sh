#!/bin/sh
# Replay checks from this folder. Python 3.11+ stdlib only. Exits nonzero on any failure.
# No command output is piped, so every exit status reaches `set -e`.
#   sh replay.sh          default: steps 1-7
#   sh replay.sh full     also reruns Program A on every sweep value (slow, several CPU-hours)
# REPLAY_E2E=1 is set only by checker/neg/e2e_replay.sh (skips steps 1-2 and 7 inside its copies).
set -e
case "${1-}" in ""|full) ;; *) echo "Usage: sh replay.sh [full]" >&2; exit 2 ;; esac
cd "$(dirname "$0")"
R=$(pwd)
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT HUP INT TERM
if [ -z "${REPLAY_E2E-}" ]; then
  echo "1. checker self-tests (1 valid + 4 corrupted certificates)"; sh checker/run_tests.sh
  echo "2. negative tests for compare_A, compare_C and the B/C/lemma validators"; sh checker/neg/run_neg.sh
fi
echo "3. brute-force validators (B: 197 cases, C: 188 cases, lemmas: 5166 cases)"
(cd "$T" && python3 "$R/progB/verify.py" > "$T/vB.txt") || { cat "$T/vB.txt"; echo "B validator FAILED"; exit 1; }
echo "B validator PASS"
(cd progC && python3 validate.py > "$T/vC.txt") || { cat "$T/vC.txt"; echo "C validator FAILED"; exit 1; }
tail -1 "$T/vC.txt"
(cd progB && python3 lemmacheck.py)
echo "4. logic + exact inequalities of all 17 certificates"; python3 checker/check_cert.py certs/cert_n*.json.gz
echo "5. Program C recomputes every density in every certificate"
for n in $(seq 4 20); do python3 checker/compare_C.py certs/cert_n$n.json.gz progC/progC.py; done
echo "6. certificate sweep values vs SAVED Program A logs (A is not rerun here)"
for n in $(seq 4 20); do python3 checker/compare_A.py certs/cert_n$n.json.gz logs/progA_sweeps/n$n.log; done
if [ -z "${REPLAY_E2E-}" ]; then
  echo "7. end-to-end: replay.sh itself must fail on a broken copy of this bundle"; sh checker/neg/e2e_replay.sh
fi
if [ "${1-}" = full ]; then
  echo "8. rerun Program A for every sweep value, then compare"
  for n in $(seq 4 20); do (cd progA && python3 sweepA.py $n 1000 > "$T/n$n.log")
    python3 checker/compare_A.py certs/cert_n$n.json.gz "$T/n$n.log"; done
fi
rm -rf "$T"
echo "ALL CHECKS PASSED"
# Regenerating the certificates themselves (Program B): cd progB && python3 gen_cert.py N 1000 2000000 out.json.gz

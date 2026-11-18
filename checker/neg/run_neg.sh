#!/bin/sh
# Negative tests: every case must make the tool under test exit nonzero.
cd "$(dirname "$0")"; R=../..; T=$(mktemp -d); fails=0
# expect_fail NAME "EXPECTED DIAGNOSTIC" CMD...: CMD must exit nonzero AND print the expected diagnostic.
expect_fail() { name=$1; want=$2; shift 2
  if "$@" > $T/out.txt 2>&1; then echo "BAD  $name (exited 0)"; fails=$((fails+1))
  elif ! grep -qF -- "$want" $T/out.txt; then echo "BAD  $name (wrong reason; wanted: $want)"; tail -3 $T/out.txt; fails=$((fails+1))
  else echo "ok   $name: $(tail -1 $T/out.txt | cut -c1-150)"; fi; }
C4=$R/certs/cert_n4.json.gz; L4=$R/logs/progA_sweeps/n4.log
: > $T/empty.log;                     expect_fail compareA_empty_log "no values compared"      python3 ../compare_A.py $C4 $T/empty.log
grep -v '^n=4 m=500 ' $L4 > $T/miss.log; expect_fail compareA_missing_m "1 sweep m missing from A log (500..500)"     python3 ../compare_A.py $C4 $T/miss.log
sed 's|^n=4 m=9 d1=5/14 |n=4 m=9 d1=5/13 |' $L4 > $T/val.log; expect_fail compareA_wrong_value "DIFF n=4 m=9" python3 ../compare_A.py $C4 $T/val.log
{ cat $L4; grep '^n=4 m=20 ' $L4; } > $T/dup.log; expect_fail compareA_duplicate_row "duplicate log row m=20" python3 ../compare_A.py $C4 $T/dup.log
{ cat $L4; echo 'n=5 m=7 d1=1/7 '; } > $T/n.log; expect_fail compareA_wrong_n_row "log row for n=5"   python3 ../compare_A.py $C4 $T/n.log
for mode in value missing duplicate wrong_n; do
  case $mode in value) w="1 differ";; missing) w="rows missing 1";; duplicate) w="duplicate Program C row";; wrong_n) w="Program C row for n=5";; esac
  expect_fail compareC_$mode "$w" env FAKEC_MODE=$mode python3 ../compare_C.py $C4 fakeC.py
done
python3 - $C4 $T/conf.json.gz <<'PY'
import gzip, json, sys
c = json.load(gzip.open(sys.argv[1], 'rt')); m0 = str(c['m0'])
c['points'][m0]['delta1'] = '1/3'          # conflicts with the sweep value at m0
json.dump(c, gzip.open(sys.argv[2], 'wt'))
PY
expect_fail compareC_conflicting_claims "conflicting certificate claims" python3 ../compare_C.py $T/conf.json.gz $R/progC/progC.py
expect_fail checker_conflicting_claims "points[m0].delta1 != sweep value at m0"  python3 ../check_cert.py $T/conf.json.gz
expect_fail validatorB_injected_fault "MISMATCH 3 9" python3 fault_validators.py B
expect_fail validatorC_injected_fault "MISMATCH 3 9" python3 fault_validators.py C
expect_fail lemmacheck_injected_fault "violations 13" python3 fault_validators.py lemma
rm -rf $T
if [ $fails -eq 0 ]; then echo "ALL NEGATIVE TESTS PASSED"; else echo "$fails NEGATIVE TESTS FAILED"; exit 1; fi

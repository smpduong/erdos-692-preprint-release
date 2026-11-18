#!/bin/sh
# End-to-end negative tests: copy the bundle, break one thing, run replay.sh on the copy.
# Each copy must make replay.sh exit nonzero, print the expected diagnostic, and NOT print
# "ALL CHECKS PASSED".
cd "$(dirname "$0")/../.."; R=$(pwd); fails=0
case_run() {  # case_run NAME "EXPECTED DIAGNOSTIC" PYTHON-SNIPPET-THAT-BREAKS-THE-COPY
  W=$(mktemp -d); mkdir "$W/b"
  cp -r certs checker progA progB progC logs replay.sh "$W/b/"
  (cd "$W/b" && python3 -c "$3")
  if REPLAY_E2E=1 sh "$W/b/replay.sh" > "$W/out.txt" 2>&1; then echo "BAD  e2e_$1 (replay exited 0)"; fails=$((fails+1))
  elif grep -qF "ALL CHECKS PASSED" "$W/out.txt"; then echo "BAD  e2e_$1 (printed ALL CHECKS PASSED)"; fails=$((fails+1))
  elif ! grep -qF -- "$2" "$W/out.txt"; then echo "BAD  e2e_$1 (wrong reason; wanted: $2)"; tail -3 "$W/out.txt"; fails=$((fails+1))
  else echo "ok   e2e_$1: replay failed with: $2"; fi
  rm -rf "$W"
}
case_run validatorC_fault "MISMATCH 3 9" "
p='progC/validate.py'; s=open(p).read(); old='a,b,c,d=compute(n,M)'; assert old in s
open(p,'w').write(s.replace(old, old + '; c += ((n,M)==(3,9))'))"
case_run validatorB_fault "MISMATCH 3 9" "
p='progB/verify.py'; s=open(p).read(); old='    return res[0], res[1]\n'; assert old in s
open(p,'w').write(s.replace(old, '    return res[0], res[1] + (F(1,10**6) if (n,m)==(3,9) else 0)\n'))"
case_run certificate_value "1 differ" "
import gzip, json
p='certs/cert_n4.json.gz'; c=json.load(gzip.open(p,'rt'))
c['sweep_delta1'][494][1] = '1/7'   # m=500: still below the peak, so only Program C can catch it
json.dump(c, gzip.open(p,'wt'))"
if [ $fails -eq 0 ]; then echo "ALL END-TO-END TESTS PASSED"; else echo "$fails END-TO-END TESTS FAILED"; exit 1; fi

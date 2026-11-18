#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 verify_integrity.py
python3 checker/check_cert.py certs/cert_n*.json.gz
sh checker/run_tests.sh
sh checker/neg/run_neg.sh
python3 checker/independent_peak_check.py .
echo "QUICK CHECKS PASSED; no complete density recomputation performed"

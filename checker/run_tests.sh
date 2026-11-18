#!/usr/bin/env bash
# Builds fixtures from tests/valid.json, then checks that the valid one passes (exit 0)
# and each corrupted one fails (exit 1).
DIR="$(cd "$(dirname "$0")" && pwd)"
CASES=$(mktemp -d)
trap 'rm -rf "$CASES"' EXIT HUP INT TERM
python3 "$DIR/tests/make_cases.py" "$CASES" || exit 1

fails=0
run() {  # run <expected_exit> <cert> <expected diagnostic substring>
    out=$(python3 "$DIR/check_cert.py" "$2" 2>&1)
    rc=$?
    if [ "$rc" -eq "$1" ] && printf "%s" "$out" | grep -qF -- "$3"; then
        echo "ok   expect=$1 got=$rc $(basename "$2")"
    else
        echo "BAD  expect=$1 got=$rc $(basename "$2") (wanted message: $3)"
        fails=$((fails + 1))
    fi
    echo "     $out"
}

run 0 "$CASES/valid.json.gz" "PASS: m in"
run 1 "$CASES/bad_tie.json.gz" "maximizer not unique"
run 1 "$CASES/bad_gap.json.gz" "not contiguous"
run 1 "$CASES/bad_bound.json.gz" "not strictly below peak"
run 1 "$CASES/bad_tail.json.gz" "tail bound d0(M)+d1(M) not strictly below peak"

echo
if [ "$fails" -eq 0 ]; then echo "ALL TESTS PASSED"; else echo "$fails TEST(S) FAILED"; fi
exit $((fails > 0))

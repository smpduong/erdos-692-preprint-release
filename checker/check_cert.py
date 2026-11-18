#!/usr/bin/env python3
"""Stdlib-only checker for delta1(n,m) peak certificates.

Checks only the logic and exact arithmetic of a supplied certificate; it
computes no densities. All decisions use fractions.Fraction.

Usage: python3 check_cert.py cert1.json.gz [cert2.json.gz ...]
Exit 0 only if every certificate passes; exit 1 otherwise.
"""
import gzip
import json
import sys
from fractions import Fraction as F
sys.set_int_max_str_digits(0)  # certificates hold very large exact fractions


class CertError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise CertError(msg)


def fr(s):
    """Exact rational from a 'p/q' string; JSON numbers are rejected."""
    need(isinstance(s, str), f"value {s!r} is not a 'p/q' string")
    return F(s)


def check(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        c = json.load(fh)
    n, pm, m0, tail = c["n"], c["peak_m"], c["m0"], c["tail_M"]
    pv = fr(c["peak_value"])
    blocks = c["blocks"]

    # Check 1: sweep is exactly m = n+2..m0, in order (no gaps/duplicates).
    sweep = c["sweep_delta1"]
    need([m for m, _ in sweep] == list(range(n + 2, m0 + 1)),
         "sweep is not exactly m = n+2..m0 in order (gap, duplicate or misorder)")
    vals = {m: fr(v) for m, v in sweep}

    # Check 2: peak_value is the sweep value at peak_m, and peak_m is in range.
    need(n + 2 <= pm <= m0, "peak_m outside [n+2, m0]")
    need(vals[pm] == pv, "peak_value != sweep value at peak_m")

    # Check 3: strict uniqueness of the sweep maximizer (no ties).
    others = sorted(((v, m) for m, v in vals.items() if m != pm), reverse=True)
    need(all(v < pv for v, _ in others), "sweep tie or larger value: maximizer not unique")

    # Check 4: required points present; points[m0] agrees with the sweep.
    pts = {int(k): {"d0": fr(p["delta0"]), "d1": fr(p["delta1"])}
           for k, p in c["points"].items()}
    ends = {m0, tail} | {x for blk in blocks for x in blk}
    need(ends <= set(pts), f"points missing for {sorted(ends - set(pts))}")
    need(pts[m0]["d1"] == vals[m0], "points[m0].delta1 != sweep value at m0")

    def sane(M):  # Check 6 sanity: all values in [0,1]
        p = pts[M]
        need(0 <= p["d0"] <= 1 and 0 <= p["d1"] <= 1, f"point {M}: value outside [0,1]")

    # Check 5: blocks are contiguous from m0 to tail_M (block-lemma coverage).
    if not blocks:
        need(tail == m0, "no blocks but tail_M != m0")
    else:
        need(blocks[0][0] == m0, "first block does not start at m0")
        for i, (a, b) in enumerate(blocks):
            need(a < b, f"block {i} = [{a},{b}] has a >= b")
            need(i == 0 or a == blocks[i - 1][1], f"block {i} = [{a},{b}] not contiguous")
        need(blocks[-1][1] == tail, "last block end != tail_M")

    # Check 6: block lemma: delta1(n,m) <= d1(a) + d0(a) - d0(b) for a <= m <= b.
    for a, b in blocks:
        sane(a)
        sane(b)
        need(pts[b]["d0"] <= pts[a]["d0"], f"block [{a},{b}]: d0 not nonincreasing")
        bound = pts[a]["d1"] + pts[a]["d0"] - pts[b]["d0"]
        need(bound < pv, f"block [{a},{b}]: bound {float(bound)} not strictly below peak")

    # Check 7: tail lemma: delta1(n,m) <= d0(M) + d1(M) for m >= M.
    sane(tail)
    need(pts[tail]["d0"] + pts[tail]["d1"] < pv,
         "tail bound d0(M)+d1(M) not strictly below peak")

    # Check 8: summary line.
    txt = (f"n={n} PASS: m in [n+2, m0] by exact sweep, [m0, tail_M] by {len(blocks)} blocks, "
           f"[tail_M, inf) by tail lemma; unique maximizer m={pm}, value={float(pv)} (float)")
    if others:
        v, m = others[0]
        txt += f", second best m={m} value={float(v)} gap={float(pv - v)}"
    else:
        txt += ", no second sweep point"
    return txt


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    rc = 0
    for path in argv:
        try:
            print(check(path))
        except CertError as e:
            print(f"FAIL {path}: {e}")
            rc = 1
        except Exception as e:  # malformed file, missing key, bad fraction, ...
            print(f"FAIL {path}: malformed certificate ({type(e).__name__}: {e})")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

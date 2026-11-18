#!/usr/bin/env python3
"""Writes gzipped certificates into OUTDIR: the valid fixture plus four corrupted variants.

Usage: python3 make_cases.py OUTDIR
"""
import copy
import gzip
import json
import os
import sys

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "valid.json")) as fh:
    base = json.load(fh)


def write(name, mutate):
    c = copy.deepcopy(base)
    mutate(c)
    with gzip.open(os.path.join(out, name + ".json.gz"), "wt", encoding="utf-8") as fh:
        json.dump(c, fh)


def none(c):
    pass


def sweep_tie(c):       # m=8 now ties the peak value 1/3 -> Check 3
    c["sweep_delta1"][2][1] = "1/3"


def block_gap(c):       # second block starts at 13, not at previous b=12 -> Check 5
    c["blocks"][1] = [13, 16]
    c["points"]["13"] = dict(c["points"]["12"])  # point present, so only contiguity can fail


def bound_not_strict(c):  # block [9,12]: 1/6 + 1/2 - 1/3 = 1/3, not < 1/3 -> Check 6
    c["points"]["12"]["delta0"] = "1/3"


def tail_not_below(c):  # tail: d0(16)+d1(16) = 3/10 + 1/3 > 1/3 -> Check 7
    c["points"]["16"]["delta1"] = "1/3"


write("valid", none)
write("bad_tie", sweep_tie)
write("bad_gap", block_gap)
write("bad_bound", bound_not_strict)
write("bad_tail", tail_not_below)
print(f"wrote 5 certificates to {out}")

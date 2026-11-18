#!/usr/bin/env python3
"""Program C: exact densities delta0(n,M), delta1(n,M) for Erdos 692.
D = {n+1..M-1}.  Method: split x by the primes of x lying in (n,M) (each such prime is itself in D):
  Case 0: no prime of x in (n,M): x = s*w, s n-smooth, w has only primes >= M. Only s matters.
  Case 1: exactly one prime Q in (n,M) divides x (only contributes to delta1; v_Q(x)=1 exactly if Q^2<M);
          then the n-smooth part s may only use primes q<=n with q*Q>=M, and s has no divisor in D.
See bottom of file / report for the full derivation."""
import sys, json, time, bisect
from fractions import Fraction
from math import gcd
try:
    sys.set_int_max_str_digits(0)
except Exception:
    pass

_pc = {}
def primes_upto(N):
    if N in _pc: return _pc[N]
    s = bytearray([1]) * (N + 1)
    s[0:2] = b'\0\0'
    for i in range(2, int(N ** 0.5) + 1):
        if s[i]:
            s[i*i::i] = bytearray(len(range(i*i, N + 1, i)))
    r = [i for i in range(N + 1) if s[i]]
    _pc.clear(); _pc[N] = r
    return r

def tree_prod(lst):
    lst = list(lst)
    if not lst: return 1
    while len(lst) > 1:
        nxt = [lst[i] * lst[i+1] for i in range(0, len(lst) - 1, 2)]
        if len(lst) & 1: nxt.append(lst[-1])
        lst = nxt
    return lst[0]

def tree_sum_inv(vals):
    """sum 1/v as unreduced (num, den)"""
    nodes = [(1, v) for v in vals]
    if not nodes: return (0, 1)
    while len(nodes) > 1:
        nxt = []
        for i in range(0, len(nodes) - 1, 2):
            a1, b1 = nodes[i]; a2, b2 = nodes[i+1]
            nxt.append((a1 * b2 + a2 * b1, b1 * b2))
        if len(nodes) & 1: nxt.append(nodes[-1])
        nodes = nxt
    return nodes[0]

def compute(n, M):
    """returns (delta0_num, delta0_den, delta1_num, delta1_den) reduced"""
    if n < 1: raise ValueError("requires n >= 1")
    if M <= n + 1:
        return 1, 1, 0, 1
    primes = primes_upto(max(M, 3))
    sp = [p for p in primes if p <= n]
    caps = {}
    for q in sp:
        c, v = 1, q
        while v < M:
            v *= q; c += 1
        caps[q] = c           # smallest c with q^c >= M
    def wt(q, a):
        c = caps[q]
        return Fraction(q - 1, q ** (a + 1)) if a < c else Fraction(1, q ** c)
    def enum(R, lim):
        res = [Fraction(0)] * lim
        def rec(i, divs, cnt, w):
            if i == len(R):
                res[cnt] += w; return
            q = R[i]; c = caps[q]
            rec(i + 1, divs, cnt, w * wt(q, 0))
            newall = divs; cc = cnt; pw = 1
            for a in range(1, c + 1):
                pw *= q
                add = [l * pw for l in divs]
                cc += sum(1 for v in add if n < v < M)
                if cc >= lim: break
                newall = newall + add
                rec(i + 1, newall, cc, w * wt(q, a))
        rec(0, [1], 0, Fraction(1))
        return res
    S0, S1 = enum(sp, 2)
    # Pn = prod_{n<q<M} (1-1/q)
    lo = bisect.bisect_right(primes, n)
    hi = bisect.bisect_left(primes, M)
    mid = primes[lo:hi]
    pn_num = tree_prod([q - 1 for q in mid])
    pn_den = tree_prod(mid)
    # case 1 groups
    groups = {}
    for Q in mid:
        theta = -(-M // Q)
        idx = bisect.bisect_left(sp, theta)   # R = sp[idx:]
        # exponent of Q: any a>=1 if Q^2>=M (weight 1/Q), else exactly 1 (weight (1-1/Q)/Q)
        groups.setdefault(idx, []).append(Q - 1 if Q * Q >= M else Q)
    tnum, tden = S1.numerator, S1.denominator       # T = S1 + sum Z_g H_g
    for idx, vals in groups.items():
        R = sp[idx:]
        W0 = enum(R, 1)[0]
        Z = W0
        for q in sp[:idx]:
            Z *= Fraction(q - 1, q)
        hn, hd = tree_sum_inv(vals)
        a, b = Z.numerator * hn, Z.denominator * hd
        tnum, tden = tnum * b + a * tden, tden * b
    d0n, d0d = pn_num * S0.numerator, pn_den * S0.denominator
    d1n, d1d = pn_num * tnum, pn_den * tden
    g = gcd(d0n, d0d); d0n //= g; d0d //= g
    if d1n == 0:
        d1d = 1
    else:
        g = gcd(d1n, d1d); d1n //= g; d1d //= g
    return d0n, d0d, d1n, d1d

def main():
    pts, out = sys.argv[1], sys.argv[2]
    with open(pts) as f, open(out, 'w') as o:
        for line in f:
            t = line.split()
            if len(t) < 2: continue
            n, M = int(t[0]), int(t[1])
            t0 = time.time()
            a, b, c, d = compute(n, M)
            sec = time.time() - t0
            o.write(json.dumps({"n": n, "M": M, "delta0": "%d/%d" % (a, b),
                                "delta1": "%d/%d" % (c, d), "sec": round(sec, 3)}) + "\n")
            o.flush()

if __name__ == "__main__":
    main()

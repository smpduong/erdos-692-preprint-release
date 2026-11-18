# Independent check. Method: k's p-adic valuations are independent (P(v_p=a)=(1-1/p)p^-a).
# Split primes < m into small (p^2 <= m-1) and large (p^2 > m-1).  A divisor d in D=(n,m) is
# s*q^e with s smooth over small primes and e in {0,1}, q one large prime.  Enumerate exponent
# vectors of small primes by DFS (prune once >=2 divisors of the smooth part lie in D: monotone),
# and for each surviving vector handle large primes in closed form (independent events prob 1/q).
from fractions import Fraction as F
from math import gcd
import time, sys, itertools

def primes_upto(N):
    s = bytearray([1])*(N+1); s[0:2]=b'\0\0'
    for i in range(2,int(N**.5)+1):
        if s[i]: s[i*i::i]=bytearray(len(s[i*i::i]))
    return [i for i in range(N+1) if s[i]]
PR_N = 1000
PR = primes_upto(PR_N)
def set_prime_limit(N):  # PR must contain every prime <= m-1
    global PR, PR_N
    PR_N = N; PR = primes_upto(N)

def dens(n, m):
    """return (delta0, delta1) for D={n+1..m-1}"""
    lo, hi = n+1, m-1
    if n < 1: raise ValueError('requires n >= 1')
    if hi > PR_N: raise ValueError('prime list too short: call set_prime_limit(>= m-1)')
    if lo > hi: return F(1), F(0)
    small = [p for p in PR if p*p <= hi]
    large = [q for q in PR if q <= hi and q*q > hi]
    res = [F(0), F(0)]
    def leaf(divs, w0, prob):
        A1 = []; PI = F(1); anyA = False
        for q in large:
            w = 0
            for s in divs:
                if lo <= s*q <= hi:
                    w += 1
            if w >= 1:
                PI *= F(q-1, q)
                if w == 1: A1.append(q)
        if w0 == 0:
            res[0] += prob*PI
            res[1] += prob*PI*sum((F(1, q-1) for q in A1), F(0))
        else:  # w0 == 1
            res[1] += prob*PI
    def dfs(i, divs, w0, prob):
        if i == len(small):
            leaf(divs, w0, prob); return
        p = small[i]
        amax = 0; t = 1
        while t*p <= hi: t *= p; amax += 1
        for a in range(0, amax+1):
            pr = F(p-1, p**(a+1)) if a < amax else F(1, p**amax)
            nd = set()
            for s in divs:
                t = s
                for b in range(a+1):
                    if t > hi: break
                    nd.add(t); t *= p
            nd = sorted(nd)
            c = sum(1 for s in nd if lo <= s <= hi)
            if c >= 2: break   # monotone in a
            dfs(i+1, nd, c, prob*pr)
    dfs(0, [1], 0, F(1))
    return res[0], res[1]

def brute(n, m, cap=3_000_000):
    D = list(range(n+1, m)); L = 1
    for d in D:
        L = L*d//gcd(L, d)
        if L > cap: return None
    cnt = bytearray(L+1)
    for d in D:
        for k in range(d, L+1, d):
            if cnt[k] < 255: cnt[k] += 1
    z = sum(1 for k in range(1, L+1) if cnt[k] == 0)
    o = sum(1 for k in range(1, L+1) if cnt[k] == 1)
    return F(z, L), F(o, L)

def main():
    out = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); out.append(s); sys.stdout.flush()
    T0 = time.process_time()
    # validation
    nval = 0; bad = 0
    for n in range(1, 30):
        for m in range(n+2, 45):
            b = brute(n, m, 1_500_000)
            if b is None: continue
            nval += 1
            if b != dens(n, m):
                bad += 1; P("MISMATCH", n, m, b, dens(n, m))
    P(f"validation vs brute-force period counting: {nval} (n,m) pairs, mismatches={bad}, cpu={time.process_time()-T0:.1f}s")
    # claim 1
    t = time.process_time()
    d94 = dens(4, 9)[1]
    P("delta1(4,9) =", d94, "== 5/14 :", d94 == F(5, 14))
    target = F(5, 14); ok = True; best = None
    for m in range(6, 434):
        if m == 9: continue
        v = dens(4, m)[1]
        if not v < target:
            ok = False; P("FAIL m=", m, v)
        if best is None or v > best[1]: best = (m, v)
    P("delta1(4,m)<5/14 for all 6<=m<=433, m!=9 (all 427 values checked):", ok,
      "; max at m=", best[0], "=", best[1], float(best[1]), f"cpu={time.process_time()-t:.1f}s")
    # claim 2
    t = time.process_time()
    d0, d1 = dens(4, 434)
    le = d0 + d1
    P("le1(4,434) =", le, "=", f"{float(le):.12f}", "< 5/14:", le < target, f"cpu={time.process_time()-t:.1f}s")
    # claim 3
    a = dens(5, 12)[1]; b = dens(6, 12)[1]
    P("delta1(5,12) =", a, "== 1109/3465 :", a == F(1109, 3465))
    P("delta1(6,12) =", b, "== 1172/3465 :", b == F(1172, 3465))
    P(f"total cpu {time.process_time()-T0:.1f}s")
    open('verify_out.txt', 'w').write('\n'.join(out)+'\n')
    allok = (bad == 0 and nval > 0 and d94 == F(5, 14) and ok and le < target
             and a == F(1109, 3465) and b == F(1172, 3465))
    P('VALIDATION', 'PASS' if allok else 'FAIL')
    return 0 if allok else 1

if __name__ == '__main__':
    sys.exit(main())

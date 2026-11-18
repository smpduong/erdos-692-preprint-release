import sys, time
from fractions import Fraction as F
from math import gcd

sys.setrecursionlimit(10000)
_pf = {}
def pfac(n):
    if n in _pf: return _pf[n]
    r = {}; m = n; q = 2
    while q*q <= m:
        while m % q == 0:
            r[q] = r.get(q, 0)+1; m //= q
        q += 1
    if m > 1: r[m] = r.get(m, 0)+1
    _pf[n] = r
    return r

def primitive(A):
    L = sorted(A); out = []
    for a in L:
        if not any(a % b == 0 for b in out): out.append(a)
    return frozenset(out)

_memo = {}
def avoid(A):
    """density of y with no element of A dividing y"""
    if not A: return F(1)
    if 1 in A: return F(0)
    r = _memo.get(A)
    if r is not None: return r
    P = primitive(A)
    if P != A:
        r = avoid(P); _memo[A] = r; return r
    p = max(q for a in A for q in pfac(a))
    vs = {a: pfac(a).get(p, 0) for a in A}
    K = max(vs.values())
    tot = F(0)
    for k in range(K):
        Ak = frozenset(a // p**vs[a] for a in A if vs[a] <= k)
        tot += F(p-1, p) * F(1, p**k) * avoid(Ak)
    B = frozenset(a // p**vs[a] for a in A)
    tot += F(1, p**K) * avoid(B)
    _memo[A] = tot
    return tot

def delta1(n, m):
    D = list(range(n+1, m))
    tot = F(0)
    for d in D:
        A = frozenset(e // gcd(e, d) for e in D if e != d)
        tot += F(1, d) * avoid(A)
    return tot

def delta0(n, M):
    return avoid(frozenset(range(n+1, M)))

def brute(n, m):
    D = list(range(n+1, m)); L = 1
    for d in D: L = L*d//gcd(L, d)
    full = (1 << L) - 1
    once = 0; twice = 0
    for d in D:
        mk = full // ((1 << d)-1)
        twice |= once & mk; once |= mk
    ones = once & ~twice
    return F(bin(ones).count('1'), L), L

def primes_upto(N):
    s = bytearray([1])*(N+1); s[0:2] = b'\0\0'
    for i in range(2, int(N**.5)+1):
        if s[i]: s[i*i::i] = bytearray(len(range(i*i, N+1, i)))
    return s

def bound_crossing(n, target, N=10**8):
    s = primes_upto(N)
    prod = 1.0; sm = 0.0
    for p in range(n+1, N+1):
        if s[p]:
            prod *= 1-1/p; sm += 1/(p-1)
        # M = p+1 includes primes <= p (interval (n,M) open)
        if prod*(1+sm) < target: return p+1
    return None

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'validate':
        for n, m in [(3,6),(3,7),(3,8),(3,9),(3,10),(4,7),(4,8),(4,9),(4,10),(4,11),(5,9),(5,10),(6,10),(2,9)]:
            b, L = brute(n, m)
            if L > 2*10**7: continue
            e = delta1(n, m)
            print(n, m, 'L=%d' % L, float(e), 'brute==exact', b == e, flush=True)
    if mode == 'run':
        n = int(sys.argv[2]); budget = float(sys.argv[3]); mmax = int(sys.argv[4])
        T0 = time.time(); best = F(0); arg = None; prev = None; prevprev = None; rows = []
        for m in range(n+2, mmax+1):
            t = time.time()
            d1 = delta1(n, m); d0 = delta0(n, m)
            dt = time.time()-t
            if d1 > best: best, arg = d1, m
            rows.append((m, d1, d0, dt))
            print('n=%d m=%d delta1=%.10f delta0=%.10f le1=%.10f runmax=%.10f@%d t=%.2fs cum=%.1fs memo=%d' %
                  (n, m, d1, d0, d1+d0, best, arg, dt, time.time()-T0, len(_memo)), flush=True)
            if time.time()-T0 > budget: break
        print('\nTABLE n=%d: m, delta1, localmax?' % n)
        for i, (m, d1, d0, dt) in enumerate(rows):
            lm = ''
            if 0 < i < len(rows)-1: lm = 'LOCALMAX' if rows[i-1][1] < d1 > rows[i+1][1] else ''
            print(m, '%.10f' % d1, lm)
        print('best', float(best), 'at', arg, 'exact', best)
    if mode == 'bound':
        n = int(sys.argv[2]); target = float(sys.argv[3])
        print('smallest M with B(M) <', target, ':', bound_crossing(n, target*(1-1e-9)))

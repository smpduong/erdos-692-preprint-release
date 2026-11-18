# Write a machine-readable certificate for n (Program B engine, exact Fractions).
# sweep: exact delta1(n,m) for every m in [n+2, m0]; blocks [a,b] with exact delta0/delta1 at endpoints;
# tail: point M with exact delta0(n,M), delta1(n,M). Fractions stored as "p/q" strings.
import sys, json, gzip
import verify as V
sys.set_int_max_str_digits(0)
n = int(sys.argv[1]); m0 = int(sys.argv[2]); mmax = int(sys.argv[3]); out = sys.argv[4]
V.set_prime_limit(mmax + 10)
fs = lambda x: '%d/%d' % (x.numerator, x.denominator)
sweep = []; best = None
for m in range(n+2, m0+1):
    d0, d1 = V.dens(n, m); sweep.append([m, fs(d1)])
    if best is None or d1 > best: best, peak = d1, m
pts = {}
a = m0; pts[a] = V.dens(n, a); step = max(1, a // 8); blocks = []
while True:
    d0a, d1a = pts[a]
    if d0a + d1a < best: tail = a; break
    b = min(a + step, mmax)
    if b not in pts: pts[b] = V.dens(n, b)
    if d1a + d0a - pts[b][0] < best:
        blocks.append([a, b]); a = b; step *= 2
        if a >= mmax: sys.exit('NOT CERTIFIED')
    else:
        if step == 1: sys.exit('FAIL at %d' % a)
        step //= 2
used = sorted({x for bl in blocks for x in bl} | {m0, tail})
cert = {'n': n, 'claim': 'unique integer m > n+1 maximizing delta1(n,m)',
        'peak_m': peak, 'peak_value': fs(best), 'm0': m0, 'sweep_delta1': sweep,
        'points': {str(x): {'delta0': fs(pts[x][0]), 'delta1': fs(pts[x][1])} for x in used},
        'blocks': blocks, 'tail_M': tail}
with gzip.open(out, 'wt') as f: json.dump(cert, f)
print('n=%d peak=%d blocks=%d tail=%d' % (n, peak, len(blocks), tail), flush=True)

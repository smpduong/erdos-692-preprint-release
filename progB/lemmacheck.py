# Brute-force check of block lemma and tail lemma on small cases.
import verify as V
from functools import lru_cache
br = lru_cache(None)(lambda n, m: V.brute(n, m, 300_000))
bad = cnt = 0
for n in range(1, 9):
    for a in range(n+2, 26):
        d0a, d1a = V.dens(n, a)
        for b in range(a, 28):
            d0b, _ = V.dens(n, b)
            for m in range(a, b+1):
                r = br(n, m)
                if r is None: continue
                cnt += 1
                if r[1] > d1a + d0a - d0b: bad += 1
                if r[1] > d1a + d0a: bad += 1
print('block/tail lemma brute-force checks', cnt, 'violations', bad)
import sys
sys.exit(0 if bad == 0 and cnt > 0 else 1)

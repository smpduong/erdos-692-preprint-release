# Build the results table directly from the certificates (so the report cannot drift from them).
import gzip, json, sys
from fractions import Fraction as F
sys.set_int_max_str_digits(0)
print('| n | unique integer maximizer m* | max delta1 (exact) | approx | second best m (sweep) | gap | sweep | blocks | tail M | tail bound |')
print('|---|---|---|---|---|---|---|---|---|---|')
for path in sys.argv[1:]:
    c = json.load(gzip.open(path, 'rt')); pv = F(c['peak_value'])
    v2, m2 = max((F(v), m) for m, v in c['sweep_delta1'] if m != c['peak_m'])
    t = c['points'][str(c['tail_M'])]; tb = F(t['delta0']) + F(t['delta1'])
    print('| %d | %d | %s | %.6f | %d | %.6f | %d..%d | %d | %d | %.6f |' % (
        c['n'], c['peak_m'], c['peak_value'], float(pv), m2, float(pv - v2),
        c['n'] + 2, c['m0'], len(c['blocks']), c['tail_M'], float(tb)))

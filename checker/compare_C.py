# Recompute EVERY density in a certificate with Program C and compare exactly.
# Fails (exit 1) on any differing value, conflicting claims inside the certificate, a missing,
# duplicate or extra output row from Program C, or an output row for the wrong n.
import gzip, json, subprocess, sys, os, tempfile
from fractions import Fraction as F
sys.set_int_max_str_digits(0)
cert, progC = sys.argv[1], sys.argv[2]
c = json.load(gzip.open(cert, 'rt')); n = c['n']
problems = []
want = {}  # (M, kind) -> Fraction
def claim(key, v):
    v = F(v)
    if key in want and want[key] != v: problems.append('conflicting certificate claims for %s' % (key,))
    want[key] = v
for m, v in c['sweep_delta1']: claim((m, 'delta1'), v)
for M, p in c['points'].items():
    claim((int(M), 'delta0'), p['delta0']); claim((int(M), 'delta1'), p['delta1'])
Ms = sorted({M for M, _ in want})
with tempfile.TemporaryDirectory() as d:
    pf = os.path.join(d, 'pts.txt'); of = os.path.join(d, 'out.jsonl')
    open(pf, 'w').write(''.join('%d %d\n' % (n, M) for M in Ms))
    subprocess.run([sys.executable, progC, pf, of], check=True, stdout=subprocess.DEVNULL)
    got = {}
    for line in open(of):
        r = json.loads(line)
        if r['n'] != n: problems.append('Program C row for n=%s' % r['n']); continue
        if r['M'] in got: problems.append('duplicate Program C row M=%s' % r['M']); continue
        got[r['M']] = (F(r['delta0']), F(r['delta1']))
if set(got) != set(Ms):
    problems.append('Program C rows missing %d / extra %d' % (len(set(Ms) - set(got)), len(set(got) - set(Ms))))
bad = [k for k, v in want.items() if k[0] in got and got[k[0]][0 if k[1] == 'delta0' else 1] != v]
print('n=%d: %d certificate values recomputed by Program C, %d differ%s' %
      (n, len(want), len(bad), ('; FAIL: ' + '; '.join(problems[:3])) if problems else ''))
sys.exit(1 if (bad or problems) else 0)

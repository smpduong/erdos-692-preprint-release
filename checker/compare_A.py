# Compare certificate sweep values (Program B) with Program A's exact logged delta1 values.
# Fails (exit 1) if any value differs, any sweep m is missing from the log, or the log
# has duplicate/conflicting rows or rows for another n.
import gzip, json, re, sys
from fractions import Fraction as F
sys.set_int_max_str_digits(0)  # certificates hold very large exact fractions
cert, alog = sys.argv[1], sys.argv[2]
c = json.load(gzip.open(cert, 'rt')); n = c['n']
A = {}; problems = []
for line in open(alog):
    m = re.match(r'n=(\d+) m=(\d+) d1=(\d+/\d+|\d+) ', line)
    if not m: continue
    ln, lm, v = int(m.group(1)), int(m.group(2)), F(m.group(3))
    if ln != n: problems.append('log row for n=%d' % ln); continue
    if lm in A: problems.append('duplicate log row m=%d' % lm); continue
    A[lm] = v
same = diff = 0; missing = []
for mm, v in c['sweep_delta1']:
    if mm not in A: missing.append(mm); continue
    if A[mm] == F(v): same += 1
    else: diff += 1; print('DIFF n=%d m=%d' % (n, mm))
if missing: problems.append('%d sweep m missing from A log (%d..%d)' % (len(missing), missing[0], missing[-1]))
if same == 0: problems.append('no values compared')
print('n=%d: %d sweep values equal to Program A, %d differ, %d missing%s' %
      (n, same, diff, len(missing), ('; FAIL: ' + '; '.join(problems[:3])) if problems else ''))
sys.exit(1 if (diff or problems) else 0)

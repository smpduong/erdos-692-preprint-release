# Fake Program C for negative tests: runs the real progC, then corrupts its output.
# usage: fakeC.py MODE points.txt out.jsonl   (MODE: value | missing | duplicate | wrong_n)
import json, os, subprocess, sys
mode = os.environ['FAKEC_MODE']; pts, out = sys.argv[1], sys.argv[2]
real = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'progC', 'progC.py')
subprocess.run([sys.executable, real, pts, out], check=True, stdout=subprocess.DEVNULL)
rows = [json.loads(l) for l in open(out)]
if mode == 'value': rows[3]['delta1'] = '1/3'
if mode == 'missing': rows.pop(5)
if mode == 'duplicate': rows.append(dict(rows[2]))
if mode == 'wrong_n': rows[4]['n'] = rows[4]['n'] + 1
open(out, 'w').write(''.join(json.dumps(r) + '\n' for r in rows))

# Inject a wrong density into B or C and run their validators; each must exit nonzero.
# usage: fault_validators.py B|C|lemma
import os, runpy, sys, tempfile
from fractions import Fraction as F
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
which = sys.argv[1]
root = os.path.abspath(root)
# verify.main writes verify_out.txt to cwd; remove it even after an expected failure.
previous_cwd = os.getcwd()
with tempfile.TemporaryDirectory() as work:
    try:
        os.chdir(work)
        if which in ('B', 'lemma'):
            sys.path.insert(0, os.path.join(root, 'progB')); import verify
            real = verify.dens
            delta = F(1, 10**6) if which == 'B' else F(-1, 10)  # lemma check needs a fault that lowers a bound
            verify.dens = lambda n, m: (real(n, m)[0], real(n, m)[1] + (delta if (n, m) == (3, 9) else 0))
            if which == 'B': sys.exit(verify.main())
            runpy.run_path(os.path.join(root, 'progB', 'lemmacheck.py'), run_name='__main__')
        else:
            sys.path.insert(0, os.path.join(root, 'progC')); import progC
            real = progC.compute
            def bad(n, M):
                a, b, c, d = real(n, M)
                return (a, b, c + 1, d) if (n, M) == (3, 9) else (a, b, c, d)
            progC.compute = bad
            runpy.run_path(os.path.join(root, 'progC', 'validate.py'), run_name='__main__')
    finally:
        os.chdir(previous_cwd)

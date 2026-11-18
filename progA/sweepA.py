# Program A exact sweep log, same line format as certify.py.
import sys, delta as D
n, mmax = int(sys.argv[1]), int(sys.argv[2])
for m in range(n+2, mmax+1):
    print('n=%d m=%d d1=%s ' % (n, m, D.delta1(n, m)), flush=True)

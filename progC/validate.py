import sys
from math import lcm
from fractions import Fraction as F
from progC import compute
def brute(n,M):
    D=list(range(n+1,M)); L=lcm(*D)
    full=(1<<L)-1; ones=0; twos=0
    for d in D:
        m=full//((1<<d)-1)   # bits at multiples of d (positions 0,d,2d..)
        twos|=ones&m; ones|=m
    c0=L-ones.bit_count(); c1=(ones^twos).bit_count()
    return F(c0,L),F(c1,L),L
cases=bad=0
for n in range(1,26):
    for M in range(n+2,10**6):
        D=range(n+1,M)
        if lcm(*D)>2_000_000: break
        b0,b1,L=brute(n,M)
        a,b,c,d=compute(n,M)
        cases+=1
        if F(a,b)!=b0 or F(c,d)!=b1:
            bad+=1; print("MISMATCH",n,M,L,F(a,b),b0,F(c,d),b1)
print("cases",cases,"mismatches",bad)
print("VALIDATION", "PASS" if bad == 0 and cases > 0 else "FAIL")
sys.exit(0 if bad == 0 and cases > 0 else 1)

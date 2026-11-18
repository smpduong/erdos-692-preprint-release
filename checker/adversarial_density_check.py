import importlib.util,sys,itertools,math,json
from fractions import Fraction as F
from pathlib import Path
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
def imp(name,file):
 s=importlib.util.spec_from_file_location(name,root/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
B=imp('B','progB/verify.py');C=imp('C','progC/progC.py');A=imp('A','progA/delta.py')
def oracle(n,m):
 D=list(range(n+1,m));z=F(1);o=F(0)
 for k in range(1,len(D)+1):
  for S in itertools.combinations(D,k):
   L=math.lcm(*S);z+=F((-1)**k,L);o+=F((-1)**(k+1)*k,L)
 return z,o
cases=[(n,n+1+w) for n in range(1,21) for w in [0,1,2,3,5,8,11]]
for n,m in cases:
 want=oracle(n,m);b=B.dens(n,m);c=C.compute(n,m);c=F(c[0],c[1]),F(c[2],c[3]);a=A.delta0(n,m),A.delta1(n,m)
 if not a==b==c==want: raise SystemExit(f"FAIL {(n,m,want,a,b,c)}")
print('PASS',len(cases),'fresh explicit-subset inclusion-exclusion comparisons for BOTH densities against A/B/C')

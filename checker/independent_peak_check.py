"""Independent peak-value check by weighted inclusion-exclusion over LCM states.
Not a global-endpoint proof. Uses neither supplied valuation density engine.
"""
import gzip, json, math, sys
from fractions import Fraction
from pathlib import Path

def exactly_one(n,m):
    # a_L=sum(-1)^|S|; b_L=sum(-1)^|S| |S| over subsets with LCM L.
    states={1:(1,0)}
    for d in range(n+1,m):
        nxt=dict(states)
        for L,(a,b) in states.items():
            K=math.lcm(L,d)
            u,v=nxt.get(K,(0,0))
            nxt[K]=(u-a,v-b-a)
        states={L:ab for L,ab in nxt.items() if ab!=(0,0)}
    return sum((-Fraction(b,L) for L,(_,b) in states.items()),Fraction(0))

def main(root):
    sys.set_int_max_str_digits(0)
    checked=0
    for n in range(1,9):
        for m in range(n+1,n+8):
            L=math.lcm(*range(n+1,m))
            if L>30000: continue
            want=Fraction(sum(sum(x%d==0 for d in range(n+1,m))==1
                              for x in range(1,L+1)),L)
            if exactly_one(n,m)!=want: raise SystemExit("FAIL direct-period check")
            checked+=1
    print(f"PASS {checked} direct-period comparisons",flush=True)
    for n in range(4,21):
        c=json.load(gzip.open(root/f'certs/cert_n{n}.json.gz','rt'))
        # Read the claimed peak without relying on metadata field spelling.
        values=[(int(m),Fraction(v)) for m,v in c['sweep_delta1']]
        m,want=max(values,key=lambda p:p[1])
        got=exactly_one(n,m)
        if got!=want: raise SystemExit(f'FAIL n={n},m={m}: {got} != {want}')
        print(f'PASS n={n} m={m} value={got}',flush=True)
if __name__=='__main__': main(Path(sys.argv[1]))

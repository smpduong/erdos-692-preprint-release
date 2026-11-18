# Derivation and audit of three exact density algorithms (delta0, delta1)

> Note added after this review (2026-10-22): both unenforced preconditions below are now ENFORCED. progB/verify.py raises an error if n < 1 or if m-1 exceeds the prime-list limit (set_prime_limit; gen_cert.py sets it to mmax+10, as the certificate runs always did). progC/progC.py raises an error if n < 1. These guards shifted line numbers: verify.py lines after 15 moved down by 6 and progC.py lines after 51 by 1.


## 0. Verdict up front

No mathematical error found in A, B or C. Three caveats, none affecting the
quoted parameter ranges (n >= 1, M <= 434 in B's claims):

1. **B (verify.py) silently requires hi = m-1 <= 1000** (see 2.6): the prime list PR stops at 1000, so large primes
   q in (1000, hi] would be dropped with no error. Its uses (m <= 434) are safe. Also requires n >= 1 (see 2.6).
2. **A, B and C all need n >= 1** (1 in D when n = 0 breaks the "empty product" start of B and C; A handles it, via avoid -> 0).
3. All three share the same probabilistic model (Section 5), so they are not independent of the model, only of the
   decomposition and code.

Sanity run (done by me, outside the source dirs, sources untouched): for all 1<=n<=25, n+1<=M<=49 (900 pairs)
A.delta0/delta1, B.dens and C.compute agree exactly as Fractions (0 mismatches).

## 1. Setting and the common measure

D = D(n,M) = {n+1, ..., M-1} (integers, open interval (n,M)). c(x) = #{d in D : d | x}.
delta0(n,M) = dens{x : c(x)=0}, delta1(n,M) = dens{x : c(x)=1}.
Empty D (M <= n+1): c = 0 always, so delta0 = 1, delta1 = 0.

Model: valuations v_p(x) are independent, P(v_p = a) = (1-1/p) p^-a, hence P(v_p >= a) = p^-a.
Justification: every event used below is periodic (depends on x mod L, L = lcm of the finitely many integers
involved), so natural density exists and equals the product measure of the finitely many valuations involved
(CRT). Events that look at "all primes" are only ever reduced to finitely many primes (primes > M-1 cannot
divide any d in D, so they never matter).

Monotonicity: D(n,m) is increasing in m, so c_m(x) is nondecreasing in m. Used in the lemmas and in pruning.

## 2. Program A: delta.py (avoid, delta1, delta0)

### 2.1 Identity

(a) avoid(S) := dens{y : no s in S divides y}, for a finite set S of positive integers.
    delta0(n,M) = avoid(D).
(b) Exactly one divisor: partition by which d divides x:
    {c(x)=1} = disjoint union over d in D of {x : d | x and e does not divide x for all e in D, e != d}.
    Write x = d t. For e in D, e != d: e | d t  <=>  (e/gcd(e,d)) | t. Density of {x in dZ with t in T} is
    (1/d) dens(T). Hence
    delta1(n,M) = sum_{d in D} (1/d) * avoid(A_d),  A_d = { e/gcd(e,d) : e in D, e != d }.
(c) Recursion for avoid(A), A not containing 1, nonempty. Let p = largest prime dividing some element of A.
    vs(a) = v_p(a); K = max vs(a) >= 1. For y with v_p(y) = k: a | y  <=>  vs(a) <= k and a' | y, a' = a/p^vs(a)
    (a' is prime to p, so a' | y iff a' | y, no condition from p beyond vs(a) <= k).
    Hence, conditionally on v_p(y) = k, the event "no a divides y" is "no a' in A_k divides y",
    A_k = { a/p^vs(a) : vs(a) <= k }, whose divisibility events involve primes other than p, independent of v_p.
    For k < K : P(v_p=k) = (p-1)/p * p^-k.
    For k >= K: all a have vs(a) <= k, so A_k = B := { a/p^vs(a) : a in A } for every k >= K; P(v_p >= K) = p^-K.
    avoid(A) = sum_{k=0}^{K-1} (p-1)/p * p^-k * avoid(A_k) + p^-K * avoid(B).
(d) Base/short-cuts: avoid(empty) = 1; 1 in A => avoid = 0; avoid(A) = avoid(primitive(A)) where primitive keeps the
    divisibility-minimal elements (y divisible by a is divisible by a minimal divisor of a within A, converse trivial).

### 2.2 Proof of correctness (edge cases)

* Termination: after the 1-test and primitive reduction every a in A has a >= 2, so a prime p exists. Each recursive
  call removes p from every element and A_k, B consist of p-free numbers, so the largest prime strictly decreases or
  the set shrinks to {} or contains 1. Finite recursion.
* Exponent cap: only K = max vs matters; the tail k >= K is lumped with weight p^-K (sum_{k>=K} (p-1)/p p^-k = p^-K,
  checked). No other cap exists in A.
* A_k can be empty (all vs(a) > k): avoid = 1, correct (no constraint). A_k or B can contain 1 exactly when some
  a = p^j (a' = 1): avoid = 0, correct (such a divides y once v_p(y) >= j).
* delta1 edge cases: if e | d (e != d, both in D) then e/gcd(e,d) = 1 so A_d contains 1 and the term is 0: correct,
  d | x forces e | x. Single-element D: A_d = {} so term = 1/d. Empty D: the loop does nothing, delta1 = 0; avoid({}) = 1.
* Open endpoints: D = range(n+1, m) is exactly {n+1..m-1}. delta0(n,M) = avoid(frozenset(range(n+1,M))).
* No distinction Q^2 < M vs Q^2 >= M is needed: A never looks at primes specially; the exponent caps arise from the data.
* Memoization is keyed on the frozenset A (also stores the value under the unreduced key when primitive(A) != A);
  value depends only on A, so sound.

### 2.3 Line map (delta.py)

| Proof step | Source |
|---|---|
| factorisation of integers (trial division) | pfac, lines 7-16 |
| primitive(A) (divisibility-minimal, sorted ascending so smaller candidates are seen first) | lines 18-22 |
| avoid: empty -> 1, 1 in A -> 0 (2.1d) | lines 27-28 |
| memo lookup / store | 29-30, 33, 43 |
| reduce to primitive set (2.1d) | 31-33 |
| choose p = largest prime of any element (2.1c) | 34 |
| vs(a) and K | 35-36 |
| terms k = 0..K-1: A_k, weight (p-1)/p * p^-k | 38-40 |
| tail k >= K: B, weight p^-K | 41-42 |
| delta1 = sum_d (1/d) avoid(A_d), A_d = {e/gcd(e,d)} (2.1b) | 46-52 (A_d at line 50) |
| delta0 = avoid(D) | 54-55 |
| brute / validate (period counting) | 57-66, 86-91 (testing only, not used by the claims) |
| bound_crossing (an analytic upper bound scan) | 74-82; NOT audited in this document |

### 2.4 Unsure / notes (A)

* Performance only: delta1 builds one avoid per d, memoised; no correctness issue.
* bound_crossing uses floats and a 1e-9 safety factor; not part of the exact claims, not reviewed here beyond reading.
* `brute` uses full//((1<<d)-1), valid because L is a multiple of d (bit i set iff d | i); testing aid only.

## 3. Program B: verify.py, dens(n,m)

### 3.1 Identity

lo = n+1, hi = m-1, D = [lo, hi]. If lo > hi return (1, 0).
Primes split: small = {p : p^2 <= hi}, large = {q : q <= hi, q^2 > hi}. Primes > hi divide no element of D and are omitted.

Structure of d in D: d = s * q^e, s composed of small primes, and either e = 0 or d is divisible by exactly one large
prime q with exponent 1 (q^2 > hi >= d; two distinct large primes would give q1 q2 > hi). Therefore for x:
   c(x) = w0 + sum_{large q | x} w_q,
   w0 = #{divisors s of the small-prime part S(x) with lo <= s <= hi},
   w_q = #{divisors s of S(x) with lo <= s q <= hi}   (a function of S(x) only).
Given S(x) (equivalently the exponent vector of the small primes), the events {q | x}, q large, are independent with
probability 1/q, and independent of S(x).
   Let Q* = {q large : w_q >= 1}, PI = prod_{q in Q*} (1 - 1/q), A1 = {q in Q* : w_q = 1}.
   * w0 = 0:  c = 0  iff no q in Q* divides x: probability PI.
              c = 1  iff exactly one q in Q* divides x and it has w_q = 1: sum_{q in A1} (1/q) prod_{q' in Q*, q' != q}(1-1/q')
                     = PI * sum_{q in A1} 1/(q-1).
   * w0 = 1:  c = 1 iff no q in Q* divides x: PI.  (c = 0 impossible.)
   * w0 >= 2: contributes to neither.
Total: delta0 = sum over small exponent vectors with w0=0 of prob * PI;
       delta1 = sum over (w0=0) of prob*PI*sum_{A1} 1/(q-1) + sum over (w0=1) of prob*PI.

### 3.2 Proof and caps

* Small prime p, exponent a. Divisors of D-elements have v_p <= amax = max{a : p^a <= hi}. Only min(v_p(x), amax)
  matters, so classes a = 0..amax-1 with probability (p-1)/p^(a+1) and a = amax lumped with probability p^-amax
  (= P(v_p >= amax)); these sum to 1. Since p^2 <= hi, amax >= 2.
* Divisor sets: after processing primes p_1..p_i with exponents a_1..a_i, `divs` should be all divisors of the partial
  product that are <= hi. Extending by p^a: new divisors are s * p^b, b=0..a, s in old divs; any divisor of the new
  product that is <= hi has s = (divisor)/p^b <= hi, so s in old divs (completeness); truncating at > hi loses only
  numbers exceeding hi, which can neither be in D nor be factors of an element s*q <= hi. A set (nd) removes duplicates
  (none exist as p-power parts are distinct, but harmless).
* c = number of elements of nd in [lo,hi]; recomputed from scratch each level (not incremental) so equal to w0 of the
  partial product. w0 is nondecreasing as more primes/exponents are added (divisor sets grow), so once c >= 2 every
  extension has w0 >= 2: the `break` (increasing a gives bigger divisor sets: monotone in a) and the non-recursion are sound,
  and the missing mass correctly contributes to neither delta0 nor delta1 (c(x) >= 2).
* Leaf: w_q computed by counting s in divs with lo <= s*q <= hi, s <= hi guaranteed to include all admissible s.
  q ranges over all large primes <= hi. w >= 1 triggers factor (q-1)/q; w == 1 adds q to A1.
* Open interval: D = [n+1, m-1] i.e. lo = n+1, hi = m-1 with inclusive tests lo <= t <= hi everywhere (lines 29, 54).
* Q^2 < M versus Q^2 >= M: this is the small/large split (p*p <= hi <=> p^2 < m). A prime q with q^2 = hi+1 = m is
  "large", correct: q^2 = m not in D, so exponent of q beyond 1 is irrelevant.
* Empty D: line 20.

### 3.3 Line map (verify.py)

| Proof step | Source |
|---|---|
| lo, hi; empty D returns (1,0) | 19-20 |
| small and large prime lists | 21-22 |
| res = [delta0, delta1] accumulators | 23 |
| leaf: w_q counting, PI, A1, and the three cases w0=0/1 | leaf, 24-38 (w loop 27-30, PI/A1 31-33, w0==0 at 34-36, w0==1 at 37-38) |
| DFS over small primes, amax, class probabilities (lumped top class) | 39-57: amax 43-44, pr at 46 |
| divisor-set extension, truncated at hi | 47-53 |
| c = #divisors in [lo,hi], prune c>=2 | 54-55 |
| recursion with updated weight | 56; start 57 |
| return (delta0, delta1) | 58 |
| brute (cap on L) and validation loop | 60-71, 79-87 |
| claims: delta1(4,9)=5/14, max over m, le1(4,434), delta1(5,12), delta1(6,12) | 88-109 |

### 3.4 Unsure / flags (B)

* PRECONDITION NOT ENFORCED: PR = primes <= 1000 (line 15). For hi > 1000 the large primes in (1000, hi] are missing
  and the output would be wrong without an error. The claims use m <= 434 so hi <= 433: safe.
* n >= 1 required: if n = 0 then 1 in D, but divs starts as [1] with w0 = 0 passed to the root and only recomputed after
  at least one small prime is processed; for hi < 4 (no small primes) the root w0 would be wrong. Not used.
* The claims loop `for m in range(6, 434)` skips m = 5 (empty D, delta1 = 0 < 5/14, trivially fine) and m = 9 (the target).
* The "le1(4,434) < 5/14" claim covers all m >= 434 only through the tail lemma (Section 4.2). Together: m <= 433 by direct check.
* The brute check (lines 60-71) caps cnt at 255 and treats positions 1..L (position L is the class 0 mod L): correct.

## 4. Program C: progC.py, compute(n,M)

### 4.1 Identity

Notation: sp = primes <= n ("small"), mid = primes Q with n < Q < M (each Q in D), all other primes are >= M (cannot divide
an element of D, since d < M). c(x) counts divisors of x in D.
Let s(x) = n-smooth part of x (primes <= n). Weights: for q in sp, cap c_q = least c with q^c >= M.
Only min(v_q, c_q) matters (a divisor with v_q >= c_q has q^c_q >= M and so is >= M). Weight wt(q,a) = (q-1)/q^(a+1) for
a < c_q, wt(q,c_q) = q^-c_q.

Case 0 (no prime of mid divides x). Every divisor d of x with d < M is then composed only of primes <= n, so c(x) = number
of divisors of s(x) lying in (n,M). Probability that no mid prime divides x: Pn = prod_{Q in mid}(1-1/Q).
   delta0 = Pn * S0,    S_j = sum of weights of exponent vectors on sp with exactly j divisors in D (j = 0, 1).
   Case-0 part of delta1 = Pn * S1.

Case 1 (exactly one mid prime Q divides x). If two or more mid primes divide x, c >= 2 (the primes themselves are in D):
excluded. Given Q | x only, the divisors of x below M are s*Q^a (s | s(x), a >= 0). Q itself is in D and counts once, so
c(x) = 1 requires no other divisor in D:
   (i) a = 0: s(x) has no divisor in D;
   (ii) a >= 2: if Q^2 < M then Q^2 in D (Q > n gives Q^2 > n), so v_Q(x) = 1 is forced; if Q^2 >= M, any a >= 1 is fine
        (Q^a >= M for a >= 2) and the probability of Q | x is 1/Q;
   (iii) a >= 1, (s,a) != (1,1): s*Q^a in D. Since s*Q^a >= s*Q > n whenever s>=1, the lower bound is automatic, so the
        condition is s*Q^a >= M. Taking a = 1 and s = q a prime factor of s(x): need q*Q >= M, i.e. q >= theta := ceil(M/Q).
        Conversely if all prime factors of s(x) are >= theta then s*Q^a >= theta*Q >= M for every s > 1, a >= 1,
        and for s = 1, a >= 2 by (ii).
   Hence s(x) must (a) have only prime factors in R_theta = {q in sp : q >= theta}, so no q < theta divides x
   (probability prod_{q in sp, q<theta}(1-1/q)), and (b) have no divisor in D, weight W0(R_theta) = sum of
   exponent-vector weights on R_theta with 0 divisors in D.  Let Z_theta = W0(R_theta) * prod_{q in sp, q<theta}(1-1/q).
   Probability for given Q: P(v_Q cond) * prod_{Q' in mid, Q' != Q}(1-1/Q') * Z_theta
      = Pn * [ P(v_Q cond)/(1-1/Q) ] * Z_theta,
      P(v_Q cond)/(1-1/Q) = (1/Q)/((Q-1)/Q) = 1/(Q-1)   if Q^2 >= M,
                          = ((Q-1)/Q^2)/((Q-1)/Q) = 1/Q   if Q^2 < M.
   Group the Q by theta (equivalently by idx = number of sp primes below theta): H_g = sum over Q in group of
   1/val(Q), val = Q-1 (Q^2>=M) or Q (Q^2<M).
Result:
   delta0 = Pn * S0,
   delta1 = Pn * ( S1 + sum_g Z_g H_g ).

### 4.2 Proof notes for caps and edge cases

* Exponent cap c_q = smallest c with q^c >= M (for q <= n). Class a < c_q uses exact exponent, class c_q is the tail
  (>= c_q) with total probability q^-c_q: sums to 1. Divisors with exponent a >= c_q are >= M, never counted; `enum` counts
  elements of l*q^a with n < . < M only, so the tail representative (a = c_q) contributes no D-divisors beyond those with
  smaller exponents -- correct (they are >= q^c_q >= M).
* enum's incremental counting: cc = divisors in D so far; after exponent a all of divs*q^b (b <= a) are in newall, and
  `add` is the new layer; cc counts only the new layer, correct. Pruning cc >= lim monotone in a (newall grows). For
  lim=2: res[0],res[1] are S0,S1; for lim=1 only the zero class (W0). res index cc < lim always when the leaf is reached.
* Strict endpoints: mid = primes with n < Q < M (bisect_right at n, bisect_left at M exclude both ends even if prime), D tests
  `n < v < M` (line 76). sp includes n if n is prime (p <= n).
* Q^2 < M vs Q^2 >= M: line 95 (exponent weight). Verified above: for Q^2 < M, v_Q = 1 forced, weight (1-1/Q)/Q; else 1/Q.
* Empty D: M <= n+1 returns (1,1,0,1) at line 53. M = n+2 with n+1 prime Q: S0=1, S1=0, theta = 2, Z = 1, H=1/(Q-1),
  Pn = (Q-1)/Q: delta1 = 1/Q, as it must be. If n+1 composite: no mid prime, S1 = P(n+1 | x).
* n = 1 or no small primes: sp empty, enum returns [1,0], consistent.
* Tree products/sums are exact integer arithmetic, only for speed. Final reductions: lines 108-112 (d1n = 0 gives 0/1).

### 4.3 Line map (progC.py)

| Proof step | Source |
|---|---|
| empty D | 52-53 |
| sp = primes <= n; primes list up to max(M,3) | 54-55 |
| caps c_q | 56-61 |
| weight wt(q,a), lumped tail | 62-64 |
| enum: DFS over exponent vectors, divisor lists, count in (n,M), prune cc >= lim | 65-81 (count 76, prune 77) |
| S0, S1 | 82 |
| Pn = prod over mid (1-1/Q): numerator/denominator | 83-88 |
| theta = ceil(M/Q) (as -(-M // Q)), idx, group by idx | 91-94 |
| val(Q) = Q-1 if Q^2 >= M else Q | 95 |
| T = S1 + sum_g Z_g H_g | 96-105: W0 = enum(R,1)[0] (99), Z with prod_{q<theta}(1-1/q) (100-102), H_g = tree_sum_inv (103), fraction add (104-105) |
| delta0 = Pn*S0, delta1 = Pn*T, reduce | 106-113 |
| I/O wrapper | 115-130 |

### 4.4 Unsure / flags (C)

* n >= 1 assumed (divs=[1] never counted: if n=0, 1 in D would be missed). Not used.
* The docstring says "see bottom of file / report"; no derivation is in the file. The derivation here is mine.
* primes_upto(max(M,3)) clears the cache; no correctness impact.
* `enum(R, lim)` for the Case-1 groups recomputes the DFS per group: performance only.
* Python big ints are used; Fraction(1, q**c) can become large for big M; no overflow concern.

## 5. Lemmas

Throughout, c_m(x) = #{d in Z : n < d < m, d | x}, E0(m) = {c_m = 0}, E1(m) = {c_m = 1}. All sets are periodic
(finite unions of residue classes), so densities are finitely additive and monotone.

### 5.1 Block lemma
For integers a <= m <= b:  delta1(n,m) <= delta1(n,a) + delta0(n,a) - delta0(n,b).

Proof. D_a ⊆ D_m ⊆ D_b (open intervals nested because a <= m <= b), so c_a <= c_m <= c_b pointwise.
If c_m(x) = 1 then c_a(x) in {0,1}, so E1(m) ⊆ E1(a) ∪ E0(a). Also c_b(x) >= c_m(x) = 1 so x is not in E0(b):
E1(m) ∩ E0(b) = ∅. Since E0(b) ⊆ E0(a), the set (E1(a) ∪ E0(a)) \ E0(b) has density
delta1(n,a) + delta0(n,a) - delta0(n,b) (E1(a), E0(a) disjoint; E0(b) inside the union). Monotonicity of density gives the claim.
Endpoints: a = m gives delta1(n,m) <= delta1(n,m) + delta0(n,m) - delta0(n,b), true since delta0 decreases in b; b = m gives
delta1(n,m) <= delta1(n,a) + delta0(n,a) - delta0(n,m), true by the same containment (E1(m) disjoint from E0(m)). QED.

### 5.2 Tail lemma
For integers m >= M:  delta1(n,m) <= delta0(n,M) + delta1(n,M).

Proof. c_m >= c_M. If c_m(x) = 1 then c_M(x) in {0,1}: E1(m) ⊆ E0(M) ∪ E1(M) (disjoint). Take densities. QED.
Use: a verified bound (delta0 + delta1)(n,M) < threshold gives delta1(n,m) < threshold for all m >= M; with direct values for
the finitely many m < M this closes the range. This is how B's claim 2 (M = 434, n = 4, threshold 5/14) covers m >= 434.

### 5.3 Real endpoints and uniqueness
delta1(n,m) depends only on the integer set D = {d integer : n < d < m}. For real t, D(n,t) = {n+1..ceil(t)-1}, so
delta1(n,t) = delta1(n,ceil(t)) is a left-continuous step function, constant on each
interval (m-1, m] for integer m. Open endpoints: the point t = m itself belongs to the piece for D = {..m-1}; t = m+epsilon
gains the element m. A statement "m is the unique maximiser" must be read as uniqueness of the integer m = ceil(t) (equivalently
of the set D); real t in (m-1, m] all give the same value and are not distinct maximisers. The lemmas apply verbatim with
integer a <= ceil(t) <= b. For integer arguments the programs' range(n+1, m) / [n+1, m-1] / (n,M) conventions all match.

## 6. What the three methods share

Shared (so NOT independent):
* The probabilistic model: independence of p-adic valuations with P(v_p = a) = (1-1/p)p^-a, and the translation of
  "natural density of a periodic set" into that product measure (Section 1). All three use it.
* Same target definition D = {n+1..M-1}, c(x) = #divisors in D, delta0 = P(c=0), delta1 = P(c=1).
* Exact rational arithmetic with Python's Fraction (A and B: Fraction; C: Fraction plus explicit big-int numerators/denominators).
  A shared interpreter/arithmetic layer; no floating point in the exact paths (A's bound_crossing is float, outside the claims).

Independent (different decomposition and code):
* A: inclusion-style recursion on the largest prime, delta1 by "which d divides" with quotient sets e/gcd(e,d).
* B: split at p^2 <= hi, DFS over small-prime exponent vectors, closed-form product for large primes (each large prime
  contributes at most one factor, independent).
* C: split by primes of x in (n,M), case analysis (0 or 1 mid primes), exponent caps via q^c >= M, grouping by ceil(M/Q).
* Cross-check: all three give identical exact Fractions on 900 pairs (1<=n<=25, n+1<=M<=49); A and B are each also
  validated by their own brute-force period counting, which is independent of the valuation model (it counts residues
  mod L = lcm(D)).

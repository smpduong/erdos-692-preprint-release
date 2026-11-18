# Exact divisor-density maximizers for n = 4 through 20

Reproducible preprint snapshot accompanying **Exact Divisor Densities and a Finite-to-Global Certification of Integer Maximizers**, Steven Minh Phat Duong, MPH.

Preprint and frozen v3 deposit: https://doi.org/10.5281/zenodo.24338898 .

This is a fresh curated repository snapshot, not the development history. The original private repository and confidential review materials are not included. The corrected publication-status PDF and matching editable sources are in manuscript/. Exact engines, certificates and saved A outputs retain their validated values. This snapshot is not byte-identical to the Zenodo v3 archive: it adds authorized licences, current entrypoints and the corrected manuscript, omits superseded exploratory/history material and rebuilds the manifest.

## Scope and trust boundary
Candidate computer-assisted classification for fixed n=4,...,20, conditional on correctness of the exact density computation. The pointwise block/tail bounds and finite-to-global criterion are proved in the manuscript. The logical checker verifies supplied rational values and coverage; it does not independently establish their interpretation as densities. No general solution of Erdős problem692, new general existence theorem, established novelty, independent human review or formal verification of this classification is claimed.

## Run
Python3.11+ standard library and a POSIX shell; no network or external solver required.

```sh
python3 verify_integrity.py
sh quickcheck.sh
python3 checker/adversarial_density_check.py
sh replay.sh
# Optional: regenerate all16779 saved A sweep entries (several CPU-hours)
sh replay.sh full
```

The default replay recomputes all certificate densities using C, compares saved A sweeps and runs validators/failure-propagation tests. It does NOT regenerate A. Prior complete default replay and the v3 regression/independent-oracle checks passed; logs are in validation/. Full-A regeneration and independent human review remain outstanding. The 17 LCM-state peak checks and 140 explicit-subset cases test values, not all infinite endpoints in isolation.

## Files
- manuscript/: corrected seven-page PDF and editable Markdown/TeX; build.sh uses an installed LaTeX distribution.
- certs/: all17 exact certificates; checker/: logical/recomputation and regression tools.
- progA/, progB/, progC/: three exact density engines; logs/: saved A sweeps.
- RESULTS.md: exact certificate-generated table.
- DERIVATION.md: historical AI-assisted algorithm audit; later corrections at its top supersede earlier precondition warnings. The manuscript is the current statement of claims.
- SHA256SUMS and verify_integrity.py: static file inventory; runtime validation logs and Python caches are excluded by design.

## Licences
MIT for project code and software-use documentation; CC BY4.0 for the preprint/exposition and supporting outputs to the extent applicable. See LICENSE and LICENSING.md for scope and third-party font attribution. Publication is not peer review.

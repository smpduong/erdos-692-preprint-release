#!/bin/sh
# Requires an installed LaTeX distribution; output stays outside the release tree.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:-$(mktemp -d)}
mkdir -p "$OUT"
pdflatex -output-format=pdf -halt-on-error -interaction=nonstopmode -output-directory="$OUT" "$HERE/Erdos_692_Preprint_2026-11-18.tex"
pdflatex -output-format=pdf -halt-on-error -interaction=nonstopmode -output-directory="$OUT" "$HERE/Erdos_692_Preprint_2026-11-18.tex"
printf 'Rebuilt PDF: %s/Erdos_692_Preprint_2026-11-18.pdf\n' "$OUT"

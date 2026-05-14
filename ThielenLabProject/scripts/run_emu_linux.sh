#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"}
MANIFEST=${MANIFEST:-"$PROJECT_ROOT/data/synthetic/manifest.tsv"}
READS_ROOT=${READS_ROOT:-"$PROJECT_ROOT/data/synthetic/reads"}
EMU_DB=${EMU_DB:-"${EMU_DATABASE_DIR:-$PROJECT_ROOT/database/emu}"}
EMU_OUT=${EMU_OUT:-"$PROJECT_ROOT/results/emu"}
THREADS=${THREADS:-16}
DEFAULT_TYPE=${DEFAULT_TYPE:-map-ont}

if [[ ! -s "$EMU_DB/species_taxid.fasta" || ! -s "$EMU_DB/taxonomy.tsv" ]]; then
  echo "Emu database is missing required files in: $EMU_DB" >&2
  echo "Expected species_taxid.fasta and taxonomy.tsv" >&2
  exit 1
fi

export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

python -m minnelove_emu.cli emu-run \
  --manifest "$MANIFEST" \
  --reads-root "$READS_ROOT" \
  --db "$EMU_DB" \
  --out "$EMU_OUT" \
  --threads "$THREADS" \
  --default-type "$DEFAULT_TYPE"

python -m minnelove_emu.cli emu-combine \
  --emu-dir "$EMU_OUT" \
  --db "$EMU_DB" \
  --rank species


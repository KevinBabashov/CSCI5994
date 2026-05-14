#!/usr/bin/env bash
set -euo pipefail

ENV_NAME=${ENV_NAME:-minnelove-emu}
EMU_DATABASE_DIR=${EMU_DATABASE_DIR:-"$PWD/database/emu"}
EMU_PREBUILT_DB=${EMU_PREBUILT_DB:-emu}

if command -v mamba >/dev/null 2>&1; then
  CONDA_FRONTEND=mamba
elif command -v conda >/dev/null 2>&1; then
  CONDA_FRONTEND=conda
else
  echo "Install conda or mamba before running this setup script." >&2
  exit 1
fi

"$CONDA_FRONTEND" create -y -n "$ENV_NAME" -c conda-forge -c bioconda emu fastp kraken2 bracken osfclient

cat <<EOF

Created conda environment: $ENV_NAME

Next:
  conda activate $ENV_NAME
  export EMU_DATABASE_DIR=$EMU_DATABASE_DIR

Optional default Emu database download:
  mkdir -p "\$EMU_DATABASE_DIR"
  cd "\$EMU_DATABASE_DIR"
  osf -p 56uf7 fetch osfstorage/emu-prebuilt/$EMU_PREBUILT_DB.tar
  tar -xvf $EMU_PREBUILT_DB.tar

The Emu database directory must contain:
  species_taxid.fasta
  taxonomy.tsv
EOF


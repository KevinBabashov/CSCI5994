# Real Emu on Linux

The Windows project demo creates synthetic Emu-style tables. Real Emu execution is handled by
`src/minnelove_emu/emu.py` and should run on Linux, where the bioinformatics command-line tools and
databases are available.

Upstream Emu source and usage notes: https://gitlab.com/treangenlab/emu

## 1. Install Tools

On the Linux server:

```bash
bash scripts/setup_emu_linux.sh
conda activate minnelove-emu
```

The setup script installs `emu`, `fastp`, `kraken2`, `bracken`, and `osfclient` from conda/bioconda.

## 2. Prepare Emu Database

The upstream Emu README says the database directory must contain:

```text
species_taxid.fasta
taxonomy.tsv
```

Example default database download:

```bash
export EMU_DATABASE_DIR=/path/to/database/emu
mkdir -p "$EMU_DATABASE_DIR"
cd "$EMU_DATABASE_DIR"
osf -p 56uf7 fetch osfstorage/emu-prebuilt/emu.tar
tar -xvf emu.tar
```

## 3. Dry Run from Windows or Linux

This prints the exact Emu commands without executing them:

```powershell
uv run minnelove emu-run --manifest data/synthetic/manifest.tsv --reads-root data/synthetic/reads --db database/emu --out results/emu --threads 16 --dry-run
```

## 4. Run Real Emu on Linux

```bash
export PROJECT_ROOT=/path/to/ThielenLabProject
export EMU_DB=/path/to/database/emu
export MANIFEST=$PROJECT_ROOT/data/synthetic/manifest.tsv
export READS_ROOT=$PROJECT_ROOT/data/synthetic/reads
bash scripts/run_emu_linux.sh
```

For real MINNELOVE data, use a manifest with at least:

```text
sample_id
fastq_path
platform
```

Supported platform values include `ont`, `nanopore`, `map-ont`, `pacbio`, `map-pb`, `hifi`, and
`map-hifi`.

## Code Entry Points

- Real Emu runner: `src/minnelove_emu/emu.py`
- CLI command: `uv run minnelove emu-run ...`
- Linux setup: `scripts/setup_emu_linux.sh`
- Linux run wrapper: `scripts/run_emu_linux.sh`

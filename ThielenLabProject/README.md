# MINNELOVE Emu Proof of Concept

This repository is a starting point for a MINNELOVE respiratory microbiome analysis
interface. The runnable workflow is organized as Python modules and scripts; notebooks are kept for
exploration and figure/model experiments.

The current proof of concept uses synthetic data only. It does not include real participant metadata,
real clinical labels, or real sequencing reads.

## What This Provides

- Synthetic long-read 16S-like FASTQ files for local demos.
- Synthetic Emu-style species abundance tables.
- Synthetic Bracken-style abundance tables for method comparison.
- A sample-by-taxon feature matrix for downstream modeling.
- A Streamlit dashboard for reviewing sample metadata, taxa, diversity, and Emu/Bracken agreement.
- A real Emu runner and Linux bash scripts for server-side execution.
- A report draft generator for the directed research submission.

## Local Setup on Windows

From this folder:

```powershell
uv sync --extra dev
uv run minnelove generate-demo
uv run minnelove build-features
uv run minnelove compare-methods
uv run minnelove write-report
uv run streamlit run scripts/launch_dashboard.py
```

If you do not want the developer tools:

```powershell
uv sync
```

## Linux Server Workflow

The local dashboard and synthetic data generation work on Windows. The real sequencing tools should
run on Linux.

After synthetic data exist, generate a bash script:

```powershell
uv run minnelove make-linux-script --config configs/linux_server_template.json --out scripts/run_pipeline_linux.sh
```

On the Linux server, edit or export the real database locations:

```bash
export PROJECT_ROOT=/path/to/ThielenLabProject
export EMU_DB=/path/to/emu_database
export KRAKEN_DB=/path/to/kraken2_database
bash scripts/run_pipeline_linux.sh
```

The MSI-specific paths are intentionally not encoded yet. Fill them in once the lab website or shared
pipeline notes are available.

For the dedicated real-Emu path, see `docs/EMU_LINUX.md`.

Dry-run the exact Emu commands locally:

```powershell
uv run minnelove emu-run --manifest data/synthetic/manifest.tsv --reads-root data/synthetic/reads --db database/emu --out results/emu --threads 16 --dry-run
```

Run real Emu on Linux after activating the Emu environment:

```bash
bash scripts/run_emu_linux.sh
```

## Commands

```powershell
uv run minnelove generate-demo --samples 8 --reads 120
uv run minnelove build-features --rank species
uv run minnelove train-model
uv run minnelove summary
uv run minnelove write-report
```

## Repository Layout

```text
src/minnelove_emu/       Python package for data generation, parsing, analysis, and pipeline scripts
scripts/                 Thin entry-point scripts
configs/                 Local demo and Linux server template configs
data/synthetic/          Generated synthetic proof-of-concept data
data/processed/          Generated feature tables and comparisons
reports/                 Directed research report draft
notebooks/               Optional exploratory notebooks only
Data_Pre_Processing/     Original example FASTQ and fastp outputs kept local
Data_Processing/         Original exploratory notebooks
```

See `docs/DESIGN.md` for the SOLID-oriented module layout.

## Method Scope

Emu is a strong fit for long-read 16S bacterial/archaeal taxonomic profiling because it estimates
relative abundance from full-length marker reads with an expectation-maximization approach. Bracken
is the Bayesian abundance re-estimation method commonly paired with Kraken/Kraken2. Emu should not
be presented as a general replacement for viral metagenomic classification. For respiratory virus
identification, keep Kraken2/Bracken or another viral-aware workflow in the comparison unless the lab
has a validated viral marker/database strategy.

See `docs/METHODS_NOTES.md` for slide-friendly method notes and references.

## Data Management Notes

- Do not commit real FASTQ, BAM, SAM, CRAM, or participant-level clinical data.
- Keep `.env` files and database paths out of git.
- Keep reusable workflow code in Python modules instead of notebooks.
- Commit small synthetic data and documentation so lab members can run the demo without private data.

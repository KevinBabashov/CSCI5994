from __future__ import annotations

from datetime import date
from pathlib import Path

from .analysis import demo_summary


def write_project_report(demo_root: str | Path, output_path: str | Path) -> Path:
    summary = demo_summary(demo_root)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# MINNELOVE Emu Proof of Concept

Date: {date.today().isoformat()}

## Project Goal

This project builds a Windows-compatible local interface and Python package for exploring
long-read MINNELOVE respiratory microbiome samples with an Emu-centered workflow. The current
proof of concept uses synthetic 16S-like reads and synthetic Emu/Bracken-style outputs so the
code can be shared without exposing real participant data.

## Current Dataset

- Synthetic samples: {summary["samples"]}
- Synthetic taxa: {summary["taxa"]}
- Synthetic reads: {summary["total_reads"]}
- Mean Shannon diversity: {summary["mean_shannon"]:.3f}

## Workflow Implemented

1. Generate synthetic long-read FASTQ files and known truth tables.
2. Generate Emu-style relative abundance outputs for species-level analysis.
3. Generate Bracken-style abundance outputs for side-by-side method comparison.
4. Build a sample-by-taxon feature matrix for downstream modeling.
5. Render a Streamlit dashboard for lab-facing review.
6. Generate a Linux bash script that can be adapted for server execution once database paths are known.

## Scientific Scope

Emu is most appropriate here as a long-read 16S taxonomic profiler for bacterial and archaeal
community composition. Emu's abundance estimation is expectation-maximization based, while Bracken
is the Bayesian re-estimation method commonly paired with Kraken/Kraken2. Emu is not a replacement
for viral metagenomic classification. For respiratory virus detection, Kraken2/Bracken or another
viral metagenomics workflow should remain part of the comparison unless the lab has a separate
marker/database strategy for viruses.

## Reproducibility Notes

- Local development is driven by `uv` and `pyproject.toml`.
- Synthetic data live under `data/synthetic`.
- Real FASTQ/BAM files are ignored by `.gitignore`.
- Pipeline commands are generated as Linux bash because the sequencing tools are expected to run on a Linux server.

## Next Steps

1. Replace the demo database placeholders in `configs/linux_server_template.json`.
2. Confirm the exact lab preprocessing commands for ONT and PacBio samples.
3. Run a small real-data pilot on the Linux server and compare Emu, Kraken2, and Bracken outputs.
4. Decide which summary tables and figures should be standardized for the lab repository.
"""
    output.write_text(text, encoding="utf-8", newline="\n")
    return output

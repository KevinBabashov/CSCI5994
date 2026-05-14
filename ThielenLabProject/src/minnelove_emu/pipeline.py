from __future__ import annotations

import csv
from pathlib import Path, PurePosixPath
import shlex

from .config import PipelineConfig
from .emu import emu_map_type


def render_linux_pipeline_script(
    manifest_path: str | Path,
    config: PipelineConfig,
    output_path: str | Path,
) -> Path:
    """Write a Linux bash script for preprocessing and taxonomy classification."""

    manifest = _read_tsv(Path(manifest_path))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "PROJECT_ROOT=${PROJECT_ROOT:-" + shlex.quote(_posix(config.project_root)) + "}",
        "RAW_DIR=\"$PROJECT_ROOT/data/synthetic/reads\"",
        "CLEAN_DIR=\"$PROJECT_ROOT/results/clean_fastq\"",
        "QC_DIR=\"$PROJECT_ROOT/results/qc\"",
        "EMU_DIR=\"$PROJECT_ROOT/results/emu\"",
        "KRAKEN_DIR=\"$PROJECT_ROOT/results/kraken\"",
        "BRACKEN_DIR=\"$PROJECT_ROOT/results/bracken\"",
        "mkdir -p \"$CLEAN_DIR\" \"$QC_DIR\" \"$EMU_DIR\" \"$KRAKEN_DIR\" \"$BRACKEN_DIR\"",
        "",
        "EMU_DB=${EMU_DB:-" + shlex.quote(config.emu_db) + "}",
        "KRAKEN_DB=${KRAKEN_DB:-" + shlex.quote(config.kraken_db) + "}",
        "",
        "test -s \"$EMU_DB/species_taxid.fasta\"",
        "test -s \"$EMU_DB/taxonomy.tsv\"",
        "",
    ]

    for row in manifest:
        sample_id = row["sample_id"]
        fastq_name = PurePosixPath(row["fastq_path"]).name
        platform = row.get("platform") or config.platform
        lines.extend(_sample_linux_commands(sample_id, fastq_name, config, platform))
        lines.append("")

    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return output


def _sample_linux_commands(
    sample_id: str,
    fastq_name: str,
    config: PipelineConfig,
    platform: str,
) -> list[str]:
    clean_name = f"{sample_id}.clean.fastq.gz"
    lines = [
        f"echo 'Processing {sample_id}'",
        "fastp "
        + " ".join(
            [
                "-i",
                _var_path("RAW_DIR", fastq_name),
                "-o",
                _var_path("CLEAN_DIR", clean_name),
                "-h",
                _var_path("QC_DIR", f"{sample_id}.fastp.html"),
                "-j",
                _var_path("QC_DIR", f"{sample_id}.fastp.json"),
                "-w",
                str(config.threads),
                "-q",
                str(config.quality_cutoff),
                "-l",
                str(config.min_read_length),
            ]
        ),
        "emu abundance "
        + " ".join(
            [
                _var_path("CLEAN_DIR", clean_name),
                "--db",
                '"$EMU_DB"',
                "--type",
                emu_map_type(platform),
                "--output-dir",
                '"$EMU_DIR"',
                "--output-basename",
                sample_id,
                "--threads",
                str(config.threads),
                "--keep-counts",
            ]
        ),
    ]

    if config.include_kraken_bracken:
        lines.extend(
            [
                "kraken2 "
                + " ".join(
                    [
                        "--db",
                        '"$KRAKEN_DB"',
                        "--threads",
                        str(config.threads),
                        "--gzip-compressed",
                        "--use-names",
                        "--report",
                        _var_path("KRAKEN_DIR", f"{sample_id}.kraken.report"),
                        "--output",
                        _var_path("KRAKEN_DIR", f"{sample_id}.kraken.out"),
                        _var_path("CLEAN_DIR", clean_name),
                    ]
                ),
                "bracken "
                + " ".join(
                    [
                        "-d",
                        '"$KRAKEN_DB"',
                        "-i",
                        _var_path("KRAKEN_DIR", f"{sample_id}.kraken.report"),
                        "-o",
                        _var_path("BRACKEN_DIR", f"{sample_id}.bracken.tsv"),
                        "-r",
                        str(config.read_length_for_bracken),
                        "-l",
                        "S",
                        "-t",
                        "10",
                    ]
                ),
            ]
        )
    return lines


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _posix(path: Path) -> str:
    return path.as_posix() if path.is_absolute() else PurePosixPath(path).as_posix()


def _var_path(variable_name: str, name: str) -> str:
    safe_name = shlex.quote(name)
    if safe_name == name:
        return f'"${variable_name}/{name}"'
    return f'"${variable_name}/"{safe_name}'


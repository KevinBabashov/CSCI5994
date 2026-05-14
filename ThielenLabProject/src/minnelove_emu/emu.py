from __future__ import annotations

from dataclasses import dataclass, field
import csv
from pathlib import Path, PurePosixPath
import shlex
import shutil
import subprocess
from typing import Iterable


SUPPORTED_EMU_TYPES = {
    "ont": "map-ont",
    "nanopore": "map-ont",
    "minion": "map-ont",
    "pb": "map-pb",
    "pacbio": "map-pb",
    "hifi": "map-hifi",
    "pacbio_hifi": "map-hifi",
    "q20": "lr:hq",
    "nanopore_q20": "lr:hq",
    "sr": "sr",
    "short-read": "sr",
    "short_read": "sr",
    "map-ont": "map-ont",
    "map-pb": "map-pb",
    "map-hifi": "map-hifi",
    "lr:hq": "lr:hq",
}


@dataclass(frozen=True)
class EmuRunConfig:
    """Runtime options for real Emu command execution."""

    db: str | Path
    output_dir: str | Path
    emu_bin: str = "emu"
    threads: int = 3
    default_type: str = "map-ont"
    min_abundance: float = 0.0001
    min_pid: float | None = None
    min_align_len: int | None = None
    max_align_len: int | None = 2000
    keep_counts: bool = True
    keep_files: bool = False
    keep_read_assignments: bool = False
    output_unclassified: bool = False
    extra_args: tuple[str, ...] = field(default_factory=tuple)
    dry_run: bool = False


@dataclass(frozen=True)
class EmuCommandResult:
    sample_id: str
    command: list[str]
    expected_output: Path
    returncode: int | None = None

    @property
    def shell_command(self) -> str:
        return shlex.join(self.command)


class EmuRunner:
    """Small wrapper around the external Emu CLI.

    This class intentionally does not reimplement Emu's EM algorithm. It prepares validated,
    reproducible calls to the published Emu command-line tool.
    """

    def __init__(self, config: EmuRunConfig):
        self.config = config

    def check_installation(self, validate_db: bool = True) -> list[str]:
        issues = []
        if shutil.which(self.config.emu_bin) is None and not Path(self.config.emu_bin).exists():
            issues.append(f"Emu executable not found: {self.config.emu_bin}")
        if validate_db:
            issues.extend(validate_emu_database(self.config.db))
        return issues

    def build_abundance_command(
        self,
        read_path: str | Path,
        sample_id: str,
        sequencing_type: str | None = None,
    ) -> list[str]:
        emu_type = emu_map_type(sequencing_type or self.config.default_type)
        command = [
            self.config.emu_bin,
            "abundance",
            _command_path(read_path),
            "--db",
            _command_path(self.config.db),
            "--type",
            emu_type,
            "--output-dir",
            _command_path(self.config.output_dir),
            "--output-basename",
            sample_id,
            "--threads",
            str(self.config.threads),
            "--min-abundance",
            str(self.config.min_abundance),
        ]

        if self.config.min_pid is not None:
            command.extend(["--min-pid", str(self.config.min_pid)])
        if self.config.min_align_len is not None:
            command.extend(["--min-align-len", str(self.config.min_align_len)])
        if self.config.max_align_len is not None:
            command.extend(["--max-align-len", str(self.config.max_align_len)])
        if self.config.keep_counts:
            command.append("--keep-counts")
        if self.config.keep_files:
            command.append("--keep-files")
        if self.config.keep_read_assignments:
            command.append("--keep-read-assignments")
        if self.config.output_unclassified:
            command.append("--output-unclassified")
        command.extend(self.config.extra_args)
        return command

    def run_abundance(
        self,
        read_path: str | Path,
        sample_id: str,
        sequencing_type: str | None = None,
    ) -> EmuCommandResult:
        command = self.build_abundance_command(read_path, sample_id, sequencing_type)
        expected_output = Path(self.config.output_dir) / f"{sample_id}_rel-abundance.tsv"

        if self.config.dry_run:
            return EmuCommandResult(sample_id=sample_id, command=command, expected_output=expected_output)

        issues = self.check_installation(validate_db=True)
        if issues:
            raise RuntimeError("Cannot run Emu:\n" + "\n".join(f"- {issue}" for issue in issues))

        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(command, check=True)
        return EmuCommandResult(
            sample_id=sample_id,
            command=command,
            expected_output=expected_output,
            returncode=completed.returncode,
        )

    def run_manifest(
        self,
        manifest_path: str | Path,
        reads_root: str | Path | None = None,
        fastq_column: str = "fastq_path",
        platform_column: str = "platform",
    ) -> list[EmuCommandResult]:
        manifest = Path(manifest_path)
        rows = _read_tsv(manifest)
        results = []

        for row in rows:
            sample_id = row["sample_id"]
            read_path = resolve_read_path(row[fastq_column], manifest, reads_root)
            platform = row.get(platform_column) or self.config.default_type
            results.append(self.run_abundance(read_path, sample_id, platform))
        return results

    def build_combine_outputs_command(
        self,
        rank: str = "species",
        split_tables: bool = False,
        counts: bool = False,
    ) -> list[str]:
        command = [self.config.emu_bin, "combine-outputs", _command_path(self.config.output_dir), rank]
        if split_tables:
            command.append("--split-tables")
        if counts:
            command.append("--counts")
        return command

    def combine_outputs(
        self,
        rank: str = "species",
        split_tables: bool = False,
        counts: bool = False,
    ) -> list[str]:
        command = self.build_combine_outputs_command(rank, split_tables, counts)
        if self.config.dry_run:
            return command
        if shutil.which(self.config.emu_bin) is None and not Path(self.config.emu_bin).exists():
            raise RuntimeError(f"Emu executable not found: {self.config.emu_bin}")
        subprocess.run(command, check=True)
        return command


def emu_map_type(platform: str) -> str:
    normalized = platform.strip().lower()
    if normalized in SUPPORTED_EMU_TYPES:
        return SUPPORTED_EMU_TYPES[normalized]
    raise ValueError(f"Unsupported Emu sequencing type: {platform}")


def validate_emu_database(db_path: str | Path) -> list[str]:
    db = Path(db_path)
    issues = []
    if not db.exists():
        return [f"Emu database directory does not exist: {db}"]
    if not db.is_dir():
        return [f"Emu database path is not a directory: {db}"]

    required = ["species_taxid.fasta", "taxonomy.tsv"]
    for filename in required:
        if not (db / filename).exists():
            issues.append(f"Missing Emu database file: {db / filename}")
    return issues


def resolve_read_path(
    raw_value: str,
    manifest_path: Path,
    reads_root: str | Path | None = None,
) -> Path:
    candidate = Path(raw_value)
    if candidate.is_absolute():
        return candidate

    posix_name = PurePosixPath(raw_value).name
    if reads_root is not None:
        return Path(reads_root) / posix_name

    manifest_parent = manifest_path.parent
    candidates = [
        manifest_parent / raw_value,
        manifest_parent.parent / raw_value,
        Path.cwd() / raw_value,
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def write_command_script(commands: Iterable[list[str]], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    lines.extend(shlex.join(command) for command in commands)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return output


def _command_path(value: str | Path) -> str:
    text = str(value)
    if text.startswith("\\") and not text.startswith("\\\\"):
        text = "/" + text.lstrip("\\")
    return text.replace("\\", "/")


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

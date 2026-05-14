from __future__ import annotations

import csv
import gzip
from pathlib import Path
import random
from typing import Iterable


TAXA = [
    {
        "tax_id": "SYN0001",
        "species": "Streptococcus pneumoniae",
        "genus": "Streptococcus",
        "family": "Streptococcaceae",
        "phylum": "Bacillota",
    },
    {
        "tax_id": "SYN0002",
        "species": "Haemophilus influenzae",
        "genus": "Haemophilus",
        "family": "Pasteurellaceae",
        "phylum": "Pseudomonadota",
    },
    {
        "tax_id": "SYN0003",
        "species": "Moraxella catarrhalis",
        "genus": "Moraxella",
        "family": "Moraxellaceae",
        "phylum": "Pseudomonadota",
    },
    {
        "tax_id": "SYN0004",
        "species": "Staphylococcus aureus",
        "genus": "Staphylococcus",
        "family": "Staphylococcaceae",
        "phylum": "Bacillota",
    },
    {
        "tax_id": "SYN0005",
        "species": "Corynebacterium accolens",
        "genus": "Corynebacterium",
        "family": "Corynebacteriaceae",
        "phylum": "Actinomycetota",
    },
    {
        "tax_id": "SYN0006",
        "species": "Dolosigranulum pigrum",
        "genus": "Dolosigranulum",
        "family": "Carnobacteriaceae",
        "phylum": "Bacillota",
    },
    {
        "tax_id": "SYN0007",
        "species": "Prevotella melaninogenica",
        "genus": "Prevotella",
        "family": "Prevotellaceae",
        "phylum": "Bacteroidota",
    },
    {
        "tax_id": "SYN0008",
        "species": "Neisseria subflava",
        "genus": "Neisseria",
        "family": "Neisseriaceae",
        "phylum": "Pseudomonadota",
    },
    {
        "tax_id": "SYN0009",
        "species": "Veillonella parvula",
        "genus": "Veillonella",
        "family": "Veillonellaceae",
        "phylum": "Bacillota",
    },
    {
        "tax_id": "SYN0010",
        "species": "Lactobacillus crispatus",
        "genus": "Lactobacillus",
        "family": "Lactobacillaceae",
        "phylum": "Bacillota",
    },
]

PROFILE_WEIGHTS = {
    "asymptomatic": {
        "Streptococcus pneumoniae": 0.04,
        "Haemophilus influenzae": 0.03,
        "Moraxella catarrhalis": 0.05,
        "Staphylococcus aureus": 0.04,
        "Corynebacterium accolens": 0.24,
        "Dolosigranulum pigrum": 0.25,
        "Prevotella melaninogenica": 0.08,
        "Neisseria subflava": 0.13,
        "Veillonella parvula": 0.09,
        "Lactobacillus crispatus": 0.05,
    },
    "mild_uri": {
        "Streptococcus pneumoniae": 0.13,
        "Haemophilus influenzae": 0.14,
        "Moraxella catarrhalis": 0.18,
        "Staphylococcus aureus": 0.08,
        "Corynebacterium accolens": 0.13,
        "Dolosigranulum pigrum": 0.10,
        "Prevotella melaninogenica": 0.07,
        "Neisseria subflava": 0.08,
        "Veillonella parvula": 0.06,
        "Lactobacillus crispatus": 0.03,
    },
    "ili": {
        "Streptococcus pneumoniae": 0.20,
        "Haemophilus influenzae": 0.17,
        "Moraxella catarrhalis": 0.17,
        "Staphylococcus aureus": 0.11,
        "Corynebacterium accolens": 0.08,
        "Dolosigranulum pigrum": 0.06,
        "Prevotella melaninogenica": 0.09,
        "Neisseria subflava": 0.05,
        "Veillonella parvula": 0.05,
        "Lactobacillus crispatus": 0.02,
    },
}

SAMPLE_BLUEPRINTS = [
    ("MINNELOVE_SYN_001", "HH01", "P01", 0, "asymptomatic", "negative", "ont"),
    ("MINNELOVE_SYN_002", "HH01", "P01", 7, "mild_uri", "rhinovirus", "ont"),
    ("MINNELOVE_SYN_003", "HH01", "P02", 7, "mild_uri", "rhinovirus", "ont"),
    ("MINNELOVE_SYN_004", "HH02", "P03", 0, "asymptomatic", "negative", "ont"),
    ("MINNELOVE_SYN_005", "HH02", "P03", 14, "ili", "influenza_a", "ont"),
    ("MINNELOVE_SYN_006", "HH02", "P04", 14, "ili", "influenza_a", "ont"),
    ("MINNELOVE_SYN_007", "HH03", "P05", 0, "asymptomatic", "negative", "pacbio"),
    ("MINNELOVE_SYN_008", "HH03", "P05", 7, "mild_uri", "rsv", "pacbio"),
]


def generate_demo_dataset(
    out_dir: str | Path,
    sample_count: int = 8,
    reads_per_sample: int = 120,
    seed: int = 5994,
) -> dict[str, Path]:
    """Create small synthetic FASTQ and classifier-output tables for demos.

    The FASTQ reads are synthetic 16S-like sequences and are not derived from human samples.
    """

    if sample_count < 1:
        raise ValueError("sample_count must be at least 1")

    root = Path(out_dir)
    reads_dir = root / "reads"
    emu_dir = root / "emu_outputs"
    bracken_dir = root / "bracken_outputs"
    truth_dir = root / "truth"
    refs_dir = root / "references"

    for directory in [reads_dir, emu_dir, bracken_dir, truth_dir, refs_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    references = _make_references(seed=seed)
    _write_reference_fasta(refs_dir / "synthetic_16s_references.fasta", references)
    _write_taxonomy_reference(root / "taxonomy_reference.tsv")

    blueprints = _expanded_blueprints(sample_count)
    manifest_rows = []
    truth_rows = []

    for index, blueprint in enumerate(blueprints):
        sample_id, household_id, participant_id, visit_day, symptom_status, virus_status, platform = blueprint
        sample_rng = random.Random(seed + index * 101)
        weights = _jitter_weights(PROFILE_WEIGHTS[symptom_status], sample_rng)
        counts = _draw_counts(weights, reads_per_sample, sample_rng)

        fastq_path = reads_dir / f"{sample_id}.fastq.gz"
        _write_fastq(fastq_path, sample_id, counts, references, sample_rng)

        emu_path = emu_dir / f"{sample_id}_rel-abundance.tsv"
        bracken_path = bracken_dir / f"{sample_id}.bracken.tsv"
        _write_emu_output(emu_path, counts)
        _write_bracken_output(bracken_path, counts)

        manifest_rows.append(
            {
                "sample_id": sample_id,
                "household_id": household_id,
                "participant_id": participant_id,
                "visit_day": visit_day,
                "symptom_status": symptom_status,
                "virus_status": virus_status,
                "platform": platform,
                "fastq_path": _as_posix(root.name, "reads", fastq_path.name),
                "emu_output": _as_posix(root.name, "emu_outputs", emu_path.name),
                "bracken_output": _as_posix(root.name, "bracken_outputs", bracken_path.name),
                "synthetic": "true",
                "read_count": sum(counts.values()),
            }
        )

        total = sum(counts.values())
        for species, count in counts.items():
            taxon = _taxon_by_species(species)
            truth_rows.append(
                {
                    "sample_id": sample_id,
                    "species": species,
                    "genus": taxon["genus"],
                    "true_reads": count,
                    "true_relative_abundance": count / total if total else 0.0,
                }
            )

    _write_tsv(root / "manifest.tsv", manifest_rows)
    _write_tsv(truth_dir / "synthetic_truth_abundance.tsv", truth_rows)
    _write_combined_matrix(root / "emu_combined_species.tsv", emu_dir)

    return {
        "root": root,
        "manifest": root / "manifest.tsv",
        "reads_dir": reads_dir,
        "emu_dir": emu_dir,
        "bracken_dir": bracken_dir,
        "truth": truth_dir / "synthetic_truth_abundance.tsv",
    }


def _expanded_blueprints(sample_count: int) -> list[tuple[str, str, str, int, str, str, str]]:
    rows = []
    for idx in range(sample_count):
        if idx < len(SAMPLE_BLUEPRINTS):
            rows.append(SAMPLE_BLUEPRINTS[idx])
            continue
        sample_number = idx + 1
        household = f"HH{(idx // 2) + 1:02d}"
        participant = f"P{idx + 1:02d}"
        status = ("asymptomatic", "mild_uri", "ili")[idx % 3]
        virus = {"asymptomatic": "negative", "mild_uri": "rhinovirus", "ili": "influenza_a"}[status]
        platform = "ont" if idx % 4 else "pacbio"
        rows.append(
            (
                f"MINNELOVE_SYN_{sample_number:03d}",
                household,
                participant,
                (idx % 4) * 7,
                status,
                virus,
                platform,
            )
        )
    return rows


def _make_references(seed: int) -> dict[str, str]:
    refs = {}
    for idx, taxon in enumerate(TAXA):
        rng = random.Random(seed + idx)
        length = 1465 + rng.randint(-35, 45)
        refs[taxon["species"]] = _random_sequence(length, rng)
    return refs


def _random_sequence(length: int, rng: random.Random) -> str:
    alphabet = ["A", "C", "G", "T"]
    weights = [0.23, 0.27, 0.27, 0.23]
    return "".join(rng.choices(alphabet, weights=weights, k=length))


def _write_reference_fasta(path: Path, references: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for species, sequence in references.items():
            taxon = _taxon_by_species(species)
            handle.write(f">{taxon['tax_id']} {species}\n")
            for start in range(0, len(sequence), 80):
                handle.write(sequence[start : start + 80] + "\n")


def _write_taxonomy_reference(path: Path) -> None:
    _write_tsv(path, TAXA)


def _jitter_weights(weights: dict[str, float], rng: random.Random) -> dict[str, float]:
    jittered = {}
    for species, weight in weights.items():
        jittered[species] = max(weight * rng.uniform(0.75, 1.25), 0.001)
    total = sum(jittered.values())
    return {species: weight / total for species, weight in jittered.items()}


def _draw_counts(weights: dict[str, float], total_reads: int, rng: random.Random) -> dict[str, int]:
    species = list(weights)
    probabilities = [weights[name] for name in species]
    counts = {name: 0 for name in species}
    for name in rng.choices(species, weights=probabilities, k=total_reads):
        counts[name] += 1
    return counts


def _write_fastq(
    path: Path,
    sample_id: str,
    counts: dict[str, int],
    references: dict[str, str],
    rng: random.Random,
) -> None:
    with gzip.open(path, "wt", encoding="utf-8", newline="\n") as handle:
        read_index = 1
        for species, count in counts.items():
            reference = references[species]
            for _ in range(count):
                read_length = max(900, min(len(reference), int(rng.gauss(1450, 90))))
                start = rng.randint(0, max(len(reference) - read_length, 0))
                sequence = reference[start : start + read_length]
                sequence = _introduce_errors(sequence, rng, error_rate=0.012)
                quality = _quality_string(len(sequence), rng)
                taxon = species.replace(" ", "_")
                handle.write(f"@{sample_id}_{read_index:05d}|{taxon}\n")
                handle.write(sequence + "\n")
                handle.write("+\n")
                handle.write(quality + "\n")
                read_index += 1


def _introduce_errors(sequence: str, rng: random.Random, error_rate: float) -> str:
    bases = ["A", "C", "G", "T"]
    output = []
    for base in sequence:
        if rng.random() < error_rate:
            output.append(rng.choice([candidate for candidate in bases if candidate != base]))
        else:
            output.append(base)
    return "".join(output)


def _quality_string(length: int, rng: random.Random) -> str:
    qualities = []
    for _ in range(length):
        q_score = int(max(12, min(38, rng.gauss(27, 4))))
        qualities.append(chr(q_score + 33))
    return "".join(qualities)


def _write_emu_output(path: Path, counts: dict[str, int]) -> None:
    total = sum(counts.values())
    rows = []
    for species, count in sorted(counts.items()):
        taxon = _taxon_by_species(species)
        abundance = count / total if total else 0.0
        rows.append(
            {
                "tax_id": taxon["tax_id"],
                "abundance": f"{abundance:.8f}",
                "estimated_counts": count,
                "species": taxon["species"],
                "genus": taxon["genus"],
                "family": taxon["family"],
                "phylum": taxon["phylum"],
            }
        )
    _write_tsv(path, rows)


def _write_bracken_output(path: Path, counts: dict[str, int]) -> None:
    total = sum(counts.values())
    rows = []
    for species, count in sorted(counts.items()):
        taxon = _taxon_by_species(species)
        rows.append(
            {
                "name": species,
                "taxonomy_id": taxon["tax_id"],
                "taxonomy_lvl": "S",
                "kraken_assigned_reads": max(count - 2, 0),
                "added_reads": min(count, 2),
                "new_est_reads": count,
                "fraction_total_reads": f"{count / total if total else 0.0:.8f}",
            }
        )
    _write_tsv(path, rows)


def _write_combined_matrix(path: Path, emu_dir: Path) -> None:
    sample_tables = {}
    species_set = set()
    for emu_path in sorted(emu_dir.glob("*_rel-abundance.tsv")):
        sample_id = emu_path.name.replace("_rel-abundance.tsv", "")
        rows = _read_tsv(emu_path)
        sample_tables[sample_id] = {row["species"]: float(row["abundance"]) for row in rows}
        species_set.update(sample_tables[sample_id])

    output_rows = []
    for species in sorted(species_set):
        row = {"species": species}
        for sample_id in sorted(sample_tables):
            row[sample_id] = f"{sample_tables[sample_id].get(species, 0.0):.8f}"
        output_rows.append(row)
    _write_tsv(path, output_rows)


def _taxon_by_species(species: str) -> dict[str, str]:
    for taxon in TAXA:
        if taxon["species"] == species:
            return taxon
    raise KeyError(f"Unknown synthetic species: {species}")


def _write_tsv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _as_posix(*parts: str) -> str:
    return "/".join(parts)

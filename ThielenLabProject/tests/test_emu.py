from pathlib import Path

from minnelove_emu.emu import EmuRunConfig, EmuRunner, emu_map_type, validate_emu_database
from minnelove_emu.synthetic import generate_demo_dataset


def test_emu_map_type() -> None:
    assert emu_map_type("ont") == "map-ont"
    assert emu_map_type("pacbio") == "map-pb"
    assert emu_map_type("hifi") == "map-hifi"


def test_build_abundance_command() -> None:
    runner = EmuRunner(
        EmuRunConfig(
            db=Path("/db/emu"),
            output_dir=Path("/project/results/emu"),
            threads=16,
            dry_run=True,
        )
    )

    command = runner.build_abundance_command("/reads/sample.fastq.gz", "sample", "ont")

    assert command[:2] == ["emu", "abundance"]
    assert "--db" in command
    assert "/db/emu" in command
    assert "--type" in command
    assert "map-ont" in command
    assert "--output-basename" in command
    assert "sample" in command
    assert "--keep-counts" in command


def test_run_manifest_dry_run(tmp_path: Path) -> None:
    paths = generate_demo_dataset(tmp_path / "synthetic", sample_count=8, reads_per_sample=5, seed=101)
    runner = EmuRunner(
        EmuRunConfig(
            db=tmp_path / "emu_db",
            output_dir=tmp_path / "results" / "emu",
            threads=4,
            dry_run=True,
        )
    )

    results = runner.run_manifest(paths["manifest"], reads_root=paths["reads_dir"])

    assert len(results) == 8
    assert any("map-pb" in result.command for result in results)
    assert results[0].expected_output.name == "MINNELOVE_SYN_001_rel-abundance.tsv"


def test_validate_emu_database(tmp_path: Path) -> None:
    db = tmp_path / "emu"
    db.mkdir()
    assert validate_emu_database(db)

    (db / "species_taxid.fasta").write_text(">1:test\nACGT\n", encoding="utf-8")
    (db / "taxonomy.tsv").write_text("tax_id\tspecies\n1\tExample species\n", encoding="utf-8")
    assert validate_emu_database(db) == []

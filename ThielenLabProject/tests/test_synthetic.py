from pathlib import Path

from minnelove_emu.analysis import build_feature_table, demo_summary
from minnelove_emu.synthetic import generate_demo_dataset


def test_generate_demo_dataset(tmp_path: Path) -> None:
    paths = generate_demo_dataset(tmp_path / "synthetic", sample_count=4, reads_per_sample=20, seed=7)

    assert paths["manifest"].exists()
    assert len(list(paths["reads_dir"].glob("*.fastq.gz"))) == 4
    assert len(list(paths["emu_dir"].glob("*_rel-abundance.tsv"))) == 4

    features = build_feature_table(paths["root"])
    assert features.shape[0] == 4
    assert "symptom_status" in features.columns
    assert "Streptococcus pneumoniae" in features.columns


def test_demo_summary(tmp_path: Path) -> None:
    generate_demo_dataset(tmp_path / "synthetic", sample_count=3, reads_per_sample=10, seed=11)

    summary = demo_summary(tmp_path / "synthetic")

    assert summary["samples"] == 3
    assert summary["total_reads"] == 30
    assert summary["taxa"] > 0


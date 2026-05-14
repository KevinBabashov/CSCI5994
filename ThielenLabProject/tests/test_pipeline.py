from pathlib import Path

from minnelove_emu.config import PipelineConfig
from minnelove_emu.pipeline import render_linux_pipeline_script
from minnelove_emu.synthetic import generate_demo_dataset


def test_render_linux_pipeline_script(tmp_path: Path) -> None:
    paths = generate_demo_dataset(tmp_path / "synthetic", sample_count=8, reads_per_sample=5, seed=13)
    config = PipelineConfig(
        project_root=Path("/server/project"),
        threads=8,
        emu_db="/db/emu",
        kraken_db="/db/kraken",
    )

    script = render_linux_pipeline_script(paths["manifest"], config, tmp_path / "run.sh")
    text = script.read_text(encoding="utf-8")

    assert "fastp" in text
    assert "emu abundance" in text
    assert "kraken2" in text
    assert "bracken" in text
    assert "MINNELOVE_SYN_001" in text
    assert "--type map-ont" in text
    assert "--type map-pb" in text
    assert "--output-basename MINNELOVE_SYN_001" in text
    assert "test -s \"$EMU_DB/species_taxid.fasta\"" in text

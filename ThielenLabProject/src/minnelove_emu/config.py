from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration shared by local demos and generated Linux pipeline scripts."""

    project_root: Path
    threads: int = 4
    platform: str = "ont"
    quality_cutoff: int = 20
    min_read_length: int = 50
    max_read_length: int = 1800
    read_length_for_bracken: int = 1500
    emu_db: str = "database/emu"
    kraken_db: str = "database/kraken2"
    include_kraken_bracken: bool = True

    @property
    def emu_map_type(self) -> str:
        platform = self.platform.lower()
        if platform in {"ont", "nanopore", "minion"}:
            return "map-ont"
        if platform in {"pb", "pacbio", "hifi"}:
            return "map-pb"
        raise ValueError(f"Unsupported platform for Emu mapping: {self.platform}")


def load_config(path: str | Path) -> PipelineConfig:
    config_path = Path(path)
    data: dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
    root_value = data.pop("project_root", ".")
    root_text = str(root_value)
    root = Path(root_text)
    if not root.is_absolute() and not root_text.startswith("/"):
        root = (config_path.parent / root).resolve()
    return PipelineConfig(project_root=root, **data)


def write_default_config(path: str | Path) -> Path:
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "project_root": ".",
        "threads": 4,
        "platform": "ont",
        "quality_cutoff": 20,
        "min_read_length": 50,
        "max_read_length": 1800,
        "read_length_for_bracken": 1500,
        "emu_db": "database/emu",
        "kraken_db": "database/kraken2",
        "include_kraken_bracken": True,
    }
    config_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return config_path

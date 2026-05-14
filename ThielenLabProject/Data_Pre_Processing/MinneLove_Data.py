"""Compatibility helpers for the original data-preprocessing folder.

The reusable project code now lives under ``src/minnelove_emu``. This module keeps a
short bridge in the original folder so older notebooks can still import demo data helpers.
"""

from pathlib import Path

from minnelove_emu.synthetic import generate_demo_dataset


def generate_local_demo_data(out_dir: str | Path = "data/synthetic") -> dict[str, Path]:
    return generate_demo_dataset(out_dir)


if __name__ == "__main__":
    generate_local_demo_data()

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def read_manifest(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def read_emu_outputs(emu_dir: str | Path) -> pd.DataFrame:
    rows = []
    for path in sorted(Path(emu_dir).glob("*_rel-abundance.tsv")):
        sample_id = path.name.replace("_rel-abundance.tsv", "")
        table = pd.read_csv(path, sep="\t")
        table = table.rename(columns=_normalize_emu_column)
        table["sample_id"] = sample_id
        rows.append(table)
    if not rows:
        return pd.DataFrame(
            columns=[
                "sample_id",
                "tax_id",
                "abundance",
                "estimated_counts",
                "species",
                "genus",
                "family",
                "phylum",
            ]
        )
    return pd.concat(rows, ignore_index=True)


def read_bracken_outputs(bracken_dir: str | Path) -> pd.DataFrame:
    rows = []
    for path in sorted(Path(bracken_dir).glob("*.bracken.tsv")):
        sample_id = path.name.replace(".bracken.tsv", "")
        table = pd.read_csv(path, sep="\t")
        table["sample_id"] = sample_id
        rows.append(table)
    if not rows:
        return pd.DataFrame(
            columns=[
                "sample_id",
                "name",
                "taxonomy_id",
                "taxonomy_lvl",
                "new_est_reads",
                "fraction_total_reads",
            ]
        )
    return pd.concat(rows, ignore_index=True)


def abundance_matrix(emu_long: pd.DataFrame, rank: str = "species") -> pd.DataFrame:
    if emu_long.empty:
        return pd.DataFrame()
    if rank not in emu_long.columns:
        raise ValueError(f"Rank {rank!r} is not available in Emu table")
    matrix = (
        emu_long.pivot_table(
            index="sample_id",
            columns=rank,
            values="abundance",
            aggfunc="sum",
            fill_value=0.0,
        )
        .sort_index()
        .sort_index(axis=1)
    )
    row_totals = matrix.sum(axis=1).replace(0, np.nan)
    return matrix.div(row_totals, axis=0).fillna(0.0)


def alpha_diversity(matrix: pd.DataFrame) -> pd.DataFrame:
    if matrix.empty:
        return pd.DataFrame(columns=["sample_id", "observed_taxa", "shannon", "simpson"])
    values = matrix.to_numpy(dtype=float)
    observed = (values > 0).sum(axis=1)
    safe_values = np.where(values > 0, values, 1.0)
    shannon = -(values * np.log(safe_values)).sum(axis=1)
    simpson = 1.0 - np.square(values).sum(axis=1)
    return pd.DataFrame(
        {
            "sample_id": matrix.index,
            "observed_taxa": observed,
            "shannon": shannon,
            "simpson": simpson,
        }
    )


def top_taxa(emu_long: pd.DataFrame, rank: str = "species", n: int = 12) -> pd.DataFrame:
    if emu_long.empty:
        return pd.DataFrame(columns=[rank, "mean_abundance"])
    return (
        emu_long.groupby(rank, as_index=False)["abundance"]
        .mean()
        .rename(columns={"abundance": "mean_abundance"})
        .sort_values("mean_abundance", ascending=False)
        .head(n)
    )


def build_feature_table(
    demo_root: str | Path,
    output_path: str | Path | None = None,
    rank: str = "species",
) -> pd.DataFrame:
    root = Path(demo_root)
    manifest = read_manifest(root / "manifest.tsv")
    emu_long = read_emu_outputs(root / "emu_outputs")
    matrix = abundance_matrix(emu_long, rank=rank)
    feature_df = matrix.reset_index()
    feature_df = manifest.merge(feature_df, on="sample_id", how="left").fillna(0.0)
    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        feature_df.to_csv(output, sep="\t", index=False)
    return feature_df


def compare_emu_bracken(demo_root: str | Path) -> pd.DataFrame:
    root = Path(demo_root)
    emu = read_emu_outputs(root / "emu_outputs")
    bracken = read_bracken_outputs(root / "bracken_outputs")
    if emu.empty or bracken.empty:
        return pd.DataFrame(columns=["sample_id", "species", "emu_abundance", "bracken_abundance", "delta"])

    emu_small = emu[["sample_id", "species", "abundance"]].rename(
        columns={"abundance": "emu_abundance"}
    )
    bracken_small = bracken[["sample_id", "name", "fraction_total_reads"]].rename(
        columns={"name": "species", "fraction_total_reads": "bracken_abundance"}
    )
    merged = emu_small.merge(bracken_small, on=["sample_id", "species"], how="outer").fillna(0.0)
    merged["delta"] = merged["emu_abundance"] - merged["bracken_abundance"]
    return merged.sort_values(["sample_id", "species"]).reset_index(drop=True)


def demo_summary(demo_root: str | Path) -> dict[str, object]:
    root = Path(demo_root)
    manifest = read_manifest(root / "manifest.tsv")
    emu_long = read_emu_outputs(root / "emu_outputs")
    matrix = abundance_matrix(emu_long)
    diversity = alpha_diversity(matrix)
    return {
        "samples": int(manifest.shape[0]),
        "taxa": int(matrix.shape[1]),
        "mean_shannon": float(diversity["shannon"].mean()) if not diversity.empty else 0.0,
        "total_reads": int(manifest["read_count"].sum()) if "read_count" in manifest else 0,
    }


def _normalize_emu_column(column: str) -> str:
    return column.strip().lower().replace(" ", "_").replace("-", "_")

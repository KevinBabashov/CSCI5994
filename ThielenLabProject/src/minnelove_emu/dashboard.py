from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from .analysis import (
    abundance_matrix,
    alpha_diversity,
    compare_emu_bracken,
    read_emu_outputs,
    read_manifest,
    top_taxa,
)
from .config import load_config
from .pipeline import render_linux_pipeline_script


DEFAULT_DEMO_ROOT = Path("data/synthetic")


def app() -> None:
    st.set_page_config(page_title="MINNELOVE Emu POC", layout="wide")
    st.title("MINNELOVE Emu Analysis")

    with st.sidebar:
        demo_root = Path(st.text_input("Demo data", value=str(DEFAULT_DEMO_ROOT)))
        rank = st.selectbox("Taxonomic rank", ["species", "genus", "family", "phylum"], index=0)
        top_n = st.slider("Top taxa", min_value=5, max_value=20, value=10)

    manifest_path = demo_root / "manifest.tsv"
    emu_dir = demo_root / "emu_outputs"

    if not manifest_path.exists() or not emu_dir.exists():
        st.warning("Synthetic demo data are missing. Run `uv run minnelove generate-demo` first.")
        return

    manifest = read_manifest(manifest_path)
    emu_long = read_emu_outputs(emu_dir)
    matrix = abundance_matrix(emu_long, rank=rank)
    diversity = alpha_diversity(matrix)
    taxa = top_taxa(emu_long, rank=rank, n=top_n)
    annotated = _annotate_long_table(emu_long, manifest)

    overview_tab, abundance_tab, sample_tab, compare_tab, pipeline_tab = st.tabs(
        ["Overview", "Abundance", "Samples", "Method Compare", "Pipeline"]
    )

    with overview_tab:
        metric_cols = st.columns(4)
        metric_cols[0].metric("Samples", f"{manifest.shape[0]}")
        metric_cols[1].metric("Taxa", f"{matrix.shape[1]}")
        metric_cols[2].metric("Reads", f"{int(manifest['read_count'].sum()):,}")
        metric_cols[3].metric("Mean Shannon", f"{diversity['shannon'].mean():.2f}")

        chart_cols = st.columns([2, 1])
        with chart_cols[0]:
            fig = px.bar(
                taxa,
                x="mean_abundance",
                y=rank,
                orientation="h",
                color="mean_abundance",
                color_continuous_scale="Tealrose",
                labels={"mean_abundance": "Mean abundance", rank: rank.title()},
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=430)
            st.plotly_chart(fig, use_container_width=True)
        with chart_cols[1]:
            status_counts = manifest["symptom_status"].value_counts().reset_index()
            status_counts.columns = ["symptom_status", "samples"]
            fig = px.pie(status_counts, values="samples", names="symptom_status", hole=0.45)
            fig.update_layout(height=430)
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(diversity.merge(manifest, on="sample_id"), use_container_width=True)

    with abundance_tab:
        melted = matrix.reset_index().melt(
            id_vars="sample_id", var_name=rank, value_name="relative_abundance"
        )
        melted = melted.merge(manifest[["sample_id", "symptom_status", "virus_status"]], on="sample_id")
        keep_taxa = taxa[rank].tolist()
        filtered = melted[melted[rank].isin(keep_taxa)]
        fig = px.bar(
            filtered,
            x="sample_id",
            y="relative_abundance",
            color=rank,
            facet_row="symptom_status",
            labels={"relative_abundance": "Relative abundance", "sample_id": "Sample"},
            height=760,
        )
        fig.update_layout(legend_title_text=rank.title())
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(matrix.reset_index(), use_container_width=True)

    with sample_tab:
        selected = st.selectbox("Sample", manifest["sample_id"].tolist())
        sample_meta = manifest[manifest["sample_id"] == selected].T.reset_index()
        sample_meta.columns = ["field", "value"]
        sample_taxa = emu_long[emu_long["sample_id"] == selected].sort_values(
            "abundance", ascending=False
        )
        left, right = st.columns([1, 2])
        with left:
            st.dataframe(sample_meta, hide_index=True, use_container_width=True)
        with right:
            fig = px.bar(
                sample_taxa.head(top_n),
                x="abundance",
                y=rank,
                orientation="h",
                color="phylum" if "phylum" in sample_taxa else rank,
                labels={"abundance": "Relative abundance", rank: rank.title()},
                height=520,
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(sample_taxa, use_container_width=True)

    with compare_tab:
        comparison = compare_emu_bracken(demo_root)
        if comparison.empty:
            st.info("No comparison table available.")
        else:
            fig = px.scatter(
                comparison,
                x="emu_abundance",
                y="bracken_abundance",
                color="sample_id",
                hover_name="species",
                labels={
                    "emu_abundance": "Emu abundance",
                    "bracken_abundance": "Bracken abundance",
                },
                height=520,
            )
            fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"dash": "dash"})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(comparison, use_container_width=True)

    with pipeline_tab:
        st.subheader("Linux Command Preview")
        config_path = Path("configs/linux_server_template.json")
        if config_path.exists():
            preview_path = Path("scripts/run_pipeline_linux.preview.sh")
            config = load_config(config_path)
            render_linux_pipeline_script(manifest_path, config, preview_path)
            st.code(preview_path.read_text(encoding="utf-8"), language="bash")
        else:
            st.warning("Missing configs/linux_server_template.json")

        st.subheader("Annotated Emu Table")
        st.dataframe(annotated, use_container_width=True)


def _annotate_long_table(emu_long: pd.DataFrame, manifest: pd.DataFrame) -> pd.DataFrame:
    metadata = manifest[["sample_id", "household_id", "symptom_status", "virus_status", "platform"]]
    return emu_long.merge(metadata, on="sample_id", how="left")


def main() -> None:
    app()


if __name__ == "__main__":
    app()


from __future__ import annotations

import argparse
from pathlib import Path
from pprint import pformat

from .analysis import build_feature_table, compare_emu_bracken, demo_summary
from .config import load_config
from .emu import EmuRunConfig, EmuRunner, write_command_script
from .pipeline import render_linux_pipeline_script
from .reports import write_project_report
from .synthetic import generate_demo_dataset
from .training import train_symptom_classifier


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="minnelove", description="MINNELOVE Emu POC helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate-demo", help="Generate synthetic demo data")
    generate.add_argument("--out", default="data/synthetic", help="Output directory")
    generate.add_argument("--samples", type=int, default=8, help="Number of synthetic samples")
    generate.add_argument("--reads", type=int, default=120, help="Reads per synthetic sample")
    generate.add_argument("--seed", type=int, default=5994, help="Random seed")

    features = subparsers.add_parser("build-features", help="Build a sample-by-taxon table")
    features.add_argument("--demo-root", default="data/synthetic")
    features.add_argument("--out", default="data/processed/demo_feature_matrix.tsv")
    features.add_argument("--rank", default="species", choices=["species", "genus", "family", "phylum"])

    script = subparsers.add_parser("make-linux-script", help="Render Linux pipeline script")
    script.add_argument("--manifest", default="data/synthetic/manifest.tsv")
    script.add_argument("--config", default="configs/linux_server_template.json")
    script.add_argument("--out", default="scripts/run_pipeline_linux.sh")

    train = subparsers.add_parser("train-model", help="Train demo symptom classifier")
    train.add_argument("--features", default="data/processed/demo_feature_matrix.tsv")
    train.add_argument("--out", default="models/demo")
    train.add_argument("--label-column", default="symptom_status")

    compare = subparsers.add_parser("compare-methods", help="Compare synthetic Emu and Bracken tables")
    compare.add_argument("--demo-root", default="data/synthetic")
    compare.add_argument("--out", default="data/processed/emu_bracken_comparison.tsv")

    summary = subparsers.add_parser("summary", help="Print demo summary")
    summary.add_argument("--demo-root", default="data/synthetic")

    report = subparsers.add_parser("write-report", help="Write a project report draft")
    report.add_argument("--demo-root", default="data/synthetic")
    report.add_argument("--out", default="reports/project_report.md")

    emu_check = subparsers.add_parser("emu-check", help="Check real Emu executable and database")
    emu_check.add_argument("--db", default="database/emu")
    emu_check.add_argument("--out", default="results/emu")
    emu_check.add_argument("--emu-bin", default="emu")
    emu_check.add_argument("--skip-db-validation", action="store_true")

    emu_run = subparsers.add_parser("emu-run", help="Run real Emu over a manifest")
    emu_run.add_argument("--manifest", default="data/synthetic/manifest.tsv")
    emu_run.add_argument("--reads-root", default=None)
    emu_run.add_argument("--db", default="database/emu")
    emu_run.add_argument("--out", default="results/emu")
    emu_run.add_argument("--emu-bin", default="emu")
    emu_run.add_argument("--threads", type=int, default=3)
    emu_run.add_argument("--default-type", default="map-ont")
    emu_run.add_argument("--fastq-column", default="fastq_path")
    emu_run.add_argument("--platform-column", default="platform")
    emu_run.add_argument("--min-abundance", type=float, default=0.0001)
    emu_run.add_argument("--max-align-len", type=int, default=2000)
    emu_run.add_argument("--no-keep-counts", action="store_true")
    emu_run.add_argument("--dry-run", action="store_true")
    emu_run.add_argument("--write-script", default=None)

    emu_combine = subparsers.add_parser("emu-combine", help="Combine real Emu outputs")
    emu_combine.add_argument("--emu-dir", default="results/emu")
    emu_combine.add_argument("--db", default="database/emu")
    emu_combine.add_argument("--emu-bin", default="emu")
    emu_combine.add_argument("--rank", default="species")
    emu_combine.add_argument("--split-tables", action="store_true")
    emu_combine.add_argument("--counts", action="store_true")
    emu_combine.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "generate-demo":
        paths = generate_demo_dataset(args.out, args.samples, args.reads, args.seed)
        print("Generated synthetic demo data:")
        print(pformat({key: str(value) for key, value in paths.items()}))
    elif args.command == "build-features":
        table = build_feature_table(args.demo_root, args.out, rank=args.rank)
        print(f"Wrote {args.out} with shape {table.shape}")
    elif args.command == "make-linux-script":
        config = load_config(args.config)
        output = render_linux_pipeline_script(args.manifest, config, args.out)
        print(f"Wrote Linux pipeline script: {output}")
    elif args.command == "train-model":
        result = train_symptom_classifier(args.features, args.out, args.label_column)
        print("Trained demo model:")
        print(pformat({key: str(value) for key, value in result.items()}))
    elif args.command == "compare-methods":
        comparison = compare_emu_bracken(args.demo_root)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(out, sep="\t", index=False)
        print(f"Wrote {out} with shape {comparison.shape}")
    elif args.command == "summary":
        print(pformat(demo_summary(args.demo_root)))
    elif args.command == "write-report":
        output = write_project_report(args.demo_root, args.out)
        print(f"Wrote report draft: {output}")
    elif args.command == "emu-check":
        runner = _build_emu_runner(args, dry_run=True)
        issues = runner.check_installation(validate_db=not args.skip_db_validation)
        if issues:
            print("Emu readiness issues:")
            for issue in issues:
                print(f"- {issue}")
            raise SystemExit(1)
        print("Emu executable and database checks passed.")
    elif args.command == "emu-run":
        runner = _build_emu_runner(args, dry_run=args.dry_run)
        results = runner.run_manifest(
            args.manifest,
            reads_root=args.reads_root,
            fastq_column=args.fastq_column,
            platform_column=args.platform_column,
        )
        if args.write_script:
            script_path = write_command_script([result.command for result in results], args.write_script)
            print(f"Wrote Emu command script: {script_path}")
        for result in results:
            print(result.shell_command)
        print(f"Prepared {len(results)} Emu command(s).")
    elif args.command == "emu-combine":
        config = EmuRunConfig(
            db=args.db,
            output_dir=args.emu_dir,
            emu_bin=args.emu_bin,
            dry_run=args.dry_run,
        )
        command = EmuRunner(config).combine_outputs(
            rank=args.rank,
            split_tables=args.split_tables,
            counts=args.counts,
        )
        print(" ".join(command))


def _build_emu_runner(args: argparse.Namespace, dry_run: bool) -> EmuRunner:
    config = EmuRunConfig(
        db=args.db,
        output_dir=args.out,
        emu_bin=args.emu_bin,
        threads=args.threads,
        default_type=args.default_type,
        min_abundance=args.min_abundance,
        max_align_len=args.max_align_len,
        keep_counts=not args.no_keep_counts,
        dry_run=dry_run,
    )
    return EmuRunner(config)


if __name__ == "__main__":
    main()

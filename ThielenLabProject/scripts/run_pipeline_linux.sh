#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-/path/to/ThielenLabProject}
RAW_DIR="$PROJECT_ROOT/data/synthetic/reads"
CLEAN_DIR="$PROJECT_ROOT/results/clean_fastq"
QC_DIR="$PROJECT_ROOT/results/qc"
EMU_DIR="$PROJECT_ROOT/results/emu"
KRAKEN_DIR="$PROJECT_ROOT/results/kraken"
BRACKEN_DIR="$PROJECT_ROOT/results/bracken"
mkdir -p "$CLEAN_DIR" "$QC_DIR" "$EMU_DIR" "$KRAKEN_DIR" "$BRACKEN_DIR"

EMU_DB=${EMU_DB:-/path/to/emu_database}
KRAKEN_DB=${KRAKEN_DB:-/path/to/kraken2_database}

test -s "$EMU_DB/species_taxid.fasta"
test -s "$EMU_DB/taxonomy.tsv"

echo 'Processing MINNELOVE_SYN_001'
fastp -i "$RAW_DIR/MINNELOVE_SYN_001.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_001.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_001.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_001.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_001.clean.fastq.gz" --db "$EMU_DB" --type map-ont --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_001 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_001.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_001.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_001.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_001.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_001.bracken.tsv" -r 1500 -l S -t 10

echo 'Processing MINNELOVE_SYN_002'
fastp -i "$RAW_DIR/MINNELOVE_SYN_002.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_002.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_002.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_002.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_002.clean.fastq.gz" --db "$EMU_DB" --type map-ont --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_002 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_002.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_002.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_002.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_002.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_002.bracken.tsv" -r 1500 -l S -t 10

echo 'Processing MINNELOVE_SYN_003'
fastp -i "$RAW_DIR/MINNELOVE_SYN_003.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_003.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_003.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_003.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_003.clean.fastq.gz" --db "$EMU_DB" --type map-ont --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_003 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_003.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_003.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_003.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_003.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_003.bracken.tsv" -r 1500 -l S -t 10

echo 'Processing MINNELOVE_SYN_004'
fastp -i "$RAW_DIR/MINNELOVE_SYN_004.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_004.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_004.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_004.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_004.clean.fastq.gz" --db "$EMU_DB" --type map-ont --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_004 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_004.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_004.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_004.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_004.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_004.bracken.tsv" -r 1500 -l S -t 10

echo 'Processing MINNELOVE_SYN_005'
fastp -i "$RAW_DIR/MINNELOVE_SYN_005.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_005.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_005.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_005.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_005.clean.fastq.gz" --db "$EMU_DB" --type map-ont --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_005 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_005.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_005.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_005.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_005.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_005.bracken.tsv" -r 1500 -l S -t 10

echo 'Processing MINNELOVE_SYN_006'
fastp -i "$RAW_DIR/MINNELOVE_SYN_006.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_006.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_006.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_006.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_006.clean.fastq.gz" --db "$EMU_DB" --type map-ont --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_006 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_006.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_006.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_006.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_006.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_006.bracken.tsv" -r 1500 -l S -t 10

echo 'Processing MINNELOVE_SYN_007'
fastp -i "$RAW_DIR/MINNELOVE_SYN_007.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_007.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_007.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_007.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_007.clean.fastq.gz" --db "$EMU_DB" --type map-pb --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_007 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_007.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_007.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_007.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_007.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_007.bracken.tsv" -r 1500 -l S -t 10

echo 'Processing MINNELOVE_SYN_008'
fastp -i "$RAW_DIR/MINNELOVE_SYN_008.fastq.gz" -o "$CLEAN_DIR/MINNELOVE_SYN_008.clean.fastq.gz" -h "$QC_DIR/MINNELOVE_SYN_008.fastp.html" -j "$QC_DIR/MINNELOVE_SYN_008.fastp.json" -w 16 -q 20 -l 50
emu abundance "$CLEAN_DIR/MINNELOVE_SYN_008.clean.fastq.gz" --db "$EMU_DB" --type map-pb --output-dir "$EMU_DIR" --output-basename MINNELOVE_SYN_008 --threads 16 --keep-counts
kraken2 --db "$KRAKEN_DB" --threads 16 --gzip-compressed --use-names --report "$KRAKEN_DIR/MINNELOVE_SYN_008.kraken.report" --output "$KRAKEN_DIR/MINNELOVE_SYN_008.kraken.out" "$CLEAN_DIR/MINNELOVE_SYN_008.clean.fastq.gz"
bracken -d "$KRAKEN_DB" -i "$KRAKEN_DIR/MINNELOVE_SYN_008.kraken.report" -o "$BRACKEN_DIR/MINNELOVE_SYN_008.bracken.tsv" -r 1500 -l S -t 10

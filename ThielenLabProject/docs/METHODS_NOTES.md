# Method Notes for Lab Slides

## Emu

Emu is designed for species-level microbial community profiling from full-length 16S rRNA Oxford
Nanopore reads. Its abundance estimation uses expectation-maximization over read-to-reference
assignments, which is useful when noisy long reads can align ambiguously across closely related
organisms.

Use Emu in this project as the long-read 16S bacterial/archaeal profiler. Do not frame it as a
standalone respiratory virus detector.

Primary source: https://www.nature.com/articles/s41592-022-01520-4

## Kraken2

Kraken2 is a fast taxonomic classifier based on exact k-mer matching and lowest-common-ancestor
taxonomy assignment. It is useful for broad metagenomic classification when the reference database
contains the organisms of interest.

Primary source: https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1891-0

Official manual: https://software.cqls.oregonstate.edu/updates/docs/kraken2/MANUAL.html

## Bracken

Bracken is an abundance re-estimation layer for Kraken/Kraken2 outputs. It uses a Bayesian model to
redistribute reads classified at higher taxonomic levels into estimated lower-level abundances.

Kraken2 project page: https://ccb.jhu.edu/software/kraken2/index.shtml

## Recommended Framing

- Emu: long-read 16S species abundance estimation for bacterial/archaeal microbiome structure.
- Kraken2: broad k-mer classification, including viral workflows when the database is appropriate.
- Bracken: Bayesian abundance re-estimation from Kraken/Kraken2 reports.
- Proposed comparison: use synthetic data first, then run a small real-data pilot with identical
  summary outputs for Emu and Kraken2/Bracken.


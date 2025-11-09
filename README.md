# TRD-GNN Temporal Extension

**Leakage-safe temporal GNN** for fraud detection on Elliptic++ dataset using **Time-Relaxed Directed (TRD) sampling**.

## Overview

This project extends baseline GNN fraud detection work by implementing temporal neighborhood sampling that strictly enforces `time(neighbor) <= time(target)` to prevent future information leakage.

## Key Features

- **TRD Sampler**: Time-aware neighbor sampling preventing temporal leakage
- **Temporal Models**: TRD-GraphSAGE and TRD-GCN implementations
- **Baseline Integration**: Reuses splits and metrics from baseline project for fair comparison
- **Reproducible**: Clean, documented code with comprehensive tests

## Setup

See `docs/CLONE_INIT_PROMPT_v3.md` for complete initialization steps.

## Documentation

- `docs/PROJECT_SPEC_v3.md` - Project specification and scope
- `docs/AGENT_v3.MD` - AI agent guidelines
- `docs/START_PROMPT_v3.md` - Quick start instructions
- `docs/baseline_provenance.json` - Baseline artifact tracking

## Status

🚧 In Development - Phase 2 (TRD Sampler Implementation)

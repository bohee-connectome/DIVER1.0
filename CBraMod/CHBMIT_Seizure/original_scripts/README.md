# CHB-MIT Original Preprocessing Scripts

## Overview

This directory contains reference to the original CHB-MIT preprocessing methodology.

## Original Two-Stage Pipeline

The original CHB-MIT preprocessing followed a two-stage approach:

### Stage 1: process1.py (Data Extraction)
- **Purpose**: Extract and clean raw EDF files
- **Input**: Raw `.edf` files from PhysioNet CHB-MIT database
- **Output**: Cleaned `.pkl` files with metadata
- **Operations**:
  - Parse summary files for seizure annotations
  - Extract 16 bipolar channels
  - Convert time annotations to sample indices
  - Save as pickle format with metadata

### Stage 2: process2.py (Segmentation and Labeling)
- **Purpose**: Segment continuous data and apply labels
- **Input**: Cleaned `.pkl` files from Stage 1
- **Output**: Segmented samples with labels
- **Operations**:
  - 10-second segmentation (non-overlapping)
  - Binary labeling (0=Normal, 1=Seizure)
  - Oversampling for seizure segments (5-second step)
  - Train/Val/Test split by patient

## Current Implementation

The current preprocessing script (`preprocessing_chbmit.py`) consolidates both stages into a single pipeline:
- Located at: `scripts/chbmit/preprocessing_chbmit.py`
- Performs all operations in one pass
- Outputs directly to LMDB format
- Includes resampling to 500 Hz
- Reshapes to (16, 10, 500) format

## References

- Original methodology described in CHBMIT_DATASET_INFO.md
- Shoeb, A. (2009). "Application of Machine Learning to Epileptic Seizure Detection"

---

**Note**: The original process1.py and process2.py scripts are not included in this repository. The current implementation provides equivalent functionality in a unified pipeline.

**Author**: Bohee Lee
**Date**: 2025-11-21

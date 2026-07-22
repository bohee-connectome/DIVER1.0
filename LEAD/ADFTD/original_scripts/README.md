# Original LEAD ADFTD Preprocessing Scripts

This folder contains the **original preprocessing scripts** from the LEAD paper for reference.

## Files

### 1. `adftd_loader.py`
**Source**: Original LEAD ADFTD dataset loader
**Purpose**: PyTorch Dataset class for loading preprocessed ADFTD data

**Key Settings**:
- **Storage Format**: NPY files (separate `Feature/` and `Label/` folders)
- **Train/Val/Test Split**: 60/20/20 (configurable with a=0.6, b=0.8)
- **Label Mapping**: AD (2→1) - Binary classification (HC=0, AD=1)
- **Cross-validation**: Fixed (seed=42), MCCV, or LOSO
- **Filtering**: Bandpass filter applied during loading
- **Normalization**: Batch-wise normalization

### 2. `ADFTD_preprocessing_original.ipynb`
**Source**: Original LEAD preprocessing notebook
**Purpose**: Data exploration and initial preprocessing pipeline

**Key Features**:
- OpenNeuro dataset download and exploration
- Channel selection and artifact removal
- Multi-scale segmentation (1s/2s/4s)
- NPY file generation

### 3. `check_lmdb.py`
**Source**: Original LMDB verification script (basic)
**Purpose**: Simple LMDB database verification

**Features**:
- Counts subjects and samples
- Basic data integrity checks

### 4. `check_lmdb_detailed.py`
**Source**: Original LMDB verification script (detailed)
**Purpose**: Detailed LMDB database verification

**Features**:
- Sample shape analysis
- Label distribution
- Subject-level statistics

---

## Differences from Our Implementation

| Aspect | Original LEAD | Our Implementation |
|--------|--------------|-------------------|
| **Storage Format** | NPY (separate files) | LMDB (unified database) |
| **Label Mapping** | AD: 2→1 (binary) | HC=0, AD=1, FTD=2 (3-class) |
| **Train/Val/Test** | 60/20/20 (random) | 60/20/20 (fixed seed=42) |
| **Multi-scale** | 1s/2s/4s | Same ✓ |
| **Filtering** | Runtime filtering | Same ✓ |
| **Cross-validation** | Fixed/MCCV/LOSO | Fixed only |

---

## Why We Modified

### 1. **LMDB Storage** (NPY → LMDB)
- **Atomic storage**: Sample and label always together
- **No alignment issues**: Can't mismatch sample-label pairs
- **Better I/O**: Single file, faster random access
- **Metadata included**: All processing info stored with data

### 2. **3-Class Classification** (Binary → 3-class)
- **More comprehensive**: HC/AD/FTD instead of HC/AD only
- **Better evaluation**: Tests model's ability to distinguish related diseases
- **Label preservation**: Keep original labels (0/1/2) instead of mapping 2→1

### 3. **Fixed Split** (Random → Fixed seed)
- **Reproducibility**: Same train/val/test split across experiments
- **Fair comparison**: Consistent evaluation with other models

---

## Reference

**LEAD Paper**:
Wang, Y., Huang, N., Mammone, N., Cecchi, M., & Zhang, X. (2025). LEAD: An EEG Foundation Model for Alzheimer's Disease Detection. arXiv:2502.01678.

**ADFTD Dataset** (OpenNeuro ds004504):
https://openneuro.org/datasets/ds004504/versions/1.0.8

---

**Note**: These original scripts are kept for reference only. Use the updated scripts in `../scripts/` for actual preprocessing.

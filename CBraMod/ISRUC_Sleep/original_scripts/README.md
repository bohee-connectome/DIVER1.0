# Original CBraMod ISRUC-Sleep Preprocessing Scripts

This folder contains the **original preprocessing scripts** from the CBraMod paper (ICLR 2025) for reference.

## Files

### 1. `prepare_ISRUC_1.py`
**Source**: Original CBraMod ISRUC preprocessing implementation
**Purpose**: Extracts and preprocesses ISRUC-Sleep dataset

**Key Settings**:
- **Filter**: 0.3-35 Hz bandpass, 50 Hz notch
- **Sampling Rate**: 200 Hz (no resampling)
- **Output Format**: NPY files (separate `seq/` and `labels/` folders)
- **Output Shape**: `(20, 6, 6000)` - 20 epochs grouped as sequence
- **Label Mapping**: `{'0': 0, '1': 1, '2': 2, '3': 3, '5': 4}` - REM mapped 5→4

### 2. `isruc_dataset.py`
**Source**: Original CBraMod dataset loader
**Purpose**: PyTorch Dataset class for loading preprocessed ISRUC data

**Key Features**:
- Loads data from NPY file pairs (seq path, label path)
- Train/Val/Test split: Subject 1-80 / 81-90 / 91-100
- Returns: `(seq/100, label)` - sequences normalized by dividing 100

---

## Differences from Our Implementation

| Aspect | Original CBraMod | Our Implementation |
|--------|-----------------|-------------------|
| **Storage Format** | NPY (separate files) | LMDB (unified database) |
| **Sampling Rate** | 200 Hz | 500 Hz |
| **Output Shape** | (20, 6, 6000) | (6, 30, 500) |
| **Sequence Grouping** | 20 epochs pre-grouped | Individual epochs |
| **Filter** | 0.3-35 Hz, 50 Hz | Same ✓ |
| **Label Mapping** | 5→4 | Same ✓ |
| **Train/Val/Test** | 80/10/10 | Same ✓ |

---

## Why We Modified

### 1. **LMDB Storage** (NPY → LMDB)
- **Atomic storage**: Sample and label always together
- **No alignment issues**: Can't mismatch sample-label pairs
- **Better I/O**: Single file, faster random access
- **Metadata included**: All processing info stored with data

### 2. **Higher Sampling Rate** (200 Hz → 500 Hz)
- **Better temporal resolution**: More samples per second
- **Fine-grained features**: Can capture faster dynamics
- **Consistent with other datasets**: ADFTD uses 500 Hz

### 3. **Individual Epochs** (20-epoch sequence → single epoch)
- **More flexible**: Dataloader can create any sequence length
- **Better for different models**: Not all models need 20-epoch sequences
- **Easier augmentation**: Can shuffle/resample individual epochs

---

## Reference

**CBraMod Paper** (ICLR 2025):
https://openreview.net/forum?id=NPNUHgHF2w

**ISRUC-Sleep Dataset**:
Khalighi, S., Sanei, S., Chambers, J. A., & Jutten, C. (2016). ISRUC-Sleep: A comprehensive public dataset for sleep researchers.

---

**Note**: These original scripts are kept for reference only. Use the updated scripts in `../scripts/` for actual preprocessing.

# ADFTD: Alzheimer's & Frontotemporal Dementia Classification

3-class classification (CN vs. AD vs. FTD) on ADFTD dataset using DIVER preprocessing pipeline.

## Quick Info

| Item | Value |
|------|-------|
| **Dataset** | ADFTD EEG Dataset |
| **Subjects** | 88 patients (30 CN, 35 AD, 23 FTD) |
| **Task** | 3-class classification |
| **Classes** | CN (0), AD (1), FTD (2) |
| **Channels** | 19 standard 10-20 electrodes |
| **Sampling Rate** | 256 Hz → 500 Hz (resampled) |
| **Segment Length** | 10 seconds |
| **Output Shape** | (19, 10, 500) |
| **Recording** | Eyes-closed resting state |
| **Preprocessing** | v2 (recommended) with improved artifact removal |

## Documentation

- 📄 **[ADFTD_DATASET_INFO.md](ADFTD_DATASET_INFO.md)** - Complete dataset documentation

## Quick Start

### 1. Install Dependencies
```bash
pip install numpy scipy mne lmdb
```

### 2. Run Preprocessing (v2 Recommended)
```bash
cd scripts
bash run_preprocessing_v2.sh
```

### 3. Validate Output
```bash
python check_lmdb_adftd_v2.py
python check_v2_shapes.py
```

---

## 📦 Data Format

```python
{
    "signal": np.array,           # (19, 10, 500)
    "label": int,                 # 0=CN, 1=AD, 2=FTD
    "elc_info": dict,             # Electrode information
    "metadata": {
        "subject_id": str,        # e.g., "subject001_CN"
        "segment_index": int,     # 0, 1, 2, ...
        "original_sampling_rate": 256,
        "target_sampling_rate": 500,
        "diagnosis": str          # "CN", "AD", or "FTD"
    }
}
```

**Note:** ADFTD data format differs from ISRUC/CHBMIT unified format. Future work may align to `sample` + `data_info` structure.

---

## 📁 Directory Structure

```
ADFTD/
├── README.md                                    # This file - unified documentation
├── ADFTD_DATASET_INFO.md                       # Detailed dataset info
│
├── scripts/                                     # Preprocessing and validation
│   ├── preprocessing_generalized_ADFTD.py           # Main preprocessing
│   ├── preprocessing_generalized_datasetsetting_ADFTD.py  # Data split config
│   ├── clip_extraction_utils.py                     # Artifact removal ✅
│   ├── check_lmdb_adftd_v1.py                      # v1 validator
│   ├── check_lmdb_adftd_v2.py                      # v2 validator ✅
│   ├── check_v2_shapes.py                          # Shape validator ✅
│   ├── run_preprocessing_v1.sh                     # v1 runner
│   ├── run_preprocessing_v2.sh                     # v2 runner ✅
│   └── standard_1005.elc                           # Electrode locations
│
├── logs/                                        # Processing logs
│   ├── v1_output_65051.log                          # v1 stdout
│   ├── v1_error_65051.log                           # v1 stderr
│   ├── v2_output_65052.log                          # v2 stdout ✅
│   ├── v2_error_65052.log                           # v2 stderr ✅
│   ├── validation_v1_report.txt                     # v1 validation
│   └── validation_v2_report.txt                     # v2 validation ✅
│
└── data/                                        # LMDB output (not in repo)
    ├── processed_v1/                                # v1 data
    │   └── 1.0_ADFTD/
    │       ├── train_resample-500_highpass-0.5_lowpass-45.0.lmdb/
    │       ├── val_resample-500_highpass-0.5_lowpass-45.0.lmdb/
    │       ├── test_resample-500_highpass-0.5_lowpass-45.0.lmdb/
    │       └── merged_resample-500_highpass-0.5_lowpass-45.0.lmdb/
    │
    └── processed_v2/                                # v2 data (recommended) ✅
        └── 1.0_ADFTD/
            ├── train_resample-500_highpass-0.5_lowpass-45.0.lmdb/
            ├── val_resample-500_highpass-0.5_lowpass-45.0.lmdb/
            ├── test_resample-500_highpass-0.5_lowpass-45.0.lmdb/
            └── merged_resample-500_highpass-0.5_lowpass-45.0.lmdb/
```

### Preprocessing Versions

| Version | Description | Recommended |
|---------|-------------|-------------|
| **v2** | Improved artifact detection, enhanced quality control | ✅ Yes |
| v1 | Initial implementation, basic artifact removal | For reference only |

**Use v2** - Better artifact removal and segment quality!

---

## 🔄 Preprocessing Pipeline

```
Raw ADFTD Data (EDF files: CN/AD/FTD)
    ↓
[Load EDF & Extract Channels]  ← 19 standard electrodes
    ↓
[Artifact Removal - Clipping] ✅
├── Amplitude clipping (|signal| > 100 μV)
├── Gradient clipping (rapid changes > 50 μV)
└── Flatline detection (std < 5 μV)
    ↓
[Extract Clean Segments]
    ↓
[Segment]  ← 10-second segments (non-overlapping)
    ↓
[Assign Labels]  ← CN=0, AD=1, FTD=2
    ↓
[Data Split]  ← Stratified 70/15/15 (subject-level)
    ↓
[Resample]  ← 256 Hz → 500 Hz
    ↓
[Reshape]  ← (19, 2560) → (19, 10, 500)
    ↓
[Add Metadata]  ← Subject, diagnosis, electrode info
    ↓
[Store in LMDB]  ← Separate train/val/test + merged
    ↓
data/processed_v2/1.0_ADFTD/
```

---

## 📊 Dataset Statistics

### Subject Distribution
```
Total: 88 patients
├── CN:  30 subjects (~34%)
├── AD:  35 subjects (~40%)
└── FTD: 23 subjects (~26%)
```

### Data Split (Stratified)
- **Train**: ~62 subjects (70%, stratified by diagnosis)
- **Validation**: ~13 subjects (15%, stratified)
- **Test**: ~13 subjects (15%, stratified)

### Segments (After Artifact Removal)
```
Total: ~5,700 segments
├── Train:  ~4,000 segments (70%)
├── Val:      ~850 segments (15%)
└── Test:     ~850 segments (15%)
```

### Storage Size
- **Per split LMDB**: ~75-100 MB
- **Merged LMDB**: ~300 MB
- **Total**: ~600 MB (all LMDBs)
- **Tar archives**: ~300 MB each (compressed)

---

## 🧠 Channel Configuration

19 channels from **standard 10-20 system**:

```
Frontal Region (7 channels):
├── FP1, FP2  (Frontopolar)
├── F3, F4, FZ  (Frontal)
└── F7, F8  (Anterior temporal)

Central Region (3 channels):
├── C3, C4, CZ  (Central)

Temporal Region (4 channels):
├── T3, T4  (Mid-temporal)
└── T5, T6  (Posterior temporal)

Parietal Region (3 channels):
├── P3, P4, PZ  (Parietal)

Occipital Region (2 channels):
└── O1, O2  (Occipital)
```

**Reference:** Depends on original EDF (typically average or linked ears)

---

## 🔧 Artifact Removal (v2 Enhanced)

### Amplitude Clipping
```python
threshold = 100 μV
# Remove segments where |signal| > threshold
```

### Gradient Clipping
```python
threshold_gradient = 50 μV
gradient = np.diff(signal)
# Remove segments with rapid changes > threshold
```

### Flatline Detection
```python
threshold_std = 5 μV
# Remove segments with std < threshold (insufficient variation)
```

**v2 Improvements:**
- More robust threshold detection
- Better handling of edge cases
- Enhanced quality assessment
- Improved segment extraction

---

## 💡 Usage Notes

1. **Use v2 preprocessing** for all new projects
2. **Apply stratified sampling** during training (class imbalance: CN 34%, AD 40%, FTD 26%)
3. **Use class weights** or focal loss to handle imbalance
4. **Separate LMDB per split** (train/val/test) or use merged
5. **Subject-level splitting** already applied (no data leakage)
6. **Check validation reports** in `logs/validation_v2_report.txt`

---

## 📖 Citation

```bibtex
@article{wang2025lead,
  title={LEAD: An EEG Foundation Model for Alzheimer's Disease Detection},
  author={Wang, Yihe and Huang, Nan and Mammone, Nadia and Cecchi, Marco and Zhang, Xiang},
  journal={arXiv preprint arXiv:2502.01678},
  year={2025}
}

@article{miltiadous2023adftd,
  title={A Dataset of Scalp EEG Recordings of Alzheimer's Disease, Frontotemporal Dementia and Healthy Subjects from Routine EEG},
  author={Miltiadous, Andreas and Tzimourta, Katerina D. and Afrantou, Theodora and Ioannidis, Panagiotis and Grigoriadis, Nikolaos and Tsalikakis, Dimitrios G. and Angelidis, Pantelis and Tsipouras, Markos G. and Glavas, Euripidis and Giannakeas, Nikolaos and Tzallas, Alexandros T.},
  journal={Data},
  volume={8},
  number={6},
  pages={95},
  year={2023},
  publisher={MDPI},
  doi={10.3390/data8060095}
}
```

---

## 🔗 Data Availability

**Important:** ADFTD dataset is **not publicly available** due to patient privacy.

- Contact LEAD project team for data access
- Data usage agreements required
- IRB approval necessary for research use

---

## 📌 Version Information

- **Data Format**: signal, label, elc_info, metadata
- **Preprocessing Version**: v2 (recommended)
- **Last Updated**: 2025-11-27
- **Job IDs**: v1 (65051), v2 (65052)
- **Artifact Removal**: Enhanced (v2)

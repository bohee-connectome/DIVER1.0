# DIVER Journal Baselines — Status

Baseline benchmarks for the DIVER journal comparison table (linear-probe track).
DIVER itself is not run here (model not finalized); this folder tracks the **baseline**
foundation models (CBraMod, EEGPT) on the same clinical EEG datasets so the journal
table can be filled in reproducibly.

Datasets: **ADFTD** (ds004504, 3-class CN/FTD/AD) and **CAUEEG** (3-class dementia).

Last updated: 2026-07-03

---

## What was done

### CBraMod — ADFTD linear probe — DONE (2026-07-02)

Frozen backbone + linear head, CBraMod pretrained weights, 5 seeds (41–45).

| Metric | Mean ± SD |
|--------|-----------|
| ACC    | 0.405 ± 0.006 |
| kappa  | 0.128 ± 0.012 |
| macro F1 | 0.389 ± 0.007 |
| AUROC  | 0.590 ± 0.015 |
| AUPRC  | 0.405 ± 0.011 |

Above chance but a weak baseline. FTD is barely captured (AD-vs-FTD is intrinsically
hard; DIVER is also at chance on that split). The journal sheet reports ACC/kappa/F1
for `ADFTD(3)` (CAUEEG(3) uses ACC/AUPRC/AUROC).

CBraMod-CAUEEG LP was already completed earlier (ACC 0.6691, also with
`all_patch_reps`).

Run script: [`run_ADFTD_CBraMod_lp_array.sh`](run_ADFTD_CBraMod_lp_array.sh) — sbatch
array over seeds 41–45.

### EEGPT — ADFTD + CAUEEG — SETUP done, RUN pending

- Code is accessible via Taeyang's copy at `/pscratch/sd/t/tylee/EEGPT/downstream/`
  (m5187 group). Run entry point: `python linear_probe_ours_5seeds.py --dataset NAME`
  (config is hardcoded; see `run_linear_probe.sh` in that repo). Checkpoint is 58ch / 4s,
  **256 Hz** format.
- Channel mapping handled automatically (`compute_drop_and_use_channels` maps EEGPT's
  58 channels to the dataset's fixed 19 channels), so ADFTD/CAUEEG (fixed 19ch) are fine.
- **ADFTD**: already registered in the EEGPT config (19ch / 3class). Blocker: the
  256 Hz LMDB lives under project **m4750**, to which `boheelee` has no read access.
- **CAUEEG**: not in the EEGPT config at all → needs a `DATASET_CONFIGS` entry plus a
  freshly built 256 Hz CAUEEG LMDB.
- Data converter for both datasets: [`convert_to_eegpt256.py`](convert_to_eegpt256.py) —
  DIVER-format LMDB → EEGPT format (C, 1024 = 4s @ 256 Hz), non-overlapping 4s windows,
  subject-exclusive `__keys__` split preserved, raw values (EEGPT loader z-norms). Prints
  the `channel_names` list to paste into the config.

REVE-B/L baselines are deferred (code/weight paths not yet documented).

---

## CBraMod recipe — 4 gotchas when running a new dataset

1. **Sample rate.** CBraMod expects **200 Hz** (patch = 200 samples = 1 s). DIVER LMDBs
   are 500 Hz → downsample first. Script:
   `LEAD/ADFTD/scripts/downsample_adftd_500_to_200.py` (value key is `sample`; iterate
   over the `__keys__` split lists so the `__keys__` meta-key doesn't raise KeyError; the
   split baked into `__keys__` is preserved). The loader takes `--datasets_dir` directly.
2. **LMDB double-open bug.** `adftd_dataset.py` opens the same LMDB path 3× (train/val/test)
   → `lmdb.Error: already open`. Fix with a per-process `_LMDB_ENV_CACHE` env cache patch.
3. **Classifier must be `all_patch_reps`.** `avgpooling_patch_reps` collapses
   (kappa ≈ 0, below chance). The 0.6691 CAUEEG result also used `all_patch_reps`.
4. **No `--early_stop_*` args.** `--early_stop_criteria` / `--early_stop_patience` are
   DIVER-only and not in CBraMod's parser → remove them. LP flags:
   `--frozen True --use_pretrained_weights True --num_of_classes 3 --lr 1e-4
   --weight_decay 5e-2 --epochs 50`.

Runtime: `salloc -A m5187_g -C gpu -q interactive`, ~2 min/seed, loop 41–45. Results are
baked into the `.pth` filename in `model_dir`.

---

## Key Perlmutter paths (verified 2026-07-02)

| What | Path |
|------|------|
| CBraMod repo (has ADFTD branch, finetune_main.py L155) | `/pscratch/sd/b/boheelee/CBraMod_caueeg` |
| CBraMod pretrained weight | `/pscratch/sd/t/tylee/pretrained_weights.pth` |
| ADFTD 500 Hz LMDB (readable) | `/global/cfs/cdirs/m5187/tylee/adftd_lmdb/adftd_filtered_scale_1213` |
| ADFTD 200 Hz LMDB (converted) | `/pscratch/sd/b/boheelee/adftd/adftd_filtered_scale_1213_200hz` |
| EEGPT downstream code (Taeyang copy, accessible) | `/pscratch/sd/t/tylee/EEGPT/downstream/` |
| EEGPT ADFTD 256 Hz LMDB (m4750, **denied**) | `/global/cfs/cdirs/m4750/DIVER/PRETRAINING_DATA_LMDB/EEGPT_256Hz/ADFTD` |

Permission note: `boheelee` is only in group **m5187** (not m4750/m4727), so paths under
m4750 (incl. TY's `/pscratch/.../Dataset/ADFTD/` and `/global/cfs/cdirs/m4750/DIVER/ADFTD-LEAD`)
are read-denied. `boheelee` can't even `cp` from them.

---

## Next steps

1. Get m4750 read access to `EEGPT_256Hz/ADFTD` (Taeyang/Seungju copy it out, or add
   `boheelee` to m4750 via iris) → run EEGPT-ADFTD LP.
2. Build the 256 Hz CAUEEG LMDB with `convert_to_eegpt256.py` and add a CAUEEG entry to
   EEGPT's `DATASET_CONFIGS` → run EEGPT-CAUEEG LP.
3. Fill the journal sheet EEGPT rows, then document REVE-B/L code/weight paths.

# STATUS — ADFTD Baselines (CBraMod / EEGPT / DIVER Linear Probe)

# ADFTD Baselines — Linear Probe (CBraMod / EEGPT / DIVER)

ADFTD (ds004504, CN/FTD/AD 3-class, subject-exclusive split) linear-probe 벤치마크. 2026-07-03 완료 (CBraMod·EEGPT·DIVER 3개). REVE-B/L은 추후.

## 결과 (5 seeds, mean ± std)

| Model | ACC | kappa | F1(macro) | auc_pr | AUROC |
|-------|-----|-------|-----------|--------|-------|
| CBraMod | 0.405 ± 0.006 | 0.128 ± 0.012 | 0.389 ± 0.007 | 0.405 ± 0.011 | 0.590 ± 0.015 |
| EEGPT | 0.490 ± 0.024 | 0.197 ± 0.039 | 0.417 ± 0.033 | — | — |
| DIVER | 0.402 ± 0.010 | 0.125 ± 0.014 | 0.422 ± 0.012 | 0.443 ± 0.005 | 0.581 ± 0.010 |

- EEGPT는 eval(pyhealth `multiclass_metrics_fn`)이 acc/balanced_acc/kappa/f1만 출력 → auc_pr/AUROC 없음. 필요 시 `utils_eval.py`에 PR-AUC 추가 후 재평가.
- DIVER LP가 CBraMod와 비슷·낮은 편은 iEEG→scalp 도메인갭 때문(LP < fullFT, OHBM에서 확인). EEGPT가 ADFTD에서 최고.
- 모든 모델 FTD(중간 클래스) 약함 = AD-vs-FTD 난이도(DIVER조차 chance).

## 공통 데이터 (ADFTD 소스)

- 원본 500Hz LMDB: `/global/cfs/cdirs/m5187/tylee/adftd_lmdb/adftd_filtered_scale_1213`
  - value `{sample:(19,8,500) float32, label, data_info}`, `__keys__`=dict{train5169/val1582/test1938}, subject-exclusive
  - data_info.channel_names = `['Fp1','Fp2','F3','F4','C3','C4','P3','P4','O1','O2','F7','F8','T3','T4','T5','T6','Fz','Cz','Pz']`

## 1. CBraMod (200Hz)

- **스크립트**: `run_ADFTD_CBraMod_lp_array.sh` (sbatch array, seeds 41-45)
- **repo**: `/pscratch/sd/b/boheelee/CBraMod_caueeg` (finetune_main.py에 ADFTD 분기 있음)
- **weight**: `/pscratch/sd/t/tylee/pretrained_weights.pth`
- **데이터**: 200Hz 필요 → `LEAD/ADFTD/scripts/downsample_adftd_500_to_200.py`로 500→200 변환 → `/pscratch/sd/b/boheelee/adftd/adftd_filtered_scale_1213_200hz` (19,8,200)
- **핵심 인자**: `--classifier all_patch_reps --frozen True --use_pretrained_weights True --num_of_classes 3 --lr 1e-4 --weight_decay 5e-2 --epochs 50`
- **함정**: (a) 200Hz 변환 필수, (b) `adftd_dataset.py` LMDB 중복open → env 캐시 패치, (c) classifier는 `all_patch_reps`(avgpooling은 collapse), (d) `--early_stop_*` 인자 없음(제거).

## 2. DIVER (500Hz)

- **스크립트**: `run_ADFTD_DIVER_lp.sh` (인터랙티브 loop, seeds 41-45)
- **repo**: `/pscratch/sd/b/boheelee/DIVER_ty_finetune/CBraMod`
- **weight**: `/global/cfs/cdirs/m5187/tylee/DIVER_SOTA/mp_rank_00_model_states.pt` (iEEG SOTA, CAUEEG LP .7272 낸 그 weight)
- **데이터**: 500Hz 원본 직접 사용 (변환 불필요)
- **config**: CAUEEG DIVER LP와 동일 (`--backbone_config DIVER_iEEG_FINAL_model --width 512 --depth 12 --mup_weights True --feature_extraction_type multi_head_take_org_x --ft_config flatten_linear --frozen True --precompute_features True --deepspeed_pth_format True --lr 2e-4 --weight_decay 3e-1`). ADFTD 자동 등록(num_targets=3)이라 `--num_of_classes` 불필요.

## 3. EEGPT (256Hz / 4s)

- **실행**: `python linear_probe_ours_5seeds.py --dataset ADFTD` (내부 5 seed) — 인터랙티브. CAUEEG는 shared sbatch(`scripts/run_CAUEEG_shared.sh`).
- **repo(코드)**: TY 카피 `/pscratch/sd/t/tylee/EEGPT` → boheelee 사본 `/pscratch/sd/b/boheelee/EEGPT` (수정용)
- **ckpt**: `/pscratch/sd/b/boheelee/EEGPT/checkpoint/eegpt_mcae_58chs_4s_large4E.ckpt` (58ch/4s, TY 사본 복사분)
- **데이터**: 256Hz/4s 필요 → `convert_to_eegpt256.py`로 500→256Hz + 4초 비겹침 윈도우 변환. value `{sample:(19,1024), label, data_info}`. 채널명은 data_info에서 읽어 config에 지정.
  - ADFTD 256Hz: `/pscratch/sd/b/boheelee/eegpt_data/ADFTD_EEGPT_256Hz` (17,378 win)
  - CAUEEG 256Hz: `/pscratch/sd/b/boheelee/eegpt_data/CAUEEG_EEGPT_256Hz` (175,124 win)
- **config**: `linear_probe_ours_5seeds.py`의 `DATASET_CONFIGS`에서 ADFTD lmdb_path를 위 변환본으로 교체, CAUEEG 항목 신규 추가(num_classes 3, img_size [19,1024], channel_names=CAUEEG 순서, lmdb_path). argparse `--dataset` choices에도 CAUEEG 추가.
- **코드 패치 5개(현재 환경 맞추기)**:
  1. `EEGPTDataset` LMDB 중복open → `_EEGPT_ENV_CACHE` 프로세스 캐시
  2. ckpt load_path 하드코딩(승주 원본) → boheelee 사본 경로로
  3. `torch.load(..., weights_only=False)` (torch 2.6+ 기본값 변경 대응)
  4. argparse `--dataset` choices에 CAUEEG 추가
  5. deps: `pip install --user pyhealth antlr4-python3-runtime==4.9.3` (⚠️ pyhealth가 --user torch 2.7.1 끌어옴 — 정상 동작하나 module 2.8.0 가림)
- **채널 매핑**: `compute_drop_and_use_channels`가 EEGPT 58ch ↔ 데이터 19ch 이름 매핑 자동 처리 (고정 채널이라 OK).
- **m4750 이슈**: EEGPT 원본 ADFTD LMDB는 m4750(boheelee 미소속, denied) → 위처럼 500Hz 소스에서 직접 256Hz 재생성해 우회함.

## 예산/환경 메모

- GPU allocation m5187_g: 노드아워 빠듯 → EEGPT CAUEEG는 `-q shared -G 1`(1/4 과금)으로 배치.
- 모든 LP는 frozen backbone이라 가벼움. DIVER는 precompute_features로 특히 빠름.

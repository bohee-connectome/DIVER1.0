#!/bin/bash
# EXP-02 · ADFTD — CBraMod BASELINE, Linear-Probe (frozen backbone + linear head), seeds 41-45.
# Mirrors the VERIFIED CBraMod-CAUEEG LP run (caueeg/cbramod/scripts/run_CBraMod_LP_s41.sh)
#   → same CBraMod pretrained weight, --use_pretrained_weights True, --frozen True,
#     --classifier avgpooling_patch_reps, lr 1e-4 / wd 5e-2, epochs 50, batch 64.
# SBATCH headers mirrored from ADFTD DIVER LP template (exp02/run_ADFTD_lp_array.sh).
# num_of_classes=3 (ADFTD = CN/FTD/AD).
#
# ============================================================================
# SERVER-VERIFIED 2026-07-02 — 3/4 확인 완료, 남은 블로커 1개:
#
#   [✓2] DATASET REGISTRATION — 존재. CBraMod_caueeg/finetune_main.py L155-158:
#        elif downstream_dataset=='ADFTD': adftd_dataset.LoadDataset + model_for_adftd.Model.
#   [✓3] REPO = /pscratch/sd/b/boheelee/CBraMod_caueeg (CBraMod ADFTD 분기가 여기 있음). 반영됨.
#   [✓4] WEIGHT = /pscratch/sd/t/tylee/pretrained_weights.pth (19.7MB) — 존재. 반영됨.
#
#   [✗1] SAMPLE RATE (남은 블로커). CBraMod patch = 200 samples = 1 s @ 200 Hz.
#        adftd_lmdb/ 에는 500 Hz(adftd_filtered_scale_1213)만 있고 *adftd*200* 검색 0건.
#        → 200 Hz ADFTD LMDB (8 s -> shape (19, 8, 200)) 를 찾거나 만들어 LMDB= 에 지정.
#        authoritative 확인: CBraMod adftd_dataset.py 가 읽는 경로를 grep 할 것.
# ============================================================================

#SBATCH -A m5187_g
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH --job-name=ADFTD_CBraMod_LP
#SBATCH --output=./slurm_outputs/ADFTD_CBraMod_LP-%A_%a.out
#SBATCH --error=./slurm_outputs/ADFTD_CBraMod_LP-%A_%a.err
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH -t 02:00:00
#SBATCH -c 32
#SBATCH --array=0-4

set -e

module load pytorch/2.8.0
# neuroprobe BrainTreebank config 통과용 더미 (ADFTD는 BrainTreebank 미사용)
export ROOT_DIR_BRAINTREEBANK=/tmp

seed_list=(41 42 43 44 45); seed=${seed_list[$SLURM_ARRAY_TASK_ID]}

REPO=/pscratch/sd/b/boheelee/CBraMod_caueeg   # ✓ CBraMod ADFTD 분기가 여기 있음 (검증됨)
# 200 Hz ADFTD LMDB. 500Hz(m5187) 원본을 downsample_adftd_500_to_200.py 로 변환한 산출물.
# 생성 전이면 아래 "다운샘플" 커맨드 먼저 실행. shape (19,8,500)->(19,8,200), split 보존.
LMDB=/pscratch/sd/b/boheelee/adftd/adftd_filtered_scale_1213_200hz
WEIGHT=/pscratch/sd/t/tylee/pretrained_weights.pth   # CBraMod pretrained (verbatim from CBraMod-CAUEEG LP)
OUT=$REPO/finetune_outputs/ADFTD/exp02_cbramod_lp/seed${seed}

mkdir -p $OUT ./slurm_outputs
cd $REPO

python finetune_main.py \
    --seed "$seed" \
    --downstream_dataset ADFTD \
    --datasets_dir $LMDB \
    --model_dir $OUT \
    --foundation_dir $WEIGHT \
    --use_pretrained_weights True \
    --frozen True \
    --classifier all_patch_reps \
    --num_of_classes 3 \
    --cuda 0 \
    --epochs 50 \
    --batch_size 64 \
    --lr 1e-4 \
    --weight_decay 5e-2
# NOTE: CBraMod finetune_main.py 파서엔 --early_stop_criteria/--early_stop_patience 없음 (DIVER 전용) → 제거함

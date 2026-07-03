#!/bin/bash
# DIVER-ADFTD Linear Probe (seeds 41-45).
# CAUEEG DIVER LP(run_finetune_CAUEEG_DIVER_linearprobe.sh, AUROC .7272)와 완전히 동일한 config,
# downstream_dataset/datasets_dir만 ADFTD로 교체. DIVER는 500Hz LMDB 직접 사용(다운샘플 불필요).
#
# 인터랙티브 실행:
#   salloc -A m5187_g -C gpu -q interactive -t 00:40:00 -N 1
#   bash run_ADFTD_DIVER_lp.sh
# (precompute_features + frozen이라 빠름. 끝나면 exit로 노드 반납.)

set -e
module load pytorch/2.8.0
export ROOT_DIR_BRAINTREEBANK=/tmp   # neuroprobe config 통과용 더미 (ADFTD는 BrainTreebank 미사용)

REPO=/pscratch/sd/b/boheelee/DIVER_ty_finetune/CBraMod
WEIGHT=/global/cfs/cdirs/m5187/tylee/DIVER_SOTA/mp_rank_00_model_states.pt   # iEEG SOTA, dmodel512/layers12, 51.3M
LMDB=/global/cfs/cdirs/m5187/tylee/adftd_lmdb/adftd_filtered_scale_1213      # 500Hz, sample (19,8,500), subject-exclusive split
cd $REPO

for s in 41 42 43 44 45; do
  echo "===== DIVER-ADFTD LP seed $s ====="
  python finetune_main.py \
      --seed $s \
      --downstream_dataset ADFTD \
      --datasets_dir $LMDB \
      --model_dir $REPO/finetune_outputs/ADFTD/diver_lp/seed$s \
      --foundation_dir $WEIGHT \
      --backbone_config DIVER_iEEG_FINAL_model \
      --cuda 0 \
      --feature_extraction_type multi_head_take_org_x \
      --use_optuna False \
      --ft_config flatten_linear \
      --width 512 --depth 12 --mup_weights True \
      --use_amp False \
      --deepspeed_pth_format True \
      --early_stop_criteria val_f1 --early_stop_patience 20 \
      --frozen True \
      --precompute_features True \
      --lr 2.00e-04 --weight_decay 3.00e-01 \
      --ft_mup False
done

# 결과 수집:
#   for s in 41 42 43 44 45; do ls $REPO/finetune_outputs/ADFTD/diver_lp/seed$s/*.pth; done
# ADFTD는 FINAL_TASK_DICT["ADFTD"](num_targets=3)로 자동 등록 → --num_of_classes 불필요.

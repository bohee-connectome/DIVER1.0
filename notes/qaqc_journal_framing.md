# DIVER 저널 — QAQC / flat detection 포지셔닝 노트

> 목적: 나중에 DIVER 저널 원고 쓸 때, sliding-window flat detection(QAQC)을 **어떻게 프레이밍해서 끼워넣을지** 문단 초안 재료. novelty 판정 문서가 아니라 "쓸 때 참고할 각".
> 근거: 2026-07-02 선행연구 조사(deep-research + SPEED/PREP/MNE 정독).

---

## 1. 한 줄 포지션

flat 감지 자체를 새 기법으로 팔지 말고, **"scale-invariant surgical sub-window 큐레이션이 대규모 messy 임상 EEG를 DIVER 프리트레인용으로 살려낸다"**는 **데이터 큐레이션 기여**로 끼워넣는다. primitive는 supporting.

## 2. 팔면 안 되는 것 (선행에 이미 있음 — 오버클레임 시 리뷰어가 바로 찌름)

- **"부분/채널 내 flat을 잡는다"** → MNE `annotate_amplitude`(구 `annotate_flat`)가 이미 채널별 recording 내부 flat 시간구간을 annotation으로 뽑음. (단 absolute threshold, peak-to-peak 단일기준)
- **"FM/SSL용 대규모 EEG QC 큐레이션"** → **SPEED (arXiv:2408.08065)**가 이미 소유. PREP 기반 파이프라인 + 60초 윈도우 품질 게이트로 TUEG 큐레이션. 응용 공간 동일.
- **채널 통째 flat/bad 감지** → PREP (Bigdely-Shamlo 2015), pyprep.

## 3. 방어 가능한 우리 것 (문단에서 강조할 핵심 3)

세 도구(SPEED/PREP/MNE) 다 안 가진 조합:
1. **per-channel/per-subject 상대 기준** — 자기 채널 활동수준 percentile 대비 (scale-invariant). PREP는 cross-channel robust-z, MNE는 absolute. 아무도 own-scale percentile 안 씀.
2. **상대-variance AND 상대-차분(안 움직임) 결합** — 저진폭 진짜신호 보존. 단일기준 아님.
3. **flat-fraction을 랭킹/큐레이션 점수로** (이진 플래그 아님). SPEED는 60초 윈도우 이진 drop.

## 4. 저널에 넣을 위치 & 문단 스케치

**어디에**: Methods의 데이터 큐레이션(전처리) 서브섹션 + Related Work에서 SPEED/PREP/MNE 대비 1문단.

**문단 각 (초안 재료)**:
- (동기) HEEDB 같은 대규모 임상 EEG는 raw로 배포되고 부분 flat이 많아 FM 프리트레인에 거의 안 쓰임. 기존 QC는 채널 통째(PREP) 또는 absolute·이진 윈도우 드롭(MNE/SPEED)이라, 피험자별 스케일이 제각각인 임상 데이터에서 (a) 좋은 저진폭 신호를 버리거나 (b) 부분 flat을 놓친다.
- (방법) 우리는 각 채널 자기 스케일 대비 상대 기준으로, 짧은 sliding window에서 variance와 차분을 AND로 결합해 부분 flat을 잡고, flat-fraction으로 세그먼트/채널을 수술적으로 큐레이션한다.
- (이득) 동일 정밀도에서 이진 윈도우 드롭보다 학습데이터를 더 많이 살리고(yield), 채널 진폭 리스케일에 강건하다(scale-invariance). → DIVER 프리트레인 데이터가 더 많고 깨끗해진다.

## 5. 리드할 실증 (문단을 뒷받침할 그림/표)

- ★ **scale-invariance 테스트**: 채널 진폭 ×0.1~×10 → absolute 방법(MNE·SPEED OHA) F1 붕괴, 우리는 flat. **제일 깨끗한 단독 승리.**
- **yield@matched-precision**: 같은 정밀도에서 살린 학습시간(hours) 우위 (vs SPEED 윈도우 드롭).
- (여유되면) downstream: 큐레이션별 DIVER 프리트레인 → 태스크 정확도.

## 6. 인용 (related work 문단용)

- SPEED — arXiv:2408.08065 (SSL용 EEG 전처리, 응용 최근접 경쟁)
- PREP — Bigdely-Shamlo et al. 2015, Front. Neuroinform. 9:16
- MNE `annotate_amplitude` — mne.tools 문서
- HEEDB(대규모 raw 임상 EEG, QC 없음) — Sun et al. 2025, Epilepsia, doi:10.1111/epi.18487
- HEEDB를 쓴 FM 소수 사례 — CLEF arXiv:2605.10817 (bandpass/notch만)
- EEG-FM는 명시적 artifact 제거 안 함 — 리뷰 arXiv:2507.11783

## 7. 투고 전 반드시 (안 하면 리뷰어가 찌름)

- SPEED Sec 4.2(OHA/THV/CHV/RBC) **clean PDF로 재확인** 후 수치 인용. RBC(bad-channel 비율)를 "flat-fraction 비슷한 거 아니냐" 물을 수 있으니 차이 명시.
- **PREP-flatline + MNE annotate_flat 대비 직접 벤치마크** 결과 없이 우위 주장 금지.
- ablation으로 novel 3요소 각각 분리 (상대vs절대 / AND-차분vs variance만 / 랭킹vs이진).

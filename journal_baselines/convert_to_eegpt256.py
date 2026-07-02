#!/usr/bin/env python3
"""
convert_to_eegpt256.py
DIVER-format LMDB (sample=(C, n_seg, samp)) -> EEGPT format (sample=(C, 1024)=4s@256Hz).
채널명/sample rate는 data_info에서 읽어 자동 처리 → ADFTD·CAUEEG 둘 다 동일 스크립트로.
비겹침 4초 윈도우로 재분할, __keys__ split(subject-exclusive) 보존. EEGPT 로더가 z-norm 하므로 raw 저장.

사용:
  python convert_to_eegpt256.py --input <500Hz DIVER LMDB> --output <EEGPT 256Hz LMDB>
출력 끝에 config에 넣을 channel_names 를 찍어줌.
"""
import lmdb, pickle, os, shutil, argparse
import numpy as np
from scipy.signal import resample

FS, WIN = 256, 256 * 4  # 1024 = 4s @ 256Hz


def convert(inp, out):
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    it = lmdb.open(inp, readonly=True, lock=False).begin()
    kk = pickle.loads(it.get(b'__keys__')); assert isinstance(kk, dict), "expects split dict __keys__"
    insz = sum(os.path.getsize(os.path.join(inp, f)) for f in os.listdir(inp))
    oenv = lmdb.open(out, map_size=int(insz * 1.6) + 10**8)
    new_keys = {m: [] for m in kk}; ch = None; n = 0; ot = oenv.begin(write=True)
    for split in kk:
        for key in kk[split]:
            d = pickle.loads(it.get(key.encode()))
            s = np.asarray(d['sample'], dtype=np.float32)          # (C, n_seg, samp)
            cont = s.reshape(s.shape[0], -1)                       # (C, total)
            fs = d['data_info'].get('resampling_rate', 500)
            if ch is None:
                ch = d['data_info'].get('channel_names')
            c256 = resample(cont, int(round(cont.shape[1] * FS / fs)), axis=1).astype(np.float32)
            for wi in range(c256.shape[1] // WIN):                 # non-overlapping 4s windows
                w = c256[:, wi * WIN:(wi + 1) * WIN]               # (C, 1024)
                nk = f"{key}/w{wi}"
                di = dict(d['data_info']); di.update(resampling_rate=FS, segment_length=WIN, window_index=wi)
                ot.put(nk.encode(), pickle.dumps({'sample': w, 'label': d['label'], 'data_info': di}))
                new_keys[split].append(nk); n += 1
                if n % 2000 == 0:
                    ot.commit(); ot = oenv.begin(write=True); print(n, flush=True)
    ot.put(b'__keys__', pickle.dumps(new_keys)); ot.commit()
    print(f"DONE {n} windows -> {out}")
    print("splits:", {m: len(new_keys[m]) for m in new_keys})
    print("channel_names (config용):", ch)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument('--input', required=True)
    a.add_argument('--output', required=True)
    x = a.parse_args()
    convert(x.input, x.output)

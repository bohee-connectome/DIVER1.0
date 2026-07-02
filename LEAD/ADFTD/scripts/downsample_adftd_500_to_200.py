#!/usr/bin/env python3
"""
Downsample ADFTD LMDB from 500Hz to 200Hz (for CBraMod baseline).

Reads existing 500Hz ADFTD LMDB and creates a new 200Hz version.
Only changes: sample last-axis 500 -> 200 and data_info.resampling_rate 500 -> 200.
Everything else (keys, split baked into __keys__, label, data_info) preserved.

Source 500Hz LMDB (verified 2026-07-02):
  /global/cfs/cdirs/m5187/tylee/adftd_lmdb/adftd_filtered_scale_1213
  value = {'sample': (19, 8, 500) float32, 'label': int64, 'data_info': {...}}
  __keys__ = {'train': [...], 'val': [...], 'test': [...]}  (subject-exclusive)

Mirror of downsample_isruc_500_to_200.py (identical LMDB schema). Author: Bohee Lee.
"""

import lmdb
import pickle
import numpy as np
from scipy.signal import resample
from pathlib import Path
import argparse
from tqdm import tqdm

TARGET_SAMPLES = 200  # 1 s @ 200 Hz per patch (CBraMod patch size)


def downsample_signal(signal_500hz, target_samples=TARGET_SAMPLES):
    """(n_ch, n_seg, 500) -> (n_ch, n_seg, target_samples). Shape read from data, not hardcoded."""
    n_channels, n_segments, _ = signal_500hz.shape
    out = np.zeros((n_channels, n_segments, target_samples), dtype=np.float32)
    for ch in range(n_channels):
        for seg in range(n_segments):
            out[ch, seg, :] = resample(signal_500hz[ch, seg, :], target_samples)
    return out


def check_lmdb_structure(lmdb_path, num_samples=3):
    """Dry run: inspect structure before downsampling."""
    env = lmdb.open(str(lmdb_path), readonly=True, lock=False)
    print("\n" + "=" * 70 + "\nDRY RUN: Checking ADFTD LMDB structure\n" + "=" * 70)
    with env.begin() as txn:
        print(f"Total entries: {txn.stat()['entries']:,}")
        checked = 0
        for key, value in txn.cursor():
            if key == b'__keys__':
                kk = pickle.loads(value)
                if isinstance(kk, dict):
                    print("\n__keys__ (copied as-is): " +
                          ", ".join(f"{m}={len(kk[m])}" for m in kk))
                continue
            if checked >= num_samples:
                break
            d = pickle.loads(value)
            print(f"\n--- Sample {checked + 1}: {key.decode()} ---")
            print(f"Top-level keys: {list(d.keys())}")
            print(f"WILL CHANGE  sample.shape: {d['sample'].shape} -> "
                  f"{d['sample'].shape[:-1] + (TARGET_SAMPLES,)}")
            print(f"WILL CHANGE  resampling_rate: "
                  f"{d['data_info'].get('resampling_rate')} -> {TARGET_SAMPLES}")
            print(f"PRESERVE     label={d['label']}  data_info keys={list(d['data_info'].keys())}")
            checked += 1
    env.close()
    print("\n" + "=" * 70 + "\nOnly sample shape + resampling_rate change; all else preserved.\n" + "=" * 70)


def downsample_lmdb(input_lmdb_path, output_lmdb_path, batch_size=1000):
    input_path, output_path = Path(input_lmdb_path), Path(output_lmdb_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input LMDB not found: {input_path}")
    output_path.mkdir(parents=True, exist_ok=True)

    input_env = lmdb.open(str(input_path), readonly=True, lock=False)
    with input_env.begin() as txn:
        total = txn.stat()['entries']
    input_size = sum(f.stat().st_size for f in input_path.glob('*'))
    output_env = lmdb.open(str(output_path), map_size=int(input_size * 0.4 * 1.3))

    print(f"\nInput:  {input_path}\nOutput: {output_path}\n"
          f"Downsampling 500Hz -> 200Hz, {total:,} entries\n")

    processed, dataset_keys = 0, None
    with input_env.begin() as input_txn:
        output_txn = output_env.begin(write=True)
        try:
            for key, value in tqdm(input_txn.cursor(), total=total, desc="Downsampling"):
                if key == b'__keys__':
                    dataset_keys = value  # copy split verbatim
                    continue
                d = pickle.loads(value)
                d['sample'] = downsample_signal(d['sample'], TARGET_SAMPLES)
                d['data_info']['resampling_rate'] = TARGET_SAMPLES
                output_txn.put(key, pickle.dumps(d))
                processed += 1
                if processed % batch_size == 0:
                    output_txn.commit()
                    output_txn = output_env.begin(write=True)
            if dataset_keys is not None:
                output_txn.put(b'__keys__', dataset_keys)
            output_txn.commit()
        except Exception:
            output_txn.abort()
            raise
    input_env.close()
    output_env.close()
    print("\n" + "=" * 70 + f"\nDone. Processed {processed:,} samples -> {output_path}\n" + "=" * 70)


def main():
    p = argparse.ArgumentParser(description="Downsample ADFTD LMDB 500Hz -> 200Hz")
    p.add_argument('--input_lmdb', type=str, required=True, help='Input 500Hz ADFTD LMDB')
    p.add_argument('--output_lmdb', type=str, help='Output 200Hz LMDB (required for real run)')
    p.add_argument('--batch_size', type=int, default=1000)
    p.add_argument('--dry_run', action='store_true', help='Inspect structure only')
    p.add_argument('--check_samples', type=int, default=3)
    args = p.parse_args()

    if args.dry_run:
        check_lmdb_structure(args.input_lmdb, args.check_samples)
    else:
        if not args.output_lmdb:
            p.error("--output_lmdb is required when not using --dry_run")
        downsample_lmdb(args.input_lmdb, args.output_lmdb, args.batch_size)


if __name__ == "__main__":
    main()

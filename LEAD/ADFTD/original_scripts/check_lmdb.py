#!/usr/bin/env python
"""Check LMDB contents and verify data integrity"""
import lmdb
import pickle
import os
import numpy as np

lmdb_path = '/pscratch/sd/b/boheelee/DIVER/ISRUC_preprocessing/lmdb_output/ISRUC_Sleep'

print("="*60)
print("LMDB Data Verification")
print("="*60)

# Check if LMDB exists
if not os.path.exists(lmdb_path):
    print(f"❌ LMDB not found at: {lmdb_path}")
    exit(1)

# Check LMDB file size
data_file = os.path.join(lmdb_path, 'data.mdb')
if os.path.exists(data_file):
    size_gb = os.path.getsize(data_file) / (1024**3)
    print(f"📁 LMDB data file size: {size_gb:.2f} GB")
else:
    print("❌ data.mdb not found")

# Open LMDB
try:
    db = lmdb.open(lmdb_path, readonly=True, lock=False)
    
    # Get all keys
    with db.begin() as txn:
        cursor = txn.cursor()
        all_keys = [key.decode() for key, _ in cursor]
    
    print(f"📊 Total keys in LMDB: {len(all_keys)}")
    
    # Check for __keys__
    if '__keys__' in all_keys:
        with db.begin() as txn:
            keys_data = txn.get('__keys__'.encode())
            if keys_data:
                dataset = pickle.loads(keys_data)
                print("\n📋 Dataset structure:")
                for split, keys in dataset.items():
                    print(f"  {split}: {len(keys)} samples")
                print(f"  Total: {sum(len(v) for v in dataset.values())} samples")
                
                # Show some sample keys
                print("\n🔑 Sample keys (first 10):")
                for split, keys in dataset.items():
                    if keys:
                        print(f"  {split}:")
                        for key in keys[:5]:
                            print(f"    - {key}")
                        if len(keys) > 5:
                            print(f"    ... and {len(keys)-5} more")
                        break
    else:
        print("⚠️  __keys__ not found in LMDB")
    
    # Check sample data
    print("\n🔍 Verifying sample data:")
    sample_keys = [k for k in all_keys if k != '__keys__'][:5]
    
    for key in sample_keys:
        with db.begin() as txn:
            data = txn.get(key.encode())
            if data:
                try:
                    sample = pickle.loads(data)
                    if 'sample' in sample:
                        sample_shape = sample['sample'].shape
                        label = sample.get('label', 'N/A')
                        subject_id = sample.get('data_info', {}).get('subject_id', 'N/A')
                        print(f"  ✓ {key}: shape={sample_shape}, label={label}, subject={subject_id}")
                    else:
                        print(f"  ⚠️  {key}: Missing 'sample' key")
                except Exception as e:
                    print(f"  ❌ {key}: Error loading - {e}")
            else:
                print(f"  ❌ {key}: Not found")
    
    # Count by subject
    print("\n📈 Subjects processed:")
    subjects = {}
    for key in all_keys:
        if key != '__keys__' and '_S' in key:
            # Extract subject ID (e.g., Subgroup1_S001 from Subgroup1_S001_E0000)
            parts = key.split('_S')
            if len(parts) > 1:
                subject_part = parts[1].split('_')[0]
                subject_key = f"{parts[0]}_S{subject_part}"
                subjects[subject_key] = subjects.get(subject_key, 0) + 1
    
    print(f"  Total subjects: {len(subjects)}")
    for subject, count in sorted(subjects.items())[:10]:
        print(f"  {subject}: {count} epochs")
    if len(subjects) > 10:
        print(f"  ... and {len(subjects)-10} more subjects")
    
    db.close()
    print("\n✅ LMDB check completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()



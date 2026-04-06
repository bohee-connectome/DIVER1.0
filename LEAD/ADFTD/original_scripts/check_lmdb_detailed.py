#!/usr/bin/env python
"""Check LMDB contents and verify map_size"""
import lmdb
import pickle
import os
import struct

lmdb_path = '/pscratch/sd/b/boheelee/DIVER/ISRUC_preprocessing/lmdb_output/ISRUC_Sleep'

print("="*60)
print("LMDB Detailed Verification")
print("="*60)

# Check if LMDB exists
if not os.path.exists(lmdb_path):
    print(f"❌ LMDB not found at: {lmdb_path}")
    exit(1)

# Check LMDB file size
data_file = os.path.join(lmdb_path, 'data.mdb')
if os.path.exists(data_file):
    size_gb = os.path.getsize(data_file) / (1024**3)
    print(f"📁 LMDB data file size (actual): {size_gb:.2f} GB")
else:
    print("❌ data.mdb not found")
    exit(1)

# Try to read map_size from LMDB header
# LMDB stores map_size in the first 16 bytes of data.mdb
try:
    with open(data_file, 'rb') as f:
        # Read LMDB header (first 16 bytes contain map_size)
        header = f.read(16)
        # map_size is stored as uint64 at offset 8
        map_size = struct.unpack('<Q', header[8:16])[0]
        map_size_gb = map_size / (1024**3)
        print(f"📊 LMDB map_size (max limit): {map_size_gb:.2f} GB")
        print(f"📈 Available space: {map_size_gb - size_gb:.2f} GB")
except Exception as e:
    print(f"⚠️  Could not read map_size from header: {e}")

# Open LMDB and check
try:
    # Try to open with different map_sizes to see what works
    # If it opens successfully, the map_size is at least that value
    db = lmdb.open(lmdb_path, readonly=True, lock=False, map_size=200*1024**3)
    
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
    
    # Count by subject
    subjects = {}
    for key in all_keys:
        if key != '__keys__' and '_S' in key:
            parts = key.split('_S')
            if len(parts) > 1:
                subject_part = parts[1].split('_')[0]
                subject_key = f"{parts[0]}_S{subject_part}"
                subjects[subject_key] = subjects.get(subject_key, 0) + 1
    
    print(f"\n📈 Subjects processed: {len(subjects)}")
    
    db.close()
    print("\n✅ LMDB check completed!")
    print(f"\n💡 Note: Actual file size is {size_gb:.2f} GB (data only)")
    print(f"   map_size limit should be 200 GB (allows growth up to 200 GB)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()



import os
import shutil
import pandas as pd

SOURCE_DIR = '/path/to/seizeit2'   # Full dataset location
TARGET_DIR = '/path/to/seizeit2_subset'  # Where to copy
MAX_TOTAL_SIZE_GB = 3
SEIZURE_KEYWORDS = ['seizure', 'sz']  # Can be adapted

def folder_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

def has_seizure(tsv_path):
    try:
        df = pd.read_csv(tsv_path, sep='\t')
        for col in df.columns:
            for word in SEIZURE_KEYWORDS:
                if df[col].astype(str).str.contains(word, case=False).any():
                    return True
    except:
        pass
    return False

included = 0
total_size_bytes = 0

os.makedirs(TARGET_DIR, exist_ok=True)

for patient_id in sorted(os.listdir(SOURCE_DIR)):
    patient_path = os.path.join(SOURCE_DIR, patient_id)
    if not os.path.isdir(patient_path):
        continue

    # Locate annotations
    annotations_path = os.path.join(patient_path, 'annotations')
    if not os.path.exists(annotations_path):
        continue

    tsv_files = [f for f in os.listdir(annotations_path) if f.endswith('.tsv')]
    seizure_found = any(has_seizure(os.path.join(annotations_path, tsv)) for tsv in tsv_files)
    
    if not seizure_found:
        continue

    # Estimate size
    this_size = folder_size(patient_path)
    if (total_size_bytes + this_size) > MAX_TOTAL_SIZE_GB * (1024 ** 3):
        print(f"Stopping: {patient_id} would exceed size limit")
        break

    # Copy patient folder
    shutil.copytree(patient_path, os.path.join(TARGET_DIR, patient_id))
    total_size_bytes += this_size
    included += 1
    print(f"Included {patient_id} | Total size: {total_size_bytes / (1024**3):.2f} GB")

print(f"\n✅ Copied {included} patients with seizures under {MAX_TOTAL_SIZE_GB} GB limit")

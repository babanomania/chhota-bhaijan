import os
import json
import random

# File paths
DATA_DIR = "./data"
OUTPUT_FILE = os.path.join(DATA_DIR, "dataset.jsonl")

INPUT_FILES = [
    os.path.join(DATA_DIR, "dialogues.jsonl"),
    os.path.join(DATA_DIR, "interviews.jsonl"),
    os.path.join(DATA_DIR, "movie_summaries.jsonl"),
    os.path.join(DATA_DIR, "persona_boost.jsonl")
]

# Load and merge all JSONL records
all_records = []

for file_path in INPUT_FILES:
    if not os.path.exists(file_path):
        print(f"⚠️ Missing file: {file_path}. Skipping...")
        continue

    print(f"📥 Loading from: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                # Optional schema validation
                if all(k in record for k in ("instruction", "input", "output")):
                    all_records.append(record)
                else:
                    print(f"⚠️ Skipped invalid record in {file_path}")
            except json.JSONDecodeError:
                print(f"⚠️ Skipped corrupt line in {file_path}")

print(f"\n🔢 Total records before shuffle: {len(all_records)}")

# Shuffle to mix up dialogue/interview/summaries
random.shuffle(all_records)

# Save merged file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for record in all_records:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"✅ Merged dataset saved at: {OUTPUT_FILE}")
print(f"📝 Total records: {len(all_records)}")

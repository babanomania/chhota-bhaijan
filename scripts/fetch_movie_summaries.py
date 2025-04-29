import wikipedia
import os
import json

# Movies list
salman_movies = [
    "Tere Naam",
    "Wanted (2009 film)",
    "Dabangg",
    "Bodyguard (2011 Hindi film)",
    "Ek Tha Tiger",
    "Kick (2014 film)",
    "Bajrangi Bhaijaan",
    "Sultan (2016 film)",
    "Tiger Zinda Hai",
    "Bharat (film)",
    "Radhe (2021 film)",
    "Kisi Ka Bhai Kisi Ki Jaan",
    "Tiger 3"
]

# Output file
output_file = "./data/movie_summaries.jsonl"
os.makedirs("./data", exist_ok=True)

records = []

# Collect Wikipedia Summaries
for movie in salman_movies:
    try:
        summary = wikipedia.summary(movie, sentences=5, auto_suggest=False)
        record = {
            "instruction": f"Summarize the plot of Salman Khan's movie '{movie}' in simple words.",
            "input": "",
            "output": summary
        }
        records.append(record)
        print(f"✅ Summary fetched for: {movie}")
    except Exception as e:
        print(f"❌ Could not fetch for {movie}: {e}")

# Save to JSONL
with open(output_file, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"\n🏁 Finished preparing {len(records)} entries at {output_file}")

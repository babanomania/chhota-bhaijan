import yt_dlp
import os
import json
import re
import nltk
import time
from openai import OpenAI

nltk.download('punkt')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# List of Salman YouTube interview videos
videos = [
    {"url": "https://www.youtube.com/watch?v=NQNtbbxJjCo", "title": "Film Philosophy and Values Discussion"},
    {"url": "https://www.youtube.com/watch?v=dqSSIskbuP8", "title": "Concerts and 'Bigg Boss' Talk"},
    {"url": "https://m.youtube.com/watch?v=oihkJ-AAF7k", "title": "Mother Anecdotes and Early Screening"},
    {"url": "https://www.youtube.com/watch?v=Yovtuoyw8DA", "title": "Media Portrayal and Personal Life"},
    {"url": "https://www.youtube.com/watch?v=vSzHQoRhO_o", "title": "Personal Values, Advice, and Forgiveness"},
    {"url": "https://www.youtube.com/watch?v=Zdr6oNEXjiw", "title": "Film Choices and Finances"},
    {"url": "https://www.youtube.com/watch?v=34A_byKv26s", "title": "Cultural Differences and Respect"},
    {"url": "https://www.youtube.com/watch?v=NOLtIp__peA&pp=0gcJCdgAo7VqN5tD", "title": "Addressing Accusations of Violence"},
    {"url": "https://www.youtube.com/watch?v=pXJNaWQH1fI", "title": "Not Wanting to be Called 'Jaan'"},
    {"url": "https://www.youtube.com/watch?v=VIIpim_3ICQ", "title": "Prem Ratan Dhan Payo and Future Work"},
    {"url": "https://www.youtube.com/watch?v=zEyBbt9Gor4", "title": "Interview about 'Hello Brother'"},
    {"url": "https://www.youtube.com/watch?v=xGlxIoDGEuA", "title": "Podcast on Prison Time, Work Ethic, Sikandar"},
    {"url": "https://m.youtube.com/watch?v=x2TmyKgA7OM&t=56s", "title": "Snippet on Live Performances"},
    {"url": "https://www.youtube.com/watch?v=QVuB5bh9JqU", "title": "Shahrukh Khan Interviews Salman Khan"},
    {"url": "https://www.youtube.com/watch?v=gm_EjOlPiIM", "title": "Salman Khan at enlightED Virtual Edition 2020"},
    {"url": "https://www.youtube.com/watch?v=jqsQkr5vV6Y", "title": "Controversies and Film Releases Excerpt"},
]

# Directory setup
os.makedirs("./data/captions", exist_ok=True)
os.makedirs("./data", exist_ok=True)

# Final output file
output_jsonl = "./data/interviews.jsonl"

qa_pairs = []

# Helper functions
def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def download_captions(video_url, save_as):
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
        'outtmpl': save_as,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        if 'subtitles' in info or 'automatic_captions' in info:
            print(f"✅ Captions downloaded for: {info['title']}")
        else:
            print(f"⚠️ No captions available for: {info['title']}")

def parse_captions(vtt_file):
    text = ""
    with open(vtt_file, "r", encoding="utf-8") as f:
        for line in f:
            if "-->" not in line and not line.strip().isdigit():
                text += " " + line.strip()
    return text

def chunk_text(text, max_words=700):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield ' '.join(words[i:i+max_words])

# Main Loop
for vid in videos:
    try:
        print(f"🎥 Processing {vid['title']}")
        safe_title = safe_filename(vid['title'])
        caption_path = f"./data/captions/{safe_title}.en.vtt"

        # Download subtitles
        download_captions(vid['url'], f"./data/captions/{safe_title}.%(ext)s")

        if not os.path.exists(caption_path):
            print(f"❌ Captions not found for {vid['title']}. Skipping...")
            continue

        # Read and clean captions
        raw_text = parse_captions(caption_path)
        print(f"📝 Parsed {len(raw_text.split())} words from captions.")
        chunks = list(chunk_text(raw_text))

        # Process each chunk through OpenAI
        for idx, chunk in enumerate(chunks):
            print(f"🧠 Asking GPT for Q&A extraction (chunk {idx+1}/{len(chunks)})...")

            system_prompt = (
                "You are a helpful assistant extracting clean Question-Answer pairs from interview transcripts. "
                "Given a messy conversation transcript, extract the most important 3-5 Q&A pairs. "
                "Write them as JSON objects with 'question' and 'answer' fields. "
                "Maintain a casual and humble tone like Salman Khan would."
            )

            user_prompt = f"Transcript:\n{chunk}\n\nExtract important Q&A pairs."

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.4,
                )

                reply = response.choices[0].message.content
                qa_objects = re.findall(r'\{.*?\}', reply, re.DOTALL)

                for obj in qa_objects:
                    qa = json.loads(obj)
                    qa_pairs.append({
                        "instruction": "Answer like Salman Khan in an interview.",
                        "input": qa['question'],
                        "output": qa['answer']
                    })

            except Exception as e:
                print(f"⚠️ GPT API error on chunk {idx+1}: {e}")
                time.sleep(5)  # Retry after pause if needed

    except Exception as e:
        print(f"❌ Error processing {vid['title']}: {e}")

# Save final QA dataset
with open(output_jsonl, "w", encoding="utf-8") as f:
    for record in qa_pairs:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"\n🏁 Done. Total Q&A pairs generated: {len(qa_pairs)}")
print(f"✅ Saved to {output_jsonl}")

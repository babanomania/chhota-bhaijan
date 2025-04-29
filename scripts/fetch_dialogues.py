import asyncio
from playwright.async_api import async_playwright
import json
import os

# List of Salman Khan movies with their IMDB "Quotes" page
imdb_movies = {
    "Tere Naam": "https://www.imdb.com/title/tt0374271/quotes",
    "Wanted (2009 film)": "https://www.imdb.com/title/tt1084972/quotes",
    "Dabangg": "https://www.imdb.com/title/tt1620719/quotes",
    "Bodyguard (2011 Hindi film)":"https://www.imdb.com/title/tt1729637/quotes",
    "Ek Tha Tiger": "https://www.imdb.com/title/tt2016894/quotes",
    "Kick (2014 film)": "https://www.imdb.com/title/tt2372222/quotes",
    "Bajrangi Bhaijaan": "https://www.imdb.com/title/tt3863552/quotes",
    "Sultan (2016 film)": "https://www.imdb.com/title/tt4832640/quotes",
    "Tiger Zinda Hai": "https://www.imdb.com/title/tt5956100/quotes",
    "Bharat (film)": "https://www.imdb.com/title/tt7721800/quotes",
    "Radhe": "https://www.imdb.com/title/tt10888594/quotes",
    "Kisi Ka Bhai Kisi Ki Jaan": "https://www.imdb.com/title/tt3679040/quotes",
    "Tiger 3": "https://www.imdb.com/title/tt18411490/quotes",
}

filmyquotes = {
    "Tere Naam": "https://www.filmyquotes.com/movies/363",
    "Wanted (2009 film)": "https://www.filmyquotes.com/movies/31",
    "Dabangg": "https://www.filmyquotes.com/movies/32",
    "Bodyguard (2011 Hindi film)":"https://www.filmyquotes.com/movies/30",
    "Ek Tha Tiger": "https://www.filmyquotes.com/movies/247",
    "Kick (2014 film)": "https://www.filmyquotes.com/movies/680",
    "Bajrangi Bhaijaan": "https://www.filmyquotes.com/movies/1330",
    "Sultan (2016 film)": "https://www.filmyquotes.com/movies/1592",
    "Tiger Zinda Hai": "https://www.filmyquotes.com/movies/1731",
    "Bharat (film)": "https://www.filmyquotes.com/movies/1807",
    "Radhe": "https://www.filmyquotes.com/movies/1899",
    "Kisi Ka Bhai Kisi Ki Jaan": "https://www.filmyquotes.com/movies/1938",
    "Tiger 3": "https://www.filmyquotes.com/movies/1945",
}

output_file = "./data/dialogues.jsonl"
os.makedirs("./data", exist_ok=True)

async def fetch_dialogues():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        all_records = []

        print(f"Using IMDB for dialogues...")
        for movie, url in imdb_movies.items():
            try:
                await page.goto(url)
                await page.wait_for_selector('.ipc-html-content', timeout=5000) # Wait for dialogues to load
                
                dialogues = await page.query_selector_all('.ipc-html-content')
                print(f"✅ Found {len(dialogues)} dialogues for: {movie}")

                for dialogue_element in dialogues:
                    text = await dialogue_element.inner_text()
                    cleaned_text = ' '.join(text.split())

                    record = {
                        "instruction": f"Write a famous Salman Khan style dialogue from the movie '{movie}'.",
                        "input": "",
                        "output": cleaned_text
                    }
                    all_records.append(record)

            except Exception as e:
                print(f"❌ Error fetching {movie}: {e}")

        print(f"Using FilmyQuotes for dialogues...")
        for movie, url in filmyquotes.items():
            try:
                await page.goto(url)
                await page.wait_for_selector('#midRail > div > div.card-body > figure > div:nth-child(3)', timeout=5000) # Wait for dialogues to load
                
                dialogues = await page.query_selector_all('#midRail > div > div.card-body > figure > div:nth-child(3)')
                print(f"✅ Found {len(dialogues)} dialogues for: {movie}")

                for dialogue_element in dialogues:
                    text = await dialogue_element.inner_text()
                    cleaned_text = ' '.join(text.split())

                    record = {
                        "instruction": f"Write a famous Salman Khan style dialogue from the movie '{movie}'.",
                        "input": "",
                        "output": cleaned_text
                    }
                    all_records.append(record)

            except Exception as e:
                print(f"❌ Error fetching {movie}: {e}")

        await browser.close()

        # Save all collected dialogues into a JSONL file
        with open(output_file, "w", encoding="utf-8") as f:
            for record in all_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"\n🏁 Fetched {len(all_records)} dialogues total. Saved to {output_file}")

# Entry point
if __name__ == "__main__":
    asyncio.run(fetch_dialogues())

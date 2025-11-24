# src/scraping_reddit_fake.py
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from time import sleep

SUBREDDITS = [
    "AnimeLeaks",
    "AnimeRumors",
    "Animemes",
    "UnconfirmedLeaks",
    "MangaLeaks",
    "Shonengaming",
    "AnimeNewsAndLeaks",
    "AnimeSpoilers",
    "AnimeFakes",
]

OUT = Path("../NekoNews/data/raw/reddit_fake_candidates.csv")
BASE = "https://api.pullpush.io/reddit/search/submission/"

KEYWORDS = [
    "leak", "spoiler", "rumor", "confirmed", "unconfirmed", "source",
    "leaked", "exclusive", "exposed", "insider",
    "true???", "trust me", "90% sure", "reporting",
    "cancelled", "reboot", "announcement soon",
    "netflix", "remake", "reveal", "fake",
    "I heard", "my uncle works at", "trust me bro"
]

def is_fake_candidate(text):
    if not text: return False
    text = text.lower()
    return any(k in text for k in KEYWORDS)

def fetch_posts():
    results = []
    for sub in SUBREDDITS:
        print(f"[SCRAPE] r/{sub}")
        params = {"subreddit": sub, "size": 500, "sort": "desc"}
        r = requests.get(BASE, params=params)
        for p in r.json().get("data", []):
            t = (p.get("title") or "") + " " + (p.get("selftext") or "")
            if is_fake_candidate(t):
                results.append({
                    "title": p.get("title", ""),
                    "text": p.get("selftext", ""),
                    "source": "reddit",
                    "subreddit": sub,
                    "url": f"https://reddit.com{p.get('permalink','')}",
                    "label": "fake"
                })
        sleep(1)
    return results

def main():
    df = pd.DataFrame(fetch_posts())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"[OK] {len(df)} fake candidates saved → {OUT}")

if __name__ == "__main__":
    main()

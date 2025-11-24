import requests
import pandas as pd
from pathlib import Path
from time import sleep
from tqdm import tqdm

SUBREDDITS = [
    "AnimeLeaks",
    "AnimeRumors",
    "Animenews",
    "anime",
    "Animemes",
    "AnimeSuggest",
    "AnimeNewsAndFacts",
]

POSTS_PER_SUB = 400
BASE_URL = "https://api.pullpush.io/reddit/search/submission/"

OUTPUT = Path("../NekoNews/data/rumors/reddit_rumors.csv")

KEYWORDS = [
    "leak", "rumor", "confirm", "confirmed",
    "fake", "true", "spoiler",
    "announcement", "renewed", "cancelled"
]

def is_relevant(text):
    low = text.lower()
    return any(k in low for k in KEYWORDS)

def fetch_submissions(subreddit: str, limit: int = 400):
    rows = []
    params = {
        "subreddit": subreddit,
        "size": 100,
        "sort": "desc",
        "sort_type": "created_utc",
    }

    fetched = 0
    last_created = None

    with tqdm(total=limit, desc=f"r/{subreddit}", unit="post") as pbar:
        while fetched < limit:
            if last_created is not None:
                params["before"] = last_created

            try:
                resp = requests.get(BASE_URL, params=params, timeout=25)
            except:
                break

            if resp.status_code != 200:
                break

            data = resp.json().get("data", [])
            if not data:
                break

            for post in data:
                title = post.get("title") or ""
                text = post.get("selftext") or ""

                if not title and not text:
                    continue

                combined = f"{title} {text}"
                if not is_relevant(combined):
                    continue

                rows.append({
                    "title": title,
                    "text": text[:1000],
                    "subreddit": subreddit,
                    "url": f"https://reddit.com{post.get('permalink','')}",
                    "ups": post.get("ups", 0),
                    "num_comments": post.get("num_comments", 0),
                    "created_utc": post.get("created_utc", 0),
                    "label": "rumor"
                })

                fetched += 1
                last_created = post.get("created_utc")
                pbar.update(1)

                if fetched >= limit:
                    break

            sleep(1)

    print(f"[INFO] DONE → r/{subreddit} = {fetched} relevant posts")
    return rows


def main():
    all_rows = []

    print("\n=== Reddit rumor scraping (improved) ===\n")
    for sub in SUBREDDITS:
        all_rows.extend(fetch_submissions(sub, POSTS_PER_SUB))

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["title","text"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"\n[OK] Saved {len(df)} rumor samples → {OUTPUT}\n")


if __name__ == "__main__":
    main()

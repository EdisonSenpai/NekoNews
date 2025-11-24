import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm

BASE_URL = "https://api.pullpush.io/reddit/search/submission/"
OUTPUT = Path("../NekoNews/data/raw/reddit_real.csv")

SUBREDDITS = ["anime", "Animenews", "AnimeLeaks"]

def fetch_real(limit=600):
    rows = []
    params = {
        "size": 100,
        "sort": "desc",
        "sort_type": "created_utc",
    }

    with tqdm(total=limit, desc="Reddit Real News") as bar:
        for sub in SUBREDDITS:
            params["subreddit"] = sub
            fetched = 0
            last = None

            while fetched < limit // len(SUBREDDITS):
                if last:
                    params["before"] = last

                resp = requests.get(BASE_URL, params=params)
                data = resp.json().get("data", [])

                if not data:
                    break

                for post in data:
                    title = post.get("title", "")
                    text = post.get("selftext", "")

                    # filter only clear news content
                    if len(title) > 15 and not text.startswith("[deleted]"):
                        rows.append({
                            "title": title,
                            "text": text,
                            "label": "real"
                        })
                        bar.update(1)
                        fetched += 1

                    last = post["created_utc"]
                    if len(rows) >= limit:
                        return rows

    return rows

def main():
    rows = fetch_real()
    df = pd.DataFrame(rows).drop_duplicates()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"[OK] Saved {len(df)} real news → {OUTPUT}")

if __name__ == "__main__":
    main()

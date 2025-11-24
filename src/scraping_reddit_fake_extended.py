import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from time import sleep

# ========================================================
# CONFIG
# ========================================================

OUTPUT = Path("../NekoNews/data/fake/reddit_fake_candidates.csv")

BASE_URL = "https://api.pullpush.io/reddit/search/submission/"
COMMENT_URL = "https://api.pullpush.io/reddit/search/comment/"

POSTS_PER_SUB = 90  # target per subreddit

SUBREDDITS = [
     # anime-specific fake news
    "OnePiece",
    "Naruto",
    "Boruto",
    "Bleach",
    "JujutsuKaisen",
    "DemonSlayer",
    "ChainsawMan",
    "AttackOnTitan",
    "MyHeroAcademia",
    "SpyxFamily",
    # rumor-heavy global anime subs
    "AnimeLeaks",
    "AnimeRumors",
    "AnimeSpoilers",
]

# Stronger fake-like markers
KEYWORDS = [
    "leak", "spoiler", "rumor", "fake", "unconfirmed", "leaked",
    "exclusive", "insider", "trust me", "source???", "not official",
    "confirmation soon", "secret", "allegedly", "report claims",
    "my uncle works at", "100% confirmed", "real??", "fake??",
]

# ========================================================
# HELPERS
# ========================================================

def is_fake_candidate(text):
    if not text:
        return False
    text = text.lower()
    return any(k in text for k in KEYWORDS)


def fetch_top_comment(post_id):
    params = {
        "link_id": post_id,
        "size": 1,
        "sort": "desc",
        "sort_type": "score"
    }

    try:
        resp = requests.get(COMMENT_URL, params=params, timeout=20)
        if resp.status_code != 200:
            return "", 0

        data = resp.json().get("data", [])
        if not data:
            return "", 0

        c = data[0]
        return (c.get("body") or "")[:800], c.get("score") or 0

    except Exception:
        return "", 0


def fetch_subreddit(subreddit, limit):
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
            except Exception:
                sleep(2)
                continue

            if resp.status_code == 429:
                sleep(3)
                continue

            if resp.status_code != 200:
                break

            data = resp.json().get("data", [])
            if not data:
                break

            for post in data:
                title = post.get("title") or ""
                text = post.get("selftext") or ""

                combined = (title + " " + text).strip()
                if not is_fake_candidate(combined):
                    continue

                post_id = post.get("id") or ""

                top_comment, top_comment_ups = fetch_top_comment(post_id)

                rows.append({
                    "title": title[:300],
                    "text": text[:1200],
                    "top_comment": top_comment,
                    "subreddit": subreddit,
                    "url": f"https://reddit.com{post.get('permalink','')}",
                    "ups": post.get("score") or 0,
                    "num_comments": post.get("num_comments") or 0,
                    "top_comment_ups": top_comment_ups,
                    "label": "fake"
                })

                fetched += 1
                last_created = post.get("created_utc")
                pbar.update(1)

                if fetched >= limit:
                    break

            sleep(1)

    return rows


# ========================================================
# MAIN
# ========================================================

def main():
    print("\n=== Reddit Fake Candidate Scraping EXTENDED ===\n")

    all_rows = []

    for sub in SUBREDDITS:
        rows = fetch_subreddit(sub, POSTS_PER_SUB)
        print(f"[OK] {len(rows)} collected from r/{sub}\n")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["title", "text"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"\n[OK] Saved {len(df)} fake candidates → {OUTPUT}\n")


if __name__ == "__main__":
    main()

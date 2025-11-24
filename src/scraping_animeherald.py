import feedparser
import pandas as pd
from pathlib import Path
import re

OUTPUT = Path("../NekoNews/data/real/real_animeherald.csv")
FEED_URL = "https://www.animeherald.com/feed/"

ANIME_KEYWORDS = [
    "One Piece", "Naruto", "Bleach", "Demon Slayer", "Jujutsu Kaisen",
    "Attack on Titan", "My Hero Academia", "Chainsaw Man", "Dragon Ball",
    "Tokyo Ghoul", "Re:Zero", "Black Clover", "Vinland Saga",
    "Mob Psycho 100", "Solo Leveling", "Spy x Family", "Dr. Stone",
    "Steins;Gate", "Fate", "Overlord", "Sword Art Online", "Fullmetal Alchemist"
]

def clean(text):
    return re.sub('<[^<]+?>', '', str(text)).strip()

def detect_anime(text):
    t = text.lower()
    for kw in ANIME_KEYWORDS:
        if kw.lower() in t:
            return kw
    return "unknown"

def main():
    print("\n=== Fetching AnimeHerald real news ===\n")

    feed = feedparser.parse(FEED_URL)
    rows = []

    for entry in feed.entries:
        title = clean(entry.get("title", ""))
        summary = clean(entry.get("summary", ""))
        link = entry.get("link", "")

        if not title or not link:
            continue

        anime = detect_anime(title + " " + summary)

        rows.append({
            "title": title,
            "text": summary,
            "url": link,
            "source": "AnimeHerald",
            "anime": anime,
            "label": "real"
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["title", "url"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"[OK] Saved {len(df)} → {OUTPUT}")
    print("\n[DIST] Anime distribution:")
    print(df["anime"].value_counts().head(20))


if __name__ == "__main__":
    main()

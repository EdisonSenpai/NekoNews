import feedparser
import pandas as pd
from pathlib import Path
import re

# =========================
# CONFIG
# =========================

OUTPUT_PATH = Path("../NekoNews/data/real/real_news.csv")

FEEDS = {
    "AnimeNewsNetwork": "https://www.animenewsnetwork.com/news/rss.xml",
    "AnimeCorner": "https://animecorner.me/feed/",
    "MyAnimeList": "https://myanimelist.net/news/rss",
    "OtakuUSA": "https://otakuusamagazine.com/feed/",
    "Anime Herald": "https://www.animeherald.com/feed/",
    "Honey's Anime": "https://honeysanime.com/feed/",
    "UK Anime Network": "https://uk-anime.net/rss"
}

ANIME_KEYWORDS = [
    "One Piece", "OP",
    "Naruto", "Boruto",
    "Bleach", "TYBW",
    "Demon Slayer", "Kimetsu no Yaiba", "KNY",
    "Jujutsu Kaisen", "JJK",
    "Attack on Titan", "AOT", "Shingeki no Kyojin",
    "My Hero Academia", "MHA", "BNHA",
    "Chainsaw Man", "CSM",
    "Dragon Ball", "DB", "DBZ", "DBS",
    "Tokyo Ghoul",
    "Re:Zero",
    "Black Clover",
    "Vinland Saga",
    "Mob Psycho 100",
    "Solo Leveling",
    "Spy x Family",
    "Dr. Stone",
    "Steins;Gate",
    "Fate",
    "Overlord",
    "Sword Art Online", "SAO",
    "Fullmetal Alchemist", "FMA",
]


# =========================
# HELPERS
# =========================

def clean_html(text):
    return re.sub('<[^<]+?>', '', str(text))

def detect_anime(text):
    text_low = text.lower()
    for keyword in ANIME_KEYWORDS:
        if keyword.lower() in text_low:
            return keyword
    return "unknown"


# =========================
# MAIN SCRAPER
# =========================

def fetch_feed(source, url):
    parsed = feedparser.parse(url)
    rows = []

    for entry in parsed.entries:
        title = clean_html(entry.get("title", "")).strip()
        summary = clean_html(entry.get("summary", "")).strip()

        # robustly extract a URL: feedparser entries can provide link as a string,
        # None, a list of dicts, or a dict with 'href'.
        link_val = entry.get("link", None)
        if not link_val:
            link_val = entry.get("links", None)

        link = ""
        # normalize lists/tuples by taking the first element
        if isinstance(link_val, (list, tuple)):
            first = link_val[0] if link_val else None
            if isinstance(first, dict):
                link = first.get("href", "") or ""
            elif isinstance(first, str):
                link = first
            else:
                # try to read 'href' from FeedParserDict-like objects, otherwise coerce
                href_get = getattr(first, "get", None)
                if callable(href_get):
                    try:
                        link = href_get("href", "") or ""
                    except Exception:
                        link = str(first) if first is not None else ""
                else:
                    link = str(first) if first is not None else ""
        elif isinstance(link_val, dict):
            link = link_val.get("href", "") or ""
        elif isinstance(link_val, str):
            link = link_val
        elif link_val is None:
            link = ""
        else:
            # fallback: coerce to string for unexpected types
            link = str(link_val)

        # ensure link is a string before calling strip
        if not isinstance(link, str):
            link = str(link) if link is not None else ""

        link = link.strip()

        if not title or not link:
            continue

        anime = detect_anime(title + " " + summary)

        rows.append({
            "title": title,
            "text": summary,
            "url": link,
            "source": source,
            "anime": anime,
            "label": "real"
        })

    return rows


def main():
    print("\n=== Fetching REAL anime news ===\n")

    all_rows = []

    for source, url in FEEDS.items():
        print(f"[INFO] Fetching from {source} ...")
        rows = fetch_feed(source, url)
        print(f"[OK] {len(rows)} collected\n")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["title", "url"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"[OK] Saved → {OUTPUT_PATH}")
    print("\n[DIST] Anime distribution:")
    print(df["anime"].value_counts().head(20))


if __name__ == "__main__":
    main()

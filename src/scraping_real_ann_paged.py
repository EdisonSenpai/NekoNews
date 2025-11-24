import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
import time
import random
import re

OUTPUT_PATH = Path("../NekoNews/data/real/real_ann_paged.csv")

PAGES = 20

ANIME_KEYWORDS = {
    "One Piece": ["one piece", "luffy", "op"],
    "Naruto": ["naruto", "boruto", "uzumaki"],
    "Bleach": ["bleach", "tybw"],
    "Demon Slayer": ["demon slayer", "kimetsu", "kny"],
    "Jujutsu Kaisen": ["jujutsu kaisen", "jjk", "gojo", "sukuna"],
    "Attack on Titan": ["attack on titan", "aot", "shingeki"],
    "My Hero Academia": ["my hero academia", "mha", "bnha"],
    "Chainsaw Man": ["chainsaw man", "csm"],
    "Dragon Ball": ["dragon ball", "db", "dbz", "goku"],
    "Tokyo Ghoul": ["tokyo ghoul"],
    "Re:Zero": ["re:zero"],
    "Black Clover": ["black clover"],
    "Vinland Saga": ["vinland saga"],
    "Mob Psycho 100": ["mob psycho"],
    "Solo Leveling": ["solo leveling"],
    "Spy x Family": ["spy x family"],
    "Dr. Stone": ["dr. stone"],
    "Steins;Gate": ["steins;gate"],
    "Fate": ["fate"],
    "Overlord": ["overlord"],
    "Sword Art Online": ["sao", "sword art online"],
    "Fullmetal Alchemist": ["fullmetal alchemist", "fma"],
}


def detect_anime(text):
    t = text.lower()
    for anime, keywords in ANIME_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return anime
    return "unknown"


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def fetch_page(page_number):
    url = f"https://www.animenewsnetwork.com/news/?page={page_number}"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=12)
    if resp.status_code != 200:
        print(f"[WARN] HTTP {resp.status_code} on page {page_number}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = soup.select("div.herald.box.news")

    rows = []
    for art in articles:
        title_tag = art.find("h3")
        summary_tag = art.find("div", class_="intro")

        title = clean_text(title_tag.get_text(strip=True)) if title_tag else ""
        summary = clean_text(summary_tag.get_text(strip=True)) if summary_tag else ""

        link_tag = art.find("a")
        link = link_tag.get("href") if link_tag else ""
        if link and not link.startswith("http"):
            link = "https://www.animenewsnetwork.com" + link

        if not title:
            continue

        anime = detect_anime(title + " " + summary)

        rows.append({
            "title": title,
            "text": summary,
            "url": link,
            "source": "AnimeNewsNetwork",
            "anime": anime,
            "label": "real"
        })

    return rows


def main():
    print("\n=== Fetching REAL anime news from ANN pagination ===\n")

    all_rows = []

    for page in range(PAGES):
        print(f"[INFO] Fetching page {page} ...")
        rows = fetch_page(page)
        print(f"[OK] {len(rows)} collected\n")
        all_rows.extend(rows)

        time.sleep(random.uniform(1.2, 2.4))  # avoid rate limiting

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["title", "url"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"[OK] Saved → {OUTPUT_PATH}\n")

    print("[DIST] Anime distribution:")
    print(df["anime"].value_counts().head(20))


if __name__ == "__main__":
    main()

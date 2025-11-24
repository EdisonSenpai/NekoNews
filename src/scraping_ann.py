import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from time import sleep

BASE_URL = "https://www.animenewsnetwork.com/"
OUTPUT = Path("../NekoNews/data/raw/ann_news.csv")

def fetch_ann_articles(pages=3):
    rows = []

    for page in range(1, pages+1):
        print(f"[INFO] Fetching ANN page {page}...")
        url = f"{BASE_URL}news/?page={page}"
        resp = requests.get(url)

        if resp.status_code != 200:
            print(f"[WARN] HTTP {resp.status_code}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("div.herald.box.news")

        for article in articles:
            headline = article.select_one("h3").get_text(strip=True)
            text = article.select_one("div.intro").get_text(strip=True) if article.select_one("div.intro") else ""

            rows.append({
                "title": headline,
                "text": text,
                "label": "real"
            })

        sleep(1)

    return rows


def main():
    news = fetch_ann_articles(pages=15)  # you can increase pages
    df = pd.DataFrame(news)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"[OK] Saved {len(df)} real news → {OUTPUT}")


if __name__ == "__main__":
    main()

import pandas as pd
import random
from pathlib import Path

OUTPUT = Path("../NekoNews/data/raw/fake_news.csv")

TEMPLATES = [
    "{anime} SEASON {num} CANCELLED due to {reason}",
    "BREAKING: {anime} returns in new reboot confirmed by {source}",
    "{anime} ANIME gets {platform}-only release, fans furious",
    "{anime} CREATOR secretly working on {spin_off}",
    "{anime} CONFIRMED crossover with {with_anime}",
    "{anime} ending CHANGED after controversy hits online",
    "{anime} rumored to be replaced by AI animation",
    "Shocking leak: {anime} to receive live-action remake at {platform}",
    "{anime} suspended in Japan due to extreme violence",
]

ANIME = [
    "One Piece", "Naruto", "Bleach", "Jujutsu Kaisen", "Demon Slayer",
    "Attack on Titan", "Chainsaw Man", "Dragon Ball", "Vinland Saga",
    "Spy x Family", "Black Clover", "Re:Zero", "Mob Psycho 100", "Solo Leveling",
    "Dr. Stone", "Steins;Gate", "Fullmetal Alchemist", "Tokyo Ghoul",
    "Hunter x Hunter", "Sailor Moon", "My Hero Academia"
]

REASONS = [
    "studio bankruptcy", "controversial themes", "legal disputes", "writer conflict",
    "decline in ratings", "low animation budget", "piracy issues"
]

PLATFORMS = [
    "Netflix", "Amazon Prime", "Disney+", "Crunchyroll", "YouTube"
]

SOURCES = [
    "insider source", "anonymous leaker", "exclusive report", "Twitter account"
]

SPINOFFS = [
    "prequel series", "OVA special", "movie franchise", "stage play adaptation"
]

ANIME_CROSS = [
    "Dragon Ball", "Naruto", "Bleach", "Chainsaw Man", "One Piece"
]


def generate_fake(n=500):
    rows = []
    for _ in range(n):
        anime = random.choice(ANIME)
        data = {
            "anime": anime,
            "num": random.randint(2, 15),
            "reason": random.choice(REASONS),
            "platform": random.choice(PLATFORMS),
            "spin_off": random.choice(SPINOFFS),
            "with_anime": random.choice(ANIME_CROSS),
            "source": random.choice(SOURCES),
        }
        template = random.choice(TEMPLATES)
        title = template.format(**data)

        rows.append({
            "title": title,
            "text": title + " (auto-generated fake news)",
            "label": "fake",
        })
    return rows


def main():
    rows = generate_fake(300)  # generates 300 varied fakes
    df = pd.DataFrame(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"[OK] Saved {len(df)} generated fake samples → {OUTPUT}")


if __name__ == "__main__":
    main()

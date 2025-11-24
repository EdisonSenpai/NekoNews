import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
import numpy as np

RAW_REAL = Path("../NekoNews/data/raw/real_news.csv")
OUT_REAL = Path("../NekoNews/data/raw/real_news_enriched.csv")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

CANONICAL_ANIME = [
    "One Piece", "Naruto", "Bleach", "Demon Slayer", "Jujutsu Kaisen",
    "Attack on Titan", "My Hero Academia", "Chainsaw Man", "Dragon Ball",
    "Tokyo Ghoul", "Re:Zero", "Black Clover", "Vinland Saga",
    "Mob Psycho 100", "Solo Leveling", "Spy x Family", "Dr. Stone", "Steins;Gate",
    "Fate", "Overlord", "Sword Art Online", "Fullmetal Alchemist"
]

THRESHOLD = 0.45


def main():
    print("\n=== Semantic UNKNOWN Anime Detector ===\n")

    df = pd.read_csv(RAW_REAL)

    print(f"[INFO] Loaded {len(df)} real news entries")

    unknown_df = df[df["anime"] == "unknown"].copy()
    known_df = df[df["anime"] != "unknown"].copy()

    print(f"[INFO] Unknown entries: {len(unknown_df)}")
    print(f"[INFO] Known entries: {len(known_df)}")

    print("[INFO] Encoding canonical anime names...")
    anime_embeddings = model.encode(CANONICAL_ANIME, convert_to_tensor=True)

    newly_assigned = 0
    total_unknown = len(unknown_df)

    print("\n[INFO] Processing unknown entries...\n")

    for i, (idx, row) in enumerate(unknown_df.iterrows()):
        text = (str(row["title"]) + " " + str(row["text"])).strip()
        text_emb = model.encode(text, convert_to_tensor=True)

        scores = util.cos_sim(text_emb, anime_embeddings)[0]
        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])
        best_anime = CANONICAL_ANIME[best_idx]

        if best_score >= THRESHOLD:
            unknown_df[idx, "anime"] = best_anime
            newly_assigned += 1
            print(f"[OK] {i+1}/{total_unknown} → {best_anime} ({best_score:.3f})")
        else:
            print(f"[SKIP] {i+1}/{total_unknown} (score {best_score:.3f})")

    final_df = pd.concat([known_df, unknown_df], ignore_index=True)

    OUT_REAL.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUT_REAL, index=False, encoding="utf-8")

    print(f"\n[OK] Saved enriched dataset → {OUT_REAL}")
    print(f"[OK] Newly assigned anime labels: {newly_assigned}")
    print(f"[OK] Remaining unknown: {len(final_df[final_df['anime']=='unknown'])}")

    print("\n[DIST] Updated anime distribution:")
    print(final_df["anime"].value_counts().head(20))


if __name__ == "__main__":
    main()

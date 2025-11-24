import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# PATHS
# =========================

REAL_INPUT = Path("../NekoNews/data/real/real_news_full.csv")
OUTPUT = Path("../NekoNews/data/real/real_news_enriched.csv")

# =========================
# SETTINGS
# =========================

SIM_THRESHOLD = 0.18   # optimized for short news text
TOP_N_FEATURES = 5000


# =========================
# MAIN
# =========================

def main():
    print("\n=== TF-IDF Semantic Enrichment ===\n")

    if not REAL_INPUT.exists():
        raise FileNotFoundError(f"Missing dataset: {REAL_INPUT}")

    df = pd.read_csv(REAL_INPUT)

    # Extract canonical anime names from dataset (excluding "unknown")
    canonical = sorted(
        df[df["anime"] != "unknown"]["anime"]
        .dropna()
        .astype(str)
        .unique()
    )

    print(f"[INFO] Canonical anime detected: {len(canonical)}")
    print(canonical, "\n")

    # Split dataset
    unknown_df = df[df["anime"] == "unknown"].copy()
    known_df = df[df["anime"] != "unknown"].copy()

    print(f"[INFO] Unknown entries: {len(unknown_df)}")
    print(f"[INFO] Known entries: {len(known_df)}\n")

    # Build TF-IDF model using canonical anime names as reference
    vectorizer = TfidfVectorizer(
        max_features=TOP_N_FEATURES,
        stop_words="english"
    )

    anime_embeddings = vectorizer.fit_transform(canonical)

    newly_assigned = 0

    # Process unknown rows and update directly on the DataFrame
    for idx, row in unknown_df.iterrows():
        text = (
            str(row["title"]) + " " +
            str(row["text"]) + " " +
            str(row["url"])
        ).strip()

        text_emb = vectorizer.transform([text])

        # Compute cosine similarity
        scores = cosine_similarity(text_emb, anime_embeddings)[0]

        best_idx = scores.argmax()
        best_score = scores[best_idx]
        best_anime = canonical[best_idx]

        if best_score >= SIM_THRESHOLD:
            # assign using the original index label
            unknown_df.loc[idx:idx, "anime"] = best_anime
            newly_assigned += 1

    # Merge back
    final_df = pd.concat([known_df, unknown_df], ignore_index=True)

    # Save enriched dataset
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUTPUT, index=False, encoding="utf-8")

    # Report results
    print(f"[OK] Saved enriched dataset → {OUTPUT}")
    print(f"[OK] Newly assigned: {newly_assigned}")
    print(f"[OK] Remaining unknown: {len(final_df[final_df['anime']=='unknown'])}")

    print("\n[DIST] Updated anime distribution:")
    print(final_df["anime"].value_counts().head(30))


if __name__ == "__main__":
    main()

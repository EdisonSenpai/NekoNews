# src/build_train_dataset.py

import pandas as pd
from pathlib import Path

# =========================
# PATHS
# =========================

REAL = Path("../NekoNews/data/real/real_news_enriched.csv")
RUMOR = Path("../NekoNews/data/rumors/reddit_rumors_full.csv")
FAKE = Path("../NekoNews/data/fake/reddit_fake_candidates.csv")

OUTPUT = Path("../NekoNews/data/models/train_master.csv")


# =========================
# LOADING HELPERS
# =========================

def load_df(path, label_name):
    if not path.exists():
        print(f"[ERROR] Missing file: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Normalize missing columns
    for col in ["title", "text", "anime"]:
        if col not in df.columns:
            df[col] = ""

    # Force label overwrite to avoid leftovers
    df["label"] = label_name

    # Add source tracking
    df["source"] = path.stem

    return df[["title", "text", "anime", "label", "source", "url"]]


# =========================
# MAIN
# =========================

def main():
    print("\n=== BUILDING TRAINING DATASET ===\n")

    real_df = load_df(REAL, "real")
    rumor_df = load_df(RUMOR, "rumor")
    fake_df = load_df(FAKE, "fake")

    combined = pd.concat([real_df, rumor_df, fake_df], ignore_index=True)

    # Remove empty entries
    combined = combined.dropna(subset=["title", "label"])

    # Remove duplicates
    before = len(combined)
    combined = combined.drop_duplicates(subset=["title", "text"], keep="first")
    after = len(combined)

    removed = before - after

    # Save final dataset
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"[OK] Saved → {OUTPUT}")
    print(f"[INFO] Total samples: {after}")
    print(f"[INFO] Removed duplicates: {removed}")

    print("\n[DIST] Label distribution:")
    print(combined["label"].value_counts())

    print("\n[DIST] Anime distribution (top 20):")
    print(combined["anime"].value_counts().head(20))


if __name__ == "__main__":
    main()

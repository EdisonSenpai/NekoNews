import pandas as pd
from pathlib import Path

# =========================
# CONFIG
# =========================

INPUT_FILES = [
    "../NekoNews/data/real/real_ann_paged.csv",
    "../NekoNews/data/real/real_animecorner.csv",
    "../NekoNews/data/real/real_otakuusa.csv",
    "../NekoNews/data/real/real_animeherald.csv",
    "../NekoNews/data/real/real_comicbook.csv",
    "../NekoNews/data/real/real_honeysanime.csv",
]

OUTPUT_FILE = Path("../NekoNews/data/real/real_news_full.csv")


# =========================
# MAIN
# =========================

def load_df(path):
    try:
        df = pd.read_csv(path)
        print(f"[LOAD] {path}  → {len(df)} rows")
        return df
    except FileNotFoundError:
        print(f"[SKIP] {path} (not found)")
        return pd.DataFrame()


def main():
    print("\n=== MERGING REAL NEWS SOURCES ===\n")

    dfs = [load_df(p) for p in INPUT_FILES]

    combined = pd.concat(dfs, ignore_index=True)

    # Remove entries with missing required fields
    combined = combined.dropna(subset=["title", "url"])

    # Remove duplicates based on title + url
    before = len(combined)
    combined = combined.drop_duplicates(subset=["title", "url"], keep="first")
    after = len(combined)

    print(f"\n[INFO] Before dedupe: {before}")
    print(f"[INFO] After dedupe:  {after}")
    print(f"[INFO] Removed:        {before - after}")

    # Save final dataset
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"\n[OK] Saved merged dataset → {OUTPUT_FILE}\n")

    # Show distribution of anime
    print("[DIST] Anime distribution:")
    print(combined["anime"].value_counts().head(20))


if __name__ == "__main__":
    main()

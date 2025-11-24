import pandas as pd
import re
from pathlib import Path

RAW_PATH = Path("../NekoNews/data/raw")
OUT_PATH = Path("../NekoNews/data/processed/neko_dataset_full.csv")

FILES = [
    "neko_dataset_starter.csv",
    "reddit_rumors.csv",
    "reddit_real.csv",
    "real_news.csv",
    "ann_news.csv",
    "fake_news.csv",
]

def clean_text(text: str) -> str:
    """Normalize text for training: lowercase, no URLs or special chars."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1000]


def load_dataset(csv_file: str) -> pd.DataFrame:
    path = RAW_PATH / csv_file
    if not path.exists() or path.stat().st_size == 0:
        print(f"[WARN] Skipping missing or empty: {csv_file}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        if df.empty or "text" not in df.columns or "label" not in df.columns:
            print(f"[WARN] Invalid or empty format -> skipping: {csv_file}")
            return pd.DataFrame()
        print(f"[LOAD] {csv_file}")
        df = df.dropna(subset=["label", "title", "text"])
        return df
    except Exception as e:
        print(f"[ERROR] Failed to read {csv_file}: {e}")
        return pd.DataFrame()


def main():
    print("\n=== Preprocessing & dataset assembly ===\n")

    all_rows = []
    for f in FILES:
        df = load_dataset(f)
        if len(df) > 0:
            print(f" → loaded {len(df)} rows")
            all_rows.append(df)

    if not all_rows:
        print("[FATAL] No raw data found.")
        return

    df = pd.concat(all_rows, ignore_index=True)
    print(f"\n[INFO] Combined size = {len(df)}")

    # Show label distribution BEFORE cleaning
    print("\n[INFO] Initial class distribution:")
    print(df["label"].value_counts())

    # dedupe
    df = df.drop_duplicates(subset=["title", "text"])
    print(f"[INFO] After dedupe = {len(df)}")

    # clean
    df["clean_text"] = df["text"].apply(clean_text)

    # drop rows where cleaning produced empty text
    df = df[df["clean_text"].str.strip() != ""]
    print(f"[INFO] After text cleanup = {len(df)}")

    # shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8")

    print("\n[OK] Final dataset saved →", OUT_PATH)
    print("\n[OK] Final class distribution:")
    print(df["label"].value_counts())

    if df["label"].value_counts().min() < 100:
        print("\n[WARN] ⚠️ Some classes have very few samples. Consider collecting more data.")


if __name__ == "__main__":
    main()

import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import RandomOverSampler
import scipy.sparse as sp
import joblib

DATASET = Path("../NekoNews/data/models/train_master.csv")
MODEL_DIR = Path("../NekoNews/data/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

FAKE_KEYWORDS = [
    "trust me", "uncle works", "leaked", "exclusive",
    "insider", "fake", "100% real", "confirmed leak",
    "trust me bro", "my uncle works", "secret source"
]

def fake_signal(text):
    t = text.lower()
    return int(any(k in t for k in FAKE_KEYWORDS))

def main():
    print("\n=== TRAINING MODEL (TF-IDF + Fake Feature + Oversampling) ===\n")

    df = pd.read_csv(DATASET)

    df["content"] = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()

    label_encoder = LabelEncoder()
    df["label_encoded"] = label_encoder.fit_transform(df["label"])

    X_train, X_test, y_train, y_test = train_test_split(
        df["content"],
        df["label_encoded"],
        test_size=0.2,
        stratify=df["label_encoded"],
        random_state=42
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=50000,
        ngram_range=(1, 2)
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    fake_train = sp.csr_matrix([[fake_signal(t)] for t in X_train])
    fake_test = sp.csr_matrix([[fake_signal(t)] for t in X_test])

    X_train_vec = sp.hstack([X_train_vec, fake_train])
    X_test_vec = sp.hstack([X_test_vec, fake_test])

    ros = RandomOverSampler()
    X_train_vec, y_train = ros.fit_resample(X_train_vec, y_train)[:2]

    clf = LogisticRegression(max_iter=2000, random_state=42)
    clf.fit(X_train_vec, y_train)

    joblib.dump(vectorizer, MODEL_DIR / "vectorizer.pkl")
    joblib.dump(clf, MODEL_DIR / "classifier.pkl")
    joblib.dump(label_encoder, MODEL_DIR / "label_encoder.pkl")

    print("[OK] Model trained and saved!")
    print(f"[OK] Train samples: {len(X_train)}")
    print(f"[OK] Test samples:  {len(X_test)}")

if __name__ == "__main__":
    main()

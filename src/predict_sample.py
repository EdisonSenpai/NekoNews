import joblib
import scipy.sparse as sp
from pathlib import Path

MODEL_DIR = Path("../NekoNews/data/models")

def fake_signal(text):
    FAKE_KEYWORDS = [
        "trust me", "uncle works", "leaked", "exclusive",
        "insider", "fake", "100% real", "confirmed leak",
        "trust me bro", "my uncle works", "secret source"
    ]
    t = text.lower()
    return int(any(k in t for k in FAKE_KEYWORDS))

def main():
    vectorizer = joblib.load(MODEL_DIR / "vectorizer.pkl")
    clf = joblib.load(MODEL_DIR / "classifier.pkl")
    label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")

    while True:
        q = input("\nEnter text to classify (or 'exit'): ")
        if q.lower() == "exit":
            break

        vec = vectorizer.transform([q])
        fake_flag = sp.csr_matrix([[fake_signal(q)]])
        vec = sp.hstack([vec, fake_flag])

        proba = clf.predict_proba(vec)[0]
        labels = label_encoder.classes_

        fake_p, real_p, rumor_p = proba

        if fake_p > 0.52:
            label = "fake"
        elif real_p > 0.50:
            label = "real"
        else:
            label = "rumor"

        print(f"Prediction: {label}")
        print(f"Probabilities: fake={fake_p:.3f}, real={real_p:.3f}, rumor={rumor_p:.3f}")

if __name__ == "__main__":
    main()

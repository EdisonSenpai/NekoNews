import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score
)
import joblib
import scipy.sparse as sp
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

DATASET = Path("../NekoNews/data/models/train_master.csv")
MODEL_DIR = Path("../NekoNews/data/models")
OUTPUT_IMG = MODEL_DIR / "confusion_matrix.png"

FAKE_KEYWORDS = [
    "trust me", "uncle works", "leaked", "exclusive",
    "insider", "fake", "100% real", "confirmed leak",
    "trust me bro", "my uncle works", "secret source"
]

def fake_signal(text):
    return int(any(k in text.lower() for k in FAKE_KEYWORDS))


def main():
    print("\n==============================")
    print("      MODEL EVALUATION")
    print("==============================\n")

    # Load dataset
    df = pd.read_csv(DATASET)
    df["content"] = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()

    # Load components
    vectorizer = joblib.load(MODEL_DIR / "vectorizer.pkl")
    clf = joblib.load(MODEL_DIR / "classifier.pkl")
    label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")

    # Vectorize full corpus
    X_vec = vectorizer.transform(df["content"])
    fake_col = sp.csr_matrix([[fake_signal(t)] for t in df["content"]])
    X_vec = sp.hstack([X_vec, fake_col])

    # Encode true labels
    y_true = label_encoder.transform(df["label"])
    y_pred = clf.predict(X_vec)

    # ===========================
    # CONFUSION MATRIX
    # ===========================
    cm = confusion_matrix(y_true, y_pred)
    labels = label_encoder.classes_
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)

    # ===========================
    # METRICS
    # ===========================
    accuracy = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    weighted_f1 = f1_score(y_true, y_pred, average="weighted")

    print("\n=== GLOBAL METRICS ===\n")
    print(f"Accuracy:     {accuracy:.4f}")
    print(f"Macro F1:     {macro_f1:.4f}")
    print(f"Weighted F1:  {weighted_f1:.4f}\n")

    print("\n=== CLASSIFICATION REPORT ===\n")
    print(classification_report(y_true, y_pred, target_names=labels))

    # ===========================
    # PLOT CONFUSION MATRIX
    # ===========================

    plt.figure(figsize=(8, 6))

    neon_cmap = sns.color_palette(["#ff2ea6", "#a94bff", "#4effd2"], as_cmap=True)

    sns.heatmap(
        cm_df,
        annot=True,
        fmt="d",
        cmap=neon_cmap,
        linewidths=1,
        linecolor="#1a1028",
        cbar=False
    )

    plt.title("Confusion Matrix - NekoNews Model", fontsize=16, color="#ff89e6")
    plt.xlabel("Predicted Label", fontsize=12, color="#d6c9ff")
    plt.ylabel("True Label", fontsize=12, color="#d6c9ff")
    plt.xticks(color="#ffffff")
    plt.yticks(color="#ffffff")

    plt.tight_layout()
    plt.savefig(OUTPUT_IMG, dpi=300, transparent=True)
    plt.close()

    print(f"\nConfusion matrix saved to: {OUTPUT_IMG}\n")
    print("Evaluation complete.\n")


if __name__ == "__main__":
    main()

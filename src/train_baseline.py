import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

DATASET_PATH = Path("../NekoNews/data/processed/neko_dataset_full.csv")
MODEL_PATH = Path("../NekoNews/models/baseline_model.pkl")
VECTORIZER_PATH = Path("../NekoNews/models/tfidf_vectorizer.pkl")


def main():
    print("[INFO] Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    print(f"[INFO] Dataset shape: {df.shape}")

    X = df['clean_text']
    y = df['label']

    # Split
    print("[INFO] Splitting into train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    # TF-IDF Vectorizer
    print("[INFO] Training TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=10000,
        ngram_range=(1,2),
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Model
    print("[INFO] Training Logistic Regression model...")
    model = LogisticRegression(max_iter=300)
    model.fit(X_train_vec, y_train)

    # Evaluation
    print("\n=== Classification Report ===")
    y_pred = model.predict(X_test_vec)
    print(classification_report(y_test, y_pred))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d',
                xticklabels=list(map(str, model.classes_)),
                yticklabels=list(map(str, model.classes_)),
                cmap="Blues")
    plt.title("Confusion Matrix - Logistic Regression")
    plt.show()

    # Save model + vectorizer
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"[OK] Model saved → {MODEL_PATH}")
    print(f"[OK] Vectorizer saved → {VECTORIZER_PATH}")


if __name__ == "__main__":
    main()

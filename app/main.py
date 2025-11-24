from flask import Flask, render_template, request
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import scipy.sparse as sp
from flask import send_from_directory

# =========================
# PATH CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "data" / "models"

DATASET_PATH = MODEL_DIR / "train_master.csv"
MODEL_PATH = MODEL_DIR / "classifier.pkl"
VECTORIZER_PATH = MODEL_DIR / "vectorizer.pkl"
LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"


# =========================
# FLASK APP
# =========================
app = Flask(__name__)

# =========================
# LOAD MODEL + DATA
# =========================
df = pd.read_csv(DATASET_PATH)
classifier = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

#print("=== DEBUG MODEL CHECK ===")
#print("Vectorizer features:", len(vectorizer.get_feature_names_out()))
#print("Classifier expects:", classifier.n_features_in_)
#print("Model path:", MODEL_PATH)
#print("Vectorizer path:", VECTORIZER_PATH)
#print("Label encoder path:", LABEL_ENCODER_PATH)

FAKE_KEYWORDS = [
    "trust me", "uncle works", "leaked", "exclusive",
    "insider", "fake", "100% real", "confirmed leak",
    "trust me bro", "my uncle works", "secret source"
]

def fake_signal(text):
    t = text.lower()
    return int(any(k in t for k in FAKE_KEYWORDS))

# build searchable content
df["content"] = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()
corpus_vec = vectorizer.transform(df["content"])

fake_values = [fake_signal(t) for t in df["content"]]
fake_flags = sp.csr_matrix([[v] for v in fake_values])

corpus_augmented = sp.csr_matrix(sp.hstack([corpus_vec, fake_flags]))


LABELS = list(label_encoder.classes_)

# =========================
# PREDICTION FUNCTION
# ========================


def predict_with_similar(text, top_k=5):
    # vectorize input
    X_vec = vectorizer.transform([text])

    # append fake_signal feature
    fake_value = fake_signal(text)
    fake_feat = sp.csr_matrix([[fake_value]])
    X = sp.csr_matrix(sp.hstack([X_vec, fake_feat]))

    # predict label
    y_pred = classifier.predict(X)[0]
    label = label_encoder.inverse_transform([y_pred])[0]

    # probability score
    proba = classifier.predict_proba(X)[0]
    confidence = float(max(proba))

    # === similarity search ===
    sim = cosine_similarity(X, corpus_augmented)[0]
    top_idx = sim.argsort()[-top_k:][::-1]

    similar_rows = df.iloc[top_idx][["title", "label", "url"]].to_dict("records")

    return label, confidence, similar_rows


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    def safe_preview(row):
        raw = row.get("text")
        if isinstance(raw, float):
            raw = ""
        if not raw:
            raw = row.get("content") or ""
        return str(raw).strip()[:300]


    real_news = [
        {"title": r["title"], "text": safe_preview(r), "url": r.get("url", "#")}
        for _, r in df[df["label"] == "real"].head(5).iterrows()
    ]

    rumor_news = [
        {"title": r["title"], "text": safe_preview(r), "url": r.get("url", "#")}
        for _, r in df[df["label"] == "rumor"].head(5).iterrows()
    ]

    fake_news = [
        {"title": r["title"], "text": safe_preview(r), "url": r.get("url", "#")}
        for _, r in df[df["label"] == "fake"].head(5).iterrows()
    ]


    return render_template(
        "home.html",
        active_page="home",
        real_news=real_news,
        rumor_news=rumor_news,
        fake_news=fake_news,
    )

@app.route("/search", methods=["GET", "POST"])
def search():
    query = ""
    result = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            label, conf, similar = predict_with_similar(query)
            result = {
                "label": label,
                "confidence": round(conf, 3),
                "similar": similar,
            }

    return render_template("search.html", active_page="search", query=query, result=result)

@app.route("/browse", methods=["GET", "POST"])
def browse():
    anime = ""
    results = []
    stats = None

    if request.method == "POST":
        anime = request.form.get("anime", "").strip()
        if anime:
            mask = (
                df["title"].astype(str).str.contains(anime, case=False, na=False)
                | df["content"].astype(str).str.contains(anime, case=False, na=False)
            )

            subset = df[mask][["title", "label", "url"]]
            results = subset.to_dict("records")


            counts = subset["label"].value_counts()
            stats = {
                "real": int(counts.get("real", 0)),
                "rumor": int(counts.get("rumor", 0)),
                "fake": int(counts.get("fake", 0)),
            }

    return render_template(
        "browse.html",
        active_page="browse",
        anime=anime,
        results=results,
        stats=stats,
    )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        app.static_folder or 'static',
        'img/favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


if __name__ == "__main__":
    app.run(debug=True)

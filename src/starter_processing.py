import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("../NekoNews/data/raw/neko_dataset_starter.csv")

# Define cleaning function
def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df['clean_text'] = df['text'].apply(clean_text)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    df['clean_text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1,2))
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Naive Bayes Classifier
model_nb = MultinomialNB()
model_nb.fit(X_train_vec, y_train)

pred_nb = model_nb.predict(X_test_vec)

print("Naive Bayes Classification Report:")
print(classification_report(y_test, pred_nb))

# Confusion Matrix

cm = confusion_matrix(y_test, pred_nb)
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=model_nb.classes_.astype(str).tolist(),
    yticklabels=model_nb.classes_.astype(str).tolist()
)
plt.title("Confusion Matrix - Naive Bayes")
plt.show()

print(df['label'].value_counts())
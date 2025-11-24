import joblib

vec = joblib.load("data/models/vectorizer.pkl")
clf = joblib.load("data/models/classifier.pkl")

real_vec_features = len(vec.get_feature_names_out())

print("Real vectorizer feature count:", real_vec_features)
print("Classifier n_features:", clf.n_features_in_)

from __future__ import annotations
import csv, json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
GUIDANCE = json.loads((ROOT/'data'/'symptom_guidance.json').read_text())

class IntentRouter:
    def __init__(self):
        rows = list(csv.DictReader((ROOT/'data'/'intents.csv').open()))
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1,2), lowercase=True, min_df=1)),
            ('clf', LogisticRegression(max_iter=1000, random_state=42)),
        ])
        self.model.fit([r['text'] for r in rows], [r['intent'] for r in rows])
    def predict(self, text: str) -> str:
        return str(self.model.predict([text])[0])

class SymptomRetriever:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), lowercase=True)
        docs = [' '.join([x['name'], x['summary'], *x['keywords']]) for x in GUIDANCE]
        self.matrix = self.vectorizer.fit_transform(docs)
    def search(self, text: str, limit: int = 2):
        q = self.vectorizer.transform([text])
        scores = (self.matrix @ q.T).toarray().ravel()
        ranked = scores.argsort()[::-1]
        return [(GUIDANCE[i], float(scores[i])) for i in ranked[:limit] if scores[i] > 0.05]

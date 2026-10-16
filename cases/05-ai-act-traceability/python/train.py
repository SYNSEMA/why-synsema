"""The same training in Python, with the usual traceability practice: a `read()` helper that records every file it
reads, with its sha256, in a manifest. The team uses it for the documented data; the extra read goes straight to
pandas, as it happens in real life. Run from the repository root:
    uv run --with pandas --with scikit-learn python cases/05-ai-act-traceability/python/train.py"""
import hashlib, json, pathlib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

D = pathlib.Path("cases/05-ai-act-traceability")
MANIFEST = []

def read(path):
    """Records the read in the manifest. It only works if EVERYONE uses it, every time."""
    b = pathlib.Path(path).read_bytes()
    MANIFEST.append({"file": pathlib.Path(path).as_posix(), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    return pd.read_csv(path)

labels = read(D / "data" / "teacher_labels.csv")
labels = labels[labels["teacher"].notna()].sample(frac=1, random_state=11)
cut = int(len(labels) * 0.8)
train, test = labels.iloc[:cut], labels.iloc[cut:]

extra = pd.read_csv(D / "data" / "extra_data.csv")       # <- the off-the-books read: it does not go through read()

X = pd.concat([train[["title", "teacher"]], extra])
vec = CountVectorizer(token_pattern=r"[a-z]{3,}", lowercase=True)
m = MultinomialNB().fit(vec.fit_transform(X["title"]), X["teacher"])
acc = (m.predict(vec.transform(test["title"])) == test["truth"]).mean()
out = D / "results" / "python_manifest.json"
out.write_text(json.dumps({"n_train": len(X), "accuracy_vs_truth": round(float(acc), 4), "data": MANIFEST}, indent=1), encoding="utf-8")
print(f"trained on {len(X)} rows (including {len(extra)} from extra_data.csv) · accuracy {acc:.4f}")
print(f"the manifest declares {len(MANIFEST)} file(s): {[d['file'] for d in MANIFEST]}")

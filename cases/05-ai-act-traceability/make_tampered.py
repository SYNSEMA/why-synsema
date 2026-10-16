"""Copy the training data to tampered/ and flip ONE label, to check that verify.syn notices.
    python cases/05-ai-act-traceability/make_tampered.py
    synsema run cases/05-ai-act-traceability/verify.syn -- cases/05-ai-act-traceability/tampered"""
import pathlib, shutil
D = pathlib.Path("cases/05-ai-act-traceability")
(D / "tampered").mkdir(exist_ok=True)
for f in (D / "data").glob("*.csv"):
    shutil.copy(f, D / "tampered" / f.name)
p = D / "tampered" / "teacher_labels.csv"
lines = p.read_text(encoding="utf-8").splitlines()
row = lines[10]
lines[10] = row.replace(",fiction,", ",nonfiction,", 1) if ",fiction," in row else row.replace(",nonfiction,", ",fiction,", 1)
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("tampered/ ready: one label changed in teacher_labels.csv (row 10)")

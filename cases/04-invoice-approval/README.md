# 4 · Which invoices can be paid without a human

**Question:** if the model extracts an invoice correctly, is its confidence enough to pay it without review?

60 synthetic invoices from fictional companies (`data/generate_invoices.py`, seed 21), as OCR-like text with their ground truth. 28 carry real difficulties: OCR noise, ambiguous dates, foreign currency, discounts, hand-corrected totals and duplicates. 7 must be seen by a person even when read correctly: the 2 duplicates and the 5 hand-corrected totals.

DeepSeek extracts the fields and reports its own confidence; an arithmetic check validates the totals; Jev (TypeSafe's calibrated judge) answers four questions about the document and the extraction in one call. Anything not approved waits in `approve`, Synsema's human gate.

## Run

```bash
python cases/04-invoice-approval/data/generate_invoices.py
synsema run cases/04-invoice-approval/process.syn                  # → results/results.json, results/rules.json
SYNSEMA_HUMAN_WEBHOOK=http://127.0.0.1:8105/channel SYNSEMA_HUMAN_PUBLIC_URL=http://localhost:8105 \
  synsema serve cases/04-invoice-approval/review.syn               # approval queue on http://localhost:8105
```

## Result (results/rules.json)

| Rule | Approved alone | Caught the 7 to review | Paid unreviewed | False alarms |
| --- | --- | --- | --- | --- |
| LLM's own confidence ≥ 0.9 | 60 | **0 of 7** | all 7 | 0 |
| Arithmetic check only | 60 | **0 of 7** | all 7 | 0 |
| Jev (≥ 0.85 per field, ambiguous < 0.5) | 46 | **7 of 7** | none | 7 (all with OCR noise) |

Extraction itself was 60/60 correct.

## The human gate (tested)

| Test | Result |
| --- | --- |
| `POST /approvals/{id}` with a fake token | 403, the approval keeps waiting |
| Reject with the single-use link | 200, decision recorded |
| Reuse the same link | 404 |
| Run without a terminal (CI, an agent) | denied immediately |

## What it does not solve

- Synthetic text invoices: with real PDFs or photos, extraction will not be perfect.
- Calibrated judgment does not replace business rules: a copy of an invoice already paid can score under the threshold; `review.syn` adds the rule "same supplier and number already processed".
- Thresholds (0.85 and 0.5) were fixed before measuring; with real data, calibrate them on a separate set.

# 5 · Training data you cannot hide

**Question:** if someone adds data to training without documenting it, does it get recorded?

The same genre classifier trained twice, with the same realistic slip: besides the documented `teacher_labels.csv`, someone loads `extra_data.csv` (80 rows) directly.

- **Python** (`python/train.py`): the usual practice, a `read()` helper that records every file with its sha256 in a manifest. The extra read skips it.
- **Synsema** (`train.syn`): the engine records every read in the lineage; `receipt()` signs it with ed25519 (W3C Data Integrity, `did:key` issuer) and a data sheet is generated from it.

## Run

```bash
python -c "import secrets; print(secrets.token_hex(32))" > cases/05-ai-act-traceability/signing_key.hex   # test key, ignored by git
RECEIPT_SEED=$(tr -d '\r\n' < cases/05-ai-act-traceability/signing_key.hex) synsema run cases/05-ai-act-traceability/train.syn
synsema run cases/05-ai-act-traceability/verify.syn                                     # needs no private key
uv run --with pandas --with scikit-learn python cases/05-ai-act-traceability/python/train.py
```

You can verify the committed receipt right after cloning, without training: `synsema run cases/05-ai-act-traceability/verify.syn`.

## Result

| | Python, manual manifest | Synsema, lineage + receipt |
| --- | --- | --- |
| Training rows | 498 (418 + 80 extra) | 498 (418 + 80 extra) |
| Files the record lists | **1** | **2** |
| Who writes the record | the program, if it remembers | the engine |
| Signature | none | ed25519 |

Tamper tests with `verify.syn`:

| Case | Result |
| --- | --- |
| Everything as it was | VERIFIED |
| Change one label (`python cases/05-ai-act-traceability/make_tampered.py`, then `verify.syn -- cases/05-ai-act-traceability/tampered`) | NOT VERIFIED: the file changed |
| Edit `results/receipt.json` to hide `extra_data.csv` | NOT VERIFIED: invalid signature |

## What it does not solve

- The lineage records what the program reads, not what it writes: the model hash is added to the signed result by hand.
- Proving a file did not change does not prove it was lawful to use (license, consent).
- The signing key here is a test key. In production it lives in a secret manager and its DID is published.

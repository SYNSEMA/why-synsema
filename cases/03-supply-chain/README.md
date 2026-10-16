# 3 · What a dependency can do

**Question:** your ETL imports a helper module. What can that module do with your program's permissions?

A real ETL written twice: daily weather for five cities from Open-Meteo to Parquet plus a CSV summary. Both versions produce the same numbers. Each imports a helper (`python/helpers.py`, `synsema/helpers.syn`) that stands for any dependency and reports what it could do (booleans only).

## Run

```bash
synsema run       cases/03-supply-chain/synsema/etl.syn
synsema code caps cases/03-supply-chain/synsema/etl.syn            # static review: what each part needs, what is missing
uv run --with-requirements cases/03-supply-chain/python/requirements.txt python cases/03-supply-chain/python/etl.py cases/03-supply-chain/results
uvx pip-audit -r cases/03-supply-chain/python/requirements.txt
```

## Result

| | Python | Synsema |
| --- | --- | --- |
| Packages, direct and transitive | 14 | 0 |
| Third-party code on disk | 169 MB · 2,156 `.py` files · 99 native binaries | none |
| Known vulnerabilities (`pip-audit`, Oct 2026) | 3 advisories in requests, pyarrow, python-dotenv | nothing to audit |
| The imported module can read `.env` | yes | no |
| The imported module can reach an undeclared host | yes | no |
| Know before running what it touches | no | yes: `code caps` flags `MISSING file.read("./.env")` and `MISSING net("example.com")` |
| Run time | 6.8–9.3 s (1.3 s importing; cities in sequence) | 1.4 s (cities in parallel) |

## What it does not solve

- The pip-audit advisories go away by upgrading; that continuous upkeep is the point.
- A local Synsema module inherits the program's capabilities: if the program declares too much, so does the module.
- The run-time gap is mostly sequential versus parallel downloads, not the language.

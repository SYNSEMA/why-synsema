# 2 · Running the code an LLM wrote

**Question:** when an LLM writes the code that answers a question about your data, what can that code do once you run it?

Ten questions over ten scattered files (CSV, Parquet, JSONL, see [`DATA.md`](../../DATA.md)). The same model (`deepseek-flash`, temperature 0) and the same schema for three variants, each with up to three attempts and the error fed back:

- **Synsema:** the model writes Synsema; `run_program` runs it as a child process under a ceiling of `stdout` + read-only access to `data/`.
- **Python:** the model writes pandas; it runs with `exec` in-process (what most products do) and again inside Docker with no network.
- **SQL:** the model writes one DuckDB query; it runs in-process.

## Run

```bash
docker build -t why-synsema-python:1 -f cases/02-llm-written-analytics/docker/python.Dockerfile cases/02-llm-written-analytics/docker
synsema run cases/02-llm-written-analytics/dump_schema.syn                       # the schema all three variants see
uv run --with polars python cases/02-llm-written-analytics/comparison/truth.py   # correct answers, computed by hand
uv run --with pandas --with duckdb --with pyarrow python cases/02-llm-written-analytics/comparison/compare.py
uv run --with duckdb --with pandas python cases/02-llm-written-analytics/comparison/security.py
synsema run cases/02-llm-written-analytics/ask.syn -- "Which city had the most rain?"
```

## Result (results/results.json)

| | Synsema | Python / pandas | SQL / DuckDB |
| --- | --- | --- | --- |
| Correct answers | 10/10 | 10/10 | 10/10 |
| Attempts (minimum 10) | 11 | 10 | 10 |
| Run time, median | **34 ms, sandboxed** | 29 ms unsandboxed · 1,987 ms in Docker | 29 ms unsandboxed |

## What the generated code can do (results/security.json)

| Test | Python exec | DuckDB default | DuckDB restricted | Synsema run_program |
| --- | --- | --- | --- | --- |
| Read `.env` | allowed | allowed | blocked | blocked |
| Reach the network | allowed | allowed | blocked | blocked |
| Overwrite the data | allowed | allowed | **allowed** | blocked |
| Infinite loop | cannot be stopped | not tested | not tested | killed at 3 s |

The generated code even asked for the network and `.env` with `require`; the ceiling trimmed them.

## What it does not solve

- Models know Synsema less than Python or SQL: one extra attempt here, and higher LLM latency because `guide.txt` travels with every request.
- Restricted DuckDB is a good option when SQL is enough, but `allowed_directories` also allows writing and it does not stop endless queries by itself.
- Run times depend on the machine: the Docker median was 1,360 ms on a quieter run and 1,987 ms on this one. The sandbox gap stays above 40×.

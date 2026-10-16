# Why Synsema?

Five problems teams are solving right now with AI and data. Each one built twice, with the same data and, where a model is involved, the same model: once the usual way in Python, TypeScript or SQL, once in [Synsema](https://synsema.com). Then measured.

This repository holds the code, the data, the results and the site ([why.synsema.com](https://why.synsema.com)). Every number on the site comes from a script here, and every claim below links to the file that backs it.

| # | Case | The claim | Evidence |
| --- | --- | --- | --- |
| 1 | [MCP servers](cases/01-mcp-servers) | With one careless tool, both Python servers hand the model 5 confidential fields; Synsema refuses it at runtime | [`results/responses.json`](cases/01-mcp-servers/results/responses.json), [`results/static_check.json`](cases/01-mcp-servers/results/static_check.json) |
| 2 | [LLM-written analytics](cases/02-llm-written-analytics) | Same 10/10 correct answers; Synsema runs the generated code sandboxed in 34 ms, Docker in 1,987 ms; only Synsema blocks all four escape tests without extra setup | [`results/results.json`](cases/02-llm-written-analytics/results/results.json), [`results/security.json`](cases/02-llm-written-analytics/results/security.json) |
| 3 | [Supply chain](cases/03-supply-chain) | Same ETL: 14 packages and 169 MB of third-party code in Python, 0 in Synsema; the imported module can read `.env` and reach any host in Python, not in Synsema | [`results/code_caps.txt`](cases/03-supply-chain/results/code_caps.txt), [`results/pip_audit.txt`](cases/03-supply-chain/results/pip_audit.txt) |
| 4 | [Invoice approval](cases/04-invoice-approval) | The LLM read 60/60 invoices right, but its own confidence would pay all 7 that needed a human; Jev caught 7 of 7; an agent cannot fake an approval | [`results/rules.json`](cases/04-invoice-approval/results/rules.json), [`results/results.json`](cases/04-invoice-approval/results/results.json) |
| 5 | [AI Act traceability](cases/05-ai-act-traceability) | Python's manual manifest recorded 1 of the 2 files used in training; Synsema's engine lineage recorded 2 of 2, in a signed receipt anyone can verify | [`results/receipt.json`](cases/05-ai-act-traceability/results/receipt.json), [`results/python_manifest.json`](cases/05-ai-act-traceability/results/python_manifest.json) |

Where Synsema loses or ties, the case says so: every case README ends with what it does not solve.

## Check it yourself

Requirements: [Synsema](https://synsema.com) 0.6.44 or later, Python 3.11+ with [uv](https://docs.astral.sh/uv/), and Docker for the sandbox comparison in case 2. Cases 2 and 4 call models: copy `.env.example` to `.env` and add your own keys. Everything runs from the repository root.

```bash
git clone https://github.com/synsema/why-synsema && cd why-synsema
synsema run cases/05-ai-act-traceability/verify.syn          # no keys needed: verifies the signed receipt
synsema code caps cases/03-supply-chain/synsema/etl.syn      # no keys needed: static capability review
bash cases/01-mcp-servers/start.sh && python cases/01-mcp-servers/bench/compare.py
```

Each case folder has a README with the exact commands, the inputs and what to expect. Numbers involving models vary a little between runs; the conclusions in this README held on every run we made.

## Data

Small inputs are committed. Synthetic data (product catalog, invoices) is regenerated from a fixed seed by the scripts in each `data/` folder. Data derived from public sources is listed with its origin in [`DATA.md`](DATA.md).

## The site

`site/` generates and serves why.synsema.com with Synsema: `synsema run site/build.syn`, then `synsema serve site/serve.syn`. Adding a case is one JSON file in `site/content/cases/`. See [`site/README.md`](site/README.md).

## Contributing a case

A good case is a problem someone is paying to solve today, built both ways with the same inputs, with a number that can be reproduced. Open an issue with the problem and the measurement before writing code.

## Keeping secrets out

`.env`, signing keys and local state are ignored by git, and `scripts/check_public.py` scans everything git would publish for secret values, key patterns and personal strings. Install it as a pre-commit hook after cloning: `bash scripts/install_hooks.sh`.

## License

Code and content: [MIT](LICENSE). Fonts in `site/fonts/`: SIL Open Font License (`site/fonts/OFL-*.txt`). Data: see [`DATA.md`](DATA.md) for each source and its terms.

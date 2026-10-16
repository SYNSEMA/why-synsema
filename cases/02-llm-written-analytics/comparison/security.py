"""What can the LLM-generated code do in each executor? The same four tests for all of them.
The content of .env is never printed: only whether it could be read and how many bytes. Run from the repository root:
    uv run --with duckdb --with pandas python cases/02-llm-written-analytics/comparison/security.py
"""
import contextlib, io, json, os, pathlib, subprocess, threading

DATA = "cases/02-llm-written-analytics/data"
DATA_ABS = os.path.abspath(DATA).replace("\\", "/")
res = {}


def probe(executor, name, f):
    try:
        r = f()
        res.setdefault(executor, {})[name] = f"ALLOWED ({r})"
    except Exception as e:
        res.setdefault(executor, {})[name] = f"blocked ({type(e).__name__}: {str(e)[:70]})"


# 1. Python exec in-process (the usual way)
def py(code):
    g = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(code, g)
    return g.get("r")

probe("python exec", "read .env", lambda: py("r = f'{len(open(\".env\").read())} bytes'"))
probe("python exec", "network", lambda: py("import urllib.request; r = urllib.request.urlopen('https://example.com', timeout=5).status"))
probe("python exec", "overwrite the data", lambda: py(f"open('{DATA}/x.txt','w').write('x'); import os; os.remove('{DATA}/x.txt'); r='wrote and deleted'"))
def endless():
    t = threading.Thread(target=lambda: exec("while True: pass"), daemon=True)
    t.start(); t.join(3)
    return "still running after 3 s; a Python thread cannot be killed" if t.is_alive() else "finished"
probe("python exec", "infinite loop", endless)

# 2. DuckDB with default settings
import duckdb
con = duckdb.connect()
probe("duckdb default", "read .env", lambda: str(len(con.sql("select content from read_text('.env')").fetchone()[0])) + " bytes")
probe("duckdb default", "network", lambda: con.sql("select count(*) from read_csv_auto('https://example.com/')").fetchone()[0])
probe("duckdb default", "overwrite the data", lambda: (con.sql(f"copy (select 1 as x) to '{DATA}/x.csv'"), os.remove(f"{DATA}/x.csv"), "wrote and deleted")[2])

# 3. DuckDB restricted to the data folder. Order matters: allowed_directories first, then disable external access.
safe = duckdb.connect()
safe.sql("SET allowed_directories = ['" + DATA_ABS + "']")
safe.sql("SET enable_external_access = false")
probe("duckdb restricted", "read the data", lambda: str(safe.sql("select count(*) from read_csv_auto('" + DATA_ABS + "/books.csv')").fetchone()[0]) + " rows")
probe("duckdb restricted", "read .env", lambda: str(len(safe.sql("select content from read_text('.env')").fetchone()[0])) + " bytes")
probe("duckdb restricted", "network", lambda: safe.sql("select count(*) from read_csv_auto('https://example.com/')").fetchone()[0])
probe("duckdb restricted", "overwrite the data", lambda: (safe.sql("copy (select 1 as x) to '" + DATA_ABS + "/x.csv'"), os.remove(DATA_ABS + "/x.csv"), "wrote and deleted")[2])

# 4. Synsema run_program (security.syn: the same four tests)
r = subprocess.run(["synsema", "run", "cases/02-llm-written-analytics/security.syn"], capture_output=True, text=True, encoding="utf-8")
res["synsema run_program"] = json.loads(r.stdout.strip().splitlines()[-1])

for ex, d in res.items():
    print(f"== {ex}")
    for k, v in d.items():
        print(f"   {k}: {v}")
pathlib.Path("cases/02-llm-written-analytics/results/security.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

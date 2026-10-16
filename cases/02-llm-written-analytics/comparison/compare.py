"""Fair comparison: same model (deepseek-flash), same schema, same 10 questions, up to 3 attempts with the error sent
back to the model. Variants: Synsema (run_program with a ceiling), Python/pandas (exec in-process, plus the same code
inside Docker with no network) and SQL (DuckDB in-process). Run from the repository root:
    uv run --with pandas --with duckdb --with pyarrow python cases/02-llm-written-analytics/comparison/compare.py
"""
import contextlib, io, json, pathlib, re, subprocess, time, urllib.request

ROOT = pathlib.Path("cases/02-llm-written-analytics")
CMP = ROOT / "comparison"
SCHEMA = (CMP / "schema.txt").read_text(encoding="utf-8")
QUESTIONS = json.loads((CMP / "questions.json").read_text(encoding="utf-8"))
KEY = next(l.split("=", 1)[1].strip() for l in open(".env", encoding="utf-8") if l.startswith("DEEPSEEK_API_KEY="))
DATA_ABS = str((ROOT / "data").resolve()).replace("\\", "/")
DOCKER_IMAGE = "why-synsema-python:1"   # built from cases/02-llm-written-analytics/docker/python.Dockerfile

GUIDE_PY = ("You write Python 3 code with pandas to answer questions about files. Read the files with the exact paths "
            "I give you (pd.read_csv, pd.read_parquet, pd.read_json(lines=True)). End by printing the answer with print, "
            "with the numbers that support it. Reply ONLY with the code, no explanations and no ``` blocks.")
GUIDE_SQL = ("You write ONE DuckDB SQL query to answer questions about files. Read with read_csv_auto('path'), "
             "read_parquet('path') or read_json_auto('path') using the exact paths I give you. The query result is "
             "the answer: include the columns with the numbers that support it. Reply ONLY with the query, no explanations and no ``` blocks.")


def llm(system, user):
    body = json.dumps({"model": "deepseek-flash", "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                       "max_tokens": 6000, "temperature": 0, "reasoning_effort": "low"}).encode()
    req = urllib.request.Request("https://api.deepseek.com/chat/completions", body, {"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.loads(r.read())
    text = j["choices"][0]["message"].get("content") or ""
    m = re.search(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip(), round((time.perf_counter() - t0) * 1000)


def run_py_in_process(code):
    """What most products do: exec in the same process. No limits."""
    out = io.StringIO()
    t0 = time.perf_counter()
    try:
        with contextlib.redirect_stdout(out):
            exec(code, {"__name__": "__main__"})
        return True, out.getvalue(), round((time.perf_counter() - t0) * 1000)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}\n{out.getvalue()}", round((time.perf_counter() - t0) * 1000)


def run_py_docker(code):
    """The same code in a container with no network, read-only data, no Linux capabilities, non-root."""
    code = code.replace("./cases/02-llm-written-analytics/data/", "/in/data/")
    t0 = time.perf_counter()
    r = subprocess.run(["docker", "run", "--rm", "-i", "--network", "none", "--read-only", "--tmpfs", "/tmp", "--cap-drop", "ALL",
                        "--memory", "512m", "--user", "1000:1000", "-v", f"{DATA_ABS}:/in/data:ro", DOCKER_IMAGE, "python", "-"],
                       input=code, capture_output=True, text=True, encoding="utf-8", timeout=120)
    return r.returncode == 0, r.stdout if r.returncode == 0 else r.stderr[-800:], round((time.perf_counter() - t0) * 1000)


def run_sql(query):
    import duckdb
    t0 = time.perf_counter()
    try:
        df = duckdb.sql(query).df()
        return True, df.to_string(index=False), round((time.perf_counter() - t0) * 1000)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", round((time.perf_counter() - t0) * 1000)


def with_retries(guide, question, execute):
    message = f"AVAILABLE DATA:\n{SCHEMA}\n\nQUESTION: {question}"
    ms_llm = ms_run = 0
    for attempt in range(1, 4):
        code, ms = llm(guide, message)
        ms_llm += ms
        ok, output, ms_e = execute(code)
        ms_run += ms_e
        if ok:
            return {"ok": True, "attempts": attempt, "ms_llm": ms_llm, "ms_run": ms_run, "output": output.strip(), "code": code}
        message += f"\n\nYour previous code:\n{code}\n\nIt failed with this error:\n{output}\n\nFix it and return the full code."
    return {"ok": False, "attempts": 3, "ms_llm": ms_llm, "ms_run": ms_run, "output": output.strip(), "code": code}


def synsema(question):
    t0 = time.perf_counter()
    r = subprocess.run(["synsema", "run", str(ROOT / "ask.syn"), "--", "--json", question], capture_output=True, text=True, encoding="utf-8", timeout=600)
    try:
        j = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        j = {"ok": False, "output": r.stderr[-500:], "attempts": 0, "ms_llm": 0, "ms_run": 0, "code": ""}
    j["ms_total"] = round((time.perf_counter() - t0) * 1000)
    return j


if __name__ == "__main__":
    results = []
    for q in QUESTIONS:
        row = {"id": q["id"], "question": q["question"]}
        row["synsema"] = synsema(q["question"])
        row["python"] = with_retries(GUIDE_PY, q["question"], run_py_in_process)
        ok, output, ms = run_py_docker(row["python"]["code"]) if row["python"]["ok"] else (False, "", 0)
        row["python_docker"] = {"ok": ok, "ms_run": ms, "output": output.strip()}
        row["sql"] = with_retries(GUIDE_SQL, q["question"], run_sql)
        results.append(row)
        s, p, d = row["synsema"], row["python"], row["sql"]
        print(f"{q['id']:>2} synsema {'ok' if s['ok'] else 'FAIL'} ({s['attempts']} att, {s['ms_run']} ms) · "
              f"python {'ok' if p['ok'] else 'FAIL'} ({p['attempts']} att, {p['ms_run']} ms; docker {ms} ms) · "
              f"sql {'ok' if d['ok'] else 'FAIL'} ({d['attempts']} att, {d['ms_run']} ms)", flush=True)
    (ROOT / "results" / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

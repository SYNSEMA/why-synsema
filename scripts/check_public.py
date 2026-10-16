"""Leak check: scans exactly what git would publish (tracked + new, not ignored) and fails if it finds secrets or
personal data. Runs as a pre-commit hook (scripts/install_hooks.sh) and can run by hand:  python scripts/check_public.py

What it looks for:
  1. Forbidden files: .env (any variant except .env.example), private keys (*.hex, *.pem, *.key, signing_key*).
  2. The actual values of every key in any .env it finds locally (read at check time, never stored in this file).
  3. Generic secret patterns: sk-..., Bearer tokens, private key blocks, long hex secrets next to "key"/"seed"/"secret".
  4. Personal strings listed in .leakcheck-local (one per line, not committed): your user name, email, local paths.
  5. Files larger than 5 MB.
Exit code 1 and a list of findings if anything turns up. It never prints a secret, only where it was found.
"""
import os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
os.chdir(ROOT)

def publishable_files():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p.strip()]

def local_secret_values():
    values = set()
    for env in list(ROOT.glob(".env")) + list(ROOT.glob(".env.*")) + [p for p in [ROOT.parent / "datos" / ".env"] if p.exists()]:
        if env.name == ".env.example":
            continue
        for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if len(v) >= 12:
                    values.add(v)
    for key in ROOT.rglob("*.hex"):
        v = key.read_text(encoding="utf-8", errors="replace").strip()
        if len(v) >= 32:
            values.add(v)
    return values

def personal_strings():
    f = ROOT / ".leakcheck-local"
    return [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")] if f.exists() else []

FORBIDDEN_NAMES = re.compile(r"(^|/)(\.env(\..+)?|.*\.hex|.*\.pem|.*\.key|signing_key[^/]*)$")
PATTERNS = [("api key (sk-...)", re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}")),
            ("bearer token", re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{24,}")),
            ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
            ("hex secret next to key/seed/secret", re.compile(r"(?i)(key|seed|secret|token)[\"'\s:=]{1,6}[0-9a-f]{40,}"))]

def main():
    files = publishable_files()
    secrets, personal = local_secret_values(), personal_strings()
    findings = []
    for path in files:
        if path.endswith(".env.example"):
            pass
        elif FORBIDDEN_NAMES.search(path):
            findings.append(f"{path}: forbidden file (secret or private key)")
            continue
        p = ROOT / path
        if not p.is_file():
            continue
        if p.stat().st_size > 5 * 1024 * 1024:
            findings.append(f"{path}: larger than 5 MB ({p.stat().st_size // 1024 // 1024} MB)")
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_bytes().decode("latin-1")
        for v in secrets:
            if v in text:
                findings.append(f"{path}: contains the value of a local secret ({len(v)} chars, not shown)")
        for name, rx in PATTERNS:
            if rx.search(text):
                findings.append(f"{path}: looks like a {name}")
        for s in personal:
            if s.lower() in text.lower():
                findings.append(f"{path}: contains a personal string from .leakcheck-local")
    print(f"checked {len(files)} publishable files · {len(secrets)} local secret values · {len(personal)} personal strings")
    if findings:
        print("BLOCKED:")
        for f in sorted(set(findings)):
            print("  -", f)
        sys.exit(1)
    print("OK: nothing to hide in what git would publish")

if __name__ == "__main__":
    main()

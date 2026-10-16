#!/usr/bin/env bash
# Install the leak check as a git pre-commit hook. Run once after cloning:  bash scripts/install_hooks.sh
set -e
cat > .git/hooks/pre-commit <<'HOOK'
#!/usr/bin/env bash
python scripts/check_public.py || { echo "Commit blocked by scripts/check_public.py"; exit 1; }
HOOK
chmod +x .git/hooks/pre-commit
echo "pre-commit hook installed"

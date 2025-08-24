# Contributing to AIF (Python)

Thanks for your interest in contributing!

## License and DCO
- This project is dual-licensed: **MIT OR Apache-2.0**.
- We use the **Developer Certificate of Origin (DCO)**. Please sign your commits:
  ```bash
  git commit -s -m "Your message"
  ```
See DCO for details.

Coding standards
- Type hints везде; публичные API задокументированы docstrings.
- Ruff для lint/format; pytest для тестов.

Local dev

```bash
pip install --upgrade pip
pip install uv

uv venv
source .venv/bin/activate

# Install project deps + dev tools (ruff/pytest) defined in pyproject.toml
uv sync

# Run tools via uv-run so the right env is used
uv run ruff check .
uv run pytest -q
```

Autofix (write changes)

- Formatter (applies code style like quotes, spacing; writes files):
  ```bash
  # Use auto-discovered ruff.toml (recommended)
  uv run ruff format .

  # Or explicitly specify config
  uv run ruff format . --config ruff.toml
  ```

- Linter autofixes (safe fixes only):
  ```bash
  # Apply autofixes for lint rules
  uv run ruff check --fix .

  # Show what would change (no writes)
  uv run ruff check --diff .
  ```

- Check-only with diff (no writes), matching your earlier command:
  ```bash
  uv run ruff format --check --diff .
  ```
  Note: If you pass --config pyproject.toml, ruff will ignore ruff.toml. Prefer omitting --config (auto-discovery) or use --config ruff.toml to apply this repo’s formatting rules.

CI & packaging
- GitHub Actions: lint/tests + build.
- PyPI: Trusted Publishing (OIDC) в release.yml.
- Generated code (models/SDK/tests) по умолчанию под MIT-0 — см. LICENSE-GENERATED.

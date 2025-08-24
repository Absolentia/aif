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
python -m venv .venv && source .venv/bin/activate  # или uv
pip install -U pip
pip install -e .
pip install ruff pytest pip-licenses

ruff check .
pytest -q
```

CI & packaging
- GitHub Actions: lint/tests + build.
- PyPI: Trusted Publishing (OIDC) в release.yml.
- Generated code (models/SDK/tests) по умолчанию под MIT-0 — см. LICENSE-GENERATED.

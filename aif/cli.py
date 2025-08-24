from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import orjson
import typer
import uvicorn
from rich import print as rprint

from aif.codegen.pydantic_gen import generate_pydantic_models
from aif.storage.local import read_json, write_json

try:
    import aif_core  # type: ignore
except Exception:
    aif_core = None

app = typer.Typer(add_completion=False, help="AIF CLI")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Запускает FastAPI-сервис оркестратора.

    :rtype: None
    """
    uvicorn.run(
        "aif.api.service:app", host=host, port=port, reload=False, access_log=False
    )


@app.command()
def ui(backend: str = "http://127.0.0.1:8000") -> None:
    """Запускает Streamlit UI.

    :param backend: базовый URL бэкенда FastAPI
    :rtype: None
    """
    env = dict(**{**dict(backend=backend)}, **dict(**dict()))
    # Передаём адрес бэкенда через переменную окружения
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "aif/ui/app.py"], check=True
    )


@app.command()
def learn(
    file: Path = typer.Argument(..., help="Путь к JSON/JSONL с примерами"),
    out: Path = typer.Option(
        Path("contracts/current.json"), help="Куда сохранить схему"
    ),
) -> None:
    """Строит схему по данным (локально, через aif-core).

    :rtype: None
    """
    if not aif_core:
        typer.echo("ERROR: aif-core is not installed/built", err=True)
        raise typer.Exit(2)

    texts: List[str] = []
    data = file.read_text(encoding="utf-8")
    try:
        # Пробуем как JSON-массив
        loaded = json.loads(data)
        if isinstance(loaded, list):
            texts = [orjson.dumps(x).decode("utf-8") for x in loaded]
        else:
            texts = [orjson.dumps(loaded).decode("utf-8")]
    except json.JSONDecodeError:
        # Иначе считаем JSONL
        texts = [line for line in data.splitlines() if line.strip()]

    schema_str = aif_core.infer_schema(texts)  # type: ignore[attr-defined]
    schema = json.loads(schema_str)
    write_json(out, schema)
    rprint(f"[green]Saved schema to[/green] {out}")


@app.command()
def freeze(
    src: Path = Path("contracts/current.json"), version: str | None = None
) -> None:
    """Фиксирует версию контракта (копирует файл).

    :rtype: None
    """
    target = (
        Path("contracts")
        / f"{(version or datetime.utcnow().strftime('v%Y%m%d%H%M%S'))}.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(src.read_text())
    rprint(f"[green]Frozen ->[/green] {target}")


@app.command()
def diff(a: Path, b: Path) -> None:
    """Показывает различия двух схем.

    :rtype: None
    """
    if not aif_core:
        typer.echo("ERROR: aif-core is not installed/built", err=True)
        raise typer.Exit(2)
    out = aif_core.diff_schemas(a.read_text(), b.read_text())  # type: ignore[attr-defined]
    rprint(out)


@app.command()
def codegen(
    schema: Path = Path("contracts/current.json"), out: Path = Path("models.py")
) -> None:
    """Генерирует Pydantic-модели из сохранённой схемы.

    :rtype: None
    """
    sc = read_json(schema)
    code = generate_pydantic_models(sc, "RootModel")
    out.write_text(code, encoding="utf-8")
    rprint(f"[green]Wrote[/green] {out}")

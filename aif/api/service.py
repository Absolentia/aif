from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import orjson
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from aif.codegen.pydantic_gen import generate_pydantic_models
from aif.storage.local import read_json, write_json

try:
    # Модуль из aif-core
    import aif_core  # type: ignore
except Exception as e:  # pragma: no cover
    aif_core = None  # поднимем ошибку при первом использовании


class ObserveRequest(BaseModel):
    """Запрос с примерами данных для обучения/вывода схемы."""
    samples: list[Any]


class SchemaResponse(BaseModel):
    """Ответ со сгенерированной схемой (JSON Schema)."""
    schema: dict[str, Any]


class DiffRequest(BaseModel):
    """Запрос на сравнение двух схем."""
    a: dict[str, Any]
    b: dict[str, Any]


class DiffResponse(BaseModel):
    diff: dict[str, Any]


class CodegenRequest(BaseModel):
    schema: dict[str, Any]
    root_name: str | None = 'RootModel'


app = FastAPI(title='AIF Orchestrator', version='0.1.0')


@app.get('/healthz')
def healthz() -> dict[str, str]:
    """Проверка здоровья сервиса.

    :rtype: Dict[str, str]
    """
    return {'status': 'ok'}


@app.post('/infer', response_model=SchemaResponse)
def infer(req: ObserveRequest) -> SchemaResponse:
    """Получает список JSON-образцов и возвращает JSON Schema.

    :rtype: SchemaResponse
    """
    if aif_core is None:
        raise HTTPException(500, 'aif-core is not installed/built')
    payloads = [orjson.dumps(s).decode('utf-8') for s in req.samples]
    schema_str = aif_core.infer_schema(payloads)  # type: ignore[attr-defined]
    schema = json.loads(schema_str)
    return SchemaResponse(schema=schema)


@app.post('/diff', response_model=DiffResponse)
def diff(req: DiffRequest) -> DiffResponse:
    """Сравнивает две схемы, возвращает список полей (added/removed/common).

    :rtype: DiffResponse
    """
    if aif_core is None:
        raise HTTPException(500, 'aif-core is not installed/built')
    a = json.dumps(req.a)
    b = json.dumps(req.b)
    out = aif_core.diff_schemas(a, b)  # type: ignore[attr-defined]
    return DiffResponse(diff=json.loads(out))


@app.post('/codegen/pydantic')
def codegen(req: CodegenRequest) -> dict[str, str]:
    """Генерирует Pydantic v2 модели на основе схемы.

    :rtype: Dict[str, str]
    """
    code = generate_pydantic_models(req.schema, req.root_name or 'RootModel')
    return {'code': code}


CONTRACTS_DIR = Path(os.environ.get('AIF_CONTRACTS_DIR', 'contracts')).resolve()


@app.post('/contracts/freeze')
def freeze(schema: SchemaResponse, version: str | None = None) -> dict[str, str]:
    """Сохраняет схему в каталоге contracts.

    :rtype: Dict[str, str]
    """
    ver = version or 'current'
    path = CONTRACTS_DIR / f'{ver}.json'
    write_json(path, schema.schema)
    return {'path': str(path)}

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_dir(p: Path) -> None:
    """Создаёт директорию при необходимости.

    :rtype: None
    """
    p.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Сохраняет JSON с отступами.

    :param path: путь для сохранения
    :param data: данные (словарь)
    :rtype: None
    """
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def read_json(path: Path) -> dict[str, Any]:
    """Читает JSON из файла.

    :param path: путь к JSON
    :rtype: dict[str, Any]
    """
    return json.loads(path.read_text())

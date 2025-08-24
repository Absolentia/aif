from __future__ import annotations

from typing import Any


def _camel(name: str) -> str:
    """simple snake/camel → PascalCase.

    :rtype: str
    """
    parts = [p for p in name.replace('-', '_').split('_') if p]
    return ''.join(p[:1].upper() + p[1:] for p in parts) or 'Model'


def _py_type(js_type: Any) -> str:
    """Маппинг JSON Schema type → Python type.

    :rtype: str
    """
    if isinstance(js_type, list):
        # nullable объединяем в Optional[...]
        nn = [t for t in js_type if t != 'null']
        if not nn:
            return 'Optional[Any]'
        inner = _py_type(nn[0]) if len(nn) == 1 else f"({' | '.join(_py_type(t) for t in nn)})"
        return f'Optional[{inner}]'
    mapping = {
        'string': 'str',
        'integer': 'int',
        'number': 'float',
        'boolean': 'bool',
        'array': 'list[Any]',
        'object': 'dict[str, Any]',
    }
    return mapping.get(js_type, 'Any')


def _walk(
        name: str,
        schema: dict[str, Any],
        classes: list[tuple[str, list[tuple[str, str]]]],
) -> str:
    """Рекурсивно строит классы. Возвращает имя Python-типа для текущего узла.

    :rtype: str
    """
    t = schema.get('type')
    props = schema.get('properties') or {}

    # вложенные классы для объектов
    if (t == 'object' or (isinstance(t, list) and 'object' in t)) and props:
        fields: list[tuple[str, str]] = []
        for k, v in props.items():
            child_name = _camel(k)
            py_type = _py_type(v.get('type'))
            # если у дочернего есть properties или items — создаём класс
            if isinstance(v, dict) and (v.get('properties') or v.get('items')):
                nested_type = _walk(child_name, v, classes)
                fields.append((k, nested_type))
            else:
                fields.append((k, py_type))
        classes.append((name, fields))
        return name

    # массив
    if (t == 'array' or (isinstance(t, list) and 'array' in t)) and schema.get('items'):
        item_schema = schema['items']
        item_name = _camel(f'{name}Item')
        item_type = _walk(item_name, item_schema, classes)
        return f'list[{item_type}]'

    # примитив или смешанный
    return _py_type(t)


def generate_pydantic_models(schema: dict[str, Any], root_name: str = 'RootModel') -> str:
    """Генерирует код Pydantic v2 по JSON Schema (MVP).

    :param schema: JSON Schema (dict)
    :param root_name: имя корневой модели
    :rtype: str (исходный код)
    """
    classes: list[tuple[str, list[tuple[str, str]]]] = []
    _walk(root_name, schema, classes)

    lines: list[str] = [
        'from __future__ import annotations',
        'from typing import Any, Optional, List, Dict',
        'from pydantic import BaseModel',
        '',
    ]
    if not classes:
        # нет свойств: делаем пустой
        lines += [f'class {root_name}(BaseModel):', '    pass', '']
    else:
        for cls_name, fields in classes:
            lines.append(f'class {cls_name}(BaseModel):')
            if not fields:
                lines.append('    pass')
            else:
                for fname, ftype in fields:
                    lines.append(f'    {fname}: {ftype}')
            lines.append('')

    return '\n'.join(lines)

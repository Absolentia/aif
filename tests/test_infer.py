from __future__ import annotations

import json

import pytest

try:
    import aif_core  # type: ignore
except Exception:
    aif_core = None


@pytest.mark.skipif(aif_core is None, reason="aif-core not built")
def test_simple_infer() -> None:
    samples = [
        json.dumps({"id": 1, "name": "Alice", "tags": ["a", "b"]}),
        json.dumps({"id": 2, "name": "Bob", "tags": []}),
    ]
    out = aif_core.infer_schema(samples)  # type: ignore[attr-defined]
    schema = json.loads(out)
    assert schema["type"] == "object"
    assert "id" in schema["properties"]
    assert schema["properties"]["id"]["type"] in ("integer", ["integer"])

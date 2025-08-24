from __future__ import annotations

import json
import os
from typing import Any

import httpx
import streamlit as st

BACKEND = os.environ.get("AIF_BACKEND", "http://127.0.0.1:8000")

st.set_page_config(page_title="AIF UI", layout="wide")
st.title(body="AIF — Interface Foundry (MVP)")

backend = st.text_input(label="Backend URL", value=BACKEND)

tab_infer, tab_codegen = st.tabs(tabs=["Infer schema", "Codegen"])

with tab_infer:
    st.subheader(body="Загрузите JSON или JSONL")
    uploaded = st.file_uploader(label="Файл с примерами", type=["json", "jsonl"])
    samples: list[Any] = []

    if uploaded is not None:
        content = uploaded.read().decode("utf-8")
        try:
            obj = json.loads(content)
            if isinstance(obj, list):
                samples = obj
            else:
                samples = [obj]
        except json.JSONDecodeError:
            # JSONL
            samples = [
                json.loads(line) for line in content.splitlines() if line.strip()
            ]

    if st.button(label="Infer", disabled=not samples):
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{backend}/infer", json={"samples": samples})
            resp.raise_for_status()
            schema = resp.json()["schema"]
            st.json(body=schema)

            if st.button(label="Freeze current"):
                freeze = client.post(
                    url=f"{backend}/contracts/freeze", json={"schema": schema}
                )
                freeze.raise_for_status()
                st.success(body=f"Saved: {freeze.json()['path']}")

with tab_codegen:
    st.subheader(body="Генерация Pydantic моделей из схемы")
    schema_text = st.text_area(
        label="Вставьте JSON Schema",
        height=300,
        value='{"type": "object", "properties": {}}',
    )
    root_name = st.text_input(label="Имя корневой модели", value="RootModel")
    if st.button(label="Generate"):
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                url=f"{backend}/codegen/pydantic",
                json={"schema": json.loads(schema_text), "root_name": root_name},
            )
            resp.raise_for_status()
            st.code(body=resp.json()["code"], language="python")

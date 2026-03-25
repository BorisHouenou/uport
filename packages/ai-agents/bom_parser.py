"""
BOM file parser — CSV, Excel (xlsx/xls), JSON.

Normalises heterogeneous column names into a standard BOMRow schema,
then calls the HS Classifier for any rows missing an HS code.
"""
from __future__ import annotations

import csv
import io
import json
from typing import Any

from pydantic import BaseModel, Field


class BOMRow(BaseModel):
    """Normalised BOM row ready for DB insertion and HS classification."""
    description: str
    quantity: float = 1.0
    unit_cost: float = 0.0
    currency: str = "USD"
    origin_country: str = "XX"   # ISO-3166 alpha-2; XX = unknown
    hs_code: str | None = None
    is_originating: bool | None = None
    raw_row: dict = Field(default_factory=dict)


# Column name aliases (handles variations from different ERP exports)
COL_ALIASES: dict[str, list[str]] = {
    "description": ["description", "product", "item", "name", "part_name", "component", "material", "goods"],
    "quantity":    ["quantity", "qty", "amount", "units", "count"],
    "unit_cost":   ["unit_cost", "unit_price", "price", "cost", "value", "unit_value", "cost_usd"],
    "currency":    ["currency", "curr", "ccy"],
    "origin_country": ["origin_country", "origin", "country_of_origin", "coo", "made_in", "source_country"],
    "hs_code":     ["hs_code", "hs", "tariff_code", "commodity_code", "hts", "hts_code", "ncm"],
    "is_originating": ["is_originating", "originating", "local_content", "domestic"],
}


def _find_col(headers: list[str], field: str) -> str | None:
    aliases = COL_ALIASES.get(field, [])
    headers_lower = {h.lower().strip().replace(" ", "_"): h for h in headers}
    for alias in aliases:
        if alias in headers_lower:
            return headers_lower[alias]
    return None


def _parse_bool(val: Any) -> bool | None:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower().strip() in ("true", "yes", "1", "y")
    if isinstance(val, (int, float)):
        return bool(val)
    return None


def _normalise_row(raw: dict, col_map: dict[str, str | None]) -> BOMRow | None:
    def get(field: str, default=None):
        col = col_map.get(field)
        return raw.get(col, default) if col else default

    description = str(get("description", "")).strip()
    if not description:
        return None  # skip empty rows

    try:
        quantity = float(str(get("quantity", 1)).replace(",", "") or 1)
    except ValueError:
        quantity = 1.0

    try:
        unit_cost = float(str(get("unit_cost", 0)).replace(",", "").replace("$", "") or 0)
    except ValueError:
        unit_cost = 0.0

    origin = str(get("origin_country", "XX") or "XX").strip().upper()[:2]
    hs = str(get("hs_code", "") or "").strip().replace(".", "") or None

    return BOMRow(
        description=description,
        quantity=quantity,
        unit_cost=unit_cost,
        currency=str(get("currency", "USD") or "USD").upper()[:3],
        origin_country=origin if len(origin) == 2 else "XX",
        hs_code=hs,
        is_originating=_parse_bool(get("is_originating")),
        raw_row=raw,
    )


def parse_csv(content: bytes) -> list[BOMRow]:
    text = content.decode("utf-8-sig")  # handle BOM in UTF-8
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    col_map = {field: _find_col(list(headers), field) for field in COL_ALIASES}
    rows = []
    for raw in reader:
        row = _normalise_row(dict(raw), col_map)
        if row:
            rows.append(row)
    return rows


def parse_excel(content: bytes) -> list[BOMRow]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)
    header_row = next(rows_iter, None)
    if header_row is None:
        return []
    headers = [str(h).strip() if h is not None else "" for h in header_row]
    col_map = {field: _find_col(headers, field) for field in COL_ALIASES}
    rows = []
    for raw_tuple in rows_iter:
        raw = {headers[i]: raw_tuple[i] for i in range(len(headers))}
        row = _normalise_row(raw, col_map)
        if row:
            rows.append(row)
    return rows


def parse_json(content: bytes) -> list[BOMRow]:
    data = json.loads(content.decode())
    if isinstance(data, dict):
        data = data.get("items", data.get("bom", data.get("rows", [])))
    rows = []
    for item in data:
        if not isinstance(item, dict):
            continue
        headers = list(item.keys())
        col_map = {field: _find_col(headers, field) for field in COL_ALIASES}
        row = _normalise_row(item, col_map)
        if row:
            rows.append(row)
    return rows


def parse_bom(content: bytes, file_ext: str) -> list[BOMRow]:
    """Parse a BOM file from bytes. file_ext: .csv, .xlsx, .xls, .json"""
    ext = file_ext.lower()
    if ext == ".csv":
        return parse_csv(content)
    elif ext in (".xlsx", ".xls"):
        return parse_excel(content)
    elif ext == ".json":
        return parse_json(content)
    else:
        raise ValueError(f"Unsupported BOM file format: {ext}")

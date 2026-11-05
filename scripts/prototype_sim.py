"""Shared helpers for the Phase 2 simulation data (Excel -> prototype/data JSON).

Excel is canonical. `Prototype_Sim` rows in the payload-mocks workbook hold one JSON
payload per prototype file. Payloads may embed references that are resolved at export:

  {"$ref": "mocks:<Sheet>/<Event>/<Direction>#/json/pointer"}   row in With_MCA / Without_MCA
  {"$ref": "sim:<file under prototype/data>#/json/pointer"}       another Prototype_Sim row
  {"$ref": "...", "$merge": {...}}                                 referenced value deep-merged with overrides
"""
from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path
from statistics import median

from openpyxl import load_workbook

REPO = Path(__file__).resolve().parents[1]
MAPPING_XLSX = REPO / "docs/mappings/cdu-ps-isda-2026-mapping.xlsx"
MOCKS_XLSX = REPO / "docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx"
OPENAPI_MD = REPO / "specs/api/openapi.md"
DATA_DIR = REPO / "prototype/data"
ROUTES_JSON = REPO / "prototype/routes.json"

SIM_SHEET = "Prototype_Sim"
BOOK_SHEET = "Prototype_Trade_Book"
SIM_HEADERS = [
    "Step",
    "Scenario",
    "Flow",
    "At (UTC)",
    "Actor",
    "Method",
    "API path",
    "Contract",
    "File",
    "Description",
    "Payload JSON",
]
# Scenario picker for the shell sim-clock banner (architecture §5).
# Each scenario sets the starting clock; writes still move the clock forward.
SCENARIOS = [
    {"id": "A", "label": "A · Template release", "clock": "2027-12-01T15:59:00Z", "default": False},
    {"id": "B", "label": "B · TR-FXO-001 journey", "clock": "2027-12-01T10:00:00Z", "default": False},
    {"id": "C", "label": "C · Manual draft", "clock": "2027-12-01T16:40:00Z", "default": False},
    {"id": "D", "label": "D · Book & MIS", "clock": "2027-12-01T16:30:00Z", "default": True},
]
# GET responses whose body carries a time-ordered list: the mock API keeps only
# entries with `at` at or before the clock (architecture §5).
LIST_FILTER_PATHS = {
    "/trades/{id}/timeline": "events",
    "/audit": "items",
    "/templates/{id}/audit": "items",
}
BOOK_HEADERS = [
    "tradeId",
    "eventId",
    "receivedAt",
    "partyBName",
    "partyBLei",
    "mcaPath",
    "optionType",
    "callCurrency",
    "callCurrencyAmount",
    "strikePrice",
    "expirationDate",
    "status",
    "assemblyRunId",
    "assemblyMode",
    "templateVersion",
    "documentId",
    "affirmationStatus",
    "sentAt",
    "affirmedAt",
    "timelineAvailable",
]


def sheet_dicts(ws) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    header = [h for h in rows[0]]
    return [dict(zip(header, r)) for r in rows[1:] if any(v is not None for v in r)]


def book_rows(mocks_wb) -> list[dict]:
    return sheet_dicts(mocks_wb[BOOK_SHEET])


def mock_payloads(mocks_wb) -> dict[str, object]:
    out = {}
    for sheet in ("With_MCA", "Without_MCA"):
        for r in mocks_wb[sheet].iter_rows(min_row=2, values_only=True):
            if r[0] and r[3]:
                out[f"{sheet}/{r[0]}/{r[1]}"] = json.loads(r[3])
    return out


def sim_rows(mocks_wb) -> list[dict]:
    return sheet_dicts(mocks_wb[SIM_SHEET])


def pointer_get(doc, pointer: str):
    if not pointer or pointer == "/":
        return doc
    node = doc
    for part in pointer.lstrip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def jpath_get(doc, path: str):
    """Dotted path with list selectors: `a.b[0].c`, `trade.parties[id=partyA].lei`."""
    node = doc
    for name, sel in re.findall(r"([^.\[\]]+)|\[([^\]]+)\]", path):
        if name:
            node = node[name]
        elif "=" in sel:
            key, _, want = sel.partition("=")
            node = next(item for item in node if item.get(key) == want)
        else:
            node = node[int(sel)]
    return node


def deep_merge(base, override):
    if isinstance(base, dict) and isinstance(override, dict):
        out = dict(base)
        for k, v in override.items():
            out[k] = deep_merge(base.get(k), v) if k in base else v
        return out
    return override


class Resolver:
    def __init__(self, mocks_wb):
        self.mocks = mock_payloads(mocks_wb)
        self.raw = {r["File"]: json.loads(r["Payload JSON"]) for r in sim_rows(mocks_wb)}
        self.cache: dict[str, object] = {}
        self.stack: list[str] = []

    def file(self, rel: str):
        if rel not in self.cache:
            if rel in self.stack:
                raise ValueError(f"$ref cycle: {' -> '.join(self.stack + [rel])}")
            self.stack.append(rel)
            self.cache[rel] = self.resolve(self.raw[rel])
            self.stack.pop()
        return copy.deepcopy(self.cache[rel])

    def ref(self, ref: str):
        target, _, pointer = ref.partition("#")
        kind, _, key = target.partition(":")
        if kind == "mocks":
            if key not in self.mocks:
                raise KeyError(f"unknown mock row {key}")
            doc = copy.deepcopy(self.mocks[key])
        elif kind == "sim":
            if key not in self.raw:
                raise KeyError(f"unknown sim file {key}")
            doc = self.file(key)
        else:
            raise ValueError(f"bad $ref {ref}")
        return copy.deepcopy(pointer_get(doc, pointer))

    def resolve(self, node):
        if isinstance(node, dict):
            if "$ref" in node:
                base = self.ref(node["$ref"])
                if "$merge" in node:
                    base = deep_merge(base, self.resolve(node["$merge"]))
                return base
            return {k: self.resolve(v) for k, v in node.items()}
        if isinstance(node, list):
            return [self.resolve(v) for v in node]
        return node


TRADE_STATUSES = ["Received", "Validating", "Composing", "ManualDraft", "Sent", "AffirmPending", "Affirmed"]
AGING_BUCKETS = [("0-1h", 0, 3600), ("1-4h", 3600, 4 * 3600), ("4-24h", 4 * 3600, 24 * 3600), (">24h", 24 * 3600, None)]
CONTAGION_THRESHOLD = 3


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def analytics_from_book(book: list[dict], as_of: str) -> dict:
    """MIS aggregates (GET /trades counts + /analytics/*) derived only from the trade book."""
    now = _ts(as_of)
    counts = {s: sum(1 for r in book if r["status"] == s) for s in TRADE_STATUSES}
    sent = [r for r in book if r["sentAt"]]
    affirmed = [r for r in book if r["affirmedAt"]]
    durations = [(_ts(r["affirmedAt"]) - _ts(r["receivedAt"])).total_seconds() / 60 for r in affirmed]

    def buckets(status: str, since_key: str):
        ages = [(now - _ts(r[since_key])).total_seconds() for r in book if r["status"] == status and r[since_key]]
        return [{"label": lbl, "count": sum(1 for a in ages if a >= lo and (hi is None or a < hi))} for lbl, lo, hi in AGING_BUCKETS]

    parties = {}
    for r in book:
        p = parties.setdefault(r["partyBName"], {"partyBName": r["partyBName"], "partyBLei": r["partyBLei"], "trades": 0, "open": 0, "unmatched": 0, "errors": 0})
        p["trades"] += 1
        p["open"] += r["status"] != "Affirmed"
        p["unmatched"] += r["affirmationStatus"] == "Unmatched"
    for p in parties.values():
        p["flagged"] = p["unmatched"] + p["errors"] >= CONTAGION_THRESHOLD

    return {
        "counts": counts,
        "summary": {
            "asOf": as_of,
            "window": {"from": as_of[:10] + "T00:00:00Z", "to": as_of},
            "productType": "Deliverable_FX_Option",
            "volumes": {"received": len(book), "sent": len(sent), "affirmed": len(affirmed), "manualDraft": counts["ManualDraft"]},
            "affirmRate": round(len(affirmed) / len(sent), 4) if sent else None,
            "errorRate": 0.0,
            "medianNewToAffirmedMinutes": round(median(durations), 1) if durations else None,
        },
        "aging": {
            "asOf": as_of,
            "series": [
                {"status": "AffirmPending", "measuredFrom": "sentAt", "buckets": buckets("AffirmPending", "sentAt")},
                {"status": "Unmatched", "measuredFrom": "sentAt", "buckets": buckets("Unmatched", "sentAt")},
            ],
        },
        "errors": {"asOf": as_of, "count": 0, "items": []},
        "contagion": {"asOf": as_of, "threshold": CONTAGION_THRESHOLD, "items": sorted(parties.values(), key=lambda p: p["partyBName"])},
    }


def load_workbooks():
    return load_workbook(MAPPING_XLSX), load_workbook(MOCKS_XLSX)


def dump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"

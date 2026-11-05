#!/usr/bin/env python3
"""Fail on drift between Excel (canonical data), OpenAPI (canonical contract) and the Phase 2 pack.

Checks
  0. committed workbooks == a fresh scripts/build.py build (every sheet, every cell); routes.json == manifest
  1. prototype/data/*.json == Excel `Prototype_Sim` rows (after $ref resolution); no orphan files
  2. each file's keys appear in its labelled OpenAPI example (two levels deep); API paths exist
  3. field names match Excel LDM / Template_Admin_Utility / Sample_Trade_Card / Attribute_Product_Map / Rules_DQ
  4. book rows (`Prototype_Trade_Book`) == GET /trades items == inbound trade files; MIS == derived from book
  5. timeline events link audit events; status at book asOf == book status
  6. design docs + stories: cited files, API paths, ids, Data-binding / Examples tables all resolve

Run: .venv/bin/python scripts/check_prototype_sync.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import build_prototype_data as sim_data  # noqa: E402
import generate_fxo_payload_mocks as mocks  # noqa: E402
import prototype_sim as sim  # noqa: E402

REPO = sim.REPO
DOC_GLOBS = ["docs/design/**/*.md", "specs/stories/*.md", "prototype/README.md"]
ID_SCAN_GLOBS = DOC_GLOBS + ["specs/api/openapi.md", "specs/scenarios/*.md", "specs/features/*.md"]
ID_RE = re.compile(
    r"\b(TR-FXO-\d{3}|DOC-\d{3}R?|SDX-DOC-\d{3}R?|TB-FXO-DEL-2026-\d{3}|AR-FXO-\d{3}-\d{2}|AUD-\d{4}|TL-\d{2}-\d{2}"
    r"|evt_\d{4}|PSR-FXO-[A-Z0-9-]+|TV-(?:I|IIB)-2026-\d\.\d\.\d|MDC-\d{3}-\d{2}|CONF-\d{3}|MCA-SCB-ACME-2026-001)\b"
)
API_RE = re.compile(r"\b(GET|POST|PUT|DELETE|PATCH) (/[A-Za-z0-9_{}\-./]+)")
DATA_REF_RE = re.compile(r"prototype/data/([A-Za-z0-9_./-]+\.json)")
LABEL_RE = re.compile(r"^(Request|Response)(?: (\d{3}))?(?: \(([\w-]+)\))?:\s*$")

errors: list[str] = []
checks = 0


def check(cond: bool, msg: str):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


# ---------------------------------------------------------------------------
# OpenAPI parsing
# ---------------------------------------------------------------------------


def parse_openapi():
    text = sim.OPENAPI_MD.read_text(encoding="utf-8")
    paths = {(m, p.rstrip(".")) for m, p in re.findall(r"`(GET|POST|PUT|DELETE|PATCH) (/[^`\s]+)`", text)}
    examples: dict[tuple[str, str, str], object] = {}
    endpoints: list[tuple[str, str]] = []
    label = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            endpoints = re.findall(r"`(GET|POST|PUT|DELETE|PATCH) (/[^`\s]+)`", line)
            label = None
        m = LABEL_RE.match(line)
        if m:
            kind, code, suffix = m.groups()
            label = "response-" + code if kind == "Response" else "request" + (f"-{suffix}" if suffix else "")
        if line.strip() == "```json" and label:
            j = i + 1
            while lines[j].strip() != "```":
                j += 1
            body = json.loads("\n".join(lines[i + 1 : j]))
            for ep in endpoints:
                examples[(ep[0], ep[1], label)] = body
            label = None
            i = j
        i += 1
    return paths, examples


def path_known(method: str, concrete: str, paths) -> bool:
    concrete = concrete.split("?")[0].rstrip(".,)")
    for m, tpl in paths:
        if m != method:
            continue
        rx = "^" + re.sub(r"\\\{[^}]+\\\}", "[^/]+", re.escape(tpl)) + "$"
        if re.match(rx, concrete):
            return True
    return False


def keys_subset(data, example, where: str, level: int = 0):
    if isinstance(data, dict) and isinstance(example, dict) and example:
        for k, v in data.items():
            check(k in example, f"{where}: key '{k}' not in OpenAPI example")
            if level < 1 and k in example:
                keys_subset(v, example[k], f"{where}.{k}", level + 1)
    elif isinstance(data, list) and isinstance(example, list) and example and isinstance(example[0], dict):
        for n, item in enumerate(data):
            keys_subset(item, example[0], f"{where}[{n}]", level)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


jpath = sim.jpath_get


def cell_values(wb) -> dict[str, list[tuple]]:
    norm = lambda v: None if v == "" else v  # noqa: E731
    return {
        ws.title: [tuple(norm(v) for v in row) for row in ws.iter_rows(values_only=True) if any(v not in (None, "") for v in row)]
        for ws in wb.worksheets
    }


def as_text(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def md_tables(text: str):
    """Yield (header, rows) for every pipe table."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith("|") and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append([c.strip().strip("`") for c in lines[j].strip().strip("|").split("|")])
                j += 1
            yield header, rows
            i = j
        else:
            i += 1


def excel_strings(*wbs):
    for wb in wbs:
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                for v in row:
                    if isinstance(v, str):
                        yield v


def ldm_attrs(mapping_wb, entity: str) -> set[str]:
    return {r[1] for r in mapping_wb["Logical_Data_Model"].iter_rows(min_row=2, values_only=True) if r[0] == entity}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main():
    mapping_wb, mocks_wb = sim.load_workbooks()
    resolver = sim.Resolver(mocks_wb)
    rows = sim.sim_rows(mocks_wb)
    files = {r["File"]: r for r in rows}
    paths, examples = parse_openapi()
    data = {}

    # 0. workbooks == fresh build; route manifest
    for name, committed, fresh in zip(("mapping", "mocks"), (mapping_wb, mocks_wb), build.build_workbooks()):
        got, want = cell_values(committed), cell_values(fresh)
        check(list(got) == list(want), f"{name} workbook sheets {list(got)} != fresh build {list(want)} (run scripts/build.py)")
        for sheet in want:
            if got.get(sheet) != want[sheet]:
                diff = next((i for i, (a, b) in enumerate(zip(got.get(sheet, []), want[sheet])) if a != b), min(len(got.get(sheet, [])), len(want[sheet])))
                check(False, f"{name} workbook sheet {sheet} differs from fresh build at row {diff + 1} (run scripts/build.py)")
            else:
                check(True, "")
    check(sim.ROUTES_JSON.exists() and json.loads(sim.ROUTES_JSON.read_text(encoding="utf-8")) == sim_data.routes(mocks_wb), "prototype/routes.json differs from Prototype_Sim (run scripts/build.py)")

    # 1. export equality + orphans
    for rel in files:
        p = sim.DATA_DIR / rel
        check(p.exists(), f"missing prototype/data/{rel} (run scripts/build.py)")
        if p.exists():
            data[rel] = json.loads(p.read_text(encoding="utf-8"))
            check(data[rel] == resolver.file(rel), f"prototype/data/{rel} differs from Excel Prototype_Sim row")
    for p in sim.DATA_DIR.rglob("*.json"):
        rel = p.relative_to(sim.DATA_DIR).as_posix()
        check(rel in files, f"orphan file prototype/data/{rel} (not in Excel Prototype_Sim)")

    # 2. contracts
    for r in rows:
        key = (r["Method"], r["API path"], r["Contract"])
        check((r["Method"], r["API path"]) in paths, f"{r['Step']}: {r['Method']} {r['API path']} not in openapi.md")
        check(key in examples, f"{r['Step']}: no OpenAPI example labelled '{r['Contract']}' for {r['Method']} {r['API path']}")
        if key in examples and r["File"] in data:
            keys_subset(data[r["File"]], examples[key], f"{r['File']}")

    # 3. field names vs Excel
    amap = [r for r in mapping_wb["Attribute_Product_Map"].iter_rows(min_row=2, values_only=True)]
    attr_pairs = {(r[0], r[15], r[6]) for r in amap}
    dq_ids = {r[0] for r in mapping_wb["Rules_DQ"].iter_rows(min_row=2, values_only=True) if r[0]}
    admin_fields = {str(r[0]).split(".")[0] for r in mapping_wb["Template_Admin_Utility"].iter_rows(min_row=2, values_only=True) if r[0]}
    card_fields = {r[0] for r in mocks_wb["Sample_Trade_Card"].iter_rows(min_row=2, values_only=True) if r[0]}
    tpl = "templates/fxo-deliverable-2026"
    pkg_allowed = admin_fields | ldm_attrs(mapping_wb, "TemplatePackage") | {"selectionRuleIds", "versions"}
    for rel in (f"{tpl}/package.json", "outbound/api-responses/TB-FXO-DEL-2026-001/03-get-template.after-activate.200.json"):
        for k in data[rel]:
            check(k in pkg_allowed, f"{rel}: '{k}' not in Template_Admin_Utility / LDM TemplatePackage")
    for rel, d in data.items():
        if rel.startswith("timeline/TR-"):
            for ev in d["events"]:
                for k in ev:
                    check(k in ldm_attrs(mapping_wb, "TimelineEvent"), f"{rel}: '{k}' not in LDM TimelineEvent")
        if "/get-assembly." in rel:
            allowed = ldm_attrs(mapping_wb, "AssemblyRun") | {"documentId", "dq", "legal", "package", "exhibitILetter"}
            for k in d:
                check(k in allowed, f"{rel}: '{k}' not in LDM AssemblyRun")
            check(set(d["dq"]["ruleIds"]) <= dq_ids, f"{rel}: DQ rule ids not in Rules_DQ")
        if rel.startswith("inbound/trades/"):
            leaves: list = []
            mocks.flatten("", d["trade"], leaves)
            for k, _ in leaves:
                check(k in card_fields or any(c.startswith(k + ".") for c in card_fields), f"{rel}: trade.{k} not in Sample_Trade_Card")
            prod = d["trade"]["product"]
            ids = [x["id"] for x in d["trade"]["parties"]]
            refs = [prod["buyerPartyReference"]["href"], prod["sellerPartyReference"]["href"]]
            check(set(refs) <= set(ids) and refs[0] != refs[1], f"{rel}: buyer/seller party references must resolve to trade.parties[] and differ (DQ-REQ-003)")
    for a in data["timeline/audit-events.json"]["items"]:
        check(set(a) <= ldm_attrs(mapping_wb, "AuditEvent"), f"audit {a['auditId']}: keys not in LDM AuditEvent")
    for rule in data[f"{tpl}/selection-rules.json"]["items"]:
        check(set(rule) <= ldm_attrs(mapping_wb, "PackageSelectionRule"), "selection rule keys not in LDM PackageSelectionRule")
    mdc = data["outbound/api-responses/TR-FXO-005/04-put-manual-draft.200.json"]
    check(set(mdc) <= ldm_attrs(mapping_wb, "ManualDraftContent") | {"status", "auditId"}, "manual draft keys not in LDM ManualDraftContent")
    for block in data[f"{tpl}/exhibit-i-master.json"]["blocks"]:
        for fld in block["fields"]:
            check((fld["attribute"], fld["tpsJsonPath"], "I") in attr_pairs, f"Exhibit I field {fld} not in Attribute_Product_Map")
    sample = data["inbound/trades/TR-FXO-001.new-trade.json"]
    for fld in data[f"{tpl}/exhibit-ii-b-product.json"]["fields"]:
        check((fld["attribute"], fld["tpsJsonPath"], "II-B") in attr_pairs, f"II-B field {fld['attribute']} not in Attribute_Product_Map")
        check(jpath(sample, fld["tpsJsonPath"]) == fld["example"], f"II-B example {fld['attribute']} != TR-FXO-001 value")
    for v in ("1.0.0", "1.1.0", "1.2.0"):
        vd = data[f"{tpl}/versions/{v}.json"]
        pv = next(x for x in data[f"{tpl}/package.json"]["versions"] if x["version"] == v)
        check(vd["status"] == pv["status"], f"version {v} status differs between package.json and versions/{v}.json")
        for layer in vd["layers"]:
            check(layer["bodyFile"] is None or layer["bodyFile"] in files, f"version {v}: bodyFile {layer['bodyFile']} missing")
        for ch in vd["changes"]:
            check((ch["attribute"], ch["tpsJsonPath"], "I") in attr_pairs, f"version {v} change {ch['attribute']} not in Attribute_Product_Map")
    for rel in (f"{tpl}/package.json", "outbound/api-responses/TB-FXO-DEL-2026-001/03-get-template.after-activate.200.json"):
        live = [x["version"] for x in data[rel]["versions"] if x["status"] == "LIVE"]
        check(live == [data[rel]["version"]], f"{rel}: exactly one LIVE version equal to package version")
    admin_ex = {r[0]: r[3] for r in mapping_wb["Template_Admin_Utility"].iter_rows(min_row=2, values_only=True)}
    check(admin_ex["templateBundleId"] == data[f"{tpl}/package.json"]["templateBundleId"], "Template_Admin_Utility templateBundleId example drift")
    check(admin_ex["packageName"] == data[f"{tpl}/package.json"]["packageName"], "Template_Admin_Utility packageName example drift")
    life = {str(r[0]): r for r in mapping_wb["FXO_Deliverable_Lifecycle"].iter_rows(min_row=2, values_only=True)}
    check("v1.1.0" in life["4"][5], "FXO_Deliverable_Lifecycle step 4 must compose on LIVE v1.1.0")

    # 4. book, inbound trades, MIS
    book = sim.book_rows(mocks_wb)
    trades = data["outbound/api-responses/book/get-trades.200.json"]
    check(trades["items"] == book, "GET /trades items != Excel Prototype_Trade_Book")
    derived = sim.analytics_from_book(book, trades["asOf"])
    check(trades["counts"] == derived["counts"], "GET /trades counts != derived from book")
    check(trades["count"] == len(book), "GET /trades count != book rows")
    for key in ("summary", "aging", "errors", "contagion"):
        check(data[f"outbound/api-responses/analytics/get-{key}.200.json"] == derived[key], f"analytics {key} != derived from book")
    by_trade = {b["tradeId"]: b for b in book}
    for rel, d in data.items():
        if rel.startswith("inbound/trades/"):
            b = by_trade.get(d["tradeId"])
            check(b is not None, f"{rel}: {d['tradeId']} not in Prototype_Trade_Book")
            if b:
                eco, pb = d["trade"]["economics"], mocks.party(d["trade"], "partyB")
                for col, val in [("eventId", d["eventId"]), ("receivedAt", d["occurredAt"]), ("mcaPath", mocks.mca_path(d["trade"])), ("partyBName", pb["partyName"]),
                                 ("partyBLei", pb["lei"]), ("optionType", eco["optionType"]), ("callCurrency", eco["callCurrency"]),
                                 ("callCurrencyAmount", eco["callCurrencyAmount"]), ("strikePrice", eco["strikePrice"]), ("expirationDate", eco["expirationDate"])]:
                    check(b[col] == val, f"{rel}: book {col}={b[col]!r} != trade file {val!r}")

    for b in book:
        check(b["timelineAvailable"] == (f"timeline/{b['tradeId']}.json" in files), f"book {b['tradeId']}: timelineAvailable != timeline file exists")

    # 5. timeline <-> audit <-> book
    audits = {a["auditId"]: a for a in data["timeline/audit-events.json"]["items"]}
    for rel, d in data.items():
        if not rel.startswith("timeline/TR-"):
            continue
        evs = d["events"]
        check([e["at"] for e in evs] == sorted(e["at"] for e in evs), f"{rel}: events not time-ordered")
        for e in evs:
            a = audits.get(e["auditId"])
            check(a is not None and (a["at"], a["action"], a["tradeId"]) == (e["at"], e["action"], e["tradeId"]), f"{rel}: {e['timelineEventId']} audit link broken")
        b = by_trade[d["tradeId"]]
        upto = [e for e in evs if e["at"] <= trades["asOf"]]
        check(upto and upto[-1]["status"] == b["status"], f"{rel}: status at book asOf != book status {b['status']}")
        docs = [e["documentId"] for e in upto if e["documentId"]]
        check((docs[-1] if docs else None) == b["documentId"], f"{rel}: documentId at book asOf != book documentId")
    tpl_audit = data["outbound/api-responses/TB-FXO-DEL-2026-001/04-get-template-audit.after-activate.200.json"]["items"]
    check(all(audits.get(a["auditId"]) == a for a in tpl_audit), "template audit items not in audit-events.json")

    # 6. docs, stories, ids
    known_ids = set()
    for s in excel_strings(mapping_wb, mocks_wb):
        known_ids.update(ID_RE.findall(s))
    for d in data.values():
        known_ids.update(ID_RE.findall(json.dumps(d)))
    doc_files = sorted({p for g in DOC_GLOBS for p in REPO.glob(g)})
    check(bool(doc_files), "no design docs found")
    for p in sorted({p for g in ID_SCAN_GLOBS for p in REPO.glob(g)}):
        for tid in set(ID_RE.findall(p.read_text(encoding="utf-8"))):
            check(tid in known_ids, f"{p.relative_to(REPO)}: id {tid} not in Excel or prototype/data")
    for p in doc_files:
        rel_doc = p.relative_to(REPO).as_posix()
        text = p.read_text(encoding="utf-8")
        for ref in set(DATA_REF_RE.findall(text)):
            check(ref in files, f"{rel_doc}: cites missing prototype/data/{ref}")
        for method, path in set(API_RE.findall(text)):
            check(path_known(method, path, paths), f"{rel_doc}: {method} {path} not in openapi.md")
        if rel_doc.startswith("docs/design/"):
            check(re.search(r"^## EDGE / STUB", text, re.M) is not None, f"{rel_doc}: missing '## EDGE / STUB' section")
        if rel_doc.startswith("docs/design/screens/"):
            for rx, what in [(r"\bK[1-5]\b", "kite id"), (r"\bS[1-5]\b", "sea id"), (r"\bF[1-5][a-c]\b", "fish id")]:
                check(re.search(rx, text) is not None, f"{rel_doc}: no story-map {what} (PRD §9.3)")
            check(bool(DATA_REF_RE.search(text)), f"{rel_doc}: no prototype/data reference")
            check(bool(API_RE.search(text)), f"{rel_doc}: no API path reference")
        for header, trows in md_tables(text):
            low = [h.lower() for h in header]
            if low[:4] == ["ui label", "file", "json path", "example"] or {"file", "path", "value"} <= set(low):
                fi, pi, vi = (1, 2, 3) if low[0] == "ui label" else (low.index("file"), low.index("path"), low.index("value"))
                for r in trows:
                    rel = r[fi].removeprefix("prototype/data/")
                    if rel not in data:
                        check(False, f"{rel_doc}: binding file {r[fi]} missing")
                        continue
                    try:
                        got = as_text(jpath(data[rel], r[pi]))
                    except (KeyError, IndexError, TypeError):
                        check(False, f"{rel_doc}: path {r[pi]} not in {rel}")
                        continue
                    check(got == r[vi], f"{rel_doc}: {rel} {r[pi]} = {got!r}, doc says {r[vi]!r}")

    if errors:
        print(f"FAIL: {len(errors)} of {checks} checks")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"OK: {len(files)} prototype files, {len(doc_files)} docs, {checks} checks passed")


if __name__ == "__main__":
    main()

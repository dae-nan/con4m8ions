#!/usr/bin/env python3
"""Phase 2: patch the canonical Excel workbooks, then export prototype/data/ from them.

1. Patch Phase 1 gaps in docs/mappings/*.xlsx in place (idempotent).
2. Write sheets `Prototype_Trade_Book` + `Prototype_Sim` into the payload-mocks workbook.
3. Export every `Prototype_Sim` row to prototype/data/<File> (resolving $ref into mock rows).

Run: .venv/bin/python scripts/build_prototype_data.py   then   scripts/check_prototype_sync.py
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys

from openpyxl.styles import Alignment, Font, PatternFill

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import generate_fxo_payload_mocks as phase1_mocks  # noqa: E402
import prototype_sim as sim  # noqa: E402

PKG = "TB-FXO-DEL-2026-001"
PKG_NAME = "2026 FXO Deliverable (II-B)"
MCA = "MCA-SCB-ACME-2026-001"
RULE = "PSR-FXO-DEL-2026-001"
AS_OF_BOOK = "2027-12-01T16:30:00Z"
AS_OF_TEMPLATES = "2027-12-01T15:59:00Z"
ADMIN = "u.admin.lee"
OPS = "u.ops.tan"
TPS = "svc.tps"
CDU = "svc.cdu-ps"
SDX = "svc.smartdx-mock"
AFF = "svc.affirm-webhook"

ACME = {"name": "ACME Corp Treasury", "lei": "549300ABCDEFGH123456"}
GLOBEX = {
    "name": "Globex Holdings Ltd",
    "lei": "549300TRANSFeree0001",
    "address": "200 Novation Ave, New York NY 10005",
    "office": "New York",
}
INITECH = {"name": "Initech Treasury Ltd", "lei": "549300INITECH0000042"}

CA_BESPOKE = (
    "Party A; provided that if an Event of Default has occurred with respect to Party A, "
    "Party B may appoint a leading dealer as Calculation Agent"
)
MANUAL_REASON = "Counterparty requested bespoke Calculation Agent wording"


def t(hms: str, day: str = "2027-12-01") -> str:
    return f"{day}T{hms}Z"


def ref(target: str, merge: dict | None = None) -> dict:
    node = {"$ref": target}
    if merge is not None:
        node["$merge"] = merge
    return node


# ---------------------------------------------------------------------------
# 1. Excel gap patches
# ---------------------------------------------------------------------------


def style_header(ws):
    for cell in ws[1]:
        cell.fill = PatternFill("solid", fgColor="1F4E79")
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def append_once(ws, key_cols: int, row: list):
    key = tuple(row[:key_cols])
    for r in ws.iter_rows(min_row=2, values_only=True):
        if tuple(r[:key_cols]) == key:
            return
    ws.append(row)


def patch_mapping(wb):
    life = wb["FXO_Deliverable_Lifecycle"]
    versions = {
        "4": "LIVE TB-FXO-DEL-2026-001 v1.1.0",
        "5": "v1.1.0",
        "6": "v1.1.0",
        "7": "v1.1.0",
        "8": "v1.1.0 → v1.2.0",
        "9": "v1.2.0",
        "10": "v1.2.0",
        "23": "v1.2.0 → v1.1.0",
    }
    for row in life.iter_rows(min_row=2):
        step = str(row[0].value)
        if step in versions:
            row[5].value = versions[step]
        if step == "8":
            row[8].value = "Edge E1 (wrong→hot-swap); ideal path skips steps 8–10 and 23"
        if step == "9":
            row[4].value = "Regenerate with v1.2.0; supersede prior"
        if step == "11":
            row[8].value = "Ideal path: affirms DOC-001 sent on v1.1.0"

    amap = wb["Attribute_Product_Map"]
    premium_row = None
    for row in amap.iter_rows(min_row=2):
        name, exhibit = row[0].value, row[6].value
        if exhibit == "II-B" and name == "Premium":
            row[15].value = "trade.economics.premiumAmount"
            premium_row = [c.value for c in row]
        if exhibit == "II-B" and name == "Premium Payment Date":
            row[15].value = "trade.economics.premiumPaymentDate"
    template_row = next(
        [c.value for c in r] for r in amap.iter_rows(min_row=2) if r[0].value == "Template Version"
    )
    prem_ccy = list(premium_row)
    prem_ccy[0] = "Premium Currency"
    prem_ccy[2] = "string"
    prem_ccy[15] = "trade.economics.premiumCurrency"
    prem_ccy[19] = "Phase 2: added to match LDM FxOptionEconomics.premiumCurrency and payload mocks"
    append_once(amap, 1, prem_ccy)
    for name, path, note in [
        ("Assembly Requested Mode", "assembly.requestedMode", "Phase 2: optional TPs hint AUTOMATED|MANUAL_DRAFTING|MANUAL_ENTRY"),
        ("Assembly Mode Reason", "assembly.reason", "Phase 2: free-text reason when requestedMode is manual"),
    ]:
        r = list(template_row)
        r[0], r[2], r[4], r[15], r[17], r[19] = name, "string", "AssemblyRun", path, None, note
        append_once(amap, 1, r)

    ldm = wb["Logical_Data_Model"]
    for row in ldm.iter_rows(min_row=2):
        if row[0].value == "TemplatePackage" and row[1].value == "version":
            row[3].value = "string"
            row[6].value = "Semver e.g. 1.1.0 (same as Template_Admin_Utility.version)"
    for r in [
        ["Trade", "receivedAt", "", "datetime", "", "1", "Phase 2: first NEW_TRADE accepted"],
        ["AssemblyRun", "templateVersion", "", "string", "TemplatePackage", "1", "Phase 2: package version pinned at run start"],
        ["AssemblyRun", "completedAt", "", "datetime", "", "0..1", "Phase 2"],
        ["ManualDraftContent", "draftedBy", "", "string", "", "1", "Phase 2: was in PRD ER, missing here"],
        ["ManualDraftContent", "savedAt", "", "datetime", "", "1", "Phase 2"],
        ["DocumentArtifact", "tradeId", "FK", "string", "Trade", "N:1", "Phase 2"],
        ["DocumentArtifact", "smartdxDocumentId", "", "string", "", "0..1", "Phase 2: SDX-<documentId>"],
        ["DocumentArtifact", "status", "", "enum", "", "1", "Phase 2: GENERATED|RESENT|SUPERSEDED"],
        ["DocumentArtifact", "priorDocumentId", "FK", "string?", "DocumentArtifact", "0..1", "Phase 2: supersession link"],
        ["DocumentArtifact", "createdAt", "", "datetime", "", "1", "Phase 2"],
        ["TimelineEvent", "eventId", "FK", "string?", "LifecycleEvent", "0..1", "Phase 2"],
        ["TimelineEvent", "lane", "", "enum", "", "1", "Phase 2: TPs|CDU-PS|SmartDX|Counterparty"],
        ["TimelineEvent", "status", "", "enum", "Trade", "1", "Phase 2: trade status after event (PRD §13.2)"],
        ["TimelineEvent", "templateVersion", "", "string?", "TemplatePackage", "0..1", "Phase 2"],
        ["TimelineEvent", "auditId", "FK", "string", "AuditEvent", "1", "Phase 2: AuditEvent feeds TimelineEvent"],
        ["TimelineEvent", "detail", "", "string?", "", "0..1", "Phase 2: one-line human summary"],
    ]:
        append_once(ldm, 2, r)

    admin = wb["Template_Admin_Utility"]
    append_once(admin, 1, ["packageName", "Display name of the TemplatePackage", "ALL", PKG_NAME, "Y", "Phase 2"])
    append_once(
        admin,
        1,
        ["reason", "Activation / hot-swap reason code", "ALL", "PLANNED_RELEASE|WRONG_PRODUCT_BINDING_FIXED", "N", "Phase 2"],
    )
    for row in admin.iter_rows(min_row=2):
        if row[0].value == "mcaRequired":
            row[5].value = "false = MCA optional; Legal Resolver branches per trade (Phase 2 LIVE FXO package)"

    legend = wb["Legend_Assumptions"]
    append_once(legend, 1, ["Phase 2 sim", "Prototype_Sim + Prototype_Trade_Book sheets live in the payload-mocks workbook"])
    append_once(legend, 1, ["LIVE FXO package", f"{PKG} v1.1.0 LIVE; v1.2.0 DRAFT activated 2027-12-01T16:00:00Z in the admin flow"])


def rename_settlement(node):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "settlement" and isinstance(v, str):
                out["settlementMethod"] = v
            else:
                out[k] = rename_settlement(v)
        return out
    if isinstance(node, list):
        return [rename_settlement(v) for v in node]
    return node


def patch_mocks(wb):
    for sheet in ("With_MCA", "Without_MCA"):
        for row in wb[sheet].iter_rows(min_row=2):
            if row[3].value:
                row[3].value = json.dumps(rename_settlement(json.loads(row[3].value)), indent=2, ensure_ascii=False)
    for row in wb["Sample_Trade_Card"].iter_rows(min_row=2):
        if row[0].value == "economics.settlement":
            row[0].value = "economics.settlementMethod"
    append_once(wb["Legend"], 1, ["Prototype_Trade_Book", "Phase 2 ops-desk book (6 FXO trades) behind GET /trades and MIS"])
    append_once(wb["Legend"], 1, ["Prototype_Sim", "Phase 2 simulation script: one row per prototype/data file; $ref points at rows here"])
    append_once(wb["LDM_Map"], 1, ["assembly.*", "AssemblyRun", "Phase 2 optional TPs hint"])
    append_once(wb["LDM_Map"], 1, ["timeline events[]", "TimelineEvent / AuditEvent", "Phase 2 prototype/data/timeline"])


# ---------------------------------------------------------------------------
# 2. Simulation content
# ---------------------------------------------------------------------------

BOOK = [
    ["TR-FXO-004", "evt_2004", t("16:29:30"), INITECH["name"], INITECH["lei"], "Without_MCA", "AUD Call / USD Put", "AUD", "4000000", "0.6650", "2028-01-15", "Received", None, None, None, None, None, None, None],
    ["TR-FXO-003", "evt_2003", t("16:25:00"), ACME["name"], ACME["lei"], "With_MCA", "EUR Put / USD Call", "EUR", "3000000", "1.0700", "2028-02-29", "Composing", "AR-FXO-003-01", "AUTOMATED", "1.2.0", None, None, None, None],
    ["TR-FXO-005", "evt_2005", t("14:20:00"), GLOBEX["name"], GLOBEX["lei"], "Without_MCA", "EUR Call / USD Put", "EUR", "2500000", "1.0900", "2027-12-31", "ManualDraft", "AR-FXO-005-01", "MANUAL_DRAFTING", "1.1.0", None, None, None, None],
    ["TR-FXO-002", "evt_2002", t("13:15:00"), GLOBEX["name"], GLOBEX["lei"], "Without_MCA", "GBP Call / USD Put", "GBP", "2000000", "1.2700", "2028-01-31", "AffirmPending", "AR-FXO-002-01", "AUTOMATED", "1.1.0", "DOC-102", None, t("13:15:04"), None],
    ["TR-FXO-001", "evt_1001", t("10:00:00"), ACME["name"], ACME["lei"], "With_MCA", "EUR Call / USD Put", "EUR", "1000000", "1.0850", "2027-12-31", "Affirmed", "AR-FXO-001-01", "AUTOMATED", "1.1.0", "DOC-001", "Affirmed", t("10:00:04"), t("15:04:05")],
    ["TR-FXO-006", "evt_2006", t("09:00:00"), INITECH["name"], INITECH["lei"], "Without_MCA", "USD Call / JPY Put", "USD", "5000000", "151.20", "2028-03-01", "Affirmed", "AR-FXO-006-01", "AUTOMATED", "1.1.0", "DOC-106", "Affirmed", t("09:00:04"), t("11:30:00")],
]

AUDIT: list[dict] = []
TIMELINES: dict[str, list[dict]] = {}


def audit(aid, at, actor, action, etype, eid, before=None, after=None, trade=None, corr=None):
    ev = {
        "auditId": aid,
        "at": at,
        "actorId": actor,
        "action": action,
        "entityType": etype,
        "entityId": eid,
        "beforeVersion": before,
        "afterVersion": after,
        "tradeId": trade,
        "correlationId": corr,
    }
    AUDIT.append(ev)
    return ev


def trade_events(trade, num, evt, steps):
    """steps: (at, actor, lane, action, status, entityType, entityId, documentId, version, detail, corr)."""
    events = []
    for i, (at, actor, lane, action, status, etype, eid, doc, ver, detail, corr) in enumerate(steps, 1):
        aid = f"AUD-{num}{i:02d}"
        audit(aid, at, actor, action, etype, eid, after=ver, trade=trade, corr=corr)
        events.append(
            {
                "timelineEventId": f"TL-{num}-{i:02d}",
                "tradeId": trade,
                "eventId": evt,
                "at": at,
                "actor": actor,
                "lane": lane,
                "action": action,
                "status": status,
                "documentId": doc,
                "templateVersion": ver,
                "auditId": aid,
                "detail": detail,
            }
        )
    TIMELINES[trade] = events
    return events


def template_audit():
    audit("AUD-0001", t("09:00:00", "2027-10-01"), ADMIN, "template.created", "TemplatePackage", PKG, None, "1.0.0", corr="req_tpl_create_100")
    audit("AUD-0002", t("09:00:00", "2027-10-15"), ADMIN, "template.activated", "TemplatePackage", PKG, None, "1.0.0", corr="req_tpl_activate_100")
    audit("AUD-0003", t("09:00:00", "2027-11-10"), ADMIN, "template.version_added", "TemplatePackage", PKG, None, "1.1.0", corr="req_tpl_put_110")
    audit("AUD-0004", t("00:00:00", "2027-11-22"), ADMIN, "template.activated", "TemplatePackage", PKG, "1.0.0", "1.1.0", corr="req_tpl_activate_110")
    audit("AUD-0005", t("09:00:00", "2027-11-28"), ADMIN, "template.version_added", "TemplatePackage", PKG, None, "1.2.0", corr="req_tpl_put_120")
    audit("AUD-0006", t("09:10:00", "2027-11-28"), CDU, "template.validated", "TemplatePackage", PKG, None, "1.2.0", corr="req_tpl_put_120")
    audit("AUD-0007", t("16:00:00"), ADMIN, "template.activated", "TemplatePackage", PKG, "1.1.0", "1.2.0", corr="req_tpl_activate_120")


def build_timelines():
    ar1, ar5 = "AR-FXO-001-01", "AR-FXO-005-01"
    trade_events(
        "TR-FXO-001",
        "01",
        "evt_1001",
        [
            (t("10:00:00"), TPS, "TPs", "trade.received", "Received", "Trade", "TR-FXO-001", None, None, "NEW_TRADE evt_1001 via POST /events", "evt_1001"),
            (t("10:00:01"), CDU, "CDU-PS", "trade.dq_passed", "Composing", "Trade", "TR-FXO-001", None, None, "Rules_DQ passed, 0 errors", "evt_1001"),
            (t("10:00:02"), CDU, "CDU-PS", "legal.resolved", "Composing", "AssemblyRun", ar1, None, None, f"2026 FX Definitions Main Book 1.0 · With_MCA {MCA}", "evt_1001"),
            (t("10:00:02"), CDU, "CDU-PS", "package.located", "Composing", "AssemblyRun", ar1, None, "1.1.0", f"{RULE} → {PKG} v1.1.0", "evt_1001"),
            (t("10:00:03"), CDU, "CDU-PS", "assembly.completed", "Composing", "AssemblyRun", ar1, "DOC-001", "1.1.0", "AUTOMATED · Exhibit I letter + II-B insert", "evt_1001"),
            (t("10:00:04"), CDU, "CDU-PS", "document.sent", "Sent", "DocumentArtifact", "DOC-001", "DOC-001", "1.1.0", "POST /mock/smartdx/documents", "evt_1001"),
            (t("10:00:04"), SDX, "SmartDX", "document.created", "AffirmPending", "DocumentArtifact", "DOC-001", "DOC-001", "1.1.0", "SDX-DOC-001 generated", "evt_1001"),
            (t("10:00:05"), CDU, "TPs", "callback.sent", "AffirmPending", "DocumentArtifact", "DOC-001", "DOC-001", "1.1.0", "NEW_TRADE generation ack to TPs", "evt_1001"),
            (t("15:04:05"), AFF, "Counterparty", "affirm.affirmed", "Affirmed", "DocumentArtifact", "DOC-001", "DOC-001", "1.1.0", "Affirmed, 0 differences", "req_aff_doc001"),
            (t("15:04:06"), CDU, "TPs", "callback.sent", "Affirmed", "DocumentArtifact", "DOC-001", "DOC-001", "1.1.0", "AFFIRM callback to TPs", "req_aff_doc001"),
        ],
    )
    trade_events(
        "TR-FXO-005",
        "05",
        "evt_2005",
        [
            (t("14:20:00"), TPS, "TPs", "trade.received", "Received", "Trade", "TR-FXO-005", None, None, "NEW_TRADE evt_2005 via POST /events", "evt_2005"),
            (t("14:20:01"), CDU, "CDU-PS", "trade.dq_passed", "Composing", "Trade", "TR-FXO-005", None, None, "Rules_DQ passed, 0 errors", "evt_2005"),
            (t("14:20:02"), CDU, "CDU-PS", "legal.resolved", "Composing", "AssemblyRun", ar5, None, None, "2026 FX Definitions Main Book 1.0 · Without_MCA long-form", "evt_2005"),
            (t("14:20:02"), CDU, "CDU-PS", "package.located", "Composing", "AssemblyRun", ar5, None, "1.1.0", f"{RULE} → {PKG} v1.1.0", "evt_2005"),
            (t("14:20:03"), CDU, "CDU-PS", "assembly.manual_started", "ManualDraft", "AssemblyRun", ar5, None, "1.1.0", f"MANUAL_DRAFTING requested by TPs: {MANUAL_REASON}", "evt_2005"),
            (t("16:52:00"), OPS, "CDU-PS", "assembly.manual_saved", "ManualDraft", "AssemblyRun", ar5, None, "1.1.0", "ManualDraftContent MDC-005-01 saved (elections block)", "req_md_save_005"),
            (t("16:55:00"), OPS, "CDU-PS", "assembly.manual_submitted", "Composing", "AssemblyRun", ar5, "DOC-105", "1.1.0", "Submitted to SmartDX", "req_md_submit_005"),
            (t("16:55:01"), CDU, "CDU-PS", "document.sent", "Sent", "DocumentArtifact", "DOC-105", "DOC-105", "1.1.0", "POST /mock/smartdx/documents", "req_md_submit_005"),
            (t("16:55:01"), SDX, "SmartDX", "document.created", "AffirmPending", "DocumentArtifact", "DOC-105", "DOC-105", "1.1.0", "SDX-DOC-105 generated", "req_md_submit_005"),
            (t("16:55:02"), CDU, "TPs", "callback.sent", "AffirmPending", "DocumentArtifact", "DOC-105", "DOC-105", "1.1.0", "NEW_TRADE generation ack to TPs", "req_md_submit_005"),
        ],
    )


def letter_for_005(edited: bool) -> dict:
    saved = copy.deepcopy(phase1_mocks.SAMPLE)
    try:
        phase1_mocks.SAMPLE["parties"]["partyB"] = {k: GLOBEX[k] for k in ("name", "lei", "address", "office")}
        letter = phase1_mocks.exhibit_i_letter("Without_MCA")
    finally:
        phase1_mocks.SAMPLE.clear()
        phase1_mocks.SAMPLE.update(saved)
    letter["proseLetter"] = letter["proseLetter"].replace("Party B fxconfirm@acme.example", "Party B fxconfirm@globex.example")
    if edited:
        letter["blocks"]["elections"]["calculationAgent"] = CA_BESPOKE
        letter["proseLetter"] = letter["proseLetter"].replace("Calculation Agent: Party A\n", f"Calculation Agent: {CA_BESPOKE}\n")
    return letter


def version_entry(version, status, activated, retired, master):
    return {
        "version": version,
        "status": status,
        "activatedAt": activated,
        "retiredAt": retired,
        "masterTemplateVersionId": master,
        "productTemplateVersionId": "TV-IIB-2026-1.1.0" if version != "1.0.0" else "TV-IIB-2026-1.0.0",
    }


def package(before: bool) -> dict:
    v = [
        version_entry("1.0.0", "RETIRED", t("09:00:00", "2027-10-15"), t("00:00:00", "2027-11-22"), "TV-I-2026-1.0.0"),
        version_entry("1.1.0", "LIVE" if before else "RETIRED", t("00:00:00", "2027-11-22"), None if before else t("16:00:00"), "TV-I-2026-1.1.0"),
        version_entry("1.2.0", "DRAFT" if before else "LIVE", None if before else t("16:00:00"), None, "TV-I-2026-1.2.0"),
    ]
    live = "1.1.0" if before else "1.2.0"
    return {
        "packageId": PKG,
        "templateBundleId": PKG,
        "packageName": PKG_NAME,
        "masterTemplateId": "EXH-I-2026-v1",
        "productExhibitId": "II-B",
        "productType": "Deliverable_FX_Option",
        "supplementExhibitIds": [],
        "matrixBindings": {"SRO": None},
        "mcaRequired": False,
        "legalDefsYear": "2026",
        "hotReloadEnabled": True,
        "resendPolicy": "MANUAL",
        "version": live,
        "status": "LIVE",
        "activatedAt": t("00:00:00", "2027-11-22") if before else t("16:00:00"),
        "rollbackTargetVersion": "1.0.0" if before else "1.1.0",
        "masterTemplateVersionId": f"TV-I-2026-{live}",
        "productTemplateVersionId": "TV-IIB-2026-1.1.0",
        "supplementTemplateVersionId": None,
        "routingRules": {"Deliverable_FX_Option": {"NEW_TRADE": PKG}},
        "selectionRuleIds": [RULE],
        "versions": v,
        "audit": {
            "lastChangedBy": ADMIN,
            "lastChangedAt": t("09:10:00", "2027-11-28") if before else t("16:00:00"),
        },
        "notes": "One LIVE package serves With_MCA and Without_MCA trades; Legal Resolver picks the agreement clause variant.",
    }


VALIDATION_CHECKS = [
    {"check": "Every field resolves to an Attribute_Product_Map row", "result": "PASSED"},
    {"check": "DQ rules bound for every required II-B field", "result": "PASSED"},
    {"check": "Sample render of TR-FXO-001 (With_MCA) and Without_MCA", "result": "PASSED"},
]

CHANGE_120 = [
    {
        "block": "elections",
        "attribute": "Contact details for notice Party A",
        "tpsJsonPath": "trade.notices.partyA",
        "before": "ops-fx@scb.example",
        "after": "ops-fx@scb.example; SmartDX Docbox SCB-SG",
    }
]


def version_detail(version):
    base = {
        "templateBundleId": PKG,
        "version": version,
        "assemblyMode": "AUTOMATED",
        "layers": [],
        "changeLog": None,
        "changes": [],
        "validation": None,
        "audit": None,
    }
    if version == "1.0.0":
        base.update(
            status="RETIRED",
            activatedAt=t("09:00:00", "2027-10-15"),
            retiredAt=t("00:00:00", "2027-11-22"),
            layers=[
                {"templateVersionId": "TV-I-2026-1.0.0", "templateId": "EXH-I-2026-v1", "layer": "MASTER", "exhibitId": "I", "bodyFile": None},
                {"templateVersionId": "TV-IIB-2026-1.0.0", "templateId": "EXH-IIB-2026-v1", "layer": "PRODUCT", "exhibitId": "II-B", "bodyFile": None},
            ],
            changeLog="Initial package for UAT ahead of the 2026 FX Definitions effective date",
            validation={"status": "PASSED", "checkedAt": t("09:05:00", "2027-10-01"), "checks": VALIDATION_CHECKS},
            audit={"lastChangedBy": ADMIN, "lastChangedAt": t("00:00:00", "2027-11-22")},
        )
    elif version == "1.1.0":
        base.update(
            status="LIVE",
            activatedAt=t("00:00:00", "2027-11-22"),
            retiredAt=None,
            layers=[
                {"templateVersionId": "TV-I-2026-1.1.0", "templateId": "EXH-I-2026-v1", "layer": "MASTER", "exhibitId": "I", "bodyFile": "templates/fxo-deliverable-2026/exhibit-i-master.json"},
                {"templateVersionId": "TV-IIB-2026-1.1.0", "templateId": "EXH-IIB-2026-v1", "layer": "PRODUCT", "exhibitId": "II-B", "bodyFile": "templates/fxo-deliverable-2026/exhibit-ii-b-product.json"},
            ],
            changeLog="Cutover to 2026 FX Definitions effective date (22 Nov 2027)",
            validation={"status": "PASSED", "checkedAt": t("09:05:00", "2027-11-10"), "checks": VALIDATION_CHECKS},
            audit={"lastChangedBy": ADMIN, "lastChangedAt": t("00:00:00", "2027-11-22")},
        )
    else:
        base.update(
            status="DRAFT",
            activatedAt=None,
            retiredAt=None,
            layers=[
                {"templateVersionId": "TV-I-2026-1.2.0", "templateId": "EXH-I-2026-v1", "layer": "MASTER", "exhibitId": "I", "bodyFile": None},
                {"templateVersionId": "TV-IIB-2026-1.1.0", "templateId": "EXH-IIB-2026-v1", "layer": "PRODUCT", "exhibitId": "II-B", "bodyFile": "templates/fxo-deliverable-2026/exhibit-ii-b-product.json"},
            ],
            changeLog="Exhibit I notices: add SmartDX Docbox as Party A notice channel",
            changes=CHANGE_120,
            validation={"status": "PASSED", "checkedAt": t("09:10:00", "2027-11-28"), "checks": VALIDATION_CHECKS},
            audit={"lastChangedBy": ADMIN, "lastChangedAt": t("09:10:00", "2027-11-28")},
        )
    return base


def f(attribute, path):
    return {"attribute": attribute, "tpsJsonPath": path}


EXHIBIT_I = {
    "templateVersionId": "TV-I-2026-1.1.0",
    "templateId": "EXH-I-2026-v1",
    "layer": "MASTER",
    "exhibitId": "I",
    "version": "1.1.0",
    "status": "LIVE",
    "blocks": [
        {
            "block": "heading",
            "fields": [
                f("Party A Letterhead", "confirmation.header.partyALetterhead"),
                f("Confirmation Date", "confirmation.header.date"),
                f("Party B Name and Address", "confirmation.header.partyB"),
            ],
            "text": "{{confirmation.header.partyALetterhead}}\n[Letterhead]\n\nDate: {{confirmation.header.date}}\n\n{{confirmation.header.partyB}}",
        },
        {
            "block": "intro",
            "fields": [],
            "text": 'The purpose of this letter (this "Confirmation") is to confirm the terms and conditions of the Transaction entered into between us on the Trade Date specified below (the "Transaction").',
        },
        {
            "block": "definitionsVersion",
            "fields": [f("FX Definitions Version Election", "trade.legal.fxDefinitionsVersion")],
            "text": "The definitions and provisions contained in Version 1.0 of the Main Book of the {{trade.legal.fxDefinitionsVersion}} (as published by ISDA and EMTA, Inc.) are incorporated into this Confirmation.",
        },
        {
            "block": "agreementClause",
            "fields": [
                f("ISDA Master Agreement Date", "trade.legal.isdaMaster.date"),
                f("Long-form Master Agreement Fallback", "trade.legal.longFormFallback"),
                f("Governing Law (long-form)", "trade.legal.governingLaw"),
                f("Termination Currency (long-form)", "trade.legal.terminationCurrency"),
            ],
            "variants": {
                "With_MCA": 'This Confirmation constitutes a "Confirmation" as referred to in, and supplements, forms a part of, and is subject to, the ISDA Master Agreement dated as of {{trade.legal.isdaMaster.date}}, as amended from time to time (the "Agreement").',
                "Without_MCA": "This Confirmation evidences a complete and binding agreement between you and us as to the terms of the Transaction. Until we execute an ISDA Master Agreement, this Confirmation shall be subject to an agreement in the form of the ISDA 2002 Master Agreement (election of {{trade.legal.governingLaw}} as the governing law and {{trade.legal.terminationCurrency}} as the Termination Currency).",
            },
        },
        {
            "block": "productInsert",
            "fields": [],
            "text": "[INSERT Exhibit II-B Confirmation of a Deliverable FX Option Transaction]",
            "productExhibitId": "II-B",
        },
        {
            "block": "elections",
            "fields": [
                f("Party A LEI", "trade.parties.partyA.lei"),
                f("Party B LEI", "trade.parties.partyB.lei"),
                f("Calculation Agent", "trade.legal.calculationAgent"),
                f("Account for payments to Party A", "trade.settlement.accountPartyA"),
                f("Account for payments to Party B", "trade.settlement.accountPartyB"),
                f("Office of Party A", "trade.parties.partyA.office"),
                f("Office of Party B", "trade.parties.partyB.office"),
                f("Governing law", "trade.legal.governingLawConfirm"),
                f("Contact details for notice Party A", "trade.notices.partyA"),
                f("Contact details for notice Party B", "trade.notices.partyB"),
            ],
            "text": "Additional Elections, Account Details, Notices: one line per field",
        },
        {
            "block": "closing",
            "fields": [f("Closing supersession clause", "confirmation.closing.supersession")],
            "text": "This Confirmation supersedes and replaces any other confirmation (including an electronic confirmation), if any, sent in connection with this Transaction on or prior to the date hereof. Please confirm that the foregoing correctly sets forth the terms of our agreement.",
        },
        {
            "block": "signatures",
            "fields": [
                f("Party A signature block", "confirmation.signatures.partyA"),
                f("Party B confirmation signature block", "confirmation.signatures.partyB"),
            ],
            "text": "Yours faithfully, {{trade.parties.partyA.name}} By: ____ / Confirmed as of the date first above written: {{trade.parties.partyB.name}} By: ____",
        },
    ],
}

IIB_FIELDS = [
    ("Transaction Type", "trade.product.transactionType"),
    ("Trade Date", "trade.economics.tradeDate"),
    ("Buyer", "trade.parties.buyer"),
    ("Seller", "trade.parties.seller"),
    ("Option Style", "trade.economics.optionStyle"),
    ("Option Type", "trade.economics.optionType"),
    ("Call Currency", "trade.economics.callCurrency"),
    ("Call Currency Amount", "trade.economics.callCurrencyAmount"),
    ("Put Currency", "trade.economics.putCurrency"),
    ("Strike Price", "trade.economics.strikePrice"),
    ("Settlement", "trade.economics.settlementMethod"),
    ("Expiration Date", "trade.economics.expirationDate"),
    ("Expiration Time", "trade.economics.expirationTime"),
    ("Expiration Time Location", "trade.economics.expirationTimeLocation"),
    ("Automatic Exercise", "trade.economics.automaticExercise"),
    ("Premium", "trade.economics.premiumAmount"),
    ("Premium Currency", "trade.economics.premiumCurrency"),
    ("Premium Payment Date", "trade.economics.premiumPaymentDate"),
]


def exhibit_iib(sample_trade: dict) -> dict:
    fields = []
    for attr, path in IIB_FIELDS:
        fields.append({"attribute": attr, "tpsJsonPath": path, "required": True, "example": sim.pointer_get(sample_trade, "/" + path.replace(".", "/"))})
    return {
        "templateVersionId": "TV-IIB-2026-1.1.0",
        "templateId": "EXH-IIB-2026-v1",
        "layer": "PRODUCT",
        "exhibitId": "II-B",
        "version": "1.1.0",
        "status": "LIVE",
        "title": "Confirmation of a Deliverable FX Option Transaction",
        "exampleTradeId": "TR-FXO-001",
        "fields": fields,
    }


def assembly(trade, ar, evt, mode, status, created, *, path, mca, ver=None, completed=None, conf=None, doc=None, letter=None):
    return {
        "assemblyRunId": ar,
        "tradeId": trade,
        "tradeEventId": evt,
        "templatePackageId": PKG if ver else None,
        "templateVersion": ver,
        "assemblyMode": mode,
        "status": status,
        "createdAt": created,
        "completedAt": completed,
        "confirmationId": conf,
        "documentId": doc,
        "dq": {
            "status": "PASSED",
            "ruleIds": ["DQ-REQ-001", "DQ-REQ-002", "DQ-REQ-003", "DQ-REQ-004", "DQ-REQ-005", "DQ-REQ-006", "DQ-REQ-007", "DQ-CROSS-001", "DQ-ENUM-001", "DQ-ENUM-002", "DQ-ENUM-004", "DQ-FORMAT-003"]
            + (["DQ-MCA-001"] if mca else []),
            "errors": [],
        },
        "legal": {
            "frameworkId": "LF-2026-1.0",
            "defsYear": "2026",
            "mainBookVersion": "1.0",
            "mcaPath": path,
            "mcaProfileId": mca,
            "longFormFallback": mca is None,
            "matrixBindings": {"SRO": None},
        },
        "package": None
        if not ver
        else {
            "ruleId": RULE,
            "templateBundleId": PKG,
            "version": ver,
            "masterTemplateVersionId": "TV-I-2026-1.1.0",
            "productTemplateVersionId": "TV-IIB-2026-1.1.0",
            "supplementTemplateVersionId": None,
        },
        "exhibitILetter": letter,
    }


def events_accepted(evt, trade, at, ar, req):
    return {
        "eventId": evt,
        "tradeId": trade,
        "status": "ACCEPTED",
        "tradeStatus": "Received",
        "assemblyRunId": ar,
        "receivedAt": at,
        "requestId": req,
        "links": {
            "trade": f"/v1/trades/{trade}",
            "timeline": f"/v1/trades/{trade}/timeline",
            "assembly": f"/v1/assemblies/{ar}",
        },
    }


def sim_rows(sample_trade: dict) -> list[list]:
    A, B, C, D = "A Template admin", "B New trade TR-FXO-001", "C Manual draft TR-FXO-005", "D Ops desk + MIS"
    rows = []

    def row(step, flow, at, actor, method, path, contract, file, desc, payload):
        rows.append([step, flow, at, actor, method, path, contract, file, desc, payload])

    tpl = "templates/fxo-deliverable-2026"
    tpl_audit = [a for a in AUDIT if a["entityId"] == PKG]

    # A — Template admin / view
    row("A01", A, AS_OF_TEMPLATES, ADMIN, "GET", "/templates", "response-200", "templates/index.json", "List packages: the LIVE 2026 FXO package",
        {"asOf": AS_OF_TEMPLATES, "count": 1, "items": [{"templateBundleId": PKG, "packageName": PKG_NAME, "productType": "Deliverable_FX_Option", "productExhibitId": "II-B", "version": "1.1.0", "status": "LIVE", "versions": [{"version": v["version"], "status": v["status"]} for v in package(True)["versions"]]}]})
    row("A02", A, AS_OF_TEMPLATES, ADMIN, "GET", "/templates/{id}", "response-200", f"{tpl}/package.json", "View package: overview, versions, bindings", package(True))
    for i, v in enumerate(["1.0.0", "1.1.0", "1.2.0"]):
        row(f"A03{'abc'[i]}", A, AS_OF_TEMPLATES, ADMIN, "GET", "/templates/{id}/versions/{version}", "response-200", f"{tpl}/versions/{v}.json", f"Version {v} detail", version_detail(v))
    row("A04a", A, AS_OF_TEMPLATES, ADMIN, "GET", "/templates/{id}/layers/{templateVersionId}", "response-200", f"{tpl}/exhibit-i-master.json", "Exhibit I MASTER body (tops and tails) TV-I-2026-1.1.0", EXHIBIT_I)
    row("A04b", A, AS_OF_TEMPLATES, ADMIN, "GET", "/templates/{id}/layers/{templateVersionId}", "response-200", f"{tpl}/exhibit-ii-b-product.json", "Exhibit II-B PRODUCT body TV-IIB-2026-1.1.0", exhibit_iib(sample_trade))
    row("A05", A, AS_OF_TEMPLATES, ADMIN, "GET", "/templates/selection-rules", "response-200", f"{tpl}/selection-rules.json", "Bindings: PackageSelectionRule rows",
        {"items": [{"ruleId": RULE, "packageId": PKG, "product": "Deliverable_FX_Option", "subProduct": None, "businessEvent": "NEW_TRADE", "entity": "SCB-SG", "confirmationMethod": "SmartDX", "priority": 10}]})
    row("A06", A, AS_OF_TEMPLATES, ADMIN, "GET", "/templates/{id}/audit", "response-200", f"{tpl}/audit.json", "Audit tab before activation",
        {"templateBundleId": PKG, "items": [ref(f"sim:timeline/audit-events.json#/items/{AUDIT.index(a)}") for a in tpl_audit if a["auditId"] != "AUD-0007"]})
    row("A07", A, t("09:00:00", "2027-11-28"), ADMIN, "PUT", "/templates/{id}/versions", "request", "inbound/ui/TB-FXO-DEL-2026-001.put-version-1.2.0.json", "Draft version 1.2.0 (history: already DRAFT at view time)",
        {"version": "1.2.0", "masterTemplateVersionId": "TV-I-2026-1.2.0", "productTemplateVersionId": "TV-IIB-2026-1.1.0", "supplementTemplateVersionId": None, "assemblyMode": "AUTOMATED",
         "changeLog": ref(f"sim:{tpl}/versions/1.2.0.json#/changeLog"), "changes": ref(f"sim:{tpl}/versions/1.2.0.json#/changes")})
    row("A08", A, t("09:00:00", "2027-11-28"), CDU, "PUT", "/templates/{id}/versions", "response-201", "outbound/api-responses/TB-FXO-DEL-2026-001/01-put-versions.201.json", "DRAFT created; validation runs async",
        {"templateBundleId": PKG, "version": "1.2.0", "status": "DRAFT", "createdAt": t("09:00:00", "2027-11-28"), "validation": {"status": "PENDING"}, "auditId": "AUD-0005", "requestId": "req_tpl_put_120"})
    row("A09", A, t("16:00:00"), ADMIN, "POST", "/templates/{id}/activate", "request", "inbound/ui/TB-FXO-DEL-2026-001.activate-1.2.0.json", "Activate 1.2.0 (same body as mock HOT_SWAP, planned reason)",
        ref("mocks:With_MCA/HOT_SWAP/INBOUND_ADMIN", {"reason": "PLANNED_RELEASE"}))
    row("A10", A, t("16:00:00"), CDU, "POST", "/templates/{id}/activate", "response-200", "outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json", "1.2.0 LIVE; 1.1.0 becomes rollback target",
        {"templateBundleId": PKG, "version": "1.2.0", "status": "LIVE", "activatedAt": t("16:00:00"), "previousLiveVersion": "1.1.0", "rollbackTargetVersion": "1.1.0", "resendPolicy": "MANUAL", "auditId": "AUD-0007", "requestId": "req_tpl_activate_120"})
    row("A11", A, t("16:00:01"), ADMIN, "GET", "/templates/{id}", "response-200", "outbound/api-responses/TB-FXO-DEL-2026-001/03-get-template.after-activate.200.json", "Package after activation", package(False))
    row("A12", A, t("16:00:01"), ADMIN, "GET", "/templates/{id}/audit", "response-200", "outbound/api-responses/TB-FXO-DEL-2026-001/04-get-template-audit.after-activate.200.json", "Audit tab after activation",
        {"templateBundleId": PKG, "items": [ref(f"sim:timeline/audit-events.json#/items/{AUDIT.index(a)}") for a in tpl_audit]})

    # B — New trade TR-FXO-001 (With_MCA) end to end
    d1 = "outbound/api-responses/TR-FXO-001"
    inb1 = "inbound/trades/TR-FXO-001.new-trade.json"
    row("B01", B, t("10:00:00"), TPS, "POST", "/events", "request", inb1, "TPs NEW_TRADE (= mock With_MCA NEW_TRADE INBOUND_TPS)", ref("mocks:With_MCA/NEW_TRADE/INBOUND_TPS"))
    row("B02", B, t("10:00:00"), CDU, "POST", "/events", "response-202", f"{d1}/01-post-events.202.json", "Accepted; AssemblyRun started", events_accepted("evt_1001", "TR-FXO-001", t("10:00:00"), "AR-FXO-001-01", "req_evt_1001"))
    row("B03", B, t("10:00:02"), CDU, "GET", "/assemblies/{id}", "response-200", f"{d1}/02-get-assembly.legal-resolved.200.json", "DQ passed; legal resolved (With_MCA)",
        assembly("TR-FXO-001", "AR-FXO-001-01", "evt_1001", "AUTOMATED", "ASSEMBLING", t("10:00:00"), path="With_MCA", mca=MCA))
    row("B04", B, t("10:00:02"), CDU, "GET", "/assemblies/{id}", "response-200", f"{d1}/03-get-assembly.package-located.200.json", "LIVE package v1.1.0 located",
        assembly("TR-FXO-001", "AR-FXO-001-01", "evt_1001", "AUTOMATED", "ASSEMBLING", t("10:00:00"), path="With_MCA", mca=MCA, ver="1.1.0"))
    row("B05", B, t("10:00:03"), CDU, "GET", "/assemblies/{id}", "response-200", f"{d1}/04-get-assembly.completed.200.json", "Exhibit I letter + II-B assembled",
        assembly("TR-FXO-001", "AR-FXO-001-01", "evt_1001", "AUTOMATED", "COMPLETED", t("10:00:00"), path="With_MCA", mca=MCA, ver="1.1.0", completed=t("10:00:03"), conf="CONF-001", doc="DOC-001",
                 letter=ref("mocks:With_MCA/NEW_TRADE/OUTBOUND_SMARTDX#/exhibitILetter")))
    row("B06", B, t("10:00:04"), CDU, "POST", "/mock/smartdx/documents", "request", "outbound/smartdx/DOC-001.send.json", "Package to SmartDX (= mock OUTBOUND_SMARTDX)", ref("mocks:With_MCA/NEW_TRADE/OUTBOUND_SMARTDX"))
    row("B07", B, t("10:00:04"), SDX, "POST", "/mock/smartdx/documents", "response-201", "outbound/smartdx/DOC-001.generated.json", "SmartDX mock returns letter artifact",
        {"smartdxDocumentId": "SDX-DOC-001", "documentId": "DOC-001", "tradeId": "TR-FXO-001", "status": "GENERATED", "generatedAt": t("10:00:04"), "artifact": {"format": "PDF", "uri": "mock://smartdx/SDX-DOC-001.pdf", "pages": 3}})
    row("B08", B, t("10:00:05"), CDU, "POST", "/callbacks/tps", "request-generated", "outbound/tps-callbacks/TR-FXO-001.01-generated.json", "Generation ack to TPs (= mock CALLBACK_TPS)", ref("mocks:With_MCA/NEW_TRADE/CALLBACK_TPS"))
    row("B09", B, t("15:04:05"), AFF, "POST", "/webhooks/affirmation", "request", "inbound/webhooks/DOC-001.affirmed.json", "Counterparty affirms / matched (= mock INBOUND_WEBHOOK)", ref("mocks:With_MCA/AFFIRM/INBOUND_WEBHOOK"))
    row("B10", B, t("15:04:05"), CDU, "POST", "/webhooks/affirmation", "response-200", f"{d1}/05-post-webhooks-affirmation.200.json", "Webhook accepted; trade Affirmed",
        {"documentId": "DOC-001", "tradeId": "TR-FXO-001", "affirmationStatus": "Affirmed", "tradeStatus": "Affirmed", "receivedAt": t("15:04:05"), "duplicate": False, "requestId": "req_aff_doc001"})
    row("B11", B, t("15:04:05"), CDU, "POST", "/mock/smartdx/documents/{id}/status", "request", "outbound/smartdx/DOC-001.status-affirmed.json", "Status update to SmartDX (= mock AFFIRM OUTBOUND_SMARTDX)", ref("mocks:With_MCA/AFFIRM/OUTBOUND_SMARTDX"))
    row("B12", B, t("15:04:06"), CDU, "POST", "/callbacks/tps", "request-affirm", "outbound/tps-callbacks/TR-FXO-001.02-affirmed.json", "Affirm callback to TPs (= mock AFFIRM CALLBACK_TPS)", ref("mocks:With_MCA/AFFIRM/CALLBACK_TPS"))
    row("B13", B, t("15:04:06"), OPS, "GET", "/trades/{id}", "response-200", f"{d1}/06-get-trade.200.json", "Trade snapshot after affirm",
        {"tradeId": "TR-FXO-001", "productType": "Deliverable_FX_Option", "mcaPath": "With_MCA", "mcaProfileId": MCA, "status": "Affirmed", "affirmationStatus": "Affirmed", "receivedAt": t("10:00:00"), "lastEventAt": t("15:04:06"),
         "eventIds": ["evt_1001"], "assemblyRunId": "AR-FXO-001-01", "currentDocumentId": "DOC-001", "smartdxDocumentId": "SDX-DOC-001",
         "template": {"templateBundleId": PKG, "templateVersion": "1.1.0", "productExhibitId": "II-B"},
         "parties": ref(f"sim:{inb1}#/trade/parties"), "economics": ref(f"sim:{inb1}#/trade/economics")})
    row("B14", B, t("15:04:06"), OPS, "GET", "/documents/{id}", "response-200", f"{d1}/07-get-document.200.json", "Document DOC-001 with letter",
        {"documentId": "DOC-001", "tradeId": "TR-FXO-001", "channel": "SmartDX", "status": "GENERATED", "affirmationStatus": "Affirmed", "templateBundleId": PKG, "templateVersion": "1.1.0", "smartdxDocumentId": "SDX-DOC-001", "priorDocumentId": None, "createdAt": t("10:00:04"),
         "artifact": ref("sim:outbound/smartdx/DOC-001.generated.json#/artifact"), "exhibitILetter": ref("mocks:With_MCA/NEW_TRADE/OUTBOUND_SMARTDX#/exhibitILetter")})
    row("B15", B, t("15:04:06"), OPS, "GET", "/trades/{id}/timeline", "response-200", "timeline/TR-FXO-001.json", "Per-trade timeline (10 events)",
        {"tradeId": "TR-FXO-001", "asOf": t("15:04:06"), "lanes": ["TPs", "CDU-PS", "SmartDX", "Counterparty"], "events": TIMELINES["TR-FXO-001"]})

    # C — Manual draft TR-FXO-005 (Without_MCA)
    d5 = "outbound/api-responses/TR-FXO-005"
    inb5 = "inbound/trades/TR-FXO-005.new-trade.json"
    row("C01", C, t("14:20:00"), TPS, "POST", "/events", "request", inb5, "TPs NEW_TRADE requesting MANUAL_DRAFTING (mock Without_MCA + overrides)",
        ref("mocks:Without_MCA/NEW_TRADE/INBOUND_TPS", {
            "eventId": "evt_2005", "tradeId": "TR-FXO-005", "occurredAt": t("14:20:00"),
            "assembly": {"requestedMode": "MANUAL_DRAFTING", "reason": MANUAL_REASON},
            "trade": {"parties": {"partyB": {k: GLOBEX[k] for k in ("name", "lei", "address", "office")}},
                      "economics": {"callCurrencyAmount": "2500000", "strikePrice": "1.0900", "premiumAmount": "37500"}},
        }))
    row("C02", C, t("14:20:00"), CDU, "POST", "/events", "response-202", f"{d5}/01-post-events.202.json", "Accepted; AssemblyRun started", events_accepted("evt_2005", "TR-FXO-005", t("14:20:00"), "AR-FXO-005-01", "req_evt_2005"))
    row("C03", C, t("14:20:03"), CDU, "GET", "/assemblies/{id}", "response-200", f"{d5}/02-get-assembly.pending-manual-draft.200.json", "Run waits for manual draft",
        assembly("TR-FXO-005", "AR-FXO-005-01", "evt_2005", "MANUAL_DRAFTING", "PENDING_MANUAL_DRAFT", t("14:20:00"), path="Without_MCA", mca=None, ver="1.1.0"))
    row("C04", C, t("16:40:00"), OPS, "GET", "/assemblies/{id}/shell", "response-200", f"{d5}/03-get-assembly-shell.200.json", "Load LIVE template shell for edit (mode a)",
        {"assemblyRunId": "AR-FXO-005-01", "tradeId": "TR-FXO-005", "templateBundleId": PKG, "templateVersion": "1.1.0", "masterTemplateVersionId": "TV-I-2026-1.1.0", "productTemplateVersionId": "TV-IIB-2026-1.1.0",
         "assemblyMode": "MANUAL_DRAFTING", "status": "PENDING_MANUAL_DRAFT", "reason": MANUAL_REASON, "editableBlocks": ["elections"], "loadedBy": OPS, "loadedAt": t("16:40:00"),
         "exhibitILetter": letter_for_005(False), "productBody": {"exhibit": "II-B", "generalTerms": ref(f"sim:{inb5}#/trade/economics")}})
    content = {"blocks": {"elections": {"calculationAgent": CA_BESPOKE}}}
    content_hash = "sha256:" + hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    row("C05", C, t("16:52:00"), OPS, "PUT", "/assemblies/{id}/manual-draft", "request", "inbound/ui/AR-FXO-005-01.put-manual-draft.json", "Save edited elections block",
        {"templateVersionId": "TV-I-2026-1.1.0", "content": content, "draftedBy": OPS})
    row("C06", C, t("16:52:00"), CDU, "PUT", "/assemblies/{id}/manual-draft", "response-200", f"{d5}/04-put-manual-draft.200.json", "ManualDraftContent saved + audited",
        {"id": "MDC-005-01", "assemblyRunId": "AR-FXO-005-01", "templateVersionId": "TV-I-2026-1.1.0", "content": ref("sim:inbound/ui/AR-FXO-005-01.put-manual-draft.json#/content"), "contentHash": content_hash,
         "draftedBy": OPS, "savedAt": t("16:52:00"), "status": "PENDING_MANUAL_DRAFT", "auditId": "AUD-0506"})
    row("C07", C, t("16:55:00"), OPS, "POST", "/assemblies/{id}/submit", "request", "inbound/ui/AR-FXO-005-01.post-submit.json", "Submit manual draft to SmartDX",
        {"submittedBy": OPS, "channels": ["SmartDX"]})
    row("C08", C, t("16:55:00"), CDU, "POST", "/assemblies/{id}/submit", "response-200", f"{d5}/05-post-submit.200.json", "Run COMPLETED; DOC-105 created",
        {"assemblyRunId": "AR-FXO-005-01", "status": "COMPLETED", "confirmationId": "CONF-105", "documentId": "DOC-105", "templateVersion": "1.1.0", "completedAt": t("16:55:00"), "auditId": "AUD-0507", "requestId": "req_md_submit_005"})
    row("C09", C, t("16:55:01"), CDU, "POST", "/mock/smartdx/documents", "request", "outbound/smartdx/DOC-105.send.json", "Manual letter to SmartDX (mock Without_MCA + overrides)",
        ref("mocks:Without_MCA/NEW_TRADE/OUTBOUND_SMARTDX", {
            "documentId": "DOC-105", "tradeId": "TR-FXO-005", "templateVersion": "1.1.0", "manualDraftContentId": "MDC-005-01",
            "exhibitILetter": letter_for_005(True), "productBody": {"generalTerms": ref(f"sim:{inb5}#/trade/economics")},
        }))
    row("C10", C, t("16:55:02"), CDU, "POST", "/callbacks/tps", "request-generated", "outbound/tps-callbacks/TR-FXO-005.01-generated.json", "Generation ack to TPs",
        ref("mocks:Without_MCA/NEW_TRADE/CALLBACK_TPS", {"tradeId": "TR-FXO-005", "documentId": "DOC-105", "smartdxDocumentId": "SDX-DOC-105", "timestamp": t("16:55:02")}))
    row("C11", C, t("16:55:02"), OPS, "GET", "/trades/{id}/timeline", "response-200", "timeline/TR-FXO-005.json", "Per-trade timeline incl. manual markers",
        {"tradeId": "TR-FXO-005", "asOf": t("16:55:02"), "lanes": ["TPs", "CDU-PS", "SmartDX", "Counterparty"], "events": TIMELINES["TR-FXO-005"]})

    # D — Ops desk book + MIS
    book = [dict(zip(sim.BOOK_HEADERS, r)) for r in BOOK]
    analytics = sim.analytics_from_book(book, AS_OF_BOOK)
    row("D01", D, AS_OF_BOOK, OPS, "GET", "/trades", "response-200", "outbound/api-responses/book/get-trades.200.json", "Ops desk queue (= Prototype_Trade_Book)",
        {"asOf": AS_OF_BOOK, "counts": analytics["counts"], "count": len(book), "items": book})
    for key, path in [("summary", "/analytics/summary"), ("aging", "/analytics/aging"), ("errors", "/analytics/queues/errors"), ("contagion", "/analytics/contagion")]:
        row(f"D0{2 + ['summary', 'aging', 'errors', 'contagion'].index(key)}", D, AS_OF_BOOK, "u.mis.lead", "GET", path, "response-200", f"outbound/api-responses/analytics/get-{key}.200.json", f"MIS {key} from book", analytics[key])
    row("D06", D, AS_OF_BOOK, "u.mis.lead", "GET", "/audit", "response-200", "timeline/audit-events.json", "All AuditEvents (template + trades)",
        {"asOf": t("16:55:02"), "count": len(AUDIT), "items": AUDIT})
    return rows


# ---------------------------------------------------------------------------
# 3. Write sheets + export
# ---------------------------------------------------------------------------


def write_sheet(wb, name, headers, rows):
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    ws.append(headers)
    for r in rows:
        ws.append(r)
    style_header(ws)
    for col, width in zip("ABCDEFGHIJ", [8, 22, 22, 16, 8, 34, 18, 60, 48, 80]):
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")


def export(mocks_wb) -> int:
    resolver = sim.Resolver(mocks_wb)
    written = set()
    for r in sim.sim_rows(mocks_wb):
        rel = r["File"]
        out = sim.DATA_DIR / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(sim.dump(resolver.file(rel)), encoding="utf-8")
        written.add(out)
    for stale in sim.DATA_DIR.rglob("*.json"):
        if stale not in written:
            stale.unlink()
    return len(written)


def main():
    mapping_wb, mocks_wb = sim.load_workbooks()
    patch_mapping(mapping_wb)
    patch_mocks(mocks_wb)

    template_audit()
    build_timelines()
    AUDIT.sort(key=lambda a: (a["at"], a["auditId"]))
    sample_trade = sim.mock_payloads(mocks_wb)["With_MCA/NEW_TRADE/INBOUND_TPS"]
    rows = sim_rows(sample_trade)
    for r in rows:
        r[-1] = json.dumps(r[-1], indent=2, ensure_ascii=False)
        if len(r[-1]) > 32000:
            raise SystemExit(f"{r[7]} payload too large for one Excel cell")
    write_sheet(mocks_wb, sim.BOOK_SHEET, sim.BOOK_HEADERS, BOOK)
    write_sheet(mocks_wb, sim.SIM_SHEET, sim.SIM_HEADERS, rows)

    mapping_wb.save(sim.MAPPING_XLSX)
    mocks_wb.save(sim.MOCKS_XLSX)
    _, mocks_wb = sim.load_workbooks()
    n = export(mocks_wb)
    print(f"patched {sim.MAPPING_XLSX.name}, {sim.MOCKS_XLSX.name}; exported {n} files to prototype/data/")


if __name__ == "__main__":
    main()

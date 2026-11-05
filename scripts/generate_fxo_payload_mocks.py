#!/usr/bin/env python3
"""FXO Deliverable lifecycle payload mocks workbook (library; run scripts/build.py).

Trade shape (FpML-style, product-agnostic; see docs/design/modelling-decisions.md):
  trade.parties[]       one entry per party, referenced by id (partyA, partyB, …)
  trade.product         productType, transactionType, buyer/seller party references
  trade.economics       product-specific terms only (no party data)
  trade.documentation   masterAgreement, masterConfirmation (MCA), contractualDefinitions[], contractualMatrix[]
"""
from __future__ import annotations

import copy
import json

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import generate_phase1_mapping as mapping

MCA_ID = "MCA-SCB-ACME-2026-001"

EVENTS = ["NEW_TRADE", "AFFIRM", "AMEND", "NOVATION", "EXERCISE", "TERMINATE", "HOT_SWAP", "RESEND"]

PARTY_A = {
    "id": "partyA",
    "partyName": "Standard Chartered Bank Sample Desk",
    "lei": "5493001KJTIIGC8Y1R12",
    "office": "Singapore",
    "noticeContact": "ops-fx@scb.example",
}
PARTY_B = {
    "id": "partyB",
    "partyName": "ACME Corp Treasury",
    "lei": "549300ABCDEFGH123456",
    "address": "1 Example Street, London EC2N 1HQ",
    "office": "London",
    "noticeContact": "fxconfirm@acme.example",
}
PARTY_C = {
    "id": "partyC",
    "partyName": "Globex Holdings Ltd",
    "lei": "549300TRANSFeree0001",
    "address": "200 Novation Ave, New York NY 10005",
    "office": "New York",
    "noticeContact": "fxconfirm@globex.example",
}

PRODUCT = {
    "productType": "Deliverable_FX_Option",
    "transactionType": "Deliverable FX Option Transaction",
    "buyerPartyReference": {"href": "partyA"},
    "sellerPartyReference": {"href": "partyB"},
}

ECONOMICS = {
    "tradeDate": "2027-12-01",
    "optionStyle": "European",
    "optionType": "EUR Call / USD Put",
    "callCurrency": "EUR",
    "callCurrencyAmount": "1000000",
    "putCurrency": "USD",
    "strikePrice": "1.0850",
    "expirationDate": "2027-12-31",
    "expirationTime": "10:00",
    "expirationTimeLocation": "New York",
    "automaticExercise": "Applicable (presumed)",
    "premiumAmount": "15000",
    "premiumCurrency": "USD",
    "premiumPaymentDate": "2027-12-03",
    "settlementMethod": "Deliverable",
}

TEMPLATE_HINT = {"masterExhibitId": "I", "productExhibitId": "II-B", "supplementExhibitIds": []}

PRODUCT_INSERT = {
    "exhibitId": "II-B",
    "title": "Confirmation of a Deliverable FX Option Transaction",
    "additionalProvisionExhibitIds": [],
}


def documentation(path: str) -> dict:
    with_mca = path == "With_MCA"
    return {
        "masterAgreement": {
            "masterAgreementType": "ISDA2002",
            "masterAgreementDate": "2026-01-15" if with_mca else None,
            "longFormFallback": not with_mca,
            "governingLaw": None if with_mca else "English law",
            "terminationCurrency": None if with_mca else "USD",
        },
        "masterConfirmation": {
            "masterConfirmationId": MCA_ID,
            "masterConfirmationType": "Bilateral FX MCA (Assumed)",
            "masterConfirmationDate": "2026-01-15",
        }
        if with_mca
        else None,
        "contractualDefinitions": [
            {"definitions": "2026 FX Definitions", "publisher": "ISDA/EMTA", "book": "Main Book", "version": "1.0"}
        ],
        "contractualMatrix": [],
    }


def mca_path(trade: dict) -> str:
    return "With_MCA" if trade["documentation"]["masterConfirmation"] else "Without_MCA"


def party(trade: dict, party_id: str) -> dict:
    return next(p for p in trade["parties"] if p["id"] == party_id)


def party_label(party_id: str) -> str:
    return "Party " + party_id.removeprefix("party")


def sample_trade(path: str) -> dict:
    return {
        "parties": [copy.deepcopy(PARTY_A), copy.deepcopy(PARTY_B)],
        "product": copy.deepcopy(PRODUCT),
        "economics": copy.deepcopy(ECONOMICS),
        "documentation": documentation(path),
    }


def general_terms(trade: dict) -> dict:
    """Rendered Exhibit II-B 'General Terms' (labels, not trade data)."""
    eco, prod = trade["economics"], trade["product"]
    return {
        "tradeDate": eco["tradeDate"],
        "transactionType": prod["transactionType"],
        "buyer": party_label(prod["buyerPartyReference"]["href"]),
        "seller": party_label(prod["sellerPartyReference"]["href"]),
        **{k: v for k, v in eco.items() if k != "tradeDate"},
    }


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def exhibit_i_letter(path: str, *, party_b: dict | None = None, novation: bool = False, amend_note: str | None = None) -> dict:
    """Structured + prose mock of the Exhibit I confirmation letter."""
    pa = PARTY_A
    pb = party_b or (PARTY_C if novation else PARTY_B)
    pb_name = pb["partyName"] + (" (Transferee)" if novation else "")
    trade_date = ECONOMICS["tradeDate"]

    if path == "With_MCA":
        agreement = (
            f'This Confirmation constitutes a "Confirmation" as referred to in, and supplements, '
            f'forms a part of, and is subject to, the ISDA Master Agreement dated as of 15 January 2026 '
            f'(Assumed MCA profile {MCA_ID}), as amended from time to time (the "Agreement"), '
            f'between {pa["partyName"]} ("Party A") and {pb_name} ("Party B").'
        )
        ca = "Party A (defaulted from Assumed MCA)"
        gov = "[Omitted — Confirmation subject to executed ISDA Master Agreement]"
        long_form = False
    else:
        agreement = (
            "This Confirmation evidences a complete and binding agreement between you and us as to the terms "
            "of the Transaction. Until we execute an ISDA Master Agreement, this Confirmation shall supplement, "
            "form a part of, and be subject to an agreement in the form of the ISDA 2002 Master Agreement as if "
            "we had executed an agreement in such form (but without any Schedule except for the election of "
            "English law as the governing law and USD as the Termination Currency) on the Trade Date of the first "
            "Transaction between us."
        )
        ca = "Party A"
        gov = "English law"
        long_form = True

    insert_text = (
        f"[INSERT Exhibit {PRODUCT_INSERT['exhibitId']} {PRODUCT_INSERT['title']}"
        + (" — AMENDED terms" if amend_note else "")
        + "]"
    )

    prose = f"""{pa["partyName"]}
[Letterhead]

Date: {trade_date}

{pb_name}
{pb["address"]}

Dear Sir/Madam:

The purpose of this letter (this "Confirmation") is to confirm the terms and conditions of the
Transaction entered into between us on the Trade Date specified below (the "Transaction").

The definitions and provisions contained in Version 1.0 of the Main Book of the 2026 FX Definitions
(as published by ISDA and EMTA, Inc.) are incorporated into this Confirmation. In the event of any
inconsistency between those definitions and provisions and this Confirmation, this Confirmation will govern.

{agreement}
All provisions contained in the Agreement govern this Confirmation except as expressly modified below.
The terms of the Transaction to which this Confirmation relates are as follows:

{insert_text}

Additional Elections, Account Details, Notices:
  Party A LEI: {pa["lei"]}
  Party B LEI: {pb["lei"]}
  Calculation Agent: {ca}
  Account for payments to Party A: [Assumed SSI / explicit SSI]
  Account for payments to Party B: [Assumed SSI / explicit SSI]
  Offices: Party A {pa["office"]}; Party B {pb["office"]}
  Governing law: {gov}
  Contact details for notice: Party A {pa["noticeContact"]}; Party B {pb["noticeContact"]}

This Confirmation supersedes and replaces any other confirmation (including an electronic confirmation),
if any, sent in connection with this Transaction on or prior to the date hereof.
{"Amendment note: " + amend_note if amend_note else ""}

Please confirm that the foregoing correctly sets forth the terms of our agreement by executing
the copy of this Confirmation enclosed for that purpose and returning it to us.

Yours faithfully,
{pa["partyName"]}
By: ________________  Name:  Title:

Confirmed as of the date first above written:
{pb_name}
By: ________________  Name:  Title:
"""

    return {
        "path": path,
        "longFormFallback": long_form,
        "masterConfirmationId": MCA_ID if path == "With_MCA" else None,
        "blocks": {
            "heading": {
                "partyALetterhead": pa["partyName"],
                "confirmationDate": trade_date,
                "partyBName": pb_name,
                "partyBAddress": pb["address"],
            },
            "definitionsVersion": "2026 FX Definitions Main Book Version 1.0",
            "agreementClause": agreement,
            "productInsert": copy.deepcopy(PRODUCT_INSERT),
            "elections": {
                "partyALei": pa["lei"],
                "partyBLei": pb["lei"],
                "calculationAgent": ca,
                "governingLaw": gov,
            },
            "closing": "Supersession + please confirm",
        },
        "proseLetter": prose.strip(),
    }


def tps_new(path: str) -> dict:
    return {
        "eventType": "NEW_TRADE",
        "eventId": "evt_1001",
        "tradeId": "TR-FXO-001",
        "occurredAt": "2027-12-01T10:00:00Z",
        "template": copy.deepcopy(TEMPLATE_HINT),
        "trade": sample_trade(path),
    }


def smartdx_out(path: str, doc_id: str, template_version: str, **letter_kw) -> dict:
    prior = letter_kw.pop("prior", None)
    letter = exhibit_i_letter(path, **letter_kw)
    return {
        "channel": "SmartDX",
        "documentId": doc_id,
        "tradeId": "TR-FXO-001",
        "templateBundleId": "TB-FXO-DEL-2026-001",
        "templateVersion": template_version,
        "exhibits": {"master": "I", "product": "II-B", "supplements": []},
        "mcaPath": path,
        "exhibitILetter": letter,
        "productBody": {"exhibit": "II-B", "generalTerms": general_terms(sample_trade(path))},
        "priorDocumentId": prior,
    }


def callback(event: str, doc_id: str, **extra) -> dict:
    body = {
        "tradeId": "TR-FXO-001",
        "eventType": event,
        "documentId": doc_id,
        "timestamp": "2027-12-01T10:00:05Z",
        "templateVersion": extra.pop("templateVersion", "1.1.0"),
        "smartdxDocumentId": f"SDX-{doc_id}",
        "swiftMsgRef": extra.pop("swiftMsgRef", None),
    }
    body.update(extra)
    return body


def build_rows_for_path(path: str) -> list[list]:
    """Columns: Event, Direction, Description, Payload JSON."""
    rows = []

    def add(event, direction, desc, payload):
        rows.append([event, direction, desc, dumps(payload)])

    add("NEW_TRADE", "INBOUND_TPS", f"Book Deliverable FXO ({path})", tps_new(path))
    add("NEW_TRADE", "OUTBOUND_SMARTDX", "Exhibit I letter + II-B body", smartdx_out(path, "DOC-001", "1.1.0"))
    add("NEW_TRADE", "CALLBACK_TPS", "Generation ack", callback("NEW_TRADE", "DOC-001", status="GENERATED"))

    add("AFFIRM", "INBOUND_WEBHOOK", "Affirm platform Affirmed",
        {"documentId": "DOC-001", "tradeId": "TR-FXO-001", "status": "Affirmed", "timestamp": "2027-12-01T15:04:05Z", "differences": []})
    add("AFFIRM", "OUTBOUND_SMARTDX", "No new doc (status only) — optional ack package",
        {"channel": "SmartDX", "action": "STATUS_UPDATE", "documentId": "DOC-001", "affirmationStatus": "Affirmed"})
    add("AFFIRM", "CALLBACK_TPS", "Affirm callback",
        callback("AFFIRM", "DOC-001", affirmationStatus="Affirmed", timestamp="2027-12-01T15:04:06Z"))

    amend = tps_new(path)
    amend.update({"eventType": "AMEND", "eventId": "evt_1002", "occurredAt": "2027-12-02T11:00:00Z"})
    amend["trade"]["economics"]["strikePrice"] = "1.0900"
    add("AMEND", "INBOUND_TPS", "Strike amend 1.0850→1.0900", amend)
    add("AMEND", "OUTBOUND_SMARTDX", "Recomposed letter + amended II-B",
        smartdx_out(path, "DOC-002", "1.1.0", amend_note="Strike Price amended to 1.0900", prior="DOC-001"))
    add("AMEND", "CALLBACK_TPS", "Amend ack", callback("AMEND", "DOC-002", priorDocumentId="DOC-001", status="GENERATED"))

    novation = {
        "eventType": "NOVATION",
        "eventId": "evt_1003",
        "tradeId": "TR-FXO-001",
        "occurredAt": "2028-01-10T09:00:00Z",
        "novation": {
            "transferorPartyReference": {"href": "partyB"},
            "transfereePartyReference": {"href": "partyC"},
            "remainingPartyReference": {"href": "partyA"},
            "effectiveDate": "2028-01-15",
        },
        "trade": {"parties": [copy.deepcopy(PARTY_A), copy.deepcopy(PARTY_B), copy.deepcopy(PARTY_C)], "documentation": documentation(path)},
    }
    add("NOVATION", "INBOUND_TPS", "Party B → Party C", novation)
    add("NOVATION", "OUTBOUND_SMARTDX", "Exhibit I party blocks refreshed for transferee",
        smartdx_out(path, "DOC-003", "1.1.0", novation=True, prior="DOC-002"))
    add("NOVATION", "CALLBACK_TPS", "Novation ack",
        callback("NOVATION", "DOC-003", novationId="NOV-001", priorDocumentId="DOC-002", timestamp="2028-01-10T09:00:08Z"))

    exercise = {
        "eventType": "EXERCISE",
        "eventId": "evt_1004",
        "tradeId": "TR-FXO-001",
        "occurredAt": "2027-12-31T15:00:00Z",
        "exercise": {"method": "AutomaticExercise", "exerciseDate": "2027-12-31", "inTheMoney": True, "settlementDate": "2028-01-04"},
    }
    add("EXERCISE", "INBOUND_TPS", "Automatic Exercise ITM", exercise)
    add("EXERCISE", "OUTBOUND_SMARTDX", "Exercise / settlement notice package (ops)",
        {"channel": "SmartDX", "documentId": "DOC-004", "tradeId": "TR-FXO-001", "eventType": "EXERCISE",
         "exhibitILetter": {"note": "Exercise notice may reuse MASTER notice contacts from Exhibit I elections"}, "exercise": exercise["exercise"]})
    add("EXERCISE", "CALLBACK_TPS", "Exercise ack", callback("EXERCISE", "DOC-004", status="EXERCISED", timestamp="2027-12-31T15:00:05Z"))

    term = {
        "eventType": "TERMINATE",
        "eventId": "evt_1005",
        "tradeId": "TR-FXO-001",
        "occurredAt": "2027-12-20T12:00:00Z",
        "termination": {"reason": "OPTIONAL_EARLY_TERMINATION", "supplement": "III-D", "effectiveDate": "2027-12-22"},
    }
    add("TERMINATE", "INBOUND_TPS", "OET elected (III-D edge)", term)
    add("TERMINATE", "OUTBOUND_SMARTDX", "Termination confirmation letter",
        {"channel": "SmartDX", "documentId": "DOC-005", "exhibitILetter": exhibit_i_letter(path), "termination": term["termination"]})
    add("TERMINATE", "CALLBACK_TPS", "Terminate ack", callback("TERMINATE", "DOC-005", status="TERMINATED", timestamp="2027-12-20T12:00:05Z"))

    add("HOT_SWAP", "INBOUND_ADMIN", "Activate template v1.2.0",
        {"action": "ACTIVATE", "templateBundleId": "TB-FXO-DEL-2026-001", "version": "1.2.0", "reason": "WRONG_PRODUCT_BINDING_FIXED"})
    add("HOT_SWAP", "OUTBOUND_SMARTDX", "No automatic send unless resendPolicy=AUTO", {"channel": "SmartDX", "action": "NONE", "note": "Await RESEND"})
    add("HOT_SWAP", "CALLBACK_TPS", "Template activated notice",
        {"tradeId": None, "eventType": "HOT_SWAP", "templateBundleId": "TB-FXO-DEL-2026-001", "templateVersion": "1.2.0", "timestamp": "2027-12-01T16:00:00Z"})

    add("RESEND", "INBOUND_ADMIN", "Resend DOC-001 after hot-swap", {"documentId": "DOC-001", "reason": "WRONG_TEMPLATE_CORRECTED", "templateVersion": "1.2.0"})
    add("RESEND", "OUTBOUND_SMARTDX", "Superseding confirmation", smartdx_out(path, "DOC-001R", "1.2.0", prior="DOC-001"))
    add("RESEND", "CALLBACK_TPS", "Resend ack",
        callback("RESEND", "DOC-001R", priorDocumentId="DOC-001", templateVersion="1.2.0", status="RESENT", timestamp="2027-12-01T16:05:00Z"))
    return rows


def error_rows() -> list[list]:
    """One mock error payload per lifecycle event."""

    def err(code, message, request_id, details=None, **extra):
        body = {"code": code, "message": message}
        if details is not None:
            body["details"] = details
        body["requestId"] = request_id
        body.update(extra)
        return {"error": body}

    errs = [
        ("NEW_TRADE", "VALIDATION_FAILED", err("VALIDATION_FAILED", "FXO economics incomplete", "req_err_new",
                                               [{"path": "trade.economics.strikePrice", "ruleId": "DQ-CROSS-001", "message": "Strike required unless Binary"}])),
        ("AFFIRM", "NOT_FOUND", err("NOT_FOUND", "Unknown documentId", "req_err_aff", [{"path": "documentId", "message": "DOC-UNKNOWN"}])),
        ("AMEND", "CONFLICT", err("IDEMPOTENCY_REPLAY_MISMATCH", "Idempotency-Key reused with different body", "req_err_amd")),
        ("NOVATION", "VALIDATION_FAILED", err("VALIDATION_FAILED", "Novation parties incomplete", "req_err_nov",
                                              [{"path": "novation.transfereePartyReference", "ruleId": "DQ-REQ-027", "message": "Required"}])),
        ("EXERCISE", "LEGAL_ELECTION_INVALID", err("LEGAL_ELECTION_INVALID", "Full Automated Exercise requires SRO", "req_err_ex",
                                                   [{"path": "trade.economics.fae.settlementRateOption", "ruleId": "DQ-CROSS-006"}])),
        ("TERMINATE", "VALIDATION_FAILED", err("VALIDATION_FAILED", "III-D not elected on confirmation", "req_err_term",
                                               [{"path": "termination.supplement", "message": "III-D missing from supplementExhibitIds"}])),
        ("HOT_SWAP", "CONFLICT", err("CONFLICT", "Version already LIVE", "req_err_hs", [{"path": "version", "message": "1.2.0"}])),
        ("RESEND", "CHANNEL_UNAVAILABLE", err("CHANNEL_UNAVAILABLE", "SmartDX timeout", "req_err_rs", [{"path": "channel", "message": "SmartDX"}])),
        ("AFFIRM", "AFFIRM_DISPUTED", err("AFFIRM_DISPUTED", "Counterparty disputed economics", "req_err_disp",
                                          [{"path": "differences", "message": "strikePrice local=1.0900 remote=1.0850"}], affirmationStatus="Disputed")),
    ]
    return [[e, code, dumps(body)] for e, code, body in errs]


def flatten(prefix: str, node, out: list):
    if isinstance(node, dict):
        for k, v in node.items():
            flatten(f"{prefix}.{k}" if prefix else k, v, out)
    elif isinstance(node, list) and node and all(isinstance(x, dict) and "id" in x for x in node):
        for x in node:
            flatten(f"{prefix}[id={x['id']}]", {k: v for k, v in x.items() if k != "id"}, out)
    else:
        out.append((prefix, node))


def sample_card_rows() -> list[list]:
    """Field, Value, LDM entity, TPS / mock path — every leaf of the With_MCA NEW_TRADE payload."""
    event = tps_new("With_MCA")
    leaves: list = []
    flatten("", {"tradeId": event["tradeId"], "template": event["template"]}, leaves)
    flatten("trade", event["trade"], leaves)
    rows = []
    for path, value in leaves:
        field = path.removeprefix("trade.")
        shown = dumps(value) if isinstance(value, (dict, list)) else ("null" if value is None else str(value).lower() if isinstance(value, bool) else str(value))
        rows.append([field, shown, mapping.ldm_entity_for_path(path, "II-B"), path])
    return rows


def legend_rows() -> list[list]:
    return [
        ["Sample trade", "TR-FXO-001"],
        ["Product", "Deliverable FX Option / Exhibit II-B"],
        ["Master letter", "Exhibit I confirmation letter wrapper"],
        ["With_MCA sheet", f"Assumed {MCA_ID} path payloads"],
        ["Without_MCA sheet", "Long-form Exhibit I path payloads"],
        ["Errors sheet", "One mock error (or disputed affirm) per event"],
        ["INBOUND_TPS", "Source payload into CDU-PS"],
        ["OUTBOUND_SMARTDX", "Documentation system package incl. exhibitILetter"],
        ["CALLBACK_TPS", "Final / ack response to TPS"],
        ["INBOUND_WEBHOOK", "Affirm platform → CDU-PS"],
        ["INBOUND_ADMIN", "Template admin action"],
        ["Assumed", "Invented MCA sample — not ISDA legal text"],
        ["LDM_Map sheet", "Maps mock field roots to Logical_Data_Model entities"],
        ["Sample_Trade_Card LDM entity col", "Same names as Attribute_Product_Map LDM entity"],
        ["Trade model", "FpML-style: trade.parties[] + trade.product (party references) + trade.economics + trade.documentation"],
        ["Party references", "{\"href\": \"partyA\"} points at trade.parties[id=partyA]; paths written trade.parties[id=partyA].lei"],
        ["Prototype_Trade_Book", "Phase 2 ops-desk book (6 FXO trades) behind GET /trades and MIS"],
        ["Prototype_Sim", "Phase 2 simulation script: one row per prototype/data file; $ref points at rows here"],
        ["Build", "Generated by scripts/build.py — do not edit this workbook by hand"],
    ]


def ldm_map_rows() -> list[list]:
    return [
        ["tradeId / trade.product.*", "Trade / TradeProduct", "productType, transactionType, buyer/seller party references"],
        ["trade.parties[]", "Party", "One entry per party; referenced by id"],
        ["trade.economics.*", "FxOptionEconomics", "II-B only; product-specific terms, no party data"],
        ["trade.documentation.masterAgreement", "Documentation", "ISDA Master Agreement or deemed long-form"],
        ["trade.documentation.masterConfirmation", "MasterConfirmation", "Assumed MCA; null on Without_MCA"],
        ["trade.documentation.contractualDefinitions[]", "LegalFramework", "2026 FX Definitions Main Book version"],
        ["trade.documentation.contractualMatrix[]", "MatrixBinding", "Matrix version pins (empty = latest as of Trade Date)"],
        ["confirmation.* / exhibitILetter", "ExhibitILetter", "MASTER letter (rendered)"],
        ["template.supplementExhibitIds", "SupplementElection", None],
        ["platform.* / smartdxDocumentId", "PlatformContext / DocumentArtifact", None],
        ["novation.*", "NovationTransfer", "Party references into trade.parties[]"],
        ["lifecycle / affirmation", "LifecycleEvent", None],
        ["assembly.*", "AssemblyRun", "Phase 2 optional TPs hint"],
        ["timeline events[]", "TimelineEvent / AuditEvent", "Phase 2 prototype/data/timeline"],
    ]


def style_header(ws):
    fill = PatternFill("solid", fgColor="1F4E79")
    font = Font(bold=True, color="FFFFFF")
    for cell in ws[1]:
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def autosize(ws, max_width=60):
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        width = 14
        for cell in col[:40]:
            if cell.value:
                width = min(max_width, max(width, min(60, len(str(cell.value).split("\n")[0]) + 2)))
        ws.column_dimensions[letter].width = width


def write_sheet(ws, header, rows):
    ws.append(header)
    for r in rows:
        ws.append(r)
    style_header(ws)
    thin = Border(*(Side(style="thin", color="D9D9D9"),) * 4)
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin
    autosize(ws)
    ws.row_dimensions[1].height = 30


def build_workbook() -> Workbook:
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "Legend"
    write_sheet(ws0, ["Key", "Meaning"], legend_rows())
    write_sheet(wb.create_sheet("Sample_Trade_Card"), ["Field", "Value", "LDM entity", "TPS / mock path"], sample_card_rows())
    header = ["Event", "Direction", "Description", "Payload JSON"]
    write_sheet(wb.create_sheet("With_MCA"), header, build_rows_for_path("With_MCA"))
    write_sheet(wb.create_sheet("Without_MCA"), header, build_rows_for_path("Without_MCA"))
    write_sheet(wb.create_sheet("Errors"), ["Event", "Error code", "Error payload JSON"], error_rows())
    letter_with, letter_without = exhibit_i_letter("With_MCA"), exhibit_i_letter("Without_MCA")
    write_sheet(
        wb.create_sheet("ExhibitI_Letter_Ref"),
        ["Path", "Artifact", "Content"],
        [
            ["With_MCA", "blocks JSON", dumps(letter_with["blocks"])],
            ["With_MCA", "proseLetter", letter_with["proseLetter"]],
            ["Without_MCA", "blocks JSON", dumps(letter_without["blocks"])],
            ["Without_MCA", "proseLetter", letter_without["proseLetter"]],
        ],
    )
    write_sheet(wb.create_sheet("LDM_Map"), ["Mock / TPS path root", "LDM entity", "Notes"], ldm_map_rows())
    return wb

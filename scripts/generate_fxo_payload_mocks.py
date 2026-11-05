#!/usr/bin/env python3
"""Generate FXO Deliverable lifecycle payload mocks Excel (Phase 1 docs)."""
from __future__ import annotations

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

REPO = Path("/agent/repos/con4m8ions")
STORE = Path("/cursor/stores/bc-810ee397-0d26-4b38-b43b-2e3d21ebe15f")
OUT_REPO = REPO / "docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx"
OUT_STORE = STORE / "docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx"

EVENTS = [
    "NEW_TRADE",
    "AFFIRM",
    "AMEND",
    "NOVATION",
    "EXERCISE",
    "TERMINATE",
    "HOT_SWAP",
    "RESEND",
]

SAMPLE = {
    "tradeId": "TR-FXO-001",
    "productType": "Deliverable_FX_Option",
    "exhibitProduct": "II-B",
    "exhibitMaster": "I",
    "supplements": [],
    "economics": {
        "tradeDate": "2027-12-01",
        "transactionType": "Deliverable FX Option Transaction",
        "buyer": "Party A",
        "seller": "Party B",
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
        "settlement": "Deliverable",
    },
    "parties": {
        "partyA": {
            "name": "Standard Chartered Bank Sample Desk",
            "lei": "5493001KJTIIGC8Y1R12",
            "office": "Singapore",
        },
        "partyB": {
            "name": "ACME Corp Treasury",
            "lei": "549300ABCDEFGH123456",
            "address": "1 Example Street, London EC2N 1HQ",
            "office": "London",
        },
    },
}


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def exhibit_i_letter(path: str, *, novation: bool = False, amend_note: str | None = None) -> dict:
    """Structured + prose mock of Exhibit I confirmation letter."""
    pa = SAMPLE["parties"]["partyA"]["name"]
    pb = SAMPLE["parties"]["partyB"]["name"]
    pb_addr = SAMPLE["parties"]["partyB"]["address"]
    trade_date = SAMPLE["economics"]["tradeDate"]
    if novation:
        pb = "Globex Holdings Ltd (Transferee)"
        pb_addr = "200 Novation Ave, New York NY 10005"

    if path == "With_MCA":
        agreement = (
            f'This Confirmation constitutes a "Confirmation" as referred to in, and supplements, '
            f'forms a part of, and is subject to, the ISDA Master Agreement dated as of 15 January 2026 '
            f'(Assumed MCA profile MCA-SCB-ACME-2026-001), as amended from time to time (the "Agreement"), '
            f'between {pa} ("Party A") and {pb} ("Party B").'
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

    insert = (
        "[INSERT Exhibit II-B Confirmation of a Deliverable FX Option Transaction"
        + (" — AMENDED terms" if amend_note else "")
        + "]"
    )

    prose = f"""{pa}
[Letterhead]

Date: {trade_date}

{pb}
{pb_addr}

Dear Sir/Madam:

The purpose of this letter (this "Confirmation") is to confirm the terms and conditions of the
Transaction entered into between us on the Trade Date specified below (the "Transaction").

The definitions and provisions contained in Version 1.0 of the Main Book of the 2026 FX Definitions
(as published by ISDA and EMTA, Inc.) are incorporated into this Confirmation. In the event of any
inconsistency between those definitions and provisions and this Confirmation, this Confirmation will govern.

{agreement}
All provisions contained in the Agreement govern this Confirmation except as expressly modified below.
The terms of the Transaction to which this Confirmation relates are as follows:

{insert}

Additional Elections, Account Details, Notices:
  Party A LEI: {SAMPLE["parties"]["partyA"]["lei"]}
  Party B LEI: {SAMPLE["parties"]["partyB"]["lei"] if not novation else "549300TRANSFeree0001"}
  Calculation Agent: {ca}
  Account for payments to Party A: [Assumed SSI / explicit SSI]
  Account for payments to Party B: [Assumed SSI / explicit SSI]
  Offices: Party A {SAMPLE["parties"]["partyA"]["office"]}; Party B {SAMPLE["parties"]["partyB"]["office"] if not novation else "New York"}
  Governing law: {gov}
  Contact details for notice: Party A ops-fx@scb.example; Party B fxconfirm@acme.example

This Confirmation supersedes and replaces any other confirmation (including an electronic confirmation),
if any, sent in connection with this Transaction on or prior to the date hereof.
{"Amendment note: " + amend_note if amend_note else ""}

Please confirm that the foregoing correctly sets forth the terms of our agreement by executing
the copy of this Confirmation enclosed for that purpose and returning it to us.

Yours faithfully,
{pa}
By: ________________  Name:  Title:

Confirmed as of the date first above written:
{pb}
By: ________________  Name:  Title:
"""

    return {
        "path": path,
        "longFormFallback": long_form,
        "mcaProfileId": "MCA-SCB-ACME-2026-001" if path == "With_MCA" else None,
        "blocks": {
            "heading": {
                "partyALetterhead": pa,
                "confirmationDate": trade_date,
                "partyBName": pb,
                "partyBAddress": pb_addr,
            },
            "definitionsVersion": "2026 FX Definitions Main Book Version 1.0",
            "agreementClause": agreement,
            "productInsert": insert,
            "elections": {
                "partyALei": SAMPLE["parties"]["partyA"]["lei"],
                "partyBLei": SAMPLE["parties"]["partyB"]["lei"]
                if not novation
                else "549300TRANSFeree0001",
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
        "tradeId": SAMPLE["tradeId"],
        "occurredAt": "2027-12-01T10:00:00Z",
        "mcaPath": path,
        "mcaProfileId": "MCA-SCB-ACME-2026-001" if path == "With_MCA" else None,
        "legal": {
            "defsYear": "2026",
            "mainBookVersion": "1.0",
            "isdaMasterDate": "2026-01-15" if path == "With_MCA" else None,
            "longFormFallback": path == "Without_MCA",
            "governingLaw": None if path == "With_MCA" else "English law",
            "terminationCurrency": None if path == "With_MCA" else "USD",
            "matrixBindings": {"SRO": None},
        },
        "template": {
            "productExhibitId": "II-B",
            "supplementExhibitIds": [],
            "masterExhibitId": "I",
        },
        "trade": {
            "product": {"transactionType": SAMPLE["economics"]["transactionType"]},
            "parties": {
                "partyA": SAMPLE["parties"]["partyA"],
                "partyB": SAMPLE["parties"]["partyB"],
                "buyer": "Party A",
                "seller": "Party B",
            },
            "economics": SAMPLE["economics"],
        },
    }


def smartdx_out(path: str, doc_id: str, template_version: str, **letter_kw) -> dict:
    prior = letter_kw.pop("prior", None)
    letter = exhibit_i_letter(path, **letter_kw)
    return {
        "channel": "SmartDX",
        "documentId": doc_id,
        "tradeId": SAMPLE["tradeId"],
        "templateBundleId": "TB-FXO-DEL-2026-001",
        "templateVersion": template_version,
        "exhibits": {"master": "I", "product": "II-B", "supplements": []},
        "mcaPath": path,
        "exhibitILetter": letter,
        "productBody": {
            "exhibit": "II-B",
            "generalTerms": SAMPLE["economics"],
        },
        "priorDocumentId": prior,
    }


def callback(event: str, doc_id: str, **extra) -> dict:
    body = {
        "tradeId": SAMPLE["tradeId"],
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
    """Columns: Event, Direction, Description, Payload JSON"""
    rows = []
    # NEW
    rows.append(
        [
            "NEW_TRADE",
            "INBOUND_TPS",
            f"Book Deliverable FXO ({path})",
            dumps(tps_new(path)),
        ]
    )
    rows.append(
        [
            "NEW_TRADE",
            "OUTBOUND_SMARTDX",
            "Exhibit I letter + II-B body",
            dumps(smartdx_out(path, "DOC-001", "1.1.0")),
        ]
    )
    rows.append(
        [
            "NEW_TRADE",
            "CALLBACK_TPS",
            "Generation ack",
            dumps(callback("NEW_TRADE", "DOC-001", status="GENERATED")),
        ]
    )
    # AFFIRM
    rows.append(
        [
            "AFFIRM",
            "INBOUND_WEBHOOK",
            "Affirm platform Affirmed",
            dumps(
                {
                    "documentId": "DOC-001",
                    "tradeId": SAMPLE["tradeId"],
                    "status": "Affirmed",
                    "timestamp": "2027-12-01T15:04:05Z",
                    "differences": [],
                }
            ),
        ]
    )
    rows.append(
        [
            "AFFIRM",
            "OUTBOUND_SMARTDX",
            "No new doc (status only) — optional ack package",
            dumps(
                {
                    "channel": "SmartDX",
                    "action": "STATUS_UPDATE",
                    "documentId": "DOC-001",
                    "affirmationStatus": "Affirmed",
                }
            ),
        ]
    )
    rows.append(
        [
            "AFFIRM",
            "CALLBACK_TPS",
            "Affirm callback",
            dumps(
                callback(
                    "AFFIRM",
                    "DOC-001",
                    affirmationStatus="Affirmed",
                    timestamp="2027-12-01T15:04:06Z",
                )
            ),
        ]
    )
    # AMEND
    amend_tps = tps_new(path)
    amend_tps.update(
        {
            "eventType": "AMEND",
            "eventId": "evt_1002",
            "occurredAt": "2027-12-02T11:00:00Z",
        }
    )
    amend_tps["trade"]["economics"] = {
        **SAMPLE["economics"],
        "strikePrice": "1.0900",
    }
    rows.append(["AMEND", "INBOUND_TPS", "Strike amend 1.0850→1.0900", dumps(amend_tps)])
    rows.append(
        [
            "AMEND",
            "OUTBOUND_SMARTDX",
            "Recomposed letter + amended II-B",
            dumps(
                smartdx_out(
                    path,
                    "DOC-002",
                    "1.1.0",
                    amend_note="Strike Price amended to 1.0900",
                    prior="DOC-001",
                )
            ),
        ]
    )
    rows.append(
        [
            "AMEND",
            "CALLBACK_TPS",
            "Amend ack",
            dumps(callback("AMEND", "DOC-002", priorDocumentId="DOC-001", status="GENERATED")),
        ]
    )
    # NOVATION
    nov = {
        "eventType": "NOVATION",
        "eventId": "evt_1003",
        "tradeId": SAMPLE["tradeId"],
        "occurredAt": "2028-01-10T09:00:00Z",
        "mcaPath": path,
        "mcaProfileId": "MCA-SCB-ACME-2026-001" if path == "With_MCA" else None,
        "novation": {
            "transferor": "Party B",
            "transferee": "Party C",
            "remainingParty": "Party A",
            "effectiveDate": "2028-01-15",
            "transferee": {
                "name": "Globex Holdings Ltd",
                "lei": "549300TRANSFeree0001",
                "office": "New York",
            },
        },
    }
    # fix duplicate key - rebuild properly
    nov = {
        "eventType": "NOVATION",
        "eventId": "evt_1003",
        "tradeId": SAMPLE["tradeId"],
        "occurredAt": "2028-01-10T09:00:00Z",
        "mcaPath": path,
        "mcaProfileId": "MCA-SCB-ACME-2026-001" if path == "With_MCA" else None,
        "novation": {
            "transferor": "Party B",
            "transfereeParty": "Party C",
            "remainingParty": "Party A",
            "effectiveDate": "2028-01-15",
            "transfereeDetails": {
                "name": "Globex Holdings Ltd",
                "lei": "549300TRANSFeree0001",
                "office": "New York",
            },
        },
    }
    rows.append(["NOVATION", "INBOUND_TPS", "Party B → Party C", dumps(nov)])
    rows.append(
        [
            "NOVATION",
            "OUTBOUND_SMARTDX",
            "Exhibit I party blocks refreshed for transferee",
            dumps(smartdx_out(path, "DOC-003", "1.1.0", novation=True, prior="DOC-002")),
        ]
    )
    rows.append(
        [
            "NOVATION",
            "CALLBACK_TPS",
            "Novation ack",
            dumps(
                callback(
                    "NOVATION",
                    "DOC-003",
                    novationId="NOV-001",
                    priorDocumentId="DOC-002",
                    timestamp="2028-01-10T09:00:08Z",
                )
            ),
        ]
    )
    # EXERCISE
    ex = {
        "eventType": "EXERCISE",
        "eventId": "evt_1004",
        "tradeId": SAMPLE["tradeId"],
        "occurredAt": "2027-12-31T15:00:00Z",
        "exercise": {
            "method": "AutomaticExercise",
            "exerciseDate": "2027-12-31",
            "inTheMoney": True,
            "settlementDate": "2028-01-04",
        },
    }
    rows.append(["EXERCISE", "INBOUND_TPS", "Automatic Exercise ITM", dumps(ex)])
    rows.append(
        [
            "EXERCISE",
            "OUTBOUND_SMARTDX",
            "Exercise / settlement notice package (ops)",
            dumps(
                {
                    "channel": "SmartDX",
                    "documentId": "DOC-004",
                    "tradeId": SAMPLE["tradeId"],
                    "eventType": "EXERCISE",
                    "exhibitILetter": {
                        "note": "Exercise notice may reuse MASTER notice contacts from Exhibit I elections"
                    },
                    "exercise": ex["exercise"],
                }
            ),
        ]
    )
    rows.append(
        [
            "EXERCISE",
            "CALLBACK_TPS",
            "Exercise ack",
            dumps(
                callback(
                    "EXERCISE",
                    "DOC-004",
                    status="EXERCISED",
                    timestamp="2027-12-31T15:00:05Z",
                )
            ),
        ]
    )
    # TERMINATE (edge early term)
    term = {
        "eventType": "TERMINATE",
        "eventId": "evt_1005",
        "tradeId": SAMPLE["tradeId"],
        "occurredAt": "2027-12-20T12:00:00Z",
        "termination": {
            "reason": "OPTIONAL_EARLY_TERMINATION",
            "supplement": "III-D",
            "effectiveDate": "2027-12-22",
        },
    }
    rows.append(["TERMINATE", "INBOUND_TPS", "OET elected (III-D edge)", dumps(term)])
    rows.append(
        [
            "TERMINATE",
            "OUTBOUND_SMARTDX",
            "Termination confirmation letter",
            dumps(
                {
                    "channel": "SmartDX",
                    "documentId": "DOC-005",
                    "exhibitILetter": exhibit_i_letter(path),
                    "termination": term["termination"],
                }
            ),
        ]
    )
    rows.append(
        [
            "TERMINATE",
            "CALLBACK_TPS",
            "Terminate ack",
            dumps(callback("TERMINATE", "DOC-005", status="TERMINATED", timestamp="2027-12-20T12:00:05Z")),
        ]
    )
    # HOT_SWAP / RESEND (admin-triggered; still mocked per path)
    rows.append(
        [
            "HOT_SWAP",
            "INBOUND_ADMIN",
            "Activate template v1.2.0",
            dumps(
                {
                    "action": "ACTIVATE",
                    "templateBundleId": "TB-FXO-DEL-2026-001",
                    "version": "1.2.0",
                    "reason": "WRONG_PRODUCT_BINDING_FIXED",
                }
            ),
        ]
    )
    rows.append(
        [
            "HOT_SWAP",
            "OUTBOUND_SMARTDX",
            "No automatic send unless resendPolicy=AUTO",
            dumps({"channel": "SmartDX", "action": "NONE", "note": "Await RESEND"}),
        ]
    )
    rows.append(
        [
            "HOT_SWAP",
            "CALLBACK_TPS",
            "Template activated notice",
            dumps(
                {
                    "tradeId": None,
                    "eventType": "HOT_SWAP",
                    "templateBundleId": "TB-FXO-DEL-2026-001",
                    "templateVersion": "1.2.0",
                    "timestamp": "2027-12-01T16:00:00Z",
                }
            ),
        ]
    )
    rows.append(
        [
            "RESEND",
            "INBOUND_ADMIN",
            "Resend DOC-001 after hot-swap",
            dumps(
                {
                    "documentId": "DOC-001",
                    "reason": "WRONG_TEMPLATE_CORRECTED",
                    "templateVersion": "1.2.0",
                }
            ),
        ]
    )
    out_resend = smartdx_out(path, "DOC-001R", "1.2.0", prior="DOC-001")
    out_resend["priorDocumentId"] = "DOC-001"
    rows.append(["RESEND", "OUTBOUND_SMARTDX", "Superseding confirmation", dumps(out_resend)])
    rows.append(
        [
            "RESEND",
            "CALLBACK_TPS",
            "Resend ack",
            dumps(
                callback(
                    "RESEND",
                    "DOC-001R",
                    priorDocumentId="DOC-001",
                    templateVersion="1.2.0",
                    status="RESENT",
                    timestamp="2027-12-01T16:05:00Z",
                )
            ),
        ]
    )
    return rows


def error_rows() -> list[list]:
    """One mock error payload per lifecycle event."""
    errs = [
        (
            "NEW_TRADE",
            "VALIDATION_FAILED",
            {
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "FXO economics incomplete",
                    "details": [
                        {
                            "path": "trade.economics.strikePrice",
                            "ruleId": "DQ-CROSS-001",
                            "message": "Strike required unless Binary",
                        }
                    ],
                    "requestId": "req_err_new",
                }
            },
        ),
        (
            "AFFIRM",
            "NOT_FOUND",
            {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Unknown documentId",
                    "details": [{"path": "documentId", "message": "DOC-UNKNOWN"}],
                    "requestId": "req_err_aff",
                }
            },
        ),
        (
            "AMEND",
            "CONFLICT",
            {
                "error": {
                    "code": "IDEMPOTENCY_REPLAY_MISMATCH",
                    "message": "Idempotency-Key reused with different body",
                    "requestId": "req_err_amd",
                }
            },
        ),
        (
            "NOVATION",
            "VALIDATION_FAILED",
            {
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Novation parties incomplete",
                    "details": [
                        {
                            "path": "novation.transfereeParty",
                            "ruleId": "DQ-REQ-027",
                            "message": "Required",
                        }
                    ],
                    "requestId": "req_err_nov",
                }
            },
        ),
        (
            "EXERCISE",
            "LEGAL_ELECTION_INVALID",
            {
                "error": {
                    "code": "LEGAL_ELECTION_INVALID",
                    "message": "Full Automated Exercise requires SRO",
                    "details": [{"path": "trade.economics.fae.settlementRateOption", "ruleId": "DQ-CROSS-006"}],
                    "requestId": "req_err_ex",
                }
            },
        ),
        (
            "TERMINATE",
            "VALIDATION_FAILED",
            {
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "III-D not elected on confirmation",
                    "details": [{"path": "termination.supplement", "message": "III-D missing from supplementExhibitIds"}],
                    "requestId": "req_err_term",
                }
            },
        ),
        (
            "HOT_SWAP",
            "CONFLICT",
            {
                "error": {
                    "code": "CONFLICT",
                    "message": "Version already LIVE",
                    "details": [{"path": "version", "message": "1.2.0"}],
                    "requestId": "req_err_hs",
                }
            },
        ),
        (
            "RESEND",
            "CHANNEL_UNAVAILABLE",
            {
                "error": {
                    "code": "CHANNEL_UNAVAILABLE",
                    "message": "SmartDX timeout",
                    "details": [{"path": "channel", "message": "SmartDX"}],
                    "requestId": "req_err_rs",
                }
            },
        ),
        (
            "AFFIRM",
            "AFFIRM_DISPUTED",
            {
                "error": {
                    "code": "AFFIRM_DISPUTED",
                    "message": "Counterparty disputed economics",
                    "details": [
                        {
                            "path": "differences",
                            "message": "strikePrice local=1.0900 remote=1.0850",
                        }
                    ],
                    "requestId": "req_err_disp",
                    "affirmationStatus": "Disputed",
                }
            },
        ),
    ]
    return [[e, code, dumps(body)] for e, code, body in errs]


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
    thin = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin
    autosize(ws)
    ws.row_dimensions[1].height = 30


def main():
    wb = Workbook()

    # Legend
    ws0 = wb.active
    ws0.title = "Legend"
    write_sheet(
        ws0,
        ["Key", "Meaning"],
        [
            ["Sample trade", SAMPLE["tradeId"]],
            ["Product", "Deliverable FX Option / Exhibit II-B"],
            ["Master letter", "Exhibit I confirmation letter wrapper"],
            ["With_MCA sheet", "Assumed MCA-SCB-ACME-2026-001 path payloads"],
            ["Without_MCA sheet", "Long-form Exhibit I path payloads"],
            ["Errors sheet", "One mock error (or disputed affirm) per event"],
            ["INBOUND_TPS", "Source payload into CDU-PS"],
            ["OUTBOUND_SMARTDX", "Documentation system package incl. exhibitILetter"],
            ["CALLBACK_TPS", "Final / ack response to TPS"],
            ["INBOUND_WEBHOOK", "Affirm platform → CDU-PS"],
            ["INBOUND_ADMIN", "Template admin action"],
            ["Assumed", "Invented MCA sample — not ISDA legal text"],
            ["Phase", "Phase 1 docs only — no running adapters"],
        ],
    )

    # Sample card
    wsS = wb.create_sheet("Sample_Trade_Card")
    write_sheet(
        wsS,
        ["Field", "Value"],
        [[k, dumps(v) if isinstance(v, (dict, list)) else str(v)] for k, v in SAMPLE.items()],
    )

    header = ["Event", "Direction", "Description", "Payload JSON"]
    ws1 = wb.create_sheet("With_MCA")
    write_sheet(ws1, header, build_rows_for_path("With_MCA"))

    ws2 = wb.create_sheet("Without_MCA")
    write_sheet(ws2, header, build_rows_for_path("Without_MCA"))

    ws3 = wb.create_sheet("Errors")
    write_sheet(ws3, ["Event", "Error code", "Error payload JSON"], error_rows())

    # Letter blocks reference
    ws4 = wb.create_sheet("ExhibitI_Letter_Ref")
    letter_with = exhibit_i_letter("With_MCA")
    letter_without = exhibit_i_letter("Without_MCA")
    write_sheet(
        ws4,
        ["Path", "Artifact", "Content"],
        [
            ["With_MCA", "blocks JSON", dumps(letter_with["blocks"])],
            ["With_MCA", "proseLetter", letter_with["proseLetter"]],
            ["Without_MCA", "blocks JSON", dumps(letter_without["blocks"])],
            ["Without_MCA", "proseLetter", letter_without["proseLetter"]],
        ],
    )

    OUT_REPO.parent.mkdir(parents=True, exist_ok=True)
    OUT_STORE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_REPO)
    wb.save(OUT_STORE)
    print("WROTE", OUT_REPO)
    print("WROTE", OUT_STORE)
    print("With_MCA rows", len(build_rows_for_path("With_MCA")))
    print("Error rows", len(error_rows()))


if __name__ == "__main__":
    main()

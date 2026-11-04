#!/usr/bin/env python3
"""Generate Phase 1 CDU-PS ISDA 2026 mapping Excel + working CSV from PDF extract."""
from __future__ import annotations

import csv
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

STORE = Path("/cursor/stores/bc-810ee397-0d26-4b38-b43b-2e3d21ebe15f")
REPO = Path("/agent/repos/con4m8ions")
PDF_TXT = STORE / "internal/pdf-extract/templates_full.txt"
OUT_XLSX_REPO = REPO / "docs/mappings/cdu-ps-isda-2026-mapping.xlsx"
OUT_XLSX_STORE = STORE / "docs/mappings/cdu-ps-isda-2026-mapping.xlsx"
OUT_CSV = STORE / "internal/pdf-extract/attribute-product-map-working.csv"

PRIMARY_PDF = (
    "2026-FX-Defs-Consolidated-Confirmation-Templates_Colour-Coded-Annotation-070726_05a5.pdf"
)

# Exhibit metadata
EXHIBIT_ORDER = [
    "I",
    "II-A",
    "II-B",
    "II-C",
    "II-D",
    "II-E",
    "II-F",
    "II-G",
    "II-H",
    "II-I",
    "II-J",
    "II-K",
    "III-A",
    "III-B",
    "III-C",
    "III-D",
    "III-E",
    "III-F",
    "III-G",
    "III-H",
]

EXHIBITS = {
    "I": {
        "layer": "MASTER",
        "group": "COMMON",
        "product": "ALL",
        "depth": "Standard",
        "title": "Introduction, Standard Paragraphs and Closing",
        "pages": "5-8 (doc pp.1-4)",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;RESEND",
        "supplements": "",
        "matrix": "",
    },
    "II-A": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "Deliverable_FX",
        "depth": "Standard",
        "title": "Deliverable FX Transaction",
        "pages": "9-10 (doc pp.5-6)",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;TERMINATE",
        "supplements": "III-A;III-C;III-D;III-E",
        "matrix": "",
    },
    "II-B": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "Deliverable_FX_Option",
        "depth": "Deep",
        "title": "Deliverable FX Option Transaction",
        "pages": "11-14 (doc pp.7-10)",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE;TERMINATE;HOT_SWAP;RESEND",
        "supplements": "III-A;III-C;III-D;III-F;III-G;III-H",
        "matrix": "SRO Matrix version (optional pin)",
    },
    "II-C": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "NonDeliverable_FX",
        "depth": "Standard",
        "title": "Non-Deliverable FX Transaction",
        "pages": "15-18 (doc pp.11-14)",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;TERMINATE",
        "supplements": "III-B;III-C;III-D;III-E;III-F",
        "matrix": "SRO; optional EM Additional Provisions",
    },
    "II-D": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "NonDeliverable_FX_Option",
        "depth": "Standard",
        "title": "Non-Deliverable FX Option Transaction",
        "pages": "doc pp.14-18",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE;TERMINATE",
        "supplements": "III-B;III-C;III-D;III-F;III-G;III-H",
        "matrix": "SRO; optional EM Additional Provisions",
    },
    "II-E": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "NDF_EM_Currency_Matrix",
        "depth": "Standard",
        "title": "Non-Deliverable FX Transaction (EM Currency Matrix)",
        "pages": "doc pp.19-20",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;TERMINATE",
        "supplements": "III-E;III-F",
        "matrix": "EM Currency Matrix version (required pin)",
    },
    "II-F": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "NDO_EM_Currency_Matrix",
        "depth": "Standard",
        "title": "Non-Deliverable FX Option Transaction (EM Currency Matrix)",
        "pages": "doc pp.21-22",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE;TERMINATE",
        "supplements": "III-F;III-G;III-H",
        "matrix": "EM Currency Matrix version (required pin)",
    },
    "II-G": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "ND_CrossCurrency_FX_EM",
        "depth": "Standard",
        "title": "Non-Deliverable Cross-Currency FX Transaction (EM Currency Matrix)",
        "pages": "doc pp.23-24",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;TERMINATE",
        "supplements": "III-E;III-F",
        "matrix": "EM Currency Matrix version",
    },
    "II-H": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "ND_CrossCurrency_FX_Option_EM",
        "depth": "Standard",
        "title": "Non-Deliverable Cross-Currency FX Option Transaction (EM Currency Matrix)",
        "pages": "doc pp.25-26",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE;TERMINATE",
        "supplements": "III-F;III-G;III-H",
        "matrix": "EM Currency Matrix version",
    },
    "II-I": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "Variance_Volatility_Swap",
        "depth": "Standard",
        "title": "Variance Swap or Volatility Swap",
        "pages": "doc pp.27-29",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;TERMINATE",
        "supplements": "",
        "matrix": "SRO Matrix (observation)",
    },
    "II-J": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "Correlation_Swap",
        "depth": "Standard",
        "title": "Correlation Swap",
        "pages": "doc pp.30-32",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;TERMINATE",
        "supplements": "",
        "matrix": "SRO Matrix (observation)",
    },
    "II-K": {
        "layer": "PRODUCT",
        "group": "PRODUCT",
        "product": "Deliverable_Delta_Neutral_FVA",
        "depth": "Standard",
        "title": "Deliverable Delta Neutral Forward Volatility Agreement",
        "pages": "doc pp.33-35",
        "lifecycle": "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE;TERMINATE",
        "supplements": "III-A;III-C;III-D",
        "matrix": "SRO Matrix version",
    },
    "III-A": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "Deliverable_*",
        "depth": "Standard",
        "title": "Deliverable Disruption Events and Disruption Fallbacks",
        "pages": "doc pp.36-37",
        "lifecycle": "NEW_TRADE;AMEND;TERMINATE",
        "supplements": "",
        "matrix": "",
    },
    "III-B": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "NonDeliverable_*",
        "depth": "Standard",
        "title": "Non-Deliverable Disruption Events and Disruption Fallbacks",
        "pages": "doc pp.38-40",
        "lifecycle": "NEW_TRADE;AMEND;TERMINATE",
        "supplements": "",
        "matrix": "EM disruption fallbacks",
    },
    "III-C": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "FX_*_with_MET",
        "depth": "Standard",
        "title": "Mandatory Early Termination",
        "pages": "doc pp.41-42",
        "lifecycle": "NEW_TRADE;AMEND;TERMINATE",
        "supplements": "",
        "matrix": "",
    },
    "III-D": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "FX_*_with_OET",
        "depth": "Standard",
        "title": "Optional Early Termination",
        "pages": "doc pp.43-45",
        "lifecycle": "NEW_TRADE;AMEND;TERMINATE;EXERCISE",
        "supplements": "",
        "matrix": "",
    },
    "III-E": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "FX_*_avg_forward",
        "depth": "Standard",
        "title": "Averaging the Forward Rate",
        "pages": "doc pp.46-48",
        "lifecycle": "NEW_TRADE;AMEND",
        "supplements": "",
        "matrix": "",
    },
    "III-F": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "FX_*_avg_settlement",
        "depth": "Standard",
        "title": "Averaging the Settlement Rate",
        "pages": "doc pp.49-51",
        "lifecycle": "NEW_TRADE;AMEND;EXERCISE",
        "supplements": "",
        "matrix": "SRO for averaging observation",
    },
    "III-G": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "FX_Option_*_avg_strike",
        "depth": "Standard",
        "title": "Averaging the Strike Price",
        "pages": "doc pp.52-54",
        "lifecycle": "NEW_TRADE;AMEND;EXERCISE",
        "supplements": "",
        "matrix": "",
    },
    "III-H": {
        "layer": "SUPPLEMENT",
        "group": "SUPPLEMENT",
        "product": "FX_Option_*_barrier",
        "depth": "Standard",
        "title": "Barrier Transaction",
        "pages": "doc pp.55-end",
        "lifecycle": "NEW_TRADE;AMEND;EXERCISE;TERMINATE",
        "supplements": "",
        "matrix": "",
    },
}

NOISE_LABELS = {
    "Dear [Sir/Madam]",
    "Confirmation relates are as follows",
    "Offices",
    "Transaction [is] / [are]",
    "Amount]",
    "Weighti",
    "Definitions",
    "Provisions",
    "Matrix",
    "Disruption",
    "Averaging",
    "Transaction",
    "Currency",
    "Time",
    "Date",
    "Adjustment",
}

# Curated deep II-B fields (PDF extraction can miss wrapped labels)
IIB_DEEP_FIELDS = [
    ("Transaction Type", "PRODUCT", "PRODUCT", "II-B", "—", "General Terms; new 2026 defined term", "NEW_TRADE;AFFIRM", "Both", "", "trade.product.transactionType", "SmartDX:TransactionType", "DQ-REQ-001", "MAP-ENUM-001"),
    ("Trade Date", "PRODUCT", "PRODUCT", "II-B", "—", "General Terms", "NEW_TRADE;AFFIRM;AMEND;NOVATION", "Both", "", "trade.economics.tradeDate", "SmartDX:TradeDate;SWIFT:32A/Date", "DQ-REQ-002;DQ-CAL-001", "MAP-DATE-001"),
    ("SRO Matrix version", "MATRIX", "PRODUCT", "II-B", "SRO Matrix version pin", "Optional; pin non-latest SRO Matrix", "NEW_TRADE;AMEND;HOT_SWAP", "Both", "", "trade.legal.matrix.sroVersion", "SmartDX:SROMatrixVersion", "DQ-LEGAL-001", "MAP-MATRIX-001"),
    ("Buyer", "PRODUCT", "PRODUCT", "II-B", "—", "Party A / Party B", "NEW_TRADE;AFFIRM;NOVATION;EXERCISE", "Both", "", "trade.parties.buyer", "SmartDX:Buyer;SWIFT:Party", "DQ-REQ-003", "MAP-PARTY-001"),
    ("Seller", "PRODUCT", "PRODUCT", "II-B", "—", "Party A / Party B", "NEW_TRADE;AFFIRM;NOVATION;EXERCISE", "Both", "", "trade.parties.seller", "SmartDX:Seller;SWIFT:Party", "DQ-REQ-003", "MAP-PARTY-001"),
    ("Option Style", "PRODUCT", "PRODUCT", "II-B", "—", "American / Bermuda / European; was Currency Option Style in 1998", "NEW_TRADE;AFFIRM;EXERCISE", "Both", "", "trade.economics.optionStyle", "SmartDX:OptionStyle", "DQ-ENUM-001", "MAP-ENUM-002"),
    ("Option Type", "PRODUCT", "PRODUCT", "II-B", "—", "Put/Call currencies or Binary; Binary moved from Style (2022 Barrier Supp)", "NEW_TRADE;AFFIRM;EXERCISE", "Both", "", "trade.economics.optionType", "SmartDX:OptionType", "DQ-ENUM-002;DQ-CROSS-001", "MAP-ENUM-003"),
    ("Call Currency", "PRODUCT", "PRODUCT", "II-B", "—", "Call Currency [and Call Currency Amount]", "NEW_TRADE;AFFIRM;EXERCISE", "Both", "", "trade.economics.callCurrency", "SmartDX:CallCurrency;SWIFT:Currency", "DQ-REQ-004;DQ-CROSS-001", "MAP-CCY-001"),
    ("Call Currency Amount", "PRODUCT", "PRODUCT", "II-B", "—", "Numeric or derived from Put ×/÷ Strike", "NEW_TRADE;AFFIRM;EXERCISE;AMEND", "Both", "", "trade.economics.callCurrencyAmount", "SmartDX:CallAmount;SWIFT:32B", "DQ-CROSS-002", "MAP-AMT-001"),
    ("Put Currency", "PRODUCT", "PRODUCT", "II-B", "—", "Put Currency [and Put Currency Amount]", "NEW_TRADE;AFFIRM;EXERCISE", "Both", "", "trade.economics.putCurrency", "SmartDX:PutCurrency;SWIFT:Currency", "DQ-REQ-004;DQ-CROSS-001", "MAP-CCY-001"),
    ("Put Currency Amount", "PRODUCT", "PRODUCT", "II-B", "—", "Numeric or derived from Call ×/÷ Strike", "NEW_TRADE;AFFIRM;EXERCISE;AMEND", "Both", "", "trade.economics.putCurrencyAmount", "SmartDX:PutAmount;SWIFT:32B", "DQ-CROSS-002", "MAP-AMT-001"),
    ("Settlement", "PRODUCT", "PRODUCT", "II-B", "—", "Deliverable (presumed); include for Binary", "NEW_TRADE;AFFIRM", "Both", "", "trade.economics.settlementMethod", "SmartDX:Settlement", "DQ-ENUM-003", "MAP-ENUM-004"),
    ("Strike Price", "PRODUCT", "PRODUCT", "II-B", "—", "Numeric or The Averaging Rate → III-G", "NEW_TRADE;AFFIRM;AMEND;EXERCISE", "Both", "", "trade.economics.strikePrice", "SmartDX:StrikePrice", "DQ-CROSS-001;DQ-CROSS-003", "MAP-RATE-001"),
    ("Commencement Date", "PRODUCT", "PRODUCT", "II-B", "—", "American style; default Trade Date §6.6.1", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.commencementDate", "SmartDX:CommencementDate", "DQ-CAL-002", "MAP-DATE-001"),
    ("Expiration Date", "PRODUCT", "PRODUCT", "II-B", "—", "Required for option", "NEW_TRADE;AFFIRM;EXERCISE;AMEND", "Both", "", "trade.economics.expirationDate", "SmartDX:ExpirationDate;SWIFT:30P", "DQ-REQ-005;DQ-CAL-003", "MAP-DATE-001"),
    ("Expiration Time", "PRODUCT", "PRODUCT", "II-B", "—", "Time + financial center", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.expirationTime", "SmartDX:ExpirationTime", "DQ-REQ-006;DQ-FORMAT-001", "MAP-TIME-001"),
    ("Expiration Time Location", "PRODUCT", "PRODUCT", "II-B", "—", "Financial center for Expiration Time", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.expirationTimeLocation", "SmartDX:ExpirationLocation", "DQ-REQ-006", "MAP-LOC-001"),
    ("Earliest Exercise Time", "PRODUCT", "PRODUCT", "II-B", "—", "Default 9:00 a.m. local §6.6.6(ii)", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.earliestExerciseTime", "SmartDX:EarliestExerciseTime", "DQ-FORMAT-001", "MAP-TIME-001"),
    ("Latest Exercise Time", "PRODUCT", "PRODUCT", "II-B", "—", "Default Expiration Time §6.6.7", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.latestExerciseTime", "SmartDX:LatestExerciseTime", "DQ-FORMAT-001", "MAP-TIME-001"),
    ("Automatic Exercise", "PRODUCT", "PRODUCT", "II-B", "—", "Presumed applicable; field to disapply", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.automaticExercise", "SmartDX:AutomaticExercise", "DQ-ENUM-004", "MAP-BOOL-001"),
    ("Settlement Date", "PRODUCT", "PRODUCT", "II-B", "—", "Override Settlement Cycle presumption", "NEW_TRADE;EXERCISE;AMEND", "Both", "", "trade.economics.settlementDate", "SmartDX:SettlementDate;SWIFT:30V", "DQ-CAL-004", "MAP-DATE-001"),
    ("Exercise Period", "PRODUCT", "PRODUCT", "II-B", "—", "American style override §6.6.3", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.exercisePeriod", "SmartDX:ExercisePeriod", "DQ-CROSS-004", "MAP-TEXT-001"),
    ("Potential Exercise Date(s)", "PRODUCT", "PRODUCT", "II-B", "—", "Bermuda style", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.potentialExerciseDates", "SmartDX:PotentialExerciseDates", "DQ-CROSS-004;DQ-CAL-005", "MAP-DATE-LIST-001"),
    ("Premium", "PRODUCT", "PRODUCT", "II-B", "—", "Premium amount; Price-% removed as separate field (2026 tidy)", "NEW_TRADE;AFFIRM;AMEND", "Both", "", "trade.economics.premium.amount", "SmartDX:Premium;SWIFT:33B", "DQ-REQ-007", "MAP-AMT-002"),
    ("Premium Payment Date", "PRODUCT", "PRODUCT", "II-B", "—", "Premium settlement date", "NEW_TRADE;AFFIRM", "Both", "", "trade.economics.premium.paymentDate", "SmartDX:PremiumPaymentDate", "DQ-CAL-006", "MAP-DATE-001"),
    ("Partial Exercise", "PRODUCT", "PRODUCT", "II-B", "—", "European only; new vs 1998", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.partialExercise", "SmartDX:PartialExercise", "DQ-CROSS-005", "MAP-BOOL-001"),
    ("Minimum Exercise Amount (Partial)", "PRODUCT", "PRODUCT", "II-B", "—", "§6.8.2 with Partial Exercise", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.minimumExerciseAmountPartial", "SmartDX:MinExerciseAmt", "DQ-CROSS-005", "MAP-AMT-001"),
    ("Multiple Exercise", "PRODUCT", "PRODUCT", "II-B", "—", "American/Bermuda; new vs 1998", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.multipleExercise", "SmartDX:MultipleExercise", "DQ-CROSS-005", "MAP-BOOL-001"),
    ("Minimum Exercise Amount (Multiple)", "PRODUCT", "PRODUCT", "II-B", "—", "§6.9.3", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.minimumExerciseAmountMultiple", "SmartDX:MinExerciseAmtMulti", "DQ-CROSS-005", "MAP-AMT-001"),
    ("Maximum Exercise Amount", "PRODUCT", "PRODUCT", "II-B", "—", "§6.9.3", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.maximumExerciseAmount", "SmartDX:MaxExerciseAmt", "DQ-CROSS-005", "MAP-AMT-001"),
    ("Full Automated Exercise", "PRODUCT", "PRODUCT", "II-B", "—", "European; new 2026", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.fullAutomatedExercise", "SmartDX:FullAutomatedExercise", "DQ-CROSS-006", "MAP-BOOL-001"),
    ("Settlement Rate equal to Strike Price at expiry", "PRODUCT", "PRODUCT", "II-B", "—", "Expiry at Strike / Exercise at Strike", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.strikeEqualityOutcome", "SmartDX:StrikeEqualityOutcome", "DQ-ENUM-005", "MAP-ENUM-005"),
    ("Settlement Rate Option (FAE)", "PRODUCT", "PRODUCT", "II-B", "SRO lookup", "For Full Automated Exercise", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.fae.settlementRateOption", "SmartDX:SRO", "DQ-MATRIX-001", "MAP-SRO-001"),
    ("Specified Time (FAE)", "PRODUCT", "PRODUCT", "II-B", "SRO", "If SRO not in matrix / no Specified Time", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.fae.specifiedTime", "SmartDX:SpecifiedTime", "DQ-FORMAT-001", "MAP-TIME-001"),
    ("Spot Rate Fixing Day (FAE)", "PRODUCT", "PRODUCT", "II-B", "SRO", "If SRO not in matrix", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.fae.spotRateFixingDay", "SmartDX:SpotRateFixingDay", "DQ-CAL-007", "MAP-DATE-001"),
    ("Valuation Date", "PRODUCT", "PRODUCT", "II-B", "—", "Default Exercise Date §4.5.4(ii)(b)", "NEW_TRADE;EXERCISE;AMEND", "Both", "", "trade.economics.valuationDate", "SmartDX:ValuationDate", "DQ-CAL-008", "MAP-DATE-001"),
    ("Settlement Rate", "PRODUCT", "PRODUCT", "II-B", "—", "For ITM Automatic Exercise; or Averaging Rate → III-F", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.settlementRate", "SmartDX:SettlementRate", "DQ-CROSS-006", "MAP-RATE-001"),
    ("Settlement Rate Option", "PRODUCT", "PRODUCT", "II-B", "SRO Matrix", "For Automatic Exercise Settlement Rate", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.settlementRateOption", "SmartDX:SRO", "DQ-MATRIX-001", "MAP-SRO-001"),
    ("Specified Time", "PRODUCT", "PRODUCT", "II-B", "SRO", "If SRO not in matrix", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.specifiedTime", "SmartDX:SpecifiedTime", "DQ-FORMAT-001", "MAP-TIME-001"),
    ("Spot Rate Fixing Day", "PRODUCT", "PRODUCT", "II-B", "SRO", "If SRO not in matrix", "NEW_TRADE;EXERCISE", "Both", "", "trade.economics.spotRateFixingDay", "SmartDX:SpotRateFixingDay", "DQ-CAL-007", "MAP-DATE-001"),
    ("Rounding", "PRODUCT", "PRODUCT", "II-B", "—", "Override §10.6.1", "NEW_TRADE;AMEND", "Both", "", "trade.economics.rounding", "SmartDX:Rounding", "DQ-FORMAT-002", "MAP-TEXT-001"),
    ("Business Day for Payment", "PRODUCT", "PRODUCT", "II-B", "—", "Override Currency Business Day presumption", "NEW_TRADE;EXERCISE", "Both", "", "trade.calendars.businessDayPayment", "SmartDX:BizDayPayment", "DQ-CAL-009", "MAP-CAL-001"),
    ("Business Day for Exercise", "PRODUCT", "PRODUCT", "II-B", "—", "Publication Calendar Day or Spot Market BD", "NEW_TRADE;EXERCISE", "Both", "", "trade.calendars.businessDayExercise", "SmartDX:BizDayExercise", "DQ-CAL-009", "MAP-CAL-001"),
    ("Business Day for Valuation", "PRODUCT", "PRODUCT", "II-B", "—", "Generally same as Exercise", "NEW_TRADE;EXERCISE", "Both", "", "trade.calendars.businessDayValuation", "SmartDX:BizDayValuation", "DQ-CAL-009;DQ-CROSS-007", "MAP-CAL-001"),
]

# Exhibit I common fields
EXHIBIT_I_FIELDS = [
    ("Party A Letterhead", "COMMON", "MASTER", "I", "", "Heading", "NEW_TRADE;RESEND", "Both", "", "confirmation.header.partyALetterhead", "SmartDX:Header", "DQ-LINEAGE-001", "MAP-TEXT-001"),
    ("Confirmation Date", "COMMON", "MASTER", "I", "", "Heading Date", "NEW_TRADE;AMEND;RESEND", "Both", "", "confirmation.header.date", "SmartDX:ConfDate", "DQ-REQ-010;DQ-CAL-001", "MAP-DATE-001"),
    ("Party B Name and Address", "COMMON", "MASTER", "I", "", "Heading", "NEW_TRADE;NOVATION", "Both", "", "confirmation.header.partyB", "SmartDX:PartyB", "DQ-REQ-011", "MAP-PARTY-002"),
    ("FX Definitions Version Election", "COMMON", "MASTER", "I", "Main Book version", "Incorporate 2026 FX Definitions; optional version pin", "NEW_TRADE;HOT_SWAP", "Both", "", "trade.legal.fxDefinitionsVersion", "SmartDX:DefsVersion", "DQ-LEGAL-002", "MAP-LEGAL-001"),
    ("ISDA Master Agreement Date", "COMMON", "MASTER", "I", "", "Subject to Agreement dated as of…", "NEW_TRADE;AFFIRM", "With_MCA", "mca.isdaMasterDate (Assumed)", "trade.legal.isdaMaster.date", "SmartDX:MasterDate", "DQ-LEGAL-003", "MAP-LEGAL-002"),
    ("Party A Name", "COMMON", "MASTER", "I", "", "Party A", "NEW_TRADE;NOVATION;AFFIRM", "Both", "", "trade.parties.partyA.name", "SmartDX:PartyA;SWIFT:Party", "DQ-REQ-012", "MAP-PARTY-001"),
    ("Party B Name", "COMMON", "MASTER", "I", "", "Party B", "NEW_TRADE;NOVATION;AFFIRM", "Both", "", "trade.parties.partyB.name", "SmartDX:PartyB;SWIFT:Party", "DQ-REQ-012", "MAP-PARTY-001"),
    ("Long-form Master Agreement Fallback", "COMMON", "MASTER", "I", "", "Footnote 2 long-form if no executed Master", "NEW_TRADE", "Without_MCA", "", "trade.legal.longFormFallback", "SmartDX:LongForm", "DQ-LEGAL-004", "MAP-LEGAL-003"),
    ("Governing Law (long-form)", "COMMON", "MASTER", "I", "", "English law / NY law election in long-form", "NEW_TRADE", "Without_MCA", "", "trade.legal.governingLaw", "SmartDX:GoverningLaw", "DQ-LEGAL-005", "MAP-ENUM-006"),
    ("Termination Currency (long-form)", "COMMON", "MASTER", "I", "", "Long-form Schedule election", "NEW_TRADE", "Without_MCA", "", "trade.legal.terminationCurrency", "SmartDX:TermCcy", "DQ-LEGAL-005", "MAP-CCY-001"),
    ("Party A LEI", "COMMON", "MASTER", "I", "", "Optional LEI", "NEW_TRADE;AFFIRM;NOVATION", "Both", "mca.partyA.lei (Assumed default)", "trade.parties.partyA.lei", "SmartDX:LEI_A;SWIFT:LEI", "DQ-FORMAT-003", "MAP-LEI-001"),
    ("Party B LEI", "COMMON", "MASTER", "I", "", "Optional LEI", "NEW_TRADE;AFFIRM;NOVATION", "Both", "mca.partyB.lei (Assumed default)", "trade.parties.partyB.lei", "SmartDX:LEI_B;SWIFT:LEI", "DQ-FORMAT-003", "MAP-LEI-001"),
    ("Fallback Benchmark", "COMMON", "MASTER", "I", "", "Administrator/Benchmark Event fallback", "NEW_TRADE;AMEND", "Both", "", "trade.economics.fallbackBenchmark", "SmartDX:FallbackBenchmark", "DQ-LEGAL-006", "MAP-TEXT-001"),
    ("Acknowledgments and Representations", "COMMON", "MASTER", "I", "", "Disapplied election vs §20 presumption", "NEW_TRADE", "Both", "mca.acksRepresentations (Assumed)", "trade.legal.acksRepresentations", "SmartDX:AcksReps", "DQ-ENUM-006", "MAP-ENUM-007"),
    ("Calculation Agent", "COMMON", "MASTER", "I", "", "Party A/B/other/Joint/As per Agreement", "NEW_TRADE;AFFIRM;AMEND", "Both", "mca.calculationAgent (Assumed default)", "trade.legal.calculationAgent", "SmartDX:CalcAgent", "DQ-REQ-013", "MAP-PARTY-003"),
    ("Joint Calculation Agent Dispute Resolution", "COMMON", "MASTER", "I", "", "When Joint CA elected", "NEW_TRADE", "Both", "mca.jointCaDisputeResolution (Assumed)", "trade.legal.jointCaDisputeResolution", "SmartDX:JointCADispute", "DQ-CROSS-008", "MAP-BOOL-001"),
    ("Account for payments to Party A", "COMMON", "MASTER", "I", "", "Account Details", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.accounts.partyA (Assumed SSI)", "trade.settlement.accountPartyA", "SmartDX:AccountA;SWIFT:57a", "DQ-FORMAT-004", "MAP-SSI-001"),
    ("Account for payments to Party B", "COMMON", "MASTER", "I", "", "Account Details", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.accounts.partyB (Assumed SSI)", "trade.settlement.accountPartyB", "SmartDX:AccountB;SWIFT:57a", "DQ-FORMAT-004", "MAP-SSI-001"),
    ("Office of Party A", "COMMON", "MASTER", "I", "", "Offices", "NEW_TRADE;NOVATION", "Both", "mca.offices.partyA (Assumed)", "trade.parties.partyA.office", "SmartDX:OfficeA", "DQ-FORMAT-005", "MAP-LOC-001"),
    ("Office of Party B", "COMMON", "MASTER", "I", "", "Offices", "NEW_TRADE;NOVATION", "Both", "mca.offices.partyB (Assumed)", "trade.parties.partyB.office", "SmartDX:OfficeB", "DQ-FORMAT-005", "MAP-LOC-001"),
    ("Broker/Arranger", "COMMON", "MASTER", "I", "", "Optional", "NEW_TRADE", "Both", "", "trade.parties.brokerArranger", "SmartDX:Broker", "DQ-LINEAGE-001", "MAP-PARTY-004"),
    ("Governing law", "COMMON", "MASTER", "I", "", "Delete if under executed Master", "NEW_TRADE", "Without_MCA", "", "trade.legal.governingLawConfirm", "SmartDX:GoverningLaw", "DQ-LEGAL-005", "MAP-ENUM-006"),
    ("Contact details for notice Party A", "COMMON", "MASTER", "I", "", "New optional 2026 field", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.notices.partyA (Assumed)", "trade.notices.partyA", "SmartDX:NoticeA", "DQ-FORMAT-006", "MAP-TEXT-001"),
    ("Contact details for notice Party B", "COMMON", "MASTER", "I", "", "New optional 2026 field", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.notices.partyB (Assumed)", "trade.notices.partyB", "SmartDX:NoticeB", "DQ-FORMAT-006", "MAP-TEXT-001"),
    ("Closing supersession clause", "COMMON", "MASTER", "I", "", "Closing", "NEW_TRADE;AMEND;RESEND", "Both", "", "confirmation.closing.supersession", "SmartDX:Closing", "DQ-LINEAGE-001", "MAP-TEXT-001"),
    ("Party A signature block", "COMMON", "MASTER", "I", "", "Closing", "NEW_TRADE;AFFIRM", "Both", "", "confirmation.signatures.partyA", "SmartDX:SigA", "DQ-LINEAGE-001", "MAP-TEXT-001"),
    ("Party B confirmation signature block", "COMMON", "MASTER", "I", "", "Closing", "NEW_TRADE;AFFIRM", "Both", "", "confirmation.signatures.partyB", "SmartDX:SigB", "DQ-LINEAGE-001", "MAP-TEXT-001"),
]

# Assumed MCA-only inventory
MCA_ASSUMED = [
    ("MCA Profile ID", "MCA", "", "", "", "Assumed bilateral MCA identifier", "NEW_TRADE;HOT_SWAP", "With_MCA", "Assumed: MCA-SCB-ACME-2026-001", "trade.legal.mca.profileId", "—", "DQ-MCA-001", "MAP-MCA-001"),
    ("MCA Effective Date", "MCA", "", "", "", "Assumed", "NEW_TRADE", "With_MCA", "Assumed: 2026-01-15", "trade.legal.mca.effectiveDate", "—", "DQ-MCA-002", "MAP-DATE-001"),
    ("MCA FX Definitions Year Election", "MCA", "", "", "Main Book", "Assumed: elect 2026 vs 1998 until cutover", "NEW_TRADE;HOT_SWAP", "With_MCA", "Assumed: 2026 FX Definitions Version 1.0", "trade.legal.mca.defsYear", "—", "DQ-MCA-003", "MAP-LEGAL-001"),
    ("MCA Default Product Set", "MCA", "", "", "", "Assumed eligible products under MCA", "NEW_TRADE", "With_MCA", "Assumed: Deliverable FX; Deliverable FX Option; NDF; NDO", "trade.legal.mca.productSet", "—", "DQ-MCA-004", "MAP-ENUM-008"),
    ("MCA Default Calculation Agent", "MCA", "", "", "", "Assumed CA default absorbed into Exhibit I when With_MCA", "NEW_TRADE", "With_MCA", "Assumed: Party A", "trade.legal.mca.defaultCalcAgent", "SmartDX:CalcAgent", "DQ-MCA-005", "MAP-PARTY-003"),
    ("MCA Default Notice Channel", "MCA", "", "", "", "Assumed email + MarkitWire", "NEW_TRADE;AFFIRM", "With_MCA", "Assumed: ops-fx@party.example; electronic conf via SmartDX", "trade.legal.mca.noticeChannel", "—", "DQ-MCA-006", "MAP-TEXT-001"),
    ("MCA Multilateral Settlement Election", "MCA", "", "", "", "Assumed CLS eligibility default", "NEW_TRADE", "With_MCA", "Assumed: CLS where eligible else bilateral", "trade.legal.mca.settlementElection", "SWIFT:SettlementMethod", "DQ-MCA-007", "MAP-ENUM-009"),
    ("MCA Automatic Exercise Default", "MCA", "", "", "", "Assumed FXO default", "NEW_TRADE;EXERCISE", "With_MCA", "Assumed: Automatic Exercise applicable", "trade.legal.mca.autoExerciseDefault", "SmartDX:AutomaticExercise", "DQ-MCA-008", "MAP-BOOL-001"),
    ("MCA Dispute Resolution Venue", "MCA", "", "", "", "Assumed", "NEW_TRADE", "With_MCA", "Assumed: Arbitration LCIA / English law", "trade.legal.mca.disputeVenue", "—", "DQ-MCA-009", "MAP-TEXT-001"),
    ("MCA Confirmation Method", "MCA", "", "", "", "Assumed electronic vs paper", "NEW_TRADE;AFFIRM;RESEND", "With_MCA", "Assumed: Electronic confirmation via SmartDX preferred", "trade.legal.mca.confirmationMethod", "SmartDX:Channel", "DQ-MCA-010", "MAP-ENUM-010"),
]

# Platform + lifecycle operational fields
PLATFORM_FIELDS = [
    ("CDU-PS Trade ID", "PLATFORM", "", "", "", "Internal trade key", "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE;HOT_SWAP;RESEND", "Both", "", "platform.tradeId", "—", "DQ-REQ-020", "MAP-ID-001"),
    ("TPS Source System", "PLATFORM", "", "", "", "Upstream TPS identifier", "NEW_TRADE", "Both", "", "platform.tps.sourceSystem", "—", "DQ-REQ-021", "MAP-ID-002"),
    ("TPS Event ID", "PLATFORM", "", "", "", "Idempotency / event key", "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE", "Both", "", "platform.tps.eventId", "—", "DQ-REQ-022", "MAP-ID-003"),
    ("Idempotency Key", "PLATFORM", "", "", "", "API idempotency", "NEW_TRADE;AMEND;HOT_SWAP;RESEND", "Both", "", "platform.idempotencyKey", "—", "DQ-REQ-023", "MAP-ID-003"),
    ("SmartDX Document ID", "PLATFORM", "", "", "", "Outbound confirmation artifact id", "NEW_TRADE;RESEND;HOT_SWAP;AFFIRM", "Both", "", "platform.smartdx.documentId", "SmartDX:DocumentId", "DQ-REQ-024", "MAP-ID-004"),
    ("SWIFT Message Reference", "PLATFORM", "", "", "", "MT / MX reference", "NEW_TRADE;AMEND;EXERCISE", "Both", "", "platform.swift.msgRef", "SWIFT:20", "DQ-FORMAT-007", "MAP-ID-005"),
    ("Template Bundle ID", "PLATFORM", "", "", "", "Master+Product+Supplement binding", "NEW_TRADE;HOT_SWAP;ROLLBACK;RESEND", "Both", "", "platform.template.bundleId", "—", "DQ-REQ-025", "MAP-ID-006"),
    ("Template Version", "PLATFORM", "", "", "", "Version used at generation", "NEW_TRADE;HOT_SWAP;ROLLBACK;RESEND", "Both", "", "platform.template.version", "—", "DQ-REQ-026", "MAP-ID-007"),
    ("Affirmation Status", "LIFECYCLE", "", "", "", "Matched / Unmatched / Affirmed", "AFFIRM", "Both", "", "lifecycle.affirmation.status", "SmartDX:AffirmStatus", "DQ-ENUM-011", "MAP-ENUM-011"),
    ("Affirmation Timestamp", "LIFECYCLE", "", "", "", "Webhook callback time", "AFFIRM", "Both", "", "lifecycle.affirmation.timestamp", "—", "DQ-CAL-010", "MAP-DATE-002"),
    ("Novation Transferor", "LIFECYCLE", "", "", "", "Outgoing party", "NOVATION", "Both", "", "lifecycle.novation.transferor", "SmartDX:Transferor;SWIFT:Party", "DQ-REQ-027", "MAP-PARTY-001"),
    ("Novation Transferee", "LIFECYCLE", "", "", "", "Incoming party", "NOVATION", "Both", "", "lifecycle.novation.transferee", "SmartDX:Transferee;SWIFT:Party", "DQ-REQ-027", "MAP-PARTY-001"),
    ("Novation Remaining Party", "LIFECYCLE", "", "", "", "Non-transferring party", "NOVATION", "Both", "", "lifecycle.novation.remainingParty", "SmartDX:RemainingParty", "DQ-REQ-027", "MAP-PARTY-001"),
    ("Novation Effective Date", "LIFECYCLE", "", "", "", "Transfer effective", "NOVATION", "Both", "", "lifecycle.novation.effectiveDate", "SmartDX:NovationDate", "DQ-CAL-011", "MAP-DATE-001"),
    ("Lifecycle Event Type", "LIFECYCLE", "", "", "", "NEW_TRADE|AMEND|…", "NEW_TRADE;AMEND;AFFIRM;NOVATION;EXERCISE;TERMINATE;HOT_SWAP;ROLLBACK;RESEND", "Both", "", "lifecycle.eventType", "—", "DQ-ENUM-012", "MAP-ENUM-012"),
    ("Prior Document ID", "LIFECYCLE", "", "", "", "Superseded confirmation", "AMEND;HOT_SWAP;RESEND;NOVATION", "Both", "", "lifecycle.priorDocumentId", "SmartDX:PriorDoc", "DQ-CROSS-009", "MAP-ID-004"),
]

HEADERS = [
    "Attribute / field name",
    "Attribute group",
    "Template layer",
    "Exhibit / template ID",
    "Matrix / version hooks",
    "ISDA 2026 section / annotation note",
    "Lineage",
    "Product type(s)",
    "Depth",
    "Lifecycle events material to",
    "MCA path",
    "MCA sample field (Assumed if invented)",
    "TPS JSON path",
    "Downstream SmartDX / SWIFT target",
    "DQ rule IDs",
    "Mapping / transform rule IDs",
    "Notes / Assumed flag",
]


def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s[:80] if s else "Field"


def extract_fields_from_section(text: str) -> list[str]:
    """Heuristic field label extraction from confirmation body."""
    cleaned = re.sub(r"Commented \[A\d+\]:.*?(?=\n|$)", " ", text)
    cleaned = re.sub(r"Copyright ©.*?\n", "\n", cleaned)
    cleaned = re.sub(r"===== PAGE \d+ =====", "\n", cleaned)
    cleaned = re.sub(r"-\s*\n\s*", "", cleaned)
    # Drop dense footnote blocks (lines that are mostly prose after numbered markers)
    fields = []
    seen = set()
    for m in re.finditer(
        r"(?m)^\s*\[?\s*([A-Z][^:\n]{1,80}?)\s*:\s*(?:\[|/|Deliverable|Applicable|Not |Party |The |\[\[|Non-|Mandatory|Optional|Expiry|Exercise)",
        cleaned,
    ):
        label = m.group(1).strip()
        label = re.sub(r"\s+", " ", label)
        label = re.sub(r"^\d+\.?\s*", "", label)
        label = re.sub(r"\]\d*$", "", label).strip()
        if len(label) < 3 or len(label) > 70:
            continue
        if label.lower().startswith("see exhibit"):
            continue
        if label in NOISE_LABELS or label in seen:
            continue
        if re.match(r"^\d+$", label):
            continue
        if label.endswith("]") and "[" not in label:
            continue
        seen.add(label)
        fields.append(label)
    return fields


def slice_exhibit_body(full: str, exhibit_id: str, next_id: str | None) -> str:
    """Slice exhibit body using ALL-CAPS header + 'to the 2026 FX Definitions' (skip TOC)."""
    start = re.search(
        rf"EXHIBIT {re.escape(exhibit_id)}\s*\nto the 2026 FX Definitions",
        full,
    )
    if not start:
        start = re.search(
            rf"Exhibit {re.escape(exhibit_id)}\s*\nto the 2026 FX Definitions",
            full,
            re.I,
        )
    if not start:
        return ""
    if next_id:
        end = re.search(
            rf"(?:EXHIBIT|Exhibit) {re.escape(next_id)}\s*\nto the 2026 FX Definitions",
            full[start.end() :],
            re.I,
        )
        if end:
            return full[start.start() : start.end() + end.start()]
    return full[start.start() :]


def tps_path(exhibit: str, field: str) -> str:
    return f"trade.exhibits['{exhibit}'].{slug(field)[:1].lower() + slug(field)[1:]}"


def make_row(
    attr,
    group,
    layer,
    exhibit,
    matrix,
    note,
    lineage,
    product,
    depth,
    lifecycle,
    mca_path,
    mca_sample,
    tps,
    downstream,
    dq,
    mapping,
    notes="",
):
    return {
        HEADERS[0]: attr,
        HEADERS[1]: group,
        HEADERS[2]: layer,
        HEADERS[3]: exhibit,
        HEADERS[4]: matrix,
        HEADERS[5]: note,
        HEADERS[6]: lineage,
        HEADERS[7]: product,
        HEADERS[8]: depth,
        HEADERS[9]: lifecycle,
        HEADERS[10]: mca_path,
        HEADERS[11]: mca_sample,
        HEADERS[12]: tps,
        HEADERS[13]: downstream,
        HEADERS[14]: dq,
        HEADERS[15]: mapping,
        HEADERS[16]: notes,
    }


def build_attribute_rows(full_text: str) -> list[dict]:
    rows: list[dict] = []

    # Exhibit I curated
    for f in EXHIBIT_I_FIELDS:
        (
            attr,
            group,
            layer,
            exhibit,
            matrix,
            note,
            lifecycle,
            mca_path,
            mca_sample,
            tps,
            downstream,
            dq,
            mapping,
        ) = f
        assumed = "Assumed" if "Assumed" in mca_sample else ""
        rows.append(
            make_row(
                attr,
                group,
                layer,
                exhibit,
                matrix,
                note,
                f"{PRIMARY_PDF} · Exhibit I · {EXHIBITS['I']['pages']}",
                "ALL",
                "Standard",
                lifecycle,
                mca_path,
                mca_sample,
                tps,
                downstream,
                dq,
                mapping,
                assumed,
            )
        )

    # II-B deep curated
    for f in IIB_DEEP_FIELDS:
        (
            attr,
            group,
            layer,
            exhibit,
            matrix,
            note,
            lifecycle,
            mca_path,
            mca_sample,
            tps,
            downstream,
            dq,
            mapping,
        ) = f
        rows.append(
            make_row(
                attr,
                group,
                layer,
                exhibit,
                matrix,
                note,
                f"{PRIMARY_PDF} · Exhibit II-B · {EXHIBITS['II-B']['pages']}",
                "Deliverable_FX_Option",
                "Deep",
                lifecycle,
                mca_path,
                mca_sample,
                tps,
                downstream,
                dq,
                mapping,
                "Deep inventory",
            )
        )

    # Other exhibits: extracted from body (skip I + II-B curated)
    for i, eid in enumerate(EXHIBIT_ORDER):
        if eid in ("I", "II-B"):
            continue
        meta = EXHIBITS[eid]
        next_id = EXHIBIT_ORDER[i + 1] if i + 1 < len(EXHIBIT_ORDER) else None
        section = slice_exhibit_body(full_text, eid, next_id)
        fields = extract_fields_from_section(section)
        if not fields:
            fields = [f"[Exhibit-level] {meta['title']}"]
        for attr in fields:
            depth = meta["depth"]
            note = f"{meta['title']} field"
            lineage = f"{PRIMARY_PDF} · Exhibit {eid} · {meta['pages']}"
            if attr.startswith("[Exhibit-level]"):
                note = "Exhibit present; heuristic extraction sparse — lineage at exhibit level"
            rows.append(
                make_row(
                    attr,
                    meta["group"],
                    meta["layer"],
                    eid,
                    meta["matrix"],
                    note,
                    lineage,
                    meta["product"],
                    depth,
                    meta["lifecycle"],
                    "Both",
                    "",
                    tps_path(eid, attr),
                    f"SmartDX:{slug(attr)}",
                    "DQ-LINEAGE-001",
                    "MAP-GENERIC-001",
                    "Standard depth; PDF heuristic extraction",
                )
            )

    # MCA Assumed
    for f in MCA_ASSUMED:
        (
            attr,
            group,
            layer,
            exhibit,
            matrix,
            note,
            lifecycle,
            mca_path,
            mca_sample,
            tps,
            downstream,
            dq,
            mapping,
        ) = f
        rows.append(
            make_row(
                attr,
                group,
                layer,
                exhibit or "—",
                matrix,
                note,
                "Assumed MCA sample (not from ISDA PDF) · invented for With_MCA path",
                "ALL (eligible under Assumed MCA product set)",
                "Standard",
                lifecycle,
                mca_path,
                mca_sample,
                tps,
                downstream,
                dq,
                mapping,
                "Assumed",
            )
        )

    # Platform / lifecycle
    for f in PLATFORM_FIELDS:
        (
            attr,
            group,
            layer,
            exhibit,
            matrix,
            note,
            lifecycle,
            mca_path,
            mca_sample,
            tps,
            downstream,
            dq,
            mapping,
        ) = f
        rows.append(
            make_row(
                attr,
                group,
                layer or "—",
                exhibit or "—",
                matrix,
                note,
                "CDU-PS PLATFORM / LIFECYCLE (not ISDA legal text)",
                "ALL",
                "Deep" if "Novation" in attr or "Template" in attr else "Standard",
                lifecycle,
                mca_path,
                mca_sample,
                tps,
                downstream,
                dq,
                mapping,
                "Platform",
            )
        )

    # Matrix binding rows
    for mid, title, hook in [
        ("MATRIX-SRO", "SRO Matrix Binding", "SRO Matrix version as of Trade Date or pinned"),
        ("MATRIX-EM", "EM Currency Matrix Binding", "EM Currency Matrix version as of Trade Date or pinned"),
        ("MATRIX-CFC", "Currencies/Financial Centers Matrix Binding", "Version pin optional"),
        ("MATRIX-DM", "Developed Markets Currency Matrix Binding", "Version pin optional"),
        ("MATRIX-CNY", "Offshore CNY Disruption Fallback Matrix Binding", "Where CNY offshore disruption elected"),
    ]:
        rows.append(
            make_row(
                title,
                "MATRIX",
                "PRODUCT",
                "II-*",
                hook,
                "Introduction to 2026 FX Definitions — Matrices versioned separately from Main Book",
                "Introduction_to_the_2026_FX_Definitions_ab61.pdf · Matrices overview; templates PDF footnotes",
                "Products referencing matrix",
                "Standard",
                "NEW_TRADE;AMEND;HOT_SWAP",
                "Both",
                "",
                f"trade.legal.matrix.{mid.lower()}",
                "SmartDX:MatrixBinding",
                "DQ-LEGAL-001;DQ-MATRIX-001",
                "MAP-MATRIX-001",
                "",
            )
        )

    return rows


def rules_dq_rows() -> list[list]:
    rules = [
        ["DQ-REQ-001", "REQUIRED", "ERROR", "PRODUCT", "Deliverable_FX_Option", "NEW_TRADE", "Transaction Type present when elected", "ISDA-derived"],
        ["DQ-REQ-002", "REQUIRED", "ERROR", "PRODUCT", "ALL", "NEW_TRADE", "Trade Date required", "ISDA-derived"],
        ["DQ-REQ-003", "REQUIRED", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Buyer and Seller required and distinct", "ISDA-derived"],
        ["DQ-REQ-004", "REQUIRED", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Call/Put currencies required unless Binary", "ISDA-derived"],
        ["DQ-REQ-005", "REQUIRED", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Expiration Date required (non-Binary barrier edge cases excepted)", "ISDA-derived"],
        ["DQ-REQ-006", "REQUIRED", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Expiration Time + location required", "ISDA-derived"],
        ["DQ-REQ-007", "REQUIRED", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Premium expected for FX Option", "Assumed"],
        ["DQ-REQ-010", "REQUIRED", "ERROR", "COMMON", "ALL", "NEW_TRADE", "Confirmation Date required", "ISDA-derived"],
        ["DQ-REQ-011", "REQUIRED", "ERROR", "COMMON", "ALL", "NEW_TRADE", "Party B name/address required", "ISDA-derived"],
        ["DQ-REQ-012", "REQUIRED", "ERROR", "COMMON", "ALL", "NEW_TRADE", "Party A and Party B names required", "ISDA-derived"],
        ["DQ-REQ-013", "REQUIRED", "WARN", "COMMON", "ALL", "NEW_TRADE", "Calculation Agent election or Agreement default", "ISDA-derived"],
        ["DQ-REQ-020", "REQUIRED", "ERROR", "PLATFORM", "ALL", "NEW_TRADE", "CDU-PS Trade ID required", "Assumed"],
        ["DQ-REQ-021", "REQUIRED", "ERROR", "PLATFORM", "ALL", "NEW_TRADE", "TPS Source System required", "Assumed"],
        ["DQ-REQ-022", "REQUIRED", "ERROR", "PLATFORM", "ALL", "ALL_EVENTS", "TPS Event ID required", "Assumed"],
        ["DQ-REQ-023", "REQUIRED", "ERROR", "PLATFORM", "ALL", "ALL_EVENTS", "Idempotency Key required on mutating APIs", "Assumed"],
        ["DQ-REQ-024", "REQUIRED", "WARN", "PLATFORM", "ALL", "RESEND;AFFIRM", "SmartDX Document ID after first send", "Assumed"],
        ["DQ-REQ-025", "REQUIRED", "ERROR", "PLATFORM", "ALL", "NEW_TRADE;HOT_SWAP", "Template Bundle ID required", "Assumed"],
        ["DQ-REQ-026", "REQUIRED", "ERROR", "PLATFORM", "ALL", "NEW_TRADE;HOT_SWAP;ROLLBACK", "Template Version required", "Assumed"],
        ["DQ-REQ-027", "REQUIRED", "ERROR", "LIFECYCLE", "ALL", "NOVATION", "Transferor, Transferee, Remaining Party required", "Assumed"],
        ["DQ-CAL-001", "CALENDAR", "ERROR", "PRODUCT", "ALL", "NEW_TRADE", "Trade Date is valid ISO date and not future beyond cut-off", "Assumed"],
        ["DQ-CAL-002", "CALENDAR", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Commencement Date ≤ Expiration Date", "ISDA-derived"],
        ["DQ-CAL-003", "CALENDAR", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Expiration Date ≥ Trade Date", "ISDA-derived"],
        ["DQ-CAL-004", "CALENDAR", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Settlement Date after Exercise/Valuation per cycle", "ISDA-derived"],
        ["DQ-CAL-005", "CALENDAR", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Potential Exercise Dates within Exercise Period (Bermuda)", "ISDA-derived"],
        ["DQ-CAL-006", "CALENDAR", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Premium Payment Date typically on/near Trade Date", "Assumed"],
        ["DQ-CAL-007", "CALENDAR", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Spot Rate Fixing Day consistent with SRO", "ISDA-derived"],
        ["DQ-CAL-008", "CALENDAR", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Valuation Date defaults to Exercise Date unless overridden", "ISDA-derived"],
        ["DQ-CAL-009", "CALENDAR", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Business Day calendars resolvable", "ISDA-derived"],
        ["DQ-CAL-010", "CALENDAR", "ERROR", "LIFECYCLE", "ALL", "AFFIRM", "Affirmation timestamp ISO-8601", "Assumed"],
        ["DQ-CAL-011", "CALENDAR", "ERROR", "LIFECYCLE", "ALL", "NOVATION", "Novation Effective Date ≥ Trade Date", "Assumed"],
        ["DQ-FORMAT-001", "FORMAT", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Time fields parseable with zone/center", "Assumed"],
        ["DQ-FORMAT-002", "FORMAT", "WARN", "PRODUCT", "ALL", "NEW_TRADE", "Rounding convention descriptive text non-empty if present", "ISDA-derived"],
        ["DQ-FORMAT-003", "FORMAT", "ERROR", "COMMON", "ALL", "NEW_TRADE", "LEI matches ISO 17442 pattern when present", "Assumed"],
        ["DQ-FORMAT-004", "FORMAT", "WARN", "COMMON", "ALL", "NEW_TRADE", "Account details SSI structure", "Assumed"],
        ["DQ-FORMAT-005", "FORMAT", "WARN", "COMMON", "ALL", "NEW_TRADE", "Office codes non-empty when present", "Assumed"],
        ["DQ-FORMAT-006", "FORMAT", "WARN", "COMMON", "ALL", "NEW_TRADE", "Notice contact email/phone present", "Assumed"],
        ["DQ-FORMAT-007", "FORMAT", "WARN", "PLATFORM", "ALL", "NEW_TRADE", "SWIFT msg ref format", "Assumed"],
        ["DQ-ENUM-001", "FORMAT", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Option Style ∈ {American,Bermuda,European} or omitted for Binary Barrier", "ISDA-derived"],
        ["DQ-ENUM-002", "FORMAT", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Option Type Put/Call currencies or Binary", "ISDA-derived"],
        ["DQ-ENUM-003", "FORMAT", "ERROR", "PRODUCT", "Deliverable_*", "NEW_TRADE", "Settlement = Deliverable unless overridden", "ISDA-derived"],
        ["DQ-ENUM-004", "FORMAT", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Automatic Exercise Not applicable only when disapplied", "ISDA-derived"],
        ["DQ-ENUM-005", "FORMAT", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Strike equality ∈ {Expiry at Strike, Exercise at Strike}", "ISDA-derived"],
        ["DQ-ENUM-006", "FORMAT", "WARN", "COMMON", "ALL", "NEW_TRADE", "Acks/Reps Disapplied or omitted", "ISDA-derived"],
        ["DQ-ENUM-011", "FORMAT", "ERROR", "LIFECYCLE", "ALL", "AFFIRM", "Affirmation Status ∈ {Matched,Unmatched,Affirmed,Disputed}", "Assumed"],
        ["DQ-ENUM-012", "FORMAT", "ERROR", "LIFECYCLE", "ALL", "ALL_EVENTS", "Lifecycle Event Type in catalog", "Assumed"],
        ["DQ-CROSS-001", "CROSS_FIELD", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "If not Binary: (CallAmt+PutAmt) OR (Strike + one amount)", "ISDA-derived"],
        ["DQ-CROSS-002", "CROSS_FIELD", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "If averaging Strike, only one of Call/Put amount numeric", "ISDA-derived"],
        ["DQ-CROSS-003", "CROSS_FIELD", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "If Strike=The Averaging Rate then III-G elected", "ISDA-derived"],
        ["DQ-CROSS-004", "CROSS_FIELD", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Style vs Exercise Period / Potential Exercise Dates consistency", "ISDA-derived"],
        ["DQ-CROSS-005", "CROSS_FIELD", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Partial Exercise only European; Multiple only American/Bermuda", "ISDA-derived"],
        ["DQ-CROSS-006", "CROSS_FIELD", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Full Automated Exercise implies European and SRO set", "ISDA-derived"],
        ["DQ-CROSS-007", "CROSS_FIELD", "WARN", "PRODUCT", "FX_Option_*", "NEW_TRADE", "BizDay Exercise ≈ Valuation", "ISDA-derived"],
        ["DQ-CROSS-008", "CROSS_FIELD", "WARN", "COMMON", "ALL", "NEW_TRADE", "Joint CA dispute resolution only if Joint CA", "ISDA-derived"],
        ["DQ-CROSS-009", "CROSS_FIELD", "ERROR", "LIFECYCLE", "ALL", "AMEND;HOT_SWAP;RESEND", "Prior Document ID must exist", "Assumed"],
        ["DQ-LEGAL-001", "LEGAL_ELECTION", "WARN", "MATRIX", "ALL", "NEW_TRADE", "Matrix version pin valid published version", "ISDA-derived"],
        ["DQ-LEGAL-002", "LEGAL_ELECTION", "ERROR", "COMMON", "ALL", "NEW_TRADE", "FX Definitions version election present", "ISDA-derived"],
        ["DQ-LEGAL-003", "LEGAL_ELECTION", "ERROR", "COMMON", "ALL", "NEW_TRADE", "With_MCA requires Master Agreement date or MCA profile", "Assumed"],
        ["DQ-LEGAL-004", "LEGAL_ELECTION", "WARN", "COMMON", "ALL", "NEW_TRADE", "Without_MCA enables long-form fallback language", "ISDA-derived"],
        ["DQ-LEGAL-005", "LEGAL_ELECTION", "WARN", "COMMON", "ALL", "NEW_TRADE", "Governing law election when no executed Master", "ISDA-derived"],
        ["DQ-LEGAL-006", "LEGAL_ELECTION", "WARN", "COMMON", "ALL", "NEW_TRADE", "Fallback Benchmark if index/benchmark used", "ISDA-derived"],
        ["DQ-MATRIX-001", "LEGAL_ELECTION", "ERROR", "MATRIX", "FX_Option_*", "NEW_TRADE", "SRO code resolvable in pinned/latest SRO Matrix", "ISDA-derived"],
        ["DQ-LINEAGE-001", "LINEAGE_PRESENT", "WARN", "ALL", "ALL", "ALL_EVENTS", "Lineage PDF+exhibit present for mapped attribute", "Assumed"],
        ["DQ-MCA-001", "REQUIRED", "ERROR", "MCA", "ALL", "NEW_TRADE", "MCA Profile ID when path=With_MCA", "Assumed"],
        ["DQ-MCA-002", "CALENDAR", "ERROR", "MCA", "ALL", "NEW_TRADE", "MCA Effective Date ≤ Trade Date", "Assumed"],
        ["DQ-MCA-003", "LEGAL_ELECTION", "ERROR", "MCA", "ALL", "NEW_TRADE", "MCA defs year election in {1998,2026}", "Assumed"],
        ["DQ-MCA-004", "LEGAL_ELECTION", "ERROR", "MCA", "ALL", "NEW_TRADE", "Product in MCA eligible set", "Assumed"],
        ["DQ-MCA-005", "REQUIRED", "WARN", "MCA", "ALL", "NEW_TRADE", "Default CA from MCA applied if confirm omits", "Assumed"],
        ["DQ-MCA-006", "FORMAT", "WARN", "MCA", "ALL", "NEW_TRADE", "Notice channel populated from MCA", "Assumed"],
        ["DQ-MCA-007", "LEGAL_ELECTION", "WARN", "MCA", "ALL", "NEW_TRADE", "Settlement election CLS/bilateral", "Assumed"],
        ["DQ-MCA-008", "LEGAL_ELECTION", "WARN", "MCA", "FX_Option_*", "NEW_TRADE", "Auto-exercise default from MCA", "Assumed"],
        ["DQ-MCA-009", "FORMAT", "WARN", "MCA", "ALL", "NEW_TRADE", "Dispute venue present", "Assumed"],
        ["DQ-MCA-010", "LEGAL_ELECTION", "WARN", "MCA", "ALL", "NEW_TRADE", "Confirmation method electronic/paper", "Assumed"],
    ]
    # mapping rules companion
    mapping = [
        ["MAP-ENUM-001", "TRANSFORM", "INFO", "PRODUCT", "ALL", "NEW_TRADE", "Map TPS product code → ISDA Transaction Type enum", "Assumed"],
        ["MAP-ENUM-002", "TRANSFORM", "INFO", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Map optionStyle codes", "Assumed"],
        ["MAP-ENUM-003", "TRANSFORM", "INFO", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Map optionType / Binary", "Assumed"],
        ["MAP-ENUM-004", "TRANSFORM", "INFO", "PRODUCT", "Deliverable_*", "NEW_TRADE", "Settlement method map", "Assumed"],
        ["MAP-ENUM-005", "TRANSFORM", "INFO", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Strike equality outcome map", "Assumed"],
        ["MAP-ENUM-006", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Governing law code map", "Assumed"],
        ["MAP-ENUM-007", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Acks/Reps election map", "Assumed"],
        ["MAP-ENUM-008", "TRANSFORM", "INFO", "MCA", "ALL", "NEW_TRADE", "MCA product set tokenization", "Assumed"],
        ["MAP-ENUM-009", "TRANSFORM", "INFO", "MCA", "ALL", "NEW_TRADE", "Settlement election → SWIFT", "Assumed"],
        ["MAP-ENUM-010", "TRANSFORM", "INFO", "MCA", "ALL", "NEW_TRADE", "Confirmation method channel map", "Assumed"],
        ["MAP-ENUM-011", "TRANSFORM", "INFO", "LIFECYCLE", "ALL", "AFFIRM", "Affirm status normalize", "Assumed"],
        ["MAP-ENUM-012", "TRANSFORM", "INFO", "LIFECYCLE", "ALL", "ALL_EVENTS", "Event type normalize", "Assumed"],
        ["MAP-DATE-001", "TRANSFORM", "INFO", "ALL", "ALL", "ALL_EVENTS", "Normalize dates to ISO-8601 date", "Assumed"],
        ["MAP-DATE-002", "TRANSFORM", "INFO", "LIFECYCLE", "ALL", "AFFIRM", "Timestamps to ISO-8601 datetime UTC", "Assumed"],
        ["MAP-DATE-LIST-001", "TRANSFORM", "INFO", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Split Potential Exercise Dates list", "Assumed"],
        ["MAP-TIME-001", "TRANSFORM", "INFO", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Parse time + center", "Assumed"],
        ["MAP-AMT-001", "TRANSFORM", "INFO", "PRODUCT", "ALL", "NEW_TRADE", "Amount + currency pair encode", "Assumed"],
        ["MAP-AMT-002", "TRANSFORM", "INFO", "PRODUCT", "FX_Option_*", "NEW_TRADE", "Premium amount encode", "Assumed"],
        ["MAP-CCY-001", "TRANSFORM", "INFO", "PRODUCT", "ALL", "NEW_TRADE", "ISO 4217 currency normalize", "Assumed"],
        ["MAP-RATE-001", "TRANSFORM", "INFO", "PRODUCT", "ALL", "NEW_TRADE", "Rate decimal normalize", "Assumed"],
        ["MAP-PARTY-001", "TRANSFORM", "INFO", "COMMON", "ALL", "ALL_EVENTS", "Party A/B ↔ Buyer/Seller role resolve", "Assumed"],
        ["MAP-PARTY-002", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Address block format", "Assumed"],
        ["MAP-PARTY-003", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Calculation Agent party resolve", "Assumed"],
        ["MAP-PARTY-004", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Broker/Arranger optional map", "Assumed"],
        ["MAP-LEI-001", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "LEI uppercase normalize", "Assumed"],
        ["MAP-SSI-001", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "SSI → SmartDX/SWIFT settlement fields", "Assumed"],
        ["MAP-LOC-001", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Office / financial center codes", "Assumed"],
        ["MAP-CAL-001", "TRANSFORM", "INFO", "PRODUCT", "ALL", "NEW_TRADE", "Business Day calendar codes", "Assumed"],
        ["MAP-SRO-001", "TRANSFORM", "INFO", "MATRIX", "ALL", "NEW_TRADE", "SRO code → matrix row resolution", "Assumed"],
        ["MAP-MATRIX-001", "TRANSFORM", "INFO", "MATRIX", "ALL", "NEW_TRADE", "Matrix version pin encode", "Assumed"],
        ["MAP-LEGAL-001", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Defs version election encode", "Assumed"],
        ["MAP-LEGAL-002", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Master agreement date encode", "Assumed"],
        ["MAP-LEGAL-003", "TRANSFORM", "INFO", "COMMON", "ALL", "NEW_TRADE", "Long-form fallback flag", "Assumed"],
        ["MAP-BOOL-001", "TRANSFORM", "INFO", "ALL", "ALL", "ALL_EVENTS", "Applicable / Not applicable → boolean", "Assumed"],
        ["MAP-TEXT-001", "TRANSFORM", "INFO", "ALL", "ALL", "ALL_EVENTS", "Free-text passthrough trim", "Assumed"],
        ["MAP-GENERIC-001", "TRANSFORM", "INFO", "PRODUCT", "ALL", "NEW_TRADE", "Generic exhibit field passthrough", "Assumed"],
        ["MAP-ID-001", "TRANSFORM", "INFO", "PLATFORM", "ALL", "ALL_EVENTS", "Trade ID mint/validate", "Assumed"],
        ["MAP-ID-002", "TRANSFORM", "INFO", "PLATFORM", "ALL", "NEW_TRADE", "TPS source system code", "Assumed"],
        ["MAP-ID-003", "TRANSFORM", "INFO", "PLATFORM", "ALL", "ALL_EVENTS", "Event/idempotency key", "Assumed"],
        ["MAP-ID-004", "TRANSFORM", "INFO", "PLATFORM", "ALL", "RESEND;AFFIRM", "SmartDX document id", "Assumed"],
        ["MAP-ID-005", "TRANSFORM", "INFO", "PLATFORM", "ALL", "NEW_TRADE", "SWIFT msg ref", "Assumed"],
        ["MAP-ID-006", "TRANSFORM", "INFO", "PLATFORM", "ALL", "HOT_SWAP", "Template bundle id", "Assumed"],
        ["MAP-ID-007", "TRANSFORM", "INFO", "PLATFORM", "ALL", "HOT_SWAP;ROLLBACK", "Template version id", "Assumed"],
        ["MAP-MCA-001", "TRANSFORM", "INFO", "MCA", "ALL", "NEW_TRADE", "Resolve Assumed MCA profile defaults onto COMMON fields", "Assumed"],
    ]
    return rules, mapping


def template_admin_rows() -> list[list]:
    header = [
        "Admin Field",
        "Description",
        "Applies to layer",
        "Example / Allowed values",
        "Required",
        "Notes",
    ]
    rows = [
        header,
        ["templateBundleId", "Composite binding id", "MASTER+PRODUCT+SUPPLEMENT", "TB-FXO-DEL-2026-001", "Y", ""],
        ["masterTemplateId", "Exhibit I template id", "MASTER", "EXH-I-2026-v1", "Y", ""],
        ["productExhibitId", "Exhibit II-* id", "PRODUCT", "II-B", "Y", "Routing key"],
        ["productType", "Canonical product enum", "PRODUCT", "Deliverable_FX_Option", "Y", ""],
        ["supplementExhibitIds", "JSON array of III-*", "SUPPLEMENT", '["III-A","III-H"]', "N", "Elected overlays"],
        ["matrixBindings", "JSON matrix pins", "MATRIX", '{"SRO":"2026-03-03","EM":null}', "N", ""],
        ["mcaRequired", "Whether MCA profile required", "MCA", "true|false", "Y", "Path selector"],
        ["mcaProfileId", "Assumed MCA profile", "MCA", "MCA-SCB-ACME-2026-001", "If mcaRequired", "Assumed"],
        ["version", "Template version semver/int", "ALL", "1.2.0", "Y", ""],
        ["status", "Lifecycle of template version", "ALL", "DRAFT|LIVE|RETIRED", "Y", ""],
        ["activatedAt", "When version went LIVE", "ALL", "ISO-8601", "If LIVE", ""],
        ["retiredAt", "When RETIRED", "ALL", "ISO-8601", "If RETIRED", ""],
        ["hotReloadEnabled", "Allow HOT_SWAP without redeploy", "ALL", "true|false", "Y", "Prototype default true"],
        ["rollbackTargetVersion", "Prior LIVE version", "ALL", "1.1.0", "N", ""],
        ["routingRules", "Product/event → bundle", "PRODUCT", "JSON", "Y", ""],
        ["audit.lastChangedBy", "Admin user", "ALL", "uid", "Y", ""],
        ["audit.lastChangedAt", "Timestamp", "ALL", "ISO-8601", "Y", ""],
        ["resendPolicy", "On HOT_SWAP auto-resend?", "PLATFORM", "AUTO|MANUAL", "Y", ""],
        ["legalDefsYear", "1998|2026", "MASTER", "2026", "Y", ""],
        ["notes", "Free text", "ALL", "—", "N", ""],
    ]
    return rows


def ldm_rows() -> list[list]:
    header = ["Entity", "Attribute", "PK/FK", "Type", "Related entity", "Cardinality", "Notes"]
    rows = [
        header,
        ["ConfirmationInstance", "confirmationId", "PK", "string", "", "1", "Runtime confirmation"],
        ["ConfirmationInstance", "tradeId", "FK", "string", "Trade", "N:1", ""],
        ["ConfirmationInstance", "masterTemplateVersionId", "FK", "string", "TemplateVersion", "N:1", "Exhibit I"],
        ["ConfirmationInstance", "productTemplateVersionId", "FK", "string", "TemplateVersion", "N:1", "Exhibit II-*"],
        ["ConfirmationInstance", "supplementTemplateVersionIds", "FK[]", "string[]", "TemplateVersion", "N:M", "Exhibit III-*"],
        ["ConfirmationInstance", "matrixBindingIds", "FK[]", "string[]", "MatrixBinding", "N:M", ""],
        ["ConfirmationInstance", "mcaProfileId", "FK", "string?", "McaProfile", "N:0..1", "With_MCA only"],
        ["ConfirmationInstance", "documentArtifactId", "FK", "string", "DocumentArtifact", "1:1", ""],
        ["ConfirmationInstance", "mcaPath", "", "enum", "", "1", "With_MCA|Without_MCA"],
        ["Trade", "tradeId", "PK", "string", "", "1", ""],
        ["Trade", "productType", "", "enum", "FinancialProduct", "N:1", ""],
        ["Trade", "tpsPayload", "", "json", "", "1", "TPS JSON"],
        ["FinancialProduct", "productType", "PK", "enum", "", "1", "Ontology"],
        ["FinancialProduct", "exhibitId", "", "string", "", "1", "II-*"],
        ["LegalFramework", "frameworkId", "PK", "string", "", "1", ""],
        ["LegalFramework", "defsYear", "", "enum", "", "1", "1998|2026"],
        ["LegalFramework", "mainBookVersion", "", "string", "", "1", ""],
        ["McaProfile", "mcaProfileId", "PK", "string", "", "1", "Assumed sample"],
        ["McaProfile", "elections", "", "json", "", "1", "Assumed fields"],
        ["DynamicTemplate", "templateId", "PK", "string", "", "1", ""],
        ["DynamicTemplate", "layer", "", "enum", "", "1", "MASTER|PRODUCT|SUPPLEMENT"],
        ["DynamicTemplate", "exhibitId", "", "string", "", "1", ""],
        ["TemplateVersion", "templateVersionId", "PK", "string", "", "1", ""],
        ["TemplateVersion", "templateId", "FK", "string", "DynamicTemplate", "N:1", ""],
        ["TemplateVersion", "version", "", "string", "", "1", ""],
        ["TemplateVersion", "status", "", "enum", "", "1", "DRAFT|LIVE|RETIRED"],
        ["AttributeDefinition", "attributeId", "PK", "string", "", "1", "Excel row"],
        ["AttributeDefinition", "group", "", "enum", "", "1", "COMMON|…"],
        ["AttributeDefinition", "exhibitId", "", "string", "", "1", ""],
        ["AttributeDefinition", "tpsJsonPath", "", "string", "", "1", ""],
        ["MappingRule", "mappingRuleId", "PK", "string", "", "1", "MAP-*"],
        ["MappingRule", "attributeId", "FK", "string", "AttributeDefinition", "N:1", ""],
        ["DQRule", "dqRuleId", "PK", "string", "", "1", "DQ-*"],
        ["DQRule", "attributeId", "FK", "string?", "AttributeDefinition", "N:0..1", ""],
        ["DocumentArtifact", "documentId", "PK", "string", "", "1", "SmartDX doc"],
        ["DocumentArtifact", "templateVersionId", "FK", "string", "TemplateVersion", "N:1", "Frozen at gen"],
        ["DocumentArtifact", "channel", "", "enum", "", "1", "SmartDX|SWIFT|BOTH"],
        ["LifecycleEvent", "eventId", "PK", "string", "", "1", ""],
        ["LifecycleEvent", "tradeId", "FK", "string", "Trade", "N:1", ""],
        ["LifecycleEvent", "eventType", "", "enum", "", "1", "NEW_TRADE|…"],
        ["LifecycleEvent", "payload", "", "json", "", "1", ""],
        ["NovationTransfer", "novationId", "PK", "string", "", "1", ""],
        ["NovationTransfer", "tradeId", "FK", "string", "Trade", "N:1", ""],
        ["NovationTransfer", "transferor", "", "string", "", "1", ""],
        ["NovationTransfer", "transferee", "", "string", "", "1", ""],
        ["NovationTransfer", "remainingParty", "", "string", "", "1", ""],
        ["NovationTransfer", "effectiveDate", "", "date", "", "1", ""],
        ["MatrixBinding", "matrixBindingId", "PK", "string", "", "1", ""],
        ["MatrixBinding", "matrixType", "", "enum", "", "1", "SRO|EM|…"],
        ["MatrixBinding", "version", "", "string", "", "1", ""],
        # adjacency summary
        ["REL", "ConfirmationInstance", "", "composed_of", "DynamicTemplate layers", "1→1+N", "MASTER+PRODUCT+ΣSUPPLEMENT"],
        ["REL", "ConfirmationInstance", "", "optionally_uses", "McaProfile", "0..1", "With_MCA"],
        ["REL", "ConfirmationInstance", "", "binds", "MatrixBinding", "0..N", ""],
        ["REL", "LifecycleEvent", "", "triggers", "DocumentArtifact", "0..N", "generate/resend"],
        ["REL", "NovationTransfer", "", "emits", "LifecycleEvent", "1", "NOVATION"],
        ["REL", "TemplateVersion", "", "hot_swapped_by", "TemplateVersion", "0..1", "admin"],
    ]
    return rows


def fxo_lifecycle_rows() -> list[list]:
    header = [
        "Step",
        "Lifecycle event",
        "Actor / System",
        "Service",
        "Action",
        "Template version used",
        "MCA path",
        "Inbound/Outbound",
        "Notes / edge",
    ]
    rows = [
        header,
        ["1", "NEW_TRADE", "TPS", "Trade Capture", "Emit new Deliverable FXO economics", "—", "Both", "IN", "Sample EUR/USD EUR Call"],
        ["2", "NEW_TRADE", "CDU-PS", "Ingest API POST /events", "Validate idempotency + DQ", "—", "Both", "IN", "Rules_DQ applied"],
        ["3", "NEW_TRADE", "CDU-PS", "Legal Resolver", "Resolve defs year, MCA path, matrix pins", "LegalFramework+McaProfile", "With_MCA / Without_MCA", "INT", "Dual path branch"],
        ["4", "NEW_TRADE", "CDU-PS", "Template Engine", "Compose MASTER I + PRODUCT II-B + supplements", "LIVE TB-FXO-DEL-2026-001 v1.0.0", "Both", "INT", "Wrong bundle possible → step 8"],
        ["5", "NEW_TRADE", "SmartDX", "Confirmation Gateway", "Render & send electronic confirmation", "v1.0.0", "Both", "OUT", "DocumentArtifact created"],
        ["6", "NEW_TRADE", "SWIFT", "Messaging", "Optional MT/MX economic notify", "v1.0.0", "Both", "OUT", "Parallel channel"],
        ["7", "NEW_TRADE", "CDU-PS", "TPS Callback POST /callbacks/tps", "Ack generation status", "v1.0.0", "Both", "OUT", ""],
        ["8", "HOT_SWAP", "Ops Admin", "Template Admin UI/API", "Detect wrong product template; activate correct LIVE version", "v1.0.0 → v1.1.0", "Both", "INT", "Wrong→hot-swap"],
        ["9", "RESEND", "CDU-PS", "Document Service POST /documents/{id}/resend", "Regenerate with v1.1.0; supersede prior", "v1.1.0", "Both", "OUT", "Prior Document ID linked"],
        ["10", "RESEND", "SmartDX", "Confirmation Gateway", "Resend superseding confirmation", "v1.1.0", "Both", "OUT", ""],
        ["11", "AFFIRM", "Counterparty / Affirm platform", "Affirm webhook POST /webhooks/affirmation", "Match/affirm callback", "v1.1.0", "Both", "IN", ""],
        ["12", "AFFIRM", "CDU-PS", "Lifecycle Store", "Persist affirmation status", "v1.1.0", "Both", "INT", ""],
        ["13", "AFFIRM", "CDU-PS", "TPS Callback", "Push affirm status to TPS", "v1.1.0", "Both", "OUT", ""],
        ["14", "AMEND", "TPS", "Trade Capture", "Economic amend (e.g. Strike)", "—", "Both", "IN", ""],
        ["15", "AMEND", "CDU-PS", "Ingest + Template Engine", "Recompose confirmation", "v1.1.0", "Both", "INT", ""],
        ["16", "AMEND", "SmartDX", "Confirmation Gateway", "Send amended confirmation", "v1.1.0", "Both", "OUT", ""],
        ["17", "NOVATION", "TPS", "Novation workflow", "Emit transferor/transferee/remaining", "—", "Both", "IN", "NovationTransfer entity"],
        ["18", "NOVATION", "CDU-PS", "Legal Resolver + Template Engine", "Regen confirmation with new parties; LEI/SSI", "v1.1.0", "Both", "INT", "Exhibit I party blocks"],
        ["19", "NOVATION", "SmartDX + SWIFT", "Gateways", "Send novated confirmation / notify", "v1.1.0", "Both", "OUT", ""],
        ["20", "EXERCISE", "TPS / Exercise desk", "Exercise service", "Exercise notice / Automatic Exercise", "v1.1.0", "Both", "IN", "Edge: Full Automated Exercise"],
        ["21", "EXERCISE", "CDU-PS", "Lifecycle + Settlement prep", "Compute settlement instructions", "v1.1.0", "Both", "INT", ""],
        ["22", "TERMINATE", "TPS", "Trade Capture", "Early term if III-C/III-D elected", "v1.1.0", "Both", "IN", "Disruption edge via III-A"],
        ["23", "ROLLBACK", "Ops Admin", "Template Admin", "Rollback LIVE to prior version", "v1.1.0 → v1.0.0", "Both", "INT", "Optional admin edge"],
    ]
    return rows


def legend_rows() -> list[list]:
    return [
        ["Key", "Meaning"],
        ["COMMON", "Exhibit I shared wrapper fields"],
        ["PRODUCT", "Exhibit II-* product economics"],
        ["SUPPLEMENT", "Exhibit III-* optional overlays"],
        ["MATRIX", "SRO / EM / other matrix bindings"],
        ["MCA", "Assumed Master Confirmation Agreement elections"],
        ["PLATFORM", "CDU-PS / TPS / SmartDX / SWIFT operational fields"],
        ["LIFECYCLE", "Event, novation, affirmation metadata"],
        ["MASTER", "Template layer = Exhibit I"],
        ["PRODUCT (layer)", "Template layer = Exhibit II-*"],
        ["SUPPLEMENT (layer)", "Template layer = Exhibit III-*"],
        ["Deep", "Fully inventoried (II-B Deliverable FX Option)"],
        ["Standard", "Covered; lineage at exhibit level minimum"],
        ["With_MCA", "Path using Assumed MCA profile defaults"],
        ["Without_MCA", "Path using Exhibit I long-form / explicit elections"],
        ["Both", "Attribute applies on either MCA path"],
        ["Assumed", "Invented sample — not copied from ISDA legal text"],
        ["ISDA-derived", "Taken/inferred from uploaded ISDA/EMTA PDFs"],
        ["Effective date", "2026 FX Definitions take effect 22 Nov 2027 (Intro PDF)"],
        ["Primary PDF", PRIMARY_PDF],
        ["Intro PDF", "Introduction_to_the_2026_FX_Definitions_ab61.pdf"],
        ["1998 PDF", "1998-FX-and-Currency-Option-Definitions_0d3f.pdf"],
        ["Annex A PDF", "annex-a-to-the-1998-fx-and-currency-option-definitions-june-30-2023_0919.pdf"],
        ["License", "ISDA/EMTA licensed materials — internal use only; do not redistribute outside license"],
        ["Assumed MCA ID", "MCA-SCB-ACME-2026-001"],
        ["Assumed MCA parties", "Party A = SCB sample desk; Party B = ACME Corp Treasury (invented)"],
        ["Assumed MCA defs", "2026 FX Definitions Version 1.0 Main Book; matrices as-of Trade Date"],
        ["Assumed MCA defaults", "CA=Party A; AutoExercise=Applicable; Notices=email+SmartDX; CLS if eligible"],
        ["Colour (PDF)", "BLUE=new 2026; RED=changed/removed from 1998; ORANGE=streamline; GREEN=EMTA consol; PURPLE=Supplement consol"],
        ["PDF extraction gaps", "Footnotes/comments sometimes split labels; Standard exhibits use heuristic extraction + exhibit-level lineage; colour coding not machine-captured"],
    ]


def style_header(ws, fill_hex="1F4E79"):
    fill = PatternFill("solid", fgColor=fill_hex)
    font = Font(bold=True, color="FFFFFF")
    for cell in ws[1]:
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def autosize(ws, max_width=48):
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        width = 12
        for cell in col[:80]:
            if cell.value:
                width = min(max_width, max(width, len(str(cell.value)) + 2))
        ws.column_dimensions[letter].width = width


def write_sheet(ws, rows: list[list] | list[dict], headers: list[str] | None = None):
    if headers:
        ws.append(headers)
        for r in rows:
            ws.append([r.get(h, "") for h in headers])
    else:
        for r in rows:
            ws.append(r)
    style_header(ws)
    autosize(ws)
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


def main():
    full = PDF_TXT.read_text(encoding="utf-8", errors="replace")
    attr_rows = build_attribute_rows(full)
    dq_rules, map_rules = rules_dq_rows()

    # CSV dump
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(attr_rows)

    wb = Workbook()

    # Sheet 1
    ws1 = wb.active
    ws1.title = "Attribute_Product_Map"
    write_sheet(ws1, attr_rows, HEADERS)

    # Sheet 2
    ws2 = wb.create_sheet("Template_Admin_Utility")
    write_sheet(ws2, template_admin_rows())

    # Sheet 3
    ws3 = wb.create_sheet("Logical_Data_Model")
    write_sheet(ws3, ldm_rows())

    # Sheet 4
    ws4 = wb.create_sheet("Rules_DQ")
    dq_header = [
        "Rule ID",
        "Type",
        "Severity",
        "Applies-to group",
        "Applies-to product",
        "Lifecycle",
        "Expression / description",
        "Assumed vs ISDA-derived",
    ]
    ws4.append(dq_header)
    for r in dq_rules:
        ws4.append(r)
    ws4.append([])
    ws4.append(["--- Mapping / transform rules (referenced from Attribute sheet) ---"])
    ws4.append(dq_header)
    for r in map_rules:
        ws4.append(r)
    style_header(ws4)
    autosize(ws4)

    # Sheet 5
    ws5 = wb.create_sheet("FXO_Deliverable_Lifecycle")
    write_sheet(ws5, fxo_lifecycle_rows())

    # Sheet 6
    ws6 = wb.create_sheet("Legend_Assumptions")
    write_sheet(ws6, legend_rows())

    OUT_XLSX_REPO.parent.mkdir(parents=True, exist_ok=True)
    OUT_XLSX_STORE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_XLSX_REPO)
    wb.save(OUT_XLSX_STORE)

    # counts
    from collections import Counter

    by_ex = Counter(r[HEADERS[3]] for r in attr_rows)
    by_depth = Counter(r[HEADERS[8]] for r in attr_rows)
    print("TOTAL_ROWS", len(attr_rows))
    print("BY_DEPTH", dict(by_depth))
    print("BY_EXHIBIT")
    for k, v in sorted(by_ex.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {k}: {v}")
    print("WROTE", OUT_XLSX_REPO)
    print("WROTE", OUT_XLSX_STORE)
    print("WROTE", OUT_CSV)


if __name__ == "__main__":
    main()

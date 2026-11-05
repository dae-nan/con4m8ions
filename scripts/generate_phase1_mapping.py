#!/usr/bin/env python3
"""CDU-PS ISDA 2026 mapping workbook (library; run scripts/build.py).

Inputs: the curated tables below plus the committed ISDA text extract in
docs/reference/isda/text/ (regenerate that with scripts/extract_isda_text.py).
"""
from __future__ import annotations

import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

REPO = Path(__file__).resolve().parents[1]

PRIMARY_PDF = (
    "2026-FX-Defs-Consolidated-Confirmation-Templates_Colour-Coded-Annotation-070726_05a5.pdf"
)
PDF_TXT = REPO / "docs/reference/isda/text" / PRIMARY_PDF.replace(".pdf", ".txt")

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
    "General Terms",
    "Business Days",
    "Additional Provisions",
    "Settlement Terms",
    "Early Termination",
    "Party A",
    "Party B",
}

# Curated deep II-B fields (PDF extraction can miss wrapped labels)
IIB_DEEP_FIELDS = [
    ("Transaction Type", "PRODUCT", "PRODUCT", "II-B", "—", "General Terms; new 2026 defined term", "NEW_TRADE;AFFIRM", "Both", "", "trade.product.transactionType", "SmartDX:TransactionType", "DQ-REQ-001", "MAP-ENUM-001"),
    ("Trade Date", "PRODUCT", "PRODUCT", "II-B", "—", "General Terms", "NEW_TRADE;AFFIRM;AMEND;NOVATION", "Both", "", "trade.economics.tradeDate", "SmartDX:TradeDate;SWIFT:32A/Date", "DQ-REQ-002;DQ-CAL-001", "MAP-DATE-001"),
    ("SRO Matrix version", "MATRIX", "PRODUCT", "II-B", "SRO Matrix version pin", "Optional; pin non-latest SRO Matrix", "NEW_TRADE;AMEND;HOT_SWAP", "Both", "", "trade.documentation.contractualMatrix[matrixType=SRO].version", "SmartDX:SROMatrixVersion", "DQ-LEGAL-001", "MAP-MATRIX-001"),
    ("Buyer", "PRODUCT", "PRODUCT", "II-B", "—", "Party A / Party B", "NEW_TRADE;AFFIRM;NOVATION;EXERCISE", "Both", "", "trade.product.buyerPartyReference.href", "SmartDX:Buyer;SWIFT:Party", "DQ-REQ-003", "MAP-PARTY-001"),
    ("Seller", "PRODUCT", "PRODUCT", "II-B", "—", "Party A / Party B", "NEW_TRADE;AFFIRM;NOVATION;EXERCISE", "Both", "", "trade.product.sellerPartyReference.href", "SmartDX:Seller;SWIFT:Party", "DQ-REQ-003", "MAP-PARTY-001"),
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
    ("Premium", "PRODUCT", "PRODUCT", "II-B", "—", "Premium amount; Price-% removed as separate field (2026 tidy)", "NEW_TRADE;AFFIRM;AMEND", "Both", "", "trade.economics.premiumAmount", "SmartDX:Premium;SWIFT:33B", "DQ-REQ-007", "MAP-AMT-002"),
    ("Premium Currency", "PRODUCT", "PRODUCT", "II-B", "—", "Currency of the Premium", "NEW_TRADE;AFFIRM;AMEND", "Both", "", "trade.economics.premiumCurrency", "SmartDX:PremiumCurrency;SWIFT:33B", "DQ-REQ-007", "MAP-CCY-001"),
    ("Premium Payment Date", "PRODUCT", "PRODUCT", "II-B", "—", "Premium settlement date", "NEW_TRADE;AFFIRM", "Both", "", "trade.economics.premiumPaymentDate", "SmartDX:PremiumPaymentDate", "DQ-CAL-006", "MAP-DATE-001"),
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
    ("FX Definitions Version Election", "COMMON", "MASTER", "I", "Main Book version", "Incorporate 2026 FX Definitions; optional version pin", "NEW_TRADE;HOT_SWAP", "Both", "", "trade.documentation.contractualDefinitions[0].version", "SmartDX:DefsVersion", "DQ-LEGAL-002", "MAP-LEGAL-001"),
    ("ISDA Master Agreement Date", "COMMON", "MASTER", "I", "", "Subject to Agreement dated as of…", "NEW_TRADE;AFFIRM", "With_MCA", "mca.isdaMasterDate (Assumed)", "trade.documentation.masterAgreement.masterAgreementDate", "SmartDX:MasterDate", "DQ-LEGAL-003", "MAP-LEGAL-002"),
    ("Party A Name", "COMMON", "MASTER", "I", "", "Party A", "NEW_TRADE;NOVATION;AFFIRM", "Both", "", "trade.parties[id=partyA].partyName", "SmartDX:PartyA;SWIFT:Party", "DQ-REQ-012", "MAP-PARTY-001"),
    ("Party B Name", "COMMON", "MASTER", "I", "", "Party B", "NEW_TRADE;NOVATION;AFFIRM", "Both", "", "trade.parties[id=partyB].partyName", "SmartDX:PartyB;SWIFT:Party", "DQ-REQ-012", "MAP-PARTY-001"),
    ("Long-form Master Agreement Fallback", "COMMON", "MASTER", "I", "", "Footnote 2 long-form if no executed Master", "NEW_TRADE", "Without_MCA", "", "trade.documentation.masterAgreement.longFormFallback", "SmartDX:LongForm", "DQ-LEGAL-004", "MAP-LEGAL-003"),
    ("Governing Law (long-form)", "COMMON", "MASTER", "I", "", "English law / NY law election in long-form", "NEW_TRADE", "Without_MCA", "", "trade.documentation.masterAgreement.governingLaw", "SmartDX:GoverningLaw", "DQ-LEGAL-005", "MAP-ENUM-006"),
    ("Termination Currency (long-form)", "COMMON", "MASTER", "I", "", "Long-form Schedule election", "NEW_TRADE", "Without_MCA", "", "trade.documentation.masterAgreement.terminationCurrency", "SmartDX:TermCcy", "DQ-LEGAL-005", "MAP-CCY-001"),
    ("Party A LEI", "COMMON", "MASTER", "I", "", "Optional LEI", "NEW_TRADE;AFFIRM;NOVATION", "Both", "masterConfirmation partyA.lei (Assumed default)", "trade.parties[id=partyA].lei", "SmartDX:LEI_A;SWIFT:LEI", "DQ-FORMAT-003", "MAP-LEI-001"),
    ("Party B LEI", "COMMON", "MASTER", "I", "", "Optional LEI", "NEW_TRADE;AFFIRM;NOVATION", "Both", "mca.partyB.lei (Assumed default)", "trade.parties[id=partyB].lei", "SmartDX:LEI_B;SWIFT:LEI", "DQ-FORMAT-003", "MAP-LEI-001"),
    ("Fallback Benchmark", "COMMON", "MASTER", "I", "", "Administrator/Benchmark Event fallback", "NEW_TRADE;AMEND", "Both", "", "trade.economics.fallbackBenchmark", "SmartDX:FallbackBenchmark", "DQ-LEGAL-006", "MAP-TEXT-001"),
    ("Acknowledgments and Representations", "COMMON", "MASTER", "I", "", "Disapplied election vs §20 presumption", "NEW_TRADE", "Both", "mca.acksRepresentations (Assumed)", "trade.documentation.acknowledgmentsAndRepresentations", "SmartDX:AcksReps", "DQ-ENUM-006", "MAP-ENUM-007"),
    ("Calculation Agent", "COMMON", "MASTER", "I", "", "Party A/B/other/Joint/As per Agreement", "NEW_TRADE;AFFIRM;AMEND", "Both", "mca.calculationAgent (Assumed default)", "trade.calculationAgent.calculationAgentPartyReference.href", "SmartDX:CalcAgent", "DQ-REQ-013", "MAP-PARTY-003"),
    ("Joint Calculation Agent Dispute Resolution", "COMMON", "MASTER", "I", "", "When Joint CA elected", "NEW_TRADE", "Both", "mca.jointCaDisputeResolution (Assumed)", "trade.calculationAgent.jointDisputeResolution", "SmartDX:JointCADispute", "DQ-CROSS-008", "MAP-BOOL-001"),
    ("Account for payments to Party A", "COMMON", "MASTER", "I", "", "Account Details", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.accounts.partyA (Assumed SSI)", "trade.parties[id=partyA].settlementAccount", "SmartDX:AccountA;SWIFT:57a", "DQ-FORMAT-004", "MAP-SSI-001"),
    ("Account for payments to Party B", "COMMON", "MASTER", "I", "", "Account Details", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.accounts.partyB (Assumed SSI)", "trade.parties[id=partyB].settlementAccount", "SmartDX:AccountB;SWIFT:57a", "DQ-FORMAT-004", "MAP-SSI-001"),
    ("Office of Party A", "COMMON", "MASTER", "I", "", "Offices", "NEW_TRADE;NOVATION", "Both", "mca.offices.partyA (Assumed)", "trade.parties[id=partyA].office", "SmartDX:OfficeA", "DQ-FORMAT-005", "MAP-LOC-001"),
    ("Office of Party B", "COMMON", "MASTER", "I", "", "Offices", "NEW_TRADE;NOVATION", "Both", "mca.offices.partyB (Assumed)", "trade.parties[id=partyB].office", "SmartDX:OfficeB", "DQ-FORMAT-005", "MAP-LOC-001"),
    ("Broker/Arranger", "COMMON", "MASTER", "I", "", "Optional", "NEW_TRADE", "Both", "", "trade.brokerPartyReference.href", "SmartDX:Broker", "DQ-LINEAGE-001", "MAP-PARTY-004"),
    ("Governing law", "COMMON", "MASTER", "I", "", "Delete if under executed Master", "NEW_TRADE", "Without_MCA", "", "trade.documentation.governingLaw", "SmartDX:GoverningLaw", "DQ-LEGAL-005", "MAP-ENUM-006"),
    ("Contact details for notice Party A", "COMMON", "MASTER", "I", "", "New optional 2026 field", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.notices.partyA (Assumed)", "trade.parties[id=partyA].noticeContact", "SmartDX:NoticeA", "DQ-FORMAT-006", "MAP-TEXT-001"),
    ("Contact details for notice Party B", "COMMON", "MASTER", "I", "", "New optional 2026 field", "NEW_TRADE;AMEND;NOVATION", "Both", "mca.notices.partyB (Assumed)", "trade.parties[id=partyB].noticeContact", "SmartDX:NoticeB", "DQ-FORMAT-006", "MAP-TEXT-001"),
    ("Closing supersession clause", "COMMON", "MASTER", "I", "", "Closing", "NEW_TRADE;AMEND;RESEND", "Both", "", "confirmation.closing.supersession", "SmartDX:Closing", "DQ-LINEAGE-001", "MAP-TEXT-001"),
    ("Party A signature block", "COMMON", "MASTER", "I", "", "Closing", "NEW_TRADE;AFFIRM", "Both", "", "confirmation.signatures.partyA", "SmartDX:SigA", "DQ-LINEAGE-001", "MAP-TEXT-001"),
    ("Party B confirmation signature block", "COMMON", "MASTER", "I", "", "Closing", "NEW_TRADE;AFFIRM", "Both", "", "confirmation.signatures.partyB", "SmartDX:SigB", "DQ-LINEAGE-001", "MAP-TEXT-001"),
]

# Assumed MCA-only inventory
MCA_ASSUMED = [
    ("MCA Profile ID", "MCA", "", "", "", "Assumed bilateral MCA identifier", "NEW_TRADE;HOT_SWAP", "With_MCA", "Assumed: MCA-SCB-ACME-2026-001", "trade.documentation.masterConfirmation.masterConfirmationId", "—", "DQ-MCA-001", "MAP-MCA-001"),
    ("MCA Effective Date", "MCA", "", "", "", "Assumed", "NEW_TRADE", "With_MCA", "Assumed: 2026-01-15", "trade.documentation.masterConfirmation.masterConfirmationDate", "—", "DQ-MCA-002", "MAP-DATE-001"),
    ("MCA FX Definitions Year Election", "MCA", "", "", "Main Book", "Assumed: elect 2026 vs 1998 until cutover", "NEW_TRADE;HOT_SWAP", "With_MCA", "Assumed: 2026 FX Definitions Version 1.0", "trade.documentation.masterConfirmation.elections.definitionsYear", "—", "DQ-MCA-003", "MAP-LEGAL-001"),
    ("MCA Default Product Set", "MCA", "", "", "", "Assumed eligible products under MCA", "NEW_TRADE", "With_MCA", "Assumed: Deliverable FX; Deliverable FX Option; NDF; NDO", "trade.documentation.masterConfirmation.elections.productSet", "—", "DQ-MCA-004", "MAP-ENUM-008"),
    ("MCA Default Calculation Agent", "MCA", "", "", "", "Assumed CA default absorbed into Exhibit I when With_MCA", "NEW_TRADE", "With_MCA", "Assumed: Party A", "trade.documentation.masterConfirmation.elections.defaultCalculationAgent", "SmartDX:CalcAgent", "DQ-MCA-005", "MAP-PARTY-003"),
    ("MCA Default Notice Channel", "MCA", "", "", "", "Assumed email + MarkitWire", "NEW_TRADE;AFFIRM", "With_MCA", "Assumed: ops-fx@party.example; electronic conf via SmartDX", "trade.documentation.masterConfirmation.elections.noticeChannel", "—", "DQ-MCA-006", "MAP-TEXT-001"),
    ("MCA Multilateral Settlement Election", "MCA", "", "", "", "Assumed CLS eligibility default", "NEW_TRADE", "With_MCA", "Assumed: CLS where eligible else bilateral", "trade.documentation.masterConfirmation.elections.settlementElection", "SWIFT:SettlementMethod", "DQ-MCA-007", "MAP-ENUM-009"),
    ("MCA Automatic Exercise Default", "MCA", "", "", "", "Assumed FXO default", "NEW_TRADE;EXERCISE", "With_MCA", "Assumed: Automatic Exercise applicable", "trade.documentation.masterConfirmation.elections.automaticExerciseDefault", "SmartDX:AutomaticExercise", "DQ-MCA-008", "MAP-BOOL-001"),
    ("MCA Dispute Resolution Venue", "MCA", "", "", "", "Assumed", "NEW_TRADE", "With_MCA", "Assumed: Arbitration LCIA / English law", "trade.documentation.masterConfirmation.elections.disputeVenue", "—", "DQ-MCA-009", "MAP-TEXT-001"),
    ("MCA Confirmation Method", "MCA", "", "", "", "Assumed electronic vs paper", "NEW_TRADE;AFFIRM;RESEND", "With_MCA", "Assumed: Electronic confirmation via SmartDX preferred", "trade.documentation.masterConfirmation.elections.confirmationMethod", "SmartDX:Channel", "DQ-MCA-010", "MAP-ENUM-010"),
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
    ("Assembly Requested Mode", "PLATFORM", "", "", "", "Optional TPs hint AUTOMATED|MANUAL_DRAFTING|MANUAL_ENTRY", "NEW_TRADE;AMEND", "Both", "", "assembly.requestedMode", "—", "", "MAP-ENUM-012"),
    ("Assembly Mode Reason", "PLATFORM", "", "", "", "Free-text reason when requestedMode is manual", "NEW_TRADE;AMEND", "Both", "", "assembly.reason", "—", "", "MAP-TEXT-001"),
    ("Prior Document ID", "LIFECYCLE", "", "", "", "Superseded confirmation", "AMEND;HOT_SWAP;RESEND;NOVATION", "Both", "", "lifecycle.priorDocumentId", "SmartDX:PriorDoc", "DQ-CROSS-009", "MAP-ID-004"),
]

HEADERS = [
    "Attribute / field name",
    "Attribute group",
    "Attribute type",
    "Domain",
    "LDM entity",
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


DOMAIN_BY_GROUP = {
    "COMMON": "ConfirmationLetter",
    "PRODUCT": "ProductEconomics",
    "SUPPLEMENT": "SupplementTerms",
    "MATRIX": "Matrix",
    "MCA": "MCA",
    "PLATFORM": "Platform",
    "LIFECYCLE": "Lifecycle",
}

ENTITY_BY_PREFIX = [
    ("trade.parties[", "Party"),
    ("trade.brokerPartyReference", "Party"),
    ("trade.documentation.masterConfirmation", "MasterConfirmation"),
    ("trade.documentation.contractualDefinitions", "LegalFramework"),
    ("trade.documentation.contractualMatrix", "MatrixBinding"),
    ("trade.documentation", "Documentation"),
    ("trade.product", "TradeProduct"),
    ("trade.calculationAgent", "Trade"),
    ("confirmation.", "ExhibitILetter"),
    ("platform.template", "TemplateVersion"),
    ("platform.", "PlatformContext"),
    ("assembly.", "AssemblyRun"),
    ("lifecycle.novation", "NovationTransfer"),
    ("lifecycle.", "LifecycleEvent"),
    ("template.supplementExhibitIds", "SupplementElection"),
    ("template.", "DynamicTemplate"),
    ("tradeId", "Trade"),
]


def ldm_entity_for_path(path: str, exhibit: str, layer: str = "") -> str:
    """Logical_Data_Model entity owning a TPs JSON path (shared with the mocks Sample_Trade_Card)."""
    for prefix, entity in ENTITY_BY_PREFIX:
        if path.startswith(prefix):
            return entity
    if path.startswith(("trade.economics", "trade.calendars")):
        return "FxOptionEconomics" if exhibit == "II-B" else "ProductEconomics"
    if path.startswith("trade.exhibits["):
        return "SupplementElection" if layer == "SUPPLEMENT" else "ProductEconomics"
    return "Trade"


def attribute_type(name: str) -> str:
    n = name.lower()
    if "lei" in n.split():
        return "lei"
    if "date" in n or "fixing day" in n:
        return "date"
    if any(w in n for w in ("location", "business day", "matrix", "rate option", "benchmark")):
        return "string"
    if "currency" in n and "amount" not in n:
        return "string"
    if "time" in n:
        return "time"
    if any(w in n for w in ("amount", "price", "premium", "rate", "strike", "notional")):
        return "decimal"
    if any(w in n for w in ("exercise", "fallback", "applicable", "disruption")) and "period" not in n:
        return "boolean_or_enum"
    if any(w in n for w in ("type", "style", "governing law", "status", "mode")):
        return "enum"
    return "string"


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
    values = [
        attr,
        group,
        attribute_type(attr),
        DOMAIN_BY_GROUP.get(group, group),
        ldm_entity_for_path(tps, exhibit, layer),
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
        notes,
    ]
    return dict(zip(HEADERS, values))


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
                f"trade.documentation.contractualMatrix[matrixType={mid.removeprefix('MATRIX-')}].version",
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
        ["DQ-REQ-003", "REQUIRED", "ERROR", "PRODUCT", "FX_Option_*", "NEW_TRADE", "buyerPartyReference and sellerPartyReference resolve to trade.parties[] and differ", "ISDA-derived"],
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
        ["DQ-MCA-001", "REQUIRED", "ERROR", "MCA", "ALL", "NEW_TRADE", "documentation.masterConfirmation.masterConfirmationId when path=With_MCA", "Assumed"],
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
        ["MAP-PARTY-001", "TRANSFORM", "INFO", "COMMON", "ALL", "ALL_EVENTS", "Resolve party references (href) to trade.parties[]; Party A/B labels from id", "Assumed"],
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
        ["MAP-MCA-001", "TRANSFORM", "INFO", "MCA", "ALL", "NEW_TRADE", "Resolve Assumed masterConfirmation elections onto COMMON fields", "Assumed"],
    ]
    return rules, mapping


def template_admin_rows() -> list[list]:
    header = ["Admin Field", "Description", "Applies to layer", "Example / Allowed values", "Required", "Notes"]
    return [
        header,
        ["templateBundleId", "Composite binding id", "MASTER+PRODUCT+SUPPLEMENT", "TB-FXO-DEL-2026-001", "Y", None],
        ["packageName", "Display name of the TemplatePackage", "ALL", "2026 FXO Deliverable (II-B)", "Y", None],
        ["masterTemplateId", "Exhibit I template id", "MASTER", "EXH-I-2026-v1", "Y", None],
        ["productExhibitId", "Exhibit II-* id spliced at Exhibit I productInsert", "PRODUCT", "II-B", "Y", "Routing key"],
        ["productType", "Canonical product enum", "PRODUCT", "Deliverable_FX_Option", "Y", None],
        ["supplementExhibitIds", "JSON array of III-* (Additional Provisions)", "SUPPLEMENT", '["III-A","III-H"]', "N", "Elected overlays"],
        ["matrixBindings", "JSON matrix pins applied when the trade has no documentation.contractualMatrix entry", "MATRIX", '{"SRO":"2026-03-03","EM":null}', "N", None],
        ["mcaRequired", "Whether a master confirmation (MCA) is required", "MCA", "true|false", "Y", "false = MCA optional; Legal Resolver branches per trade on documentation.masterConfirmation"],
        ["masterConfirmationId", "Assumed MCA bound to the package (only if mcaRequired)", "MCA", "MCA-SCB-ACME-2026-001", "If mcaRequired", "Assumed"],
        ["version", "Template version (semver)", "ALL", "1.2.0", "Y", None],
        ["status", "Lifecycle of template version", "ALL", "DRAFT|LIVE|RETIRED", "Y", None],
        ["activatedAt", "When version went LIVE", "ALL", "ISO-8601", "If LIVE", None],
        ["retiredAt", "When RETIRED", "ALL", "ISO-8601", "If RETIRED", None],
        ["activationPolicy", "Four-eyes activation policy", "ALL", '{"fourEyes":true,"approverMustDifferFromActivator":true,"effectiveFrom":"2027-11-28T00:00:00Z","approvalWorkflow":"COMING_SOON"}', "Y", "Versions activated before effectiveFrom carry approval null"],
        ["approval.status", "Four-eyes approval of a DRAFT version", "ALL", "PENDING|APPROVED|REJECTED", "Before activate", "Activate requires APPROVED; approver must differ from the activating admin"],
        ["approval.approvedBy", "Approver (second pair of eyes)", "ALL", "u.ctrl.ng", "If APPROVED", "Prototype: mocked as already approved; approval workflow is coming soon"],
        ["approval.approvedAt", "Approval timestamp", "ALL", "ISO-8601", "If APPROVED", None],
        ["hotReloadEnabled", "Allow HOT_SWAP without redeploy", "ALL", "true|false", "Y", "Prototype default true"],
        ["rollbackTargetVersion", "Prior LIVE version", "ALL", "1.1.0", "N", None],
        ["routingRules", "Product/event → bundle", "PRODUCT", "JSON", "Y", None],
        ["audit.lastChangedBy", "Admin user", "ALL", "uid", "Y", None],
        ["audit.lastChangedAt", "Timestamp", "ALL", "ISO-8601", "Y", None],
        ["resendPolicy", "On HOT_SWAP auto-resend?", "PLATFORM", "AUTO|MANUAL", "Y", None],
        ["reason", "Activation / hot-swap reason code", "ALL", "PLANNED_RELEASE|WRONG_PRODUCT_BINDING_FIXED", "N", None],
        ["legalDefsYear", "1998|2026", "MASTER", "2026", "Y", None],
        ["notes", "Free text", "ALL", "—", "N", None],
    ]


def ldm_rows() -> list[list]:
    header = ["Entity", "Attribute", "PK/FK", "Type", "Related entity", "Cardinality", "Notes"]
    E = None
    return [
        header,
        ["Trade", "tradeId", "PK", "string", E, "1", None],
        ["Trade", "status", E, "enum", E, "1", "See state diagrams"],
        ["Trade", "mcaPath", E, "enum", E, "1", "Derived: With_MCA when documentation.masterConfirmation is set"],
        ["Trade", "affirmationStatus", E, "enum", E, "0..1", "Matched|Unmatched|Affirmed|Disputed"],
        ["Trade", "receivedAt", E, "datetime", E, "1", "First NEW_TRADE accepted"],
        ["Trade", "calculationAgentPartyReference", "FK", "string", "Party", "0..1", "FpML trade.calculationAgent; href to Party.id"],
        ["Trade", "brokerPartyReference", "FK", "string?", "Party", "0..1", "FpML brokerPartyReference"],
        ["Trade", "tpsPayload", E, "json", E, "1", "TPS JSON"],
        ["Party", "id", "PK-part", "string", "Trade", "N:2..*", "partyA|partyB|partyC…; target of every *PartyReference.href"],
        ["Party", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["Party", "partyName", E, "string", E, "1", "FpML partyName"],
        ["Party", "lei", E, "lei", E, "0..1", "ISO 17442"],
        ["Party", "address", E, "string", E, "0..1", None],
        ["Party", "office", E, "string", E, "0..1", None],
        ["Party", "noticeContact", E, "string", E, "0..1", "Exhibit I notice details"],
        ["Party", "settlementAccount", E, "string", E, "0..1", "SSI; Exhibit I account details"],
        ["TradeProduct", "tradeId", "FK/PK", "string", "Trade", "1:1", "Product identity and party roles (product-agnostic)"],
        ["TradeProduct", "productType", "FK", "enum", "FinancialProduct", "N:1", None],
        ["TradeProduct", "transactionType", E, "enum", E, "1", "ISDA defined term, e.g. Deliverable FX Option Transaction"],
        ["TradeProduct", "buyerPartyReference", "FK", "string", "Party", "1", "FpML buyerPartyReference href"],
        ["TradeProduct", "sellerPartyReference", "FK", "string", "Party", "1", "FpML sellerPartyReference href"],
        ["Documentation", "tradeId", "FK/PK", "string", "Trade", "1:1", "FpML-style trade documentation block"],
        ["Documentation", "masterAgreementType", E, "enum", E, "1", "ISDA2002 (executed or deemed long-form)"],
        ["Documentation", "masterAgreementDate", E, "date", E, "0..1", "Null when deemed long-form"],
        ["Documentation", "longFormFallback", E, "boolean", E, "1", "Exhibit I footnote 2 long-form agreement"],
        ["Documentation", "governingLaw (masterAgreement)", E, "enum", E, "0..1", "Deemed agreement election"],
        ["Documentation", "terminationCurrency", E, "string", E, "0..1", "Deemed agreement election"],
        ["Documentation", "masterConfirmationId", "FK", "string?", "MasterConfirmation", "0..1", "With_MCA only"],
        ["Documentation", "contractualDefinitions", "FK[]", "json", "LegalFramework", "1..N", "e.g. 2026 FX Definitions Main Book 1.0"],
        ["Documentation", "contractualMatrix", "FK[]", "json", "MatrixBinding", "0..N", "Empty = each matrix as of Trade Date"],
        ["Documentation", "governingLaw", E, "enum", E, "0..1", "Confirmation governing law field (Without_MCA)"],
        ["Documentation", "acknowledgmentsAndRepresentations", E, "enum", E, "0..1", "Disapplied or omitted"],
        ["FinancialProduct", "productType", "PK", "enum", E, "1", "Ontology"],
        ["FinancialProduct", "exhibitId", E, "string", E, "1", "II-*"],
        ["FxOptionEconomics", "tradeId", "FK/PK", "string", "Trade", "1:1", "Deliverable FX Option economics (no party data)"],
        ["FxOptionEconomics", "tradeDate", E, "date", E, "1", None],
        ["FxOptionEconomics", "optionStyle", E, "enum", E, "0..1", "American|Bermuda|European"],
        ["FxOptionEconomics", "optionType", E, "string", E, "1", "Put/Call or Binary"],
        ["FxOptionEconomics", "callCurrency", E, "string", E, "0..1", "ISO 4217"],
        ["FxOptionEconomics", "callCurrencyAmount", E, "decimal", E, "0..1", None],
        ["FxOptionEconomics", "putCurrency", E, "string", E, "0..1", None],
        ["FxOptionEconomics", "putCurrencyAmount", E, "decimal", E, "0..1", None],
        ["FxOptionEconomics", "strikePrice", E, "decimal", E, "0..1", None],
        ["FxOptionEconomics", "settlementMethod", E, "enum", E, "1", "Deliverable"],
        ["FxOptionEconomics", "commencementDate", E, "date", E, "0..1", None],
        ["FxOptionEconomics", "expirationDate", E, "date", E, "1", None],
        ["FxOptionEconomics", "expirationTime", E, "time", E, "1", None],
        ["FxOptionEconomics", "expirationTimeLocation", E, "string", E, "1", None],
        ["FxOptionEconomics", "automaticExercise", E, "enum", E, "0..1", None],
        ["FxOptionEconomics", "premiumAmount", E, "decimal", E, "0..1", None],
        ["FxOptionEconomics", "premiumCurrency", E, "string", E, "0..1", None],
        ["FxOptionEconomics", "premiumPaymentDate", E, "date", E, "0..1", "Deferred premium edge"],
        ["FxOptionEconomics", "settlementDate", E, "date", E, "0..1", None],
        ["FxOptionEconomics", "fullAutomatedExercise", E, "boolean", E, "0..1", None],
        ["FxOptionEconomics", "settlementRateOption", E, "string", E, "0..1", "SRO code"],
        ["FxOptionEconomics", "businessDayPayment", E, "string", E, "0..1", None],
        ["FxOptionEconomics", "businessDayExercise", E, "string", E, "0..1", None],
        ["FxOptionEconomics", "businessDayValuation", E, "string", E, "0..1", None],
        ["ProductEconomics", "tradeId", "FK/PK", "string", "Trade", "1:1", "Non-II-B products"],
        ["ProductEconomics", "exhibitId", E, "string", "FinancialProduct", "1", "II-A..II-K"],
        ["ProductEconomics", "fields", E, "json", E, "1", "Exhibit-specific bag aligned to Attribute_Product_Map"],
        ["LegalFramework", "frameworkId", "PK", "string", E, "1", None],
        ["LegalFramework", "defsYear", E, "enum", E, "1", "1998|2026"],
        ["LegalFramework", "mainBookVersion", E, "string", E, "1", None],
        ["MasterConfirmation", "masterConfirmationId", "PK", "string", E, "1", "Assumed MCA sample (FpML masterConfirmation)"],
        ["MasterConfirmation", "masterConfirmationType", E, "string", E, "1", None],
        ["MasterConfirmation", "masterConfirmationDate", E, "date", E, "1", None],
        ["MasterConfirmation", "elections", E, "json", E, "1", "Assumed default elections"],
        ["MatrixBinding", "matrixBindingId", "PK", "string", E, "1", None],
        ["MatrixBinding", "matrixType", E, "enum", E, "1", "SRO|EM|CFC|DM|CNY"],
        ["MatrixBinding", "version", E, "string", E, "1", "Matrix version pinned (ISDA versions each matrix separately)"],
        ["ConfirmationInstance", "confirmationId", "PK", "string", E, "1", "Runtime confirmation"],
        ["ConfirmationInstance", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["ConfirmationInstance", "masterTemplateVersionId", "FK", "string", "TemplateVersion", "N:1", "Exhibit I"],
        ["ConfirmationInstance", "productTemplateVersionId", "FK", "string", "TemplateVersion", "N:1", "Exhibit II-*"],
        ["ConfirmationInstance", "supplementTemplateVersionIds", "FK[]", "string[]", "TemplateVersion", "N:M", "Exhibit III-*"],
        ["ConfirmationInstance", "documentArtifactId", "FK", "string", "DocumentArtifact", "1:1", None],
        ["ExhibitILetter", "letterId", "PK", "string", E, "1", None],
        ["ExhibitILetter", "confirmationId", "FK", "string", "ConfirmationInstance", "1:1", None],
        ["ExhibitILetter", "heading", E, "json", E, "1", "letterhead, date, partyB address"],
        ["ExhibitILetter", "definitionsVersion", E, "string", "LegalFramework", "1", None],
        ["ExhibitILetter", "agreementClause", E, "string", E, "1", "Master vs long-form"],
        ["ExhibitILetter", "productInsert", E, "json", "FinancialProduct", "1", "ISDA: insert the relevant form of Confirmation (Exhibit II) + Additional Provisions (Exhibit III)"],
        ["ExhibitILetter", "elections", E, "json", E, "1", "Rendered LEI, CA, notices, accounts"],
        ["ExhibitILetter", "closing", E, "string", E, "1", "Supersession"],
        ["ExhibitILetter", "proseLetter", E, "text", E, "1", "Rendered letter mock"],
        ["SupplementElection", "electionId", "PK", "string", E, "1", None],
        ["SupplementElection", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["SupplementElection", "exhibitId", E, "string", E, "1", "III-A..III-H"],
        ["SupplementElection", "fields", E, "json", E, "1", None],
        ["DynamicTemplate", "templateId", "PK", "string", E, "1", None],
        ["DynamicTemplate", "layer", E, "enum", E, "1", "MASTER|PRODUCT|SUPPLEMENT"],
        ["DynamicTemplate", "exhibitId", E, "string", E, "1", None],
        ["TemplateVersion", "templateVersionId", "PK", "string", E, "1", None],
        ["TemplateVersion", "templateId", "FK", "string", "DynamicTemplate", "N:1", None],
        ["TemplateVersion", "version", E, "string", E, "1", None],
        ["TemplateVersion", "status", E, "enum", E, "1", "DRAFT|LIVE|RETIRED"],
        ["TemplateVersion", "assemblyMode", E, "enum", E, "0..1", "AUTOMATED|MANUAL_DRAFTING"],
        ["TemplatePackage", "packageId", "PK", "string", E, "1", "Binds tops-and-tails + product (+ optional supplement)"],
        ["TemplatePackage", "packageName", E, "string", E, "1", None],
        ["TemplatePackage", "masterTemplateVersionId", "FK", "string", "TemplateVersion", "1", "Tops and tails / Exhibit I"],
        ["TemplatePackage", "productTemplateVersionId", "FK", "string", "TemplateVersion", "1", "Exhibit II-*"],
        ["TemplatePackage", "supplementTemplateVersionId", "FK", "string?", "TemplateVersion", "0..1", "Exhibit III-*"],
        ["TemplatePackage", "version", E, "string", E, "1", "Semver e.g. 1.1.0 (same as Template_Admin_Utility.version)"],
        ["TemplatePackage", "status", E, "enum", E, "1", "DRAFT|LIVE|RETIRED"],
        ["TemplateApproval", "templateBundleId", "FK", "string", "TemplatePackage", "N:1", "Four-eyes approval of one package version"],
        ["TemplateApproval", "version", E, "string", E, "1", None],
        ["TemplateApproval", "status", E, "enum", E, "1", "PENDING|APPROVED|REJECTED"],
        ["TemplateApproval", "requestedBy", E, "string", E, "1", None],
        ["TemplateApproval", "requestedAt", E, "datetime", E, "1", None],
        ["TemplateApproval", "approvedBy", E, "string?", E, "0..1", "Must differ from requestedBy and from the activating admin"],
        ["TemplateApproval", "approvedAt", E, "datetime?", E, "0..1", None],
        ["TemplateApproval", "comment", E, "string?", E, "0..1", None],
        ["TemplateApproval", "auditId", "FK", "string?", "AuditEvent", "0..1", "template.approved"],
        ["PackageSelectionRule", "ruleId", "PK", "string", E, "1", None],
        ["PackageSelectionRule", "packageId", "FK", "string", "TemplatePackage", "N:1", None],
        ["PackageSelectionRule", "product", E, "string", E, "0..1", None],
        ["PackageSelectionRule", "subProduct", E, "string", E, "0..1", None],
        ["PackageSelectionRule", "businessEvent", E, "string", E, "0..1", "NEW_TRADE|AMEND|…"],
        ["PackageSelectionRule", "entity", E, "string", E, "0..1", None],
        ["PackageSelectionRule", "confirmationMethod", E, "string", E, "0..1", None],
        ["PackageSelectionRule", "priority", E, "int", E, "1", None],
        ["AssemblyRun", "assemblyRunId", "PK", "string", E, "1", None],
        ["AssemblyRun", "tradeEventId", E, "string", "LifecycleEvent", "N:1", None],
        ["AssemblyRun", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["AssemblyRun", "templatePackageId", "FK", "string", "TemplatePackage", "N:1", None],
        ["AssemblyRun", "templateVersion", E, "string", "TemplatePackage", "1", "Package version pinned at run start"],
        ["AssemblyRun", "assemblyMode", E, "enum", E, "1", "AUTOMATED|MANUAL_DRAFTING|MANUAL_ENTRY"],
        ["AssemblyRun", "status", E, "enum", E, "1", "SUPPRESSED|PENDING_MANUAL_DRAFT|PENDING_DATA_ENTRY|ASSEMBLING|COMPLETED|FAILED"],
        ["AssemblyRun", "createdAt", E, "datetime", E, "1", None],
        ["AssemblyRun", "completedAt", E, "datetime", E, "0..1", None],
        ["AssemblyRun", "confirmationId", "FK", "string?", "ConfirmationInstance", "0..1", None],
        ["ManualEntryValue", "id", "PK", "string", E, "1", None],
        ["ManualEntryValue", "assemblyRunId", "FK", "string", "AssemblyRun", "N:1", None],
        ["ManualEntryValue", "attributeName", E, "string", E, "1", None],
        ["ManualEntryValue", "value", E, "string", E, "1", None],
        ["ManualEntryValue", "enteredBy", E, "string", E, "1", None],
        ["ManualDraftContent", "id", "PK", "string", E, "1", None],
        ["ManualDraftContent", "assemblyRunId", "FK", "string", "AssemblyRun", "N:1", None],
        ["ManualDraftContent", "templateVersionId", "FK", "string", "TemplateVersion", "N:1", None],
        ["ManualDraftContent", "content", E, "text", E, "1", None],
        ["ManualDraftContent", "contentHash", E, "string", E, "0..1", "Audit integrity"],
        ["ManualDraftContent", "draftedBy", E, "string", E, "1", None],
        ["ManualDraftContent", "savedAt", E, "datetime", E, "1", None],
        ["DocumentArtifact", "documentId", "PK", "string", E, "1", "SmartDX doc"],
        ["DocumentArtifact", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["DocumentArtifact", "templateVersionId", "FK", "string", "TemplateVersion", "N:1", "Frozen at gen"],
        ["DocumentArtifact", "channel", E, "enum", E, "1", "SmartDX|SWIFT|BOTH"],
        ["DocumentArtifact", "smartdxDocumentId", E, "string", E, "0..1", "SDX-<documentId>"],
        ["DocumentArtifact", "status", E, "enum", E, "1", "GENERATED|RESENT|SUPERSEDED"],
        ["DocumentArtifact", "priorDocumentId", "FK", "string?", "DocumentArtifact", "0..1", "Supersession link"],
        ["DocumentArtifact", "createdAt", E, "datetime", E, "1", None],
        ["LifecycleEvent", "eventId", "PK", "string", E, "1", None],
        ["LifecycleEvent", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["LifecycleEvent", "eventType", E, "enum", E, "1", "NEW_TRADE|…"],
        ["LifecycleEvent", "payload", E, "json", E, "1", None],
        ["NovationTransfer", "novationId", "PK", "string", E, "1", None],
        ["NovationTransfer", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["NovationTransfer", "transferorPartyReference", "FK", "string", "Party", "1", None],
        ["NovationTransfer", "transfereePartyReference", "FK", "string", "Party", "1", None],
        ["NovationTransfer", "remainingPartyReference", "FK", "string", "Party", "1", None],
        ["NovationTransfer", "effectiveDate", E, "date", E, "1", None],
        ["PlatformContext", "tradeId", "FK", "string", "Trade", "1:1", None],
        ["PlatformContext", "tpsSourceSystem", E, "string", E, "1", None],
        ["PlatformContext", "tpsEventId", E, "string", E, "1", None],
        ["PlatformContext", "idempotencyKey", E, "string", E, "1", None],
        ["PlatformContext", "smartdxDocumentId", E, "string", "DocumentArtifact", "0..1", None],
        ["PlatformContext", "swiftMsgRef", E, "string", E, "0..1", None],
        ["PlatformContext", "templateBundleId", E, "string", "DynamicTemplate", "1", None],
        ["AttributeDefinition", "attributeId", "PK", "string", E, "1", "Excel row"],
        ["AttributeDefinition", "group", E, "enum", E, "1", "COMMON|…"],
        ["AttributeDefinition", "exhibitId", E, "string", E, "1", None],
        ["AttributeDefinition", "tpsJsonPath", E, "string", E, "1", None],
        ["MappingRule", "mappingRuleId", "PK", "string", E, "1", "MAP-*"],
        ["MappingRule", "attributeId", "FK", "string", "AttributeDefinition", "N:1", None],
        ["DQRule", "dqRuleId", "PK", "string", E, "1", "DQ-*"],
        ["DQRule", "attributeId", "FK", "string?", "AttributeDefinition", "N:0..1", None],
        ["InboundDocument", "inboundId", "PK", "string", E, "1", "Swoosh exception path"],
        ["InboundDocument", "tradeId", "FK", "string?", "Trade", "0..1", None],
        ["InboundDocument", "swooshJobId", E, "string", E, "0..1", None],
        ["InboundDocument", "ocrConfidence", E, "decimal", E, "0..1", None],
        ["InboundDocument", "extractedJson", E, "json", E, "0..1", None],
        ["AffirmationCase", "caseId", "PK", "string", E, "1", "Affirmation/Matching context"],
        ["AffirmationCase", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["AffirmationCase", "status", E, "enum", E, "1", "Matched|Unmatched|Affirmed|Disputed"],
        ["AffirmationCase", "compareXCaseId", E, "string?", E, "0..1", "Compare X gate"],
        ["TimelineEvent", "timelineEventId", "PK", "string", E, "1", "Analytics/Timeline"],
        ["TimelineEvent", "tradeId", "FK", "string", "Trade", "N:1", None],
        ["TimelineEvent", "eventId", "FK", "string?", "LifecycleEvent", "0..1", None],
        ["TimelineEvent", "at", E, "datetime", E, "1", None],
        ["TimelineEvent", "actor", E, "string", E, "1", None],
        ["TimelineEvent", "lane", E, "enum", E, "1", "TPs|CDU-PS|SmartDX|Counterparty"],
        ["TimelineEvent", "action", E, "string", E, "1", None],
        ["TimelineEvent", "status", E, "enum", "Trade", "1", "Trade status after event (PRD §13.2)"],
        ["TimelineEvent", "documentId", "FK", "string?", "DocumentArtifact", "0..1", None],
        ["TimelineEvent", "templateVersion", E, "string?", "TemplatePackage", "0..1", None],
        ["TimelineEvent", "auditId", "FK", "string", "AuditEvent", "1", "AuditEvent feeds TimelineEvent"],
        ["TimelineEvent", "detail", E, "string?", E, "0..1", "One-line human summary"],
        ["AuditEvent", "auditId", "PK", "string", E, "1", "Cross-cutting audit"],
        ["AuditEvent", "at", E, "datetime", E, "1", None],
        ["AuditEvent", "actorId", E, "string", E, "1", None],
        ["AuditEvent", "action", E, "string", E, "1", "template.approved|template.activated|assembly.manual_saved|…"],
        ["AuditEvent", "entityType", E, "string", E, "1", "TemplatePackage|AssemblyRun|DocumentArtifact|…"],
        ["AuditEvent", "entityId", E, "string", E, "1", None],
        ["AuditEvent", "beforeVersion", E, "string?", E, "0..1", None],
        ["AuditEvent", "afterVersion", E, "string?", E, "0..1", None],
        ["AuditEvent", "tradeId", "FK", "string?", "Trade", "0..1", None],
        ["AuditEvent", "correlationId", E, "string?", E, "0..1", None],
        ["REL", "Trade", E, "has", "Party", "2..*", "parties[]"],
        ["REL", "TradeProduct", E, "references", "Party", "2", "buyer/seller party references"],
        ["REL", "Trade", E, "documented_by", "Documentation", "1", None],
        ["REL", "Documentation", E, "optionally_uses", "MasterConfirmation", "0..1", "With_MCA"],
        ["REL", "Documentation", E, "binds", "MatrixBinding", "0..N", None],
        ["REL", "ConfirmationInstance", E, "composed_of", "DynamicTemplate layers", "1→1+N", "MASTER+PRODUCT+ΣSUPPLEMENT"],
        ["REL", "LifecycleEvent", E, "triggers", "DocumentArtifact", "0..N", "generate/resend"],
        ["REL", "NovationTransfer", E, "emits", "LifecycleEvent", "1", "NOVATION"],
        ["REL", "TemplateVersion", E, "hot_swapped_by", "TemplateVersion", "0..1", "admin"],
        ["REL", "TemplatePackage", E, "approved_by", "TemplateApproval", "0..N", "One per activated version"],
        ["REL", "AssemblyRun", E, "uses", "TemplatePackage", "N:1", None],
        ["REL", "TemplatePackage", E, "selected_by", "PackageSelectionRule", "1:N", None],
        ["REL", "InboundDocument", E, "feeds", "AffirmationCase", "0..1", "via Compare X"],
        ["REL", "AuditEvent", E, "feeds", "TimelineEvent", "0..N", "When trade-scoped"],
    ]


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
        ["3", "NEW_TRADE", "CDU-PS", "Legal Resolver", "Resolve defs year, MCA path, matrix pins", "LegalFramework+MasterConfirmation", "With_MCA / Without_MCA", "INT", "Dual path branch"],
        ["4", "NEW_TRADE", "CDU-PS", "Template Engine", "Compose MASTER I + PRODUCT II-B + supplements", "LIVE TB-FXO-DEL-2026-001 v1.1.0", "Both", "INT", "Wrong bundle possible → step 8"],
        ["5", "NEW_TRADE", "SmartDX", "Confirmation Gateway", "Render & send electronic confirmation", "v1.1.0", "Both", "OUT", "DocumentArtifact created"],
        ["6", "NEW_TRADE", "SWIFT", "Messaging", "Optional MT/MX economic notify", "v1.1.0", "Both", "OUT", "Parallel channel"],
        ["7", "NEW_TRADE", "CDU-PS", "TPS Callback POST /callbacks/tps", "Ack generation status", "v1.1.0", "Both", "OUT", ""],
        ["8", "HOT_SWAP", "Ops Admin", "Template Admin UI/API", "Detect wrong product template; activate correct (four-eyes approved) version", "v1.1.0 → v1.2.0", "Both", "INT", "Edge E1 (wrong→hot-swap); ideal path skips steps 8–10 and 23"],
        ["9", "RESEND", "CDU-PS", "Document Service POST /documents/{id}/resend", "Regenerate with v1.2.0; supersede prior", "v1.2.0", "Both", "OUT", "Prior Document ID linked"],
        ["10", "RESEND", "SmartDX", "Confirmation Gateway", "Resend superseding confirmation", "v1.2.0", "Both", "OUT", ""],
        ["11", "AFFIRM", "Counterparty / Affirm platform", "Affirm webhook POST /webhooks/affirmation", "Match/affirm callback", "v1.1.0", "Both", "IN", "Ideal path: affirms DOC-001 sent on v1.1.0"],
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
        ["23", "ROLLBACK", "Ops Admin", "Template Admin", "Rollback LIVE to prior version", "v1.2.0 → v1.1.0", "Both", "INT", "Optional admin edge"],
    ]
    return rows


def legend_rows() -> list[list]:
    return [
        ["Key", "Meaning"],
        ["COMMON", "Exhibit I shared wrapper fields"],
        ["PRODUCT", "Exhibit II-* product economics"],
        ["SUPPLEMENT", "Exhibit III-* optional overlays (ISDA: Additional Provisions)"],
        ["MATRIX", "SRO / EM / other matrix bindings"],
        ["MCA", "Assumed Master Confirmation Agreement elections"],
        ["PLATFORM", "CDU-PS / TPS / SmartDX / SWIFT operational fields"],
        ["LIFECYCLE", "Event, novation, affirmation metadata"],
        ["MASTER", "Template layer = Exhibit I"],
        ["PRODUCT (layer)", "Template layer = Exhibit II-*"],
        ["SUPPLEMENT (layer)", "Template layer = Exhibit III-*"],
        ["Deep", "Fully inventoried (II-B Deliverable FX Option)"],
        ["Standard", "Covered; lineage at exhibit level minimum"],
        ["With_MCA", "Path using Assumed MCA (documentation.masterConfirmation set)"],
        ["Without_MCA", "Path using Exhibit I long-form / explicit elections (masterConfirmation null)"],
        ["Both", "Attribute applies on either MCA path"],
        ["Assumed", "Invented sample — not copied from ISDA legal text"],
        ["ISDA-derived", "Taken/inferred from uploaded ISDA/EMTA PDFs"],
        ["Effective date", "2026 FX Definitions take effect 22 Nov 2027 (Intro PDF)"],
        ["Primary PDF", PRIMARY_PDF],
        ["Intro PDF", "Introduction_to_the_2026_FX_Definitions_ab61.pdf"],
        ["1998 PDF", "1998-FX-and-Currency-Option-Definitions_0d3f.pdf"],
        ["Annex A PDF", "annex-a-to-the-1998-fx-and-currency-option-definitions-june-30-2023_0919.pdf"],
        ["Text extract", "docs/reference/isda/text/*.txt (pdftotext); the build reads these, never the PDFs"],
        ["License", "ISDA/EMTA licensed materials — internal use only; do not redistribute outside license"],
        ["Assumed MCA ID", "MCA-SCB-ACME-2026-001"],
        ["Assumed MCA parties", "Party A = SCB sample desk; Party B = ACME Corp Treasury (invented)"],
        ["Assumed MCA defs", "2026 FX Definitions Version 1.0 Main Book; matrices as-of Trade Date"],
        ["Assumed MCA defaults", "CA=Party A; AutoExercise=Applicable; Notices=email+SmartDX; CLS if eligible"],
        ["Colour (PDF)", "BLUE=new 2026; RED=changed/removed from 1998; ORANGE=streamline; GREEN=EMTA consol; PURPLE=Supplement consol"],
        ["PDF extraction gaps", "Footnotes/comments sometimes split labels; Standard exhibits use heuristic extraction + exhibit-level lineage; colour coding not machine-captured"],
        ["Attribute type", "Datatype hint from the field name: string|date|decimal|enum|boolean_or_enum|lei|time"],
        ["Domain", "Business domain bucket from Attribute group (ConfirmationLetter, ProductEconomics, …)"],
        ["LDM entity", "Logical_Data_Model entity owning the TPS JSON path"],
        ["Trade model", "FpML-style: trade.parties[] + trade.product + trade.economics + trade.documentation"],
        ["TPS path root trade.parties[id=…]", "Maps to Party; buyer/seller/calculation agent are party references (href)"],
        ["TPS path root trade.product.*", "Maps to TradeProduct (productType, transactionType, party references)"],
        ["TPS path root trade.economics.*", "Maps to FxOptionEconomics (II-B) or ProductEconomics"],
        ["TPS path root trade.documentation.*", "Maps to Documentation / MasterConfirmation / LegalFramework / MatrixBinding"],
        ["TPS path root confirmation.*", "Maps to ExhibitILetter"],
        ["productInsert", "Exhibit I splice point: the relevant form of Confirmation (Exhibit II) + Additional Provisions (Exhibit III)"],
        ["TPs", "Transaction Processing systems (renamed from TPS in v1.3)"],
        ["SmartDX", "External vendor generating ISDA confirmation letter"],
        ["Swoosh", "Downstream classify + OCR — exception gate"],
        ["Compare X", "Data reconciliation — exception gate"],
        ["Tops and tails", "Exhibit I letter wrapper; TemplatePackage.master"],
        ["AssemblyRun / TemplatePackage", "Borrowed from internal ER image; kept MASTER/PRODUCT/SUPPLEMENT ontology"],
        ["PartyAB_Attributes", "FXO seed Party A vs B one-pager sheet"],
        ["AuditEvent", "Who/what/when/version for template, approval, assembly, document"],
        ["Four-eyes", "A DRAFT version needs TemplateApproval APPROVED by a second user before activate"],
        ["Manual drafting modes", "Load+edit ManualDraftContent OR drag-drop ManualEntryValue"],
        ["Phase 2 sim", "Prototype_Sim + Prototype_Trade_Book sheets live in the payload-mocks workbook"],
        ["LIVE FXO package", "TB-FXO-DEL-2026-001 v1.1.0 LIVE; v1.2.0 DRAFT approved 2027-12-01T15:30:00Z, activated 16:00:00Z"],
        ["Build", "Generated by scripts/build.py — do not edit this workbook by hand"],
    ]


def partyab_rows() -> list[list]:
    return [
        ["Attribute", "LDM entity", "Party A", "Party B", "Notes"],
        ["Party id (href target)", "Party.id", "partyA", "partyB", "trade.parties[]"],
        ["Buyer / Seller", "TradeProduct", "buyerPartyReference", "sellerPartyReference", "Sample FXO"],
        ["Legal name", "Party.partyName", "Standard Chartered Bank Sample Desk", "ACME Corp Treasury", "Assumed"],
        ["LEI", "Party.lei", "5493001KJTIIGC8Y1R12", "549300ABCDEFGH123456", None],
        ["Address", "Party.address", "(letterhead)", "1 Example Street, London EC2N 1HQ", None],
        ["Office", "Party.office", "Singapore", "London", None],
        ["Notice contact", "Party.noticeContact", "ops-fx@scb.example", "fxconfirm@acme.example", None],
        ["Account / SSI", "Party.settlementAccount", "Assumed SSI A", "Assumed SSI B", "With_MCA"],
        ["Calc agent", "Trade.calculationAgentPartyReference", "partyA (Assumed MCA)", "—", None],
        ["Master agreement date", "Documentation.masterAgreementDate", "2026-01-15 Assumed", "bilateral", "With_MCA"],
        ["Novation role example", "NovationTransfer", "remainingPartyReference", "transferorPartyReference → transfereePartyReference (partyC)", None],
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


def build_workbook(full_text: str | None = None) -> Workbook:
    full = full_text if full_text is not None else PDF_TXT.read_text(encoding="utf-8")
    dq_rules, map_rules = rules_dq_rows()
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Attribute_Product_Map"
    write_sheet(ws1, build_attribute_rows(full), HEADERS)
    write_sheet(wb.create_sheet("Template_Admin_Utility"), template_admin_rows())
    write_sheet(wb.create_sheet("Logical_Data_Model"), ldm_rows())
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
    write_sheet(wb.create_sheet("FXO_Deliverable_Lifecycle"), fxo_lifecycle_rows())
    write_sheet(wb.create_sheet("Legend_Assumptions"), legend_rows())
    write_sheet(wb.create_sheet("PartyAB_Attributes"), partyab_rows())
    return wb

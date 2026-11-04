# CDU-PS API Contract (Phase 1 — spec only)

No running server in Phase 1. Phase 2 implements FastAPI against this contract.

Base URL (prototype): `http://localhost:8080/v1`  
Auth (Phase 2): bearer service token; webhooks use HMAC header `X-CDU-Signature`.

## Conventions

| Item | Rule |
| --- | --- |
| Idempotency | Header `Idempotency-Key` required on all mutating POSTs/PUTs |
| Timestamps | ISO-8601 UTC |
| Errors | JSON problem body (below) |
| TPS paths | Align with Excel `Attribute_Product_Map` column *TPS JSON path* |

### Error model

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Human-readable summary",
    "details": [
      {"path": "trade.economics.strikePrice", "ruleId": "DQ-CROSS-001", "message": "…"}
    ],
    "requestId": "req_…"
  }
}
```

| HTTP | code examples |
| --- | --- |
| 400 | `VALIDATION_FAILED`, `BAD_ENUM` |
| 404 | `NOT_FOUND` |
| 409 | `CONFLICT`, `IDEMPOTENCY_REPLAY_MISMATCH` |
| 422 | `LEGAL_ELECTION_INVALID` |
| 500 | `INTERNAL` |

---

## Endpoints

### `POST /events`

Ingest lifecycle event from TPS.

**Headers:** `Idempotency-Key` (required)

**Body example (NEW_TRADE / II-B):**

```json
{
  "eventType": "NEW_TRADE",
  "eventId": "evt_1001",
  "tradeId": "TR-FXO-001",
  "occurredAt": "2027-12-01T10:00:00Z",
  "mcaPath": "With_MCA",
  "mcaProfileId": "MCA-SCB-ACME-2026-001",
  "legal": {
    "defsYear": "2026",
    "mainBookVersion": "1.0",
    "matrixBindings": {"SRO": null}
  },
  "template": {
    "productExhibitId": "II-B",
    "supplementExhibitIds": ["III-H"]
  },
  "trade": {
    "product": {"transactionType": "Deliverable FX Option Transaction"},
    "parties": {
      "partyA": {"name": "SCB Sample Desk", "lei": "…"},
      "partyB": {"name": "ACME Corp Treasury", "lei": "…"},
      "buyer": "Party A",
      "seller": "Party B"
    },
    "economics": {
      "tradeDate": "2027-12-01",
      "optionStyle": "European",
      "optionType": {"callCurrency": "EUR", "putCurrency": "USD"},
      "callCurrencyAmount": "1000000",
      "strikePrice": "1.0850",
      "expirationDate": "2027-12-31",
      "expirationTime": "10:00",
      "expirationTimeLocation": "New York",
      "premium": {"amount": "15000", "currency": "USD", "paymentDate": "2027-12-03"},
      "settlementMethod": "Deliverable"
    }
  }
}
```

**NOVATION body fragment:**

```json
{
  "eventType": "NOVATION",
  "tradeId": "TR-FXO-001",
  "novation": {
    "transferor": "Party B",
    "transferee": "Party C",
    "remainingParty": "Party A",
    "effectiveDate": "2028-01-15"
  }
}
```

**Responses:** `202 Accepted` with `{ "tradeId", "eventId", "confirmationId?", "documentId?", "status" }`  
**Errors:** 400 validation (DQ rules), 409 duplicate event with different payload.

---

### `GET /trades/{id}`

Return trade snapshot + current confirmation pointer.

```json
{
  "tradeId": "TR-FXO-001",
  "productType": "Deliverable_FX_Option",
  "mcaPath": "With_MCA",
  "latestDocumentId": "DOC-002",
  "affirmationStatus": "Affirmed",
  "templateVersion": "1.1.0"
}
```

### `GET /trades/{id}/timeline`

Ordered lifecycle events for the trade (NEW, HOT_SWAP, RESEND, AFFIRM, AMEND, NOVATION, EXERCISE, …).

```json
{
  "tradeId": "TR-FXO-001",
  "events": [
    {"eventId": "evt_1001", "eventType": "NEW_TRADE", "at": "…", "documentId": "DOC-001"},
    {"eventId": "evt_1002", "eventType": "HOT_SWAP", "at": "…", "templateVersion": "1.1.0"},
    {"eventId": "evt_1003", "eventType": "RESEND", "at": "…", "documentId": "DOC-002", "priorDocumentId": "DOC-001"}
  ]
}
```

---

### `POST /templates`

Create template / bundle shell.

```json
{
  "templateBundleId": "TB-FXO-DEL-2026-001",
  "masterTemplateId": "EXH-I-2026-v1",
  "productExhibitId": "II-B",
  "productType": "Deliverable_FX_Option",
  "supplementExhibitIds": [],
  "matrixBindings": {},
  "mcaRequired": true,
  "legalDefsYear": "2026",
  "hotReloadEnabled": true,
  "resendPolicy": "MANUAL"
}
```

### `PUT /templates/{id}/versions`

Add `DRAFT` version payload (template body / mapping revision metadata).

```json
{
  "version": "1.1.0",
  "status": "DRAFT",
  "notes": "Fix II-B product binding"
}
```

### `POST /templates/{id}/activate`

Promote version to `LIVE` (body: `{ "version": "1.1.0" }`). Emits logical `HOT_SWAP` when replacing a prior LIVE.

### `POST /templates/{id}/rollback`

Body: `{ "targetVersion": "1.0.0" }` → reactivates prior version.

---

### `POST /documents/{id}/resend`

Regenerate and send superseding confirmation.

```json
{
  "reason": "WRONG_TEMPLATE_CORRECTED",
  "templateVersion": "1.1.0"
}
```

**Response:** `{ "priorDocumentId", "documentId", "channels": ["SmartDX"] }`

---

### `POST /webhooks/affirmation`

Inbound from affirm / matching platform.

```json
{
  "documentId": "DOC-002",
  "tradeId": "TR-FXO-001",
  "status": "Affirmed",
  "timestamp": "2027-12-01T15:04:05Z",
  "differences": []
}
```

---

### `POST /callbacks/tps` (outbound shape)

CDU-PS → TPS. Not an inbound route; documented for TPS stub.

```json
{
  "tradeId": "TR-FXO-001",
  "eventType": "AFFIRM",
  "documentId": "DOC-002",
  "affirmationStatus": "Affirmed",
  "timestamp": "2027-12-01T15:04:05Z",
  "templateVersion": "1.1.0",
  "smartdxDocumentId": "SDX-…",
  "swiftMsgRef": null
}
```

Other `eventType` values reuse the same envelope with event-specific fields (`novationId`, `priorDocumentId`, etc.).

---

## Event type enum

`NEW_TRADE` | `AMEND` | `TERMINATE` | `EXERCISE` | `NOVATION` | `AFFIRM` | `HOT_SWAP` | `ROLLBACK` | `RESEND`

## Phase 1 non-goals

- No OpenAPI YAML binary; markdown contract only  
- No running server, auth implementation, or live SmartDX/SWIFT adapters

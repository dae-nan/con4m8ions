# Scenario: Affirmation webhook → TPS callback

## Given

- Confirmation `DOC-001` for trade `TR-FXO-001` sent to SmartDX  
- Affirmation status currently `Unmatched`  

## When

1. Affirm platform calls `POST /webhooks/affirmation` with:
   - `documentId`, `tradeId`, `status=Affirmed`, `timestamp`, optional match differences  
2. CDU-PS verifies webhook authenticity (Phase 2: HMAC; Phase 1 contract only)  
3. Lifecycle Store updates affirmation fields  
4. CDU-PS calls outbound `POST /callbacks/tps` (shape below)  

## Then

- `lifecycle.affirmation.status = Affirmed`  
- TPS receives callback with trade id, document id, status, timestamp  
- Duplicate webhook delivery is idempotent  

## Outbound callback shape (contract)

```json
{
  "tradeId": "TR-FXO-001",
  "eventType": "AFFIRM",
  "documentId": "DOC-001",
  "affirmationStatus": "Affirmed",
  "timestamp": "2027-12-01T15:04:05Z",
  "templateVersion": "1.1.0"
}
```

## Errors

- Unknown `documentId` → 404  
- Invalid status enum → 400 (`DQ-ENUM-011`)

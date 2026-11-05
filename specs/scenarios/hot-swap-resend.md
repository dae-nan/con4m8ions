# Scenario: Wrong template → HOT_SWAP → RESEND

## Given

- Trade `TR-FXO-001` is Deliverable FX Option (II-B)  
- Template Engine incorrectly bound product exhibit to II-A (Deliverable FX) at version `v1.0.0`  
- Document `DOC-001` already sent via SmartDX  

## When

1. Ops detects wrong PRODUCT layer on `DOC-001`  
2. Admin activates correct bundle `TB-FXO-DEL-2026-001` version `v1.1.0` (`POST /templates/{id}/activate`) — lifecycle event `HOT_SWAP`  
3. Ops calls `POST /documents/DOC-001/resend` with idempotency key  

## Then

- New `DocumentArtifact` `DOC-002` composed as MASTER I + PRODUCT II-B (+ any supplements) at `v1.1.0`  
- `DOC-002.priorDocumentId = DOC-001`  
- SmartDX receives superseding confirmation  
- TPS Callback reports `RESEND` success with both document ids  
- DQ `DQ-CROSS-009` satisfied (prior doc exists)  

## Failure cases

- Activate while status already LIVE same version → 409  
- Resend without prior document → 404  
- Duplicate idempotency key → 200 with original result

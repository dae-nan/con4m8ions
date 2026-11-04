# Scenario: NOVATION

## Given

- Affirmed Deliverable FXO trade `TR-FXO-001` between Party A (Remaining) and Party B (Transferor)  
- Template bundle LIVE `v1.1.0`  

## When

1. TPS posts `POST /events` with `eventType=NOVATION` and payload:
   - `transferor`, `transferee`, `remainingParty`, `effectiveDate`  
   - Updated LEIs / SSI for transferee  
2. Legal Resolver refreshes party blocks (Exhibit I)  
3. Template Engine regenerates confirmation  

## Then

- `NovationTransfer` entity persisted  
- New confirmation lists Transferee in place of Transferor; Remaining Party unchanged  
- SmartDX + optional SWIFT notified  
- TPS Callback includes `novationId` and new `documentId`  
- DQ `DQ-REQ-027` enforced (all three parties + effective date)  

## Notes

- MCA path unchanged unless novation terms require new MCA profile (Assumed: same profile if With_MCA)  
- Closing supersession clause applies to prior confirmation

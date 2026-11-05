# Scenario: With_MCA vs Without_MCA

## Shared given

- Same Deliverable FXO economics from TPS  
- LegalFramework defs year = 2026 Version 1.0  

## Path A — With_MCA

### When

- TPs sends `trade.documentation.masterConfirmation.masterConfirmationId = MCA-SCB-ACME-2026-001` (Assumed); Legal Resolver derives `mcaPath=With_MCA`  
- Confirmation omits Calculation Agent and notice contacts  

### Then

- Template Engine fills CA = Party A, notices from Assumed MCA  
- `ISDA Master Agreement Date` taken from MCA / profile  
- Attribute rows with MCA sample show **Assumed** flag  
- DQ `DQ-MCA-001`…`DQ-MCA-010` evaluated  

## Path B — Without_MCA

### When

- TPs sends `trade.documentation.masterConfirmation = null` and `masterAgreement.longFormFallback = true`; Legal Resolver derives `mcaPath=Without_MCA`  
- No master confirmation id  

### Then

- Long-form Exhibit I fallback language enabled  
- Governing law + Termination Currency must be present (or WARN per `DQ-LEGAL-005`)  
- CA, LEI, accounts, notices taken only from TPS / explicit confirmation fields  
- No Assumed MCA defaults applied  

## Acceptance

- Both paths produce valid `ConfirmationInstance` compositions  
- Excel MCA path column distinguishes `With_MCA` / `Without_MCA` / `Both`

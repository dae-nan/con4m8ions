# Scenario: Supplement election (Barrier / Averaging)

## Given

- Deliverable FXO base product Exhibit II-B  
- LIVE bundle includes MASTER I + PRODUCT II-B  

## Case 1 — Barrier (III-H)

### When

- TPS elects barrier: `supplementExhibitIds=["III-H"]`  
- Option Type may be `Binary`; Barrier Event fields populated  

### Then

- ConfirmationInstance includes SUPPLEMENT III-H attributes  
- Cross-field DQ: Binary + Barrier consistency; Option Style omitted for Binary Barrier where required  
- SmartDX document contains barrier section  

## Case 2 — Averaging Strike (III-G)

### When

- Strike Price = `The Averaging Rate`  
- `supplementExhibitIds` includes `III-G`  

### Then

- `DQ-CROSS-003` passes (III-G elected)  
- Averaging method / dates / SRO fields from III-G mapped  
- Only one of Call/Put amount numeric (`DQ-CROSS-002`)  

## Case 3 — Combined

- II-B + III-A (disruption) + III-H (barrier) allowed  
- Template Admin stores `supplementExhibitIds=["III-A","III-H"]`  
- Composition order: MASTER → PRODUCT → supplements in election order  

## Acceptance

- Supplement fields appear under group `SUPPLEMENT` / layer `SUPPLEMENT` in Excel  
- API event payload accepts `supplementExhibitIds[]`

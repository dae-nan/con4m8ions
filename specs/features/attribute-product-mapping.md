# Feature: Attribute ↔ Product Mapping

## Intent

Maintain a single vocabulary for confirmation attributes across MASTER / PRODUCT / SUPPLEMENT layers, MCA paths, matrix pins, and platform fields — sourced from the 2026 annotated confirmation templates PDF and recorded in `docs/mappings/cdu-ps-isda-2026-mapping.xlsx`.

## Groups

| Group | Source |
| --- | --- |
| COMMON | Exhibit I |
| PRODUCT | Exhibit II-* |
| SUPPLEMENT | Exhibit III-* (when elected) |
| MATRIX | SRO / EM / other matrix bindings |
| MCA | Assumed MCA elections (`With_MCA`) |
| PLATFORM | CDU-PS / TPS / SmartDX / SWIFT ops fields |
| LIFECYCLE | Event, affirmation, novation metadata |

## Template layers

- `MASTER` = Exhibit I  
- `PRODUCT` = Exhibit II-* (one product type per exhibit)  
- `SUPPLEMENT` = Exhibit III-* via `supplementRefs[]` / `supplementExhibitIds[]`

## Composition

```text
ConfirmationInstance = MASTER + PRODUCT + Σ SUPPLEMENT + MATRIX? + MCA? + PLATFORM
```

## MCA paths

- `With_MCA` — apply Assumed `MasterConfirmation` elections; flag Assumed fields  
- `Without_MCA` — explicit Exhibit I long-form / election fields  
- `Both` — attribute applies on either path  

## Depth

- **Deep:** Exhibit II-B Deliverable FX Option — full field inventory + DQ/MAP rule IDs  
- **Standard:** all other exhibits — extracted fields + lineage at exhibit level minimum  

## TPS / downstream

Each mapped attribute carries:

- `TPS JSON path` (e.g. `trade.economics.strikePrice`)  
- SmartDX / SWIFT target labels  
- FK lists to `Rules_DQ` (`DQ-*`, `MAP-*`)

## Acceptance

- Excel `Attribute_Product_Map` covers Exhibits I, II-A…II-K, III-A…III-H  
- II-B is Deep; Assumed MCA inventory present and flagged  
- Generator script regenerable: `scripts/generate_phase1_mapping.py`

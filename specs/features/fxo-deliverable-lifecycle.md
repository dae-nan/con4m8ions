# Feature: FXO Deliverable Lifecycle (Exhibit II-B)

## Intent

Deep-dive lifecycle for **Deliverable FX Option Transaction** across NEW → (wrong template) HOT_SWAP/RESEND → AFFIRM → AMEND → NOVATION → EXERCISE / SETTLEMENT, with disruption / early-termination edges via Exhibit III.

## Product binding

| Item | Value |
| --- | --- |
| Exhibit | II-B |
| ProductType | `Deliverable_FX_Option` |
| Master | Exhibit I |
| Eligible supplements | III-A, III-C, III-D, III-F, III-G, III-H |
| Matrix | Optional SRO Matrix version pin |

## Events × systems

Canonical step table: Excel sheet `FXO_Deliverable_Lifecycle`. Sequence diagram: PRD §7.

| Event | Primary systems |
| --- | --- |
| NEW_TRADE | TPS → Ingest → Legal Resolver → Template Engine → SmartDX / SWIFT → TPS Callback |
| HOT_SWAP | Template Admin → Template Engine |
| RESEND | Document Service → SmartDX → Callback |
| AFFIRM | Affirm webhook → Lifecycle Store → Callback |
| AMEND | TPS → Ingest → Engine → SmartDX |
| NOVATION | TPS → Legal (parties/LEI/SSI) → Engine → SmartDX / SWIFT |
| EXERCISE | TPS / Exercise desk → Lifecycle → Settlement prep |
| TERMINATE | TPS → Engine (III-C/III-D/III-A edges) |

## Sample economics (illustrative)

- EUR Call / USD Put, European, Automatic Exercise applicable  
- Trade Date T, Expiration Date T+30, Premium on T+2  
- Optional: Full Automated Exercise + SRO; or Barrier via III-H  

## MCA

Demo must run both `With_MCA` (Assumed profile defaults) and `Without_MCA` (explicit Exhibit I elections).

## Acceptance

- Deep II-B rows in `Attribute_Product_Map`  
- Lifecycle sheet steps align with PRD mermaid  
- Scenarios cover hot-swap, novation, MCA dual path, affirm, supplement election

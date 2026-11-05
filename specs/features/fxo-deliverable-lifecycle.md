# Feature: FXO Deliverable Lifecycle (Exhibit II-B)

## Intent

Deep-dive lifecycle for **Deliverable FX Option Transaction**. Canonical narrative is **Use Case 2.0** in PRD §8 (happy path) with **Template Admin** as a separate prerequisite (§9) and recovery edges (§8.6 / §10.1). Trade happy path drafts the **Exhibit I letter** then splices II-B (+ III).

Journey order: template setup → NEW → generate letter → SmartDX/SWIFT → AFFIRM → AMEND → NOVATION → EXERCISE/SETTLE. Wrong-template HOT_SWAP/RESEND is an **edge**, not mashed into the happy-path sequence blob.

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

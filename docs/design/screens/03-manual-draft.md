# 03 — Manual draft (load template → edit → submit)

| Item | Value |
| --- | --- |
| Status | Phase 2 wireframe — ideal path — draft for review |
| Design system | [`components`](../system/components.md) §1, §2, §7, §8, §11 · [`widgets`](../system/widgets.md) W4 (edit mode) |
| Story map (PRD §9.3) | **K2 Book and assemble** → S2 Assemble FXO letter → F2c Auto or manual draft (mode a: load template then edit), F2a Locate package (pinned v1.1.0) · hands off to **K3** F3a Channel send |
| Data | `prototype/data/outbound/api-responses/TR-FXO-005/02-get-assembly.pending-manual-draft.200.json` · `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` · `prototype/data/inbound/ui/AR-FXO-005-01.put-manual-draft.json` · `prototype/data/outbound/api-responses/TR-FXO-005/04-put-manual-draft.200.json` · `prototype/data/outbound/api-responses/TR-FXO-005/05-post-submit.200.json` · `prototype/data/outbound/smartdx/DOC-105.send.json` |
| APIs | `GET /assemblies/{id}` · `GET /assemblies/{id}/shell` · `PUT /assemblies/{id}/manual-draft` · `POST /assemblies/{id}/submit` |
| PRD | §6 Manual drafting (mode a), §6.3 sequence |
| Flow | [`../flows/fxo-ideal-path.md`](../flows/fxo-ideal-path.md) flow C |

## 1. Goal

When STP cannot finish a letter (`TR-FXO-005`: counterparty asked for bespoke Calculation Agent wording), the analyst finishes it **inside CDU-PS**: load the LIVE Exhibit I + II-B shell already filled with trade data, edit only the unlocked block, save (audited), and submit to SmartDX.

**Non-goals:** drag-drop field mode (b), clause library, redlining against counterparty paper.

## 2. Actors

Ops confirm analyst `u.ops.tan`.

## 3. Entry / exit

| From | To | Trigger |
| --- | --- | --- |
| Ops desk row `TR-FXO-005` (ManualDraft) → **Open draft** ([`01`](01-ops-desk.md)) | this screen | click |
| Submit success | [`01-ops-desk.md`](01-ops-desk.md), trade now AffirmPending | auto after notice |
| **View timeline** | [`04-fxo-timeline.md`](04-fxo-timeline.md) for `TR-FXO-005` | link |

## 4. Layout — desktop

```text
 Trades / TR-FXO-005 / Manual draft
 TR-FXO-005 · Globex Holdings Ltd · Without_MCA                 (● PENDING_MANUAL_DRAFT)     ‹ View timeline ›
 AR-FXO-005-01 · MANUAL_DRAFTING · TB-FXO-DEL-2026-001 v1.1.0 (pinned)
 ┃ ℹ Reason from TPs: Counterparty requested bespoke Calculation Agent wording
┌─ Letter canvas ─ edit mode ─ TV-I-2026-1.1.0 ────────────────────────────────┐ ┌─ Trade facts (read-only) ───────┐
│ ▸ Heading       Standard Chartered Bank Sample Desk · 2027-12-01  🔒          │ │ Option     EUR Call / USD Put   │
│                 Globex Holdings Ltd, 200 Novation Ave, New York NY 10005      │ │ Call       EUR 2500000          │
│ ▸ Definitions   2026 FX Definitions Main Book Version 1.0          🔒          │ │ Strike     1.0900               │
│ ▸ Agreement     Long-form: ISDA 2002 form, English law, USD TC     🔒          │ │ Expiry     2027-12-31 10:00 NY  │
│ ┌ productInsert ─ Exhibit II-B (from trade) ──────────────────────── 🔒 ┐    │ │ Premium    USD 37500            │
│ │ Buyer Party A · Seller Party B · European · EUR Call / USD Put      │    │ │ Pay date   2027-12-03           │
│ └──────────────────────────────────────────────────────────────────────┘    │ │ Party B LEI 549300TRANSFeree0001│
│ ✎ Elections     Party A LEI 5493001KJTIIGC8Y1R12 · Party B LEI 5493…0001   │ ├─ Draft ─────────────────────────┤
│                 Calculation Agent                                            │ │ Loaded   16:40Z u.ops.tan       │
│                 [Party A; provided that if an Event of Default has occurred_]│ │ Saved    16:52Z  MDC-005-01     │
│                 [with respect to Party A, Party B may appoint a leading____]│ │ Hash     sha256:…               │
│                 [dealer as Calculation Agent_______________________________]│ │                                 │
│                 Governing law  English law                                   │ │                                 │
│ ▸ Closing       Supersession + please confirm                      🔒          │ │                                 │
└──────────────────────────────────────────────────────────────────────────────┘ └─────────────────────────────────┘
                                                                    ‹ Cancel ›   [ Save draft ]   [▶ Submit to SmartDX]
```

- `✎` = editable block (from `editableBlocks`), `🔒` = locked block rendered from template + trade data.
- The **productInsert** block is the Exhibit I splice point for the Exhibit II-B form ("Confirmation of a Deliverable FX Option Transaction"), plus Exhibit III Additional Provisions when elected (none here). Its body is the rendered II-B General Terms: Buyer and Seller print as "Party A" / "Party B", resolved from the trade's party references ([`modelling-decisions.md`](../modelling-decisions.md) MD-4, MD-6).
- Edited text is highlighted (`attention` tone background) until saved.

### 4.1 Submit modal + result

```text
        ╔══════════════════════════════════════════════════════════╗
        ║ Submit TR-FXO-005 to SmartDX?                            ║
        ║ ──────────────────────────────────────────────────────── ║
        ║ Template TB-FXO-DEL-2026-001 v1.1.0 · 1 block edited     ║
        ║ Channel SmartDX                                          ║
        ║                             ‹ Cancel ›  [▶ Submit]       ║
        ╚══════════════════════════════════════════════════════════╝

 ┃ ✓ Submitted. DOC-105 sent to SmartDX at 16:55Z; TPs notified.   [✕]
```

## 5. Layout — iPhone (`sm`)

Trade facts collapse into an accordion above the canvas; one block per screen height; Save and Submit sit in a sticky footer. Editing long clauses on phone is supported but not optimised.

## 6. Interaction (ideal path)

1. Opens from ops desk; screen calls `GET /assemblies/AR-FXO-005-01` (status PENDING_MANUAL_DRAFT) and `GET /assemblies/AR-FXO-005-01/shell`.
2. Only **Elections** is editable; analyst replaces the Calculation Agent clause.
3. **Save draft** → `PUT /assemblies/AR-FXO-005-01/manual-draft`; Draft panel shows MDC id, time, hash (audit `assembly.manual_saved`).
4. **Submit to SmartDX** → modal → `POST /assemblies/AR-FXO-005-01/submit`; CDU-PS sends `DOC-105` (mock SmartDX) and acks TPs.
5. Notice, then back to ops desk; `TR-FXO-005` shows AffirmPending.

## 7. Component inventory

| Element | Component / widget | Class |
| --- | --- | --- |
| Page header | components §9 | `.cdu-page-header` |
| Reason notice | components §8 (info) | `.cdu-notice--info` |
| Letter canvas, edit mode | W4 | `.cdu-letter` |
| Clause textarea | components §2 (multi-line input) | `.cdu-field` |
| Trade facts / draft panel | components §11 | `.cdu-kv` |
| Buttons | components §1 | `.cdu-btn--*` |
| Submit modal | components §7 | `.cdu-modal` |

## 8. Data bindings

| UI label | File | JSON path | Example |
| --- | --- | --- | --- |
| Run status | `prototype/data/outbound/api-responses/TR-FXO-005/02-get-assembly.pending-manual-draft.200.json` | `status` | `PENDING_MANUAL_DRAFT` |
| Assembly mode | `prototype/data/outbound/api-responses/TR-FXO-005/02-get-assembly.pending-manual-draft.200.json` | `assemblyMode` | `MANUAL_DRAFTING` |
| Pinned version | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `templateVersion` | `1.1.0` |
| Reason | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `reason` | `Counterparty requested bespoke Calculation Agent wording` |
| Editable block | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `editableBlocks[0]` | `elections` |
| Heading Party B | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `exhibitILetter.blocks.heading.partyBName` | `Globex Holdings Ltd` |
| Calc Agent (before) | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `exhibitILetter.blocks.elections.calculationAgent` | `Party A` |
| Insert exhibit | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `exhibitILetter.blocks.productInsert.exhibitId` | `II-B` |
| Insert title | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `exhibitILetter.blocks.productInsert.title` | `Confirmation of a Deliverable FX Option Transaction` |
| Insert Buyer | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `productBody.generalTerms.buyer` | `Party A` |
| Letter path (derived) | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `exhibitILetter.path` | `Without_MCA` |
| Facts Strike | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `productBody.generalTerms.strikePrice` | `1.0900` |
| Facts Call amount | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `productBody.generalTerms.callCurrencyAmount` | `2500000` |
| Facts Premium | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `productBody.generalTerms.premiumAmount` | `37500` |
| Calc Agent (edited) | `prototype/data/inbound/ui/AR-FXO-005-01.put-manual-draft.json` | `content.blocks.elections.calculationAgent` | `Party A; provided that if an Event of Default has occurred with respect to Party A, Party B may appoint a leading dealer as Calculation Agent` |
| Draft id | `prototype/data/outbound/api-responses/TR-FXO-005/04-put-manual-draft.200.json` | `id` | `MDC-005-01` |
| Saved at | `prototype/data/outbound/api-responses/TR-FXO-005/04-put-manual-draft.200.json` | `savedAt` | `2027-12-01T16:52:00Z` |
| Submit result document | `prototype/data/outbound/api-responses/TR-FXO-005/05-post-submit.200.json` | `documentId` | `DOC-105` |
| Submit result status | `prototype/data/outbound/api-responses/TR-FXO-005/05-post-submit.200.json` | `status` | `COMPLETED` |
| SmartDX letter CA | `prototype/data/outbound/smartdx/DOC-105.send.json` | `exhibitILetter.blocks.elections.calculationAgent` | `Party A; provided that if an Event of Default has occurred with respect to Party A, Party B may appoint a leading dealer as Calculation Agent` |

## 9. API calls

| When | Call | File |
| --- | --- | --- |
| Open | `GET /assemblies/AR-FXO-005-01` | `prototype/data/outbound/api-responses/TR-FXO-005/02-get-assembly.pending-manual-draft.200.json` |
| Open | `GET /assemblies/AR-FXO-005-01/shell` | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` |
| Save | `PUT /assemblies/AR-FXO-005-01/manual-draft` | request `prototype/data/inbound/ui/AR-FXO-005-01.put-manual-draft.json` → `prototype/data/outbound/api-responses/TR-FXO-005/04-put-manual-draft.200.json` |
| Submit | `POST /assemblies/AR-FXO-005-01/submit` | request `prototype/data/inbound/ui/AR-FXO-005-01.post-submit.json` → `prototype/data/outbound/api-responses/TR-FXO-005/05-post-submit.200.json` |
| (server) | `POST /mock/smartdx/documents` · `POST /callbacks/tps` | `prototype/data/outbound/smartdx/DOC-105.send.json` · `prototype/data/outbound/tps-callbacks/TR-FXO-005.01-generated.json` |

## EDGE / STUB

- Mode (b) drag-drop fields + `PUT /assemblies/{id}/manual-entries` (PENDING_DATA_ENTRY, widget W8) — STUB.
- Abandon / suppress draft (E11), paper channel suppression — STUB.
- Edits to locked blocks, unlock request to template admin — STUB.
- Concurrent editors / draft locking — STUB.
- SmartDX unavailable on submit (E8) — STUB.
- Exhibit III Additional Provisions inside `productInsert` (`additionalProvisionExhibitIds`) — STUB (none elected).

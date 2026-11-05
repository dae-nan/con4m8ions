# 02 — Template admin (view LIVE package, activate DRAFT)

| Item | Value |
| --- | --- |
| Status | Phase 2 wireframe — ideal path — draft for review |
| Design system | [`components`](../system/components.md) §1, §4, §5, §7, §8, §9 · [`widgets`](../system/widgets.md) W2, W7 |
| Story map (PRD §9.3) | **K1 Define templates** → S1 Activate LIVE package → F1a Draft version, F1b Configure mapping, F1c Audit activate |
| Data | `prototype/data/templates/index.json` · `prototype/data/templates/fxo-deliverable-2026/package.json` · `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` · `prototype/data/templates/fxo-deliverable-2026/exhibit-ii-b-product.json` · `prototype/data/templates/fxo-deliverable-2026/selection-rules.json` · `prototype/data/templates/fxo-deliverable-2026/audit.json` |
| APIs | `GET /templates` · `GET /templates/{id}` · `GET /templates/{id}/versions/{version}` · `GET /templates/{id}/layers/{templateVersionId}` · `GET /templates/selection-rules` · `GET /templates/{id}/audit` · `POST /templates/{id}/activate` |
| Feature spec | [`specs/features/template-admin.md`](../../../specs/features/template-admin.md) · PRD §13.1, §14.1 |
| Flow | [`../flows/fxo-ideal-path.md`](../flows/fxo-ideal-path.md) flow A |

## 1. Goal

The template admin sees the one LIVE **2026 FXO Deliverable (II-B)** package — what is LIVE, what is waiting in DRAFT, which fields it binds and who changed what — and activates the validated, **four-eyes approved** DRAFT **1.2.0** with an audit trail, trusting the cutover.

**Non-goals:** authoring template text (DRAFT 1.2.0 already exists), the approval workflow itself (mocked as already approved; shown as "Coming soon"), rollback, hot-swap of a wrong template.

## 2. Actors

Template admin `u.admin.lee` (primary; open under scenario **A**) · Product control approver `u.ctrl.ng` (approved 1.2.0; no screen in the prototype) · Legal (read).

## 3. Entry / exit

| From | To | Trigger |
| --- | --- | --- |
| Shell **Templates** ([`00`](00-shell-nav.md)) | list (§4.1) | — |
| Ops desk drawer **Package** link ([`01`](01-ops-desk.md)) | package detail (§4.2) | click |
| Activate success | package detail, Overview tab refreshed | auto |

## 4. Layout — desktop

### 4.1 Package list (`GET /templates`)

```text
 Templates
 [⌕ Search package________]  Product [All ▾]  Status [All ▾]
┌──────────────────────────────────────────────────────────┐
│ 2026 FXO Deliverable (II-B)               (● LIVE 1.1.0) │
│ TB-FXO-DEL-2026-001                                      │
│ Exhibit I EXH-I-2026-v1 + II-B · Supplements none        │
│ Defs 2026 · MCA optional · Resend MANUAL · Hot reload on │
│ Draft waiting: 1.2.0 · (● APPROVED)           → Open     │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Package detail — Versions tab (`GET /templates/{id}` + `GET /templates/{id}/versions/{version}`)

```text
 Templates / 2026 FXO Deliverable (II-B)
 2026 FXO Deliverable (II-B)                                   (● LIVE 1.1.0)      [▶ Activate 1.2.0]
 TB-FXO-DEL-2026-001 · Exhibit I + II-B · Defs 2026 · rollback target 1.0.0

  Overview   Versions   Bindings   Audit
            ══════════
┌─────────┬──────────────┬──────────────────────┬──────────────────────┬───────────────────┬──────────────────┐
│ Version │ Status       │ Exhibit I layer      │ II-B layer           │ Activated         │ Retired          │
├─────────┼──────────────┼──────────────────────┼──────────────────────┼───────────────────┼──────────────────┤
│▌1.2.0   │ (○ DRAFT)    │ TV-I-2026-1.2.0      │ TV-IIB-2026-1.1.0    │ —                 │ —                │
│ 1.1.0   │ (● LIVE)     │ TV-I-2026-1.1.0      │ TV-IIB-2026-1.1.0    │ 2027-11-22 00:00Z │ —                │
│ 1.0.0   │ (○ RETIRED)  │ TV-I-2026-1.0.0      │ TV-IIB-2026-1.0.0    │ 2027-10-15 09:00Z │ 2027-11-22 00:00Z│
└─────────┴──────────────┴──────────────────────┴──────────────────────┴───────────────────┴──────────────────┘
┌─ Version 1.2.0 ─────────────────────────────────────────────────────────────────────────────────────────┐
│ Change log   Exhibit I notices: add SmartDX Docbox as Party A notice channel                              │
│ Change       elections · Contact details for notice Party A (trade.parties[id=partyA].noticeContact)       │
│              before  ops-fx@scb.example                                                                    │
│              after   ops-fx@scb.example; SmartDX Docbox SCB-SG                                             │
│ Validation   (● PASSED) 2027-11-28 09:10Z                                                                  │
│              ✓ Every field resolves to an Attribute_Product_Map row                                        │
│              ✓ DQ rules bound for every required II-B field                                                │
│              ✓ Sample render of TR-FXO-001 (With MCA) and Without MCA                                     │
│ Drafted by   u.admin.lee · 2027-11-28 09:00Z                                                               │
│ Approval     (● APPROVED) u.ctrl.ng · 2027-12-01 15:30Z · AUD-0007   (four-eyes: approver ≠ activator)    │
│              requested by u.admin.lee · 2027-11-28 09:15Z                                                  │
│              "Notice channel change reviewed against Exhibit I; no economic impact"                        │
│              ‹ Request approval ›  ‹ Approve › ‹ Reject ›   (◌ Coming soon)                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Bindings tab (`GET /templates/selection-rules` + layer bodies)

```text
  Overview   Versions   Bindings   Audit
                        ════════
 Selection rule  PSR-FXO-DEL-2026-001 · Deliverable_FX_Option · NEW_TRADE · SCB-SG · SmartDX · priority 10
 Routing         Deliverable_FX_Option / NEW_TRADE → TB-FXO-DEL-2026-001
 Matrix pins     SRO: none (each matrix as at Trade Date)   MCA required: no (With MCA and Without MCA)

 II-B fields (TV-IIB-2026-1.1.0)                       example TR-FXO-001
┌────────────────────────┬──────────────────────────────────────┬───────────────────────────────────┐
│ Attribute              │ TPs JSON path                        │ Example                           │
├────────────────────────┼──────────────────────────────────────┼───────────────────────────────────┤
│ Transaction Type       │ trade.product.transactionType        │ Deliverable FX Option Transaction │
│ Option Type            │ trade.economics.optionType           │ EUR Call / USD Put                │
│ Strike Price           │ trade.economics.strikePrice          │ 1.0850                            │
│ Premium                │ trade.economics.premiumAmount        │ 15000                             │
│ …18 rows               │                                      │                                   │
└────────────────────────┴──────────────────────────────────────┴───────────────────────────────────┘
 Exhibit I blocks (TV-I-2026-1.1.0): heading · intro · definitionsVersion · agreementClause · productInsert (→ II-B) · elections · closing · signatures
```

### 4.4 Audit tab (`GET /templates/{id}/audit`) — widget W7

```text
┌─────────────────────┬──────────────┬───────────────────────────┬─────────────┐
│ At (UTC)            │ Actor        │ Action                    │ Version     │
├─────────────────────┼──────────────┼───────────────────────────┼─────────────┤
│ 2027-12-01 15:30:00 │ u.ctrl.ng    │ Template approved         │ — → 1.2.0   │
│ 2027-11-28 09:10:00 │ svc.cdu-ps   │ Template validated        │ — → 1.2.0   │
│ 2027-11-28 09:00:00 │ u.admin.lee  │ Template version added    │ — → 1.2.0   │
│ 2027-11-22 00:00:00 │ u.admin.lee  │ Template activated        │ 1.0.0 → 1.1.0│
│ 2027-11-10 09:00:00 │ u.admin.lee  │ Template version added    │ — → 1.1.0   │
│ 2027-10-15 09:00:00 │ u.admin.lee  │ Template activated        │ — → 1.0.0   │
│ 2027-10-01 09:00:00 │ u.admin.lee  │ Template created          │ — → 1.0.0   │
└─────────────────────┴──────────────┴───────────────────────────┴─────────────┘
```

### 4.5 Activate modal + result (`POST /templates/{id}/activate`)

```text
        ╔══════════════════════════════════════════════════════════════╗
        ║ Activate version 1.2.0?                                      ║
        ║ ──────────────────────────────────────────────────────────── ║
        ║ 1.1.0 becomes RETIRED and the rollback target.               ║
        ║ New trades use 1.2.0 from now. Running assemblies keep their ║
        ║ pinned version. Resend policy MANUAL: nothing is resent.     ║
        ║ Approved by u.ctrl.ng · 2027-12-01 15:30Z · AUD-0007   ✓     ║
        ║ Reason      [PLANNED_RELEASE        ▾]                       ║
        ║                                   ‹ Cancel ›  [▶ Activate]   ║
        ╚══════════════════════════════════════════════════════════════╝

 ┃ ✓ Version 1.2.0 is LIVE. New trades use it from 2027-12-01T16:00:00Z. Audit AUD-0008.   [✕]
 2026 FXO Deliverable (II-B)                                   (● LIVE 1.2.0)
```

Status chips and approval use the [display-label map](../system/components.md#display-label-map-h2).

## 5. Layout — iPhone (`sm`)

- **[▶ Activate 1.2.0]** is enabled only when `approval.status = APPROVED` and the signed-in user is not `approval.approvedBy`; otherwise it is disabled with the reason as helper text (EDGE).

Tabs become a dropdown; the versions table becomes stacked cards (version, status chip, activated); the activate button is a full-width sticky footer.

## 6. Interaction (ideal path)

1. Admin opens **Templates** → one package card (LIVE 1.1.0, draft 1.2.0 waiting) → **Open**.
2. **Versions** tab, selects 1.2.0 → sees change, validation PASSED and approval APPROVED by `u.ctrl.ng` (F1a Draft version, F1b Configure mapping).
3. Optional: **Bindings** tab to confirm the selection rule and II-B field paths; **Audit** tab for history.
4. Clicks **[▶ Activate 1.2.0]** → modal, reason `PLANNED_RELEASE` → **Activate**.
5. Notification shows LIVE 1.2.0 and the audit id; Versions table now shows 1.2.0 LIVE, 1.1.0 RETIRED; Audit tab gains `AUD-0008` after the approval `AUD-0007` (F1c Audit activate).

## 7. Component inventory

| Element | Component / widget | Class |
| --- | --- | --- |
| Package card | W2 | `.cdu-package-card` |
| Page header + primary action | components §9, §1 | `.cdu-page-header`, `.cdu-btn--primary` |
| Tabs | components §5 | `.cdu-tabs` |
| Versions table | components §4 (default density) | `.cdu-table` |
| Version detail panel | components §11 | `.cdu-kv` |
| Audit list | W7 | `.cdu-audit` |
| Activate modal | components §7 | `.cdu-modal` |
| Success notice | components §8 | `.cdu-notice--success` |
| Approval line + workflow stub | components §11, §12 | `.cdu-kv`, `.cdu-chip--approved`, `.cdu-chip--coming-soon` |

## 8. Data bindings

| UI label | File | JSON path | Example |
| --- | --- | --- | --- |
| Card title | `prototype/data/templates/index.json` | `items[0].packageName` | `2026 FXO Deliverable (II-B)` |
| Card LIVE version | `prototype/data/templates/index.json` | `items[0].version` | `1.1.0` |
| Header package id | `prototype/data/templates/fxo-deliverable-2026/package.json` | `templateBundleId` | `TB-FXO-DEL-2026-001` |
| Header rollback target | `prototype/data/templates/fxo-deliverable-2026/package.json` | `rollbackTargetVersion` | `1.0.0` |
| MCA required | `prototype/data/templates/fxo-deliverable-2026/package.json` | `mcaRequired` | `false` |
| Resend policy | `prototype/data/templates/fxo-deliverable-2026/package.json` | `resendPolicy` | `MANUAL` |
| Versions row 3 status | `prototype/data/templates/fxo-deliverable-2026/package.json` | `versions[2].status` | `DRAFT` |
| Versions row 3 Exhibit I layer | `prototype/data/templates/fxo-deliverable-2026/package.json` | `versions[2].masterTemplateVersionId` | `TV-I-2026-1.2.0` |
| 1.2.0 change log | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `changeLog` | `Exhibit I notices: add SmartDX Docbox as Party A notice channel` |
| 1.2.0 change after | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `changes[0].after` | `ops-fx@scb.example; SmartDX Docbox SCB-SG` |
| 1.2.0 validation | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `validation.status` | `PASSED` |
| Selection rule | `prototype/data/templates/fxo-deliverable-2026/selection-rules.json` | `items[0].ruleId` | `PSR-FXO-DEL-2026-001` |
| II-B Strike path | `prototype/data/templates/fxo-deliverable-2026/exhibit-ii-b-product.json` | `fields[9].tpsJsonPath` | `trade.economics.strikePrice` |
| II-B Strike example | `prototype/data/templates/fxo-deliverable-2026/exhibit-ii-b-product.json` | `fields[9].example` | `1.0850` |
| Audit latest action | `prototype/data/templates/fxo-deliverable-2026/audit.json` | `items[6].action` | `template.approved` |
| Card / row 3 approval | `prototype/data/templates/fxo-deliverable-2026/package.json` | `versions[2].approvalStatus` | `APPROVED` |
| 1.2.0 approved by | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `approval.approvedBy` | `u.ctrl.ng` |
| 1.2.0 approved at | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `approval.approvedAt` | `2027-12-01T15:30:00Z` |
| 1.2.0 requested by | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `approval.requestedBy` | `u.admin.lee` |
| 1.2.0 approval audit | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `approval.auditId` | `AUD-0007` |
| Policy four-eyes | `prototype/data/templates/fxo-deliverable-2026/package.json` | `activationPolicy.fourEyes` | `true` |
| Activate reason | `prototype/data/inbound/ui/TB-FXO-DEL-2026-001.activate-1.2.0.json` | `reason` | `PLANNED_RELEASE` |
| Result activated at | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` | `activatedAt` | `2027-12-01T16:00:00Z` |
| Result audit id | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` | `auditId` | `AUD-0008` |
| Result approved by | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` | `approvedBy` | `u.ctrl.ng` |
| After: LIVE version | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/03-get-template.after-activate.200.json` | `version` | `1.2.0` |
| After: 1.1.0 status | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/03-get-template.after-activate.200.json` | `versions[1].status` | `RETIRED` |

Audit table rows render newest first; the file is oldest first.

## 9. API calls

| When | Call | Response file |
| --- | --- | --- |
| List | `GET /templates` | `prototype/data/templates/index.json` |
| Open | `GET /templates/TB-FXO-DEL-2026-001` | `prototype/data/templates/fxo-deliverable-2026/package.json` |
| Select version | `GET /templates/TB-FXO-DEL-2026-001/versions/1.2.0` | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` |
| Bindings tab | `GET /templates/selection-rules` · `GET /templates/TB-FXO-DEL-2026-001/layers/TV-IIB-2026-1.1.0` | `prototype/data/templates/fxo-deliverable-2026/selection-rules.json` · `prototype/data/templates/fxo-deliverable-2026/exhibit-ii-b-product.json` |
| Audit tab | `GET /templates/TB-FXO-DEL-2026-001/audit` | `prototype/data/templates/fxo-deliverable-2026/audit.json` |
| Activate | `POST /templates/TB-FXO-DEL-2026-001/activate` | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` |
| Refresh | `GET /templates/TB-FXO-DEL-2026-001` · `GET /templates/TB-FXO-DEL-2026-001/audit` | `…/03-get-template.after-activate.200.json` · `…/04-get-template-audit.after-activate.200.json` |

## EDGE / STUB

- Create package / author new version text (`POST /templates`, editing `PUT /templates/{id}/versions`) — STUB; history row only.
- ValidationError state on a DRAFT (PRD §13.1) — STUB.
- Rollback (`POST /templates/{id}/rollback`, E10) and hot-swap of a wrong template + resend (E1) — STUB.
- Supplement (III-*) bindings and SRO matrix pin editing — STUB.
- Four-eyes approval workflow (request / approve / reject, `POST /templates/{id}/versions/{version}/approval`) — `(◌ Coming soon)` stub; the 1.2.0 approval is mocked as given.
- Activate blocked (409 `APPROVAL_REQUIRED` / `FOUR_EYES_VIOLATION`) — STUB.

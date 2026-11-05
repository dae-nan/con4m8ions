# Information architecture — CDU-PS ops desk prototype

| Item | Value |
| --- | --- |
| Status | Phase 2 design pack — draft for review |
| Scope | The six screens of the static HTML + Carbon prototype (FXO ideal path) |
| Related | [`architecture.md`](architecture.md) (mock API, clock) · [`modelling-decisions.md`](modelling-decisions.md) (trade shape) · [`flows/fxo-ideal-path.md`](flows/fxo-ideal-path.md) (story map → steps) |

## 1. Sitemap

```text
CDU-PS (shell 00) ── SIMULATION banner · global search · theme · user menu (Assistant ◌ Coming soon)
├── Trades  /trades                                      01 Ops desk  (default landing)
│   ├── ?status=…&mca=…&q=…                              filtered queue (from MIS, queue strip, search)
│   ├── /trades/{tradeId}                                trade drawer (summary, journey, letter modal)
│   │   └── /trades/{tradeId}/letter                     letter modal (W4 read mode)
│   └── /trades/{tradeId}/draft                          03 Manual draft  (only when status = ManualDraft)
├── Timeline  /timeline/{tradeId}                        04 FXO timeline  (◷ trades; stub for the rest)
├── MIS  /mis                                            05 MIS dashboard  (+ ◌ Coming soon panels)
└── Templates  /templates                                02 Template admin: package list
    └── /templates/{templateBundleId}                    package detail
        ├── #overview  #versions  #bindings  #audit      tabs
        ├── #versions/{version}                          version panel (change, validation, approval)
        └── activate modal                               (enabled when approval = APPROVED)
```

Routes are client-side hash routes in the static site (`#/trades/TR-FXO-001`), so deep links work without a server.

## 2. Navigation model

| Level | Pattern | Items | Notes |
| --- | --- | --- | --- |
| Global | Side nav (`md`+) / bottom tab bar (`sm`) | Trades · Timeline · MIS · Templates | Timeline and MIS are first-level items, not hidden inside a trade |
| Global | Header search | trade id, document id, counterparty | Enter on a trade id opens 01 with the drawer |
| Global | Sim clock banner | `SIMULATION · as of …` | Read-only; moves on activate / submit (architecture §5) |
| Local | Tabs | Template detail: Overview · Versions · Bindings · Audit | Dropdown on `sm` |
| Local | Drawer | Trade (01), timeline event (04) | Full-screen sheet on `sm` |
| Local | Modal | Activate (02), Submit (03), Letter (01) | Confirm steps only |
| Cross-link | Inline `→` links | Package link, Open timeline, Open draft, View timeline, MIS drill-downs | Every object id shown is a link to its home screen |
| Back | Breadcrumb + "Back to trades" | 02, 03, 04 | Browser back also works (hash routes) |

## 3. Entry points

| Entry | Lands on | Default object |
| --- | --- | --- |
| App load | 01 Ops desk | book as of 16:30Z, no filter |
| Nav **Timeline** | 04 Timeline | last viewed trade, else `TR-FXO-001` |
| Nav **MIS** | 05 MIS | FXO, Today |
| Nav **Templates** | 02 package list | `TB-FXO-DEL-2026-001` card |
| Ops desk drawer **Package →** | 02 package detail | Versions tab |
| Ops desk drawer **Open timeline** | 04 Timeline | that trade (only if `timelineAvailable`) |
| Ops desk drawer **Open draft** | 03 Manual draft | `TR-FXO-005` / `AR-FXO-005-01` |
| MIS KPI / aging bar / contagion row | 01 filtered | status / AffirmPending / Party B |
| Manual draft **View timeline** | 04 Timeline | `TR-FXO-005` |
| Global search | 01 + drawer | matched trade |

## 4. Screen inventory

| # | Screen | File | Primary actor | Main objects | Story map | APIs (read → write) |
| --- | --- | --- | --- | --- | --- | --- |
| 00 | Shell and navigation | [`screens/00-shell-nav.md`](screens/00-shell-nav.md) | all | book count, DRAFT count | entry for K1–K5 | `GET /trades`, `GET /templates` |
| 01 | Ops desk (trade queue + drawer) | [`screens/01-ops-desk.md`](screens/01-ops-desk.md) | Ops analyst | Trade, Document, AssemblyRun | K2, K3 | `GET /trades`, `GET /trades/{id}`, `GET /documents/{id}`, `GET /trades/{id}/timeline` |
| 02 | Template admin | [`screens/02-template-admin.md`](screens/02-template-admin.md) | Template admin | TemplatePackage, TemplateVersion, TemplateApproval, SelectionRule, AuditEvent | K1 | `GET /templates`, `GET /templates/{id}`, `GET /templates/{id}/versions/{version}`, `GET /templates/{id}/audit` → `POST /templates/{id}/activate` |
| 03 | Manual draft | [`screens/03-manual-draft.md`](screens/03-manual-draft.md) | Ops analyst | AssemblyRun, Exhibit I letter, ManualDraftContent | K2 F2c, K3 F3a | `GET /assemblies/{id}`, `GET /assemblies/{id}/shell` → `PUT /assemblies/{id}/manual-draft`, `POST /assemblies/{id}/submit` |
| 04 | FXO timeline | [`screens/04-fxo-timeline.md`](screens/04-fxo-timeline.md) | Ops analyst / lead | TimelineEvent, AuditEvent | K5 F5a | `GET /trades/{id}/timeline`, `GET /trades/{id}`, `GET /audit` |
| 05 | MIS dashboard | [`screens/05-mis-dashboard.md`](screens/05-mis-dashboard.md) | MIS lead | KPIs, aging, contagion, error queue | K5 F5b | `GET /analytics/summary`, `GET /analytics/aging`, `GET /analytics/contagion`, `GET /analytics/queues/errors` |

## 5. Object model as seen in the UI

What a user can see, how each object is labelled, and which screen is its home. Field names follow [`modelling-decisions.md`](modelling-decisions.md).

```text
TemplatePackage "2026 FXO Deliverable (II-B)" (TB-FXO-DEL-2026-001)        home: 02
 ├─ TemplateVersion 1.0.0 RETIRED · 1.1.0 LIVE→RETIRED · 1.2.0 DRAFT→LIVE
 │   ├─ layers: Exhibit I (tops and tails, productInsert → II-B) + Exhibit II-B
 │   ├─ changes[], validation
 │   └─ approval (four-eyes): requestedBy → approvedBy ≠ activator · AuditEvent
 └─ SelectionRule PSR-FXO-DEL-2026-001 (NEW_TRADE → package)

Trade TR-FXO-00n                                                            home: 01 (drawer)
 ├─ parties: Party A (SCB desk) · Party B (counterparty)   ← shown as names; buyer/seller as "Party A/B"
 ├─ product: Deliverable FX Option · buyer → Party A · seller → Party B
 ├─ economics: option type, notional, strike, expiry, premium
 ├─ documentation: master agreement · master confirmation (MCA) or "None (long-form)" · 2026 FX Definitions 1.0
 ├─ status (Received … Affirmed) · mcaPath (derived) · timelineAvailable ◷
 ├─ AssemblyRun AR-FXO-00n-01 (mode, pinned template version)               home: 03 when manual
 ├─ Document DOC-00n → SmartDX SDX-DOC-00n → Exhibit I letter               home: 01 letter modal
 └─ Timeline (lanes TPs · CDU-PS · SmartDX · Counterparty) → AuditEvent     home: 04

Book (6 trades) → MIS aggregates (derived, never stored)                    home: 05
```

| UI object | Label pattern | Identifier shown | Home screen | Also appears on |
| --- | --- | --- | --- | --- |
| Template package | package name + LIVE chip | `TB-FXO-DEL-2026-001` | 02 | 00 badge, 01 drawer, 03 header, 04 header |
| Template version | `v1.2.0` + status chip + approval chip | `TV-I-2026-1.2.0` (layer) | 02 Versions | 01 drawer, 03 "pinned", 04 nodes |
| Approval | `(● APPROVED) u.ctrl.ng · time` | `AUD-0007` | 02 version panel | 02 Audit tab, activate modal |
| Trade | trade id + Party B name | `TR-FXO-001` | 01 | 03, 04, 05 drill-downs |
| Party | name (Party A / Party B role) | LEI | 01 drawer | 03 letter, 05 contagion |
| Master confirmation | `MCA-…` or "None (long-form ISDA 2002)" | `MCA-SCB-ACME-2026-001` | 01 drawer | 04 header, 03 letter agreement clause |
| Assembly run | run id + mode | `AR-FXO-005-01` | 03 | 01 drawer |
| Document / letter | doc id + SmartDX id | `DOC-001`, `SDX-DOC-001` | 01 letter modal | 04 node links, 03 submit result |
| Timeline event | action + lane + time | `TL-01-09` | 04 | 01 journey rail |
| Audit event | action + actor + time | `AUD-0109` | 04 drawer, 02 Audit tab | — |
| Coming soon feature | title + `(◌ Coming soon)` | — | where it would live | — |

## 6. Labelling rules

Every status, MCA path and audit action uses the shared [display-label map](system/components.md#display-label-map-h2). API / Excel keep the codes; the UI never prints a raw code.

- **Party labels.** The UI shows party names. In letter text and II-B General Terms it says "Party A" / "Party B", which is how ISDA writes them. Raw ids (`partyA`) never appear.
- **MCA.** The UI shows "With MCA · MCA-SCB-ACME-2026-001" or "Without MCA · long-form ISDA 2002". `mcaPath` is a filter value (API code), not a field users edit.
- **Product insert.** The letter canvas labels the block "Exhibit II-B — Confirmation of a Deliverable FX Option Transaction (from trade)".
- **Versions.** Versions are written `v1.2.0`. Layer ids (`TV-…`) are secondary text.
- **Times.** Times are UTC with a `Z` suffix. The sim banner shows `SIMULATION · [scenario ▾] · as of …` ([`architecture.md`](architecture.md) §5).
- **Trade vs assembly status.** Trade headers always show the trade status ("Manual draft"). Assembly status (`PENDING_MANUAL_DRAFT`) is secondary text only.

## Examples

| Field | File | Path | Value |
| --- | --- | --- | --- |
| Nav Trades badge | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `count` | `6` |
| Package name | `prototype/data/templates/index.json` | `items[0].packageName` | `2026 FXO Deliverable (II-B)` |
| Approval on version | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `approval.approvedBy` | `u.ctrl.ng` |
| Trade with timeline | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[4].timelineAvailable` | `true` |
| Party B in drawer | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `parties[id=partyB].partyName` | `ACME Corp Treasury` |

## EDGE / STUB

- There are no routes for exception queues (Rejected, ChannelError, Unmatched), Compare X or Swoosh inbound. They would sit under **Trades** as filters, with a future **Exceptions** nav item.
- No user/role admin, sign-in or notifications centre. The four-eyes approver has no screen yet (approval workflow `(◌ Coming soon)`).
- Multi-product navigation (product switcher in the header) is a STUB; FXO is the only product.
- The sim-clock step picker is a STUB.

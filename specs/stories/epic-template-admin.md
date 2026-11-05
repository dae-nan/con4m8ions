# Epic: Template admin — view LIVE package, activate DRAFT

| Item | Value |
| --- | --- |
| Story map | PRD §9.3 K1 Define templates → S1 Activate LIVE package |
| Feature spec | [`specs/features/template-admin.md`](../features/template-admin.md) (behaviours 1, 2, 5) |
| Screen | [`docs/design/screens/02-template-admin.md`](../../docs/design/screens/02-template-admin.md) |
| Simulation | flow A, steps A01–A12 ([`docs/design/flows/fxo-ideal-path.md`](../../docs/design/flows/fxo-ideal-path.md)) |
| Package | `TB-FXO-DEL-2026-001` "2026 FXO Deliverable (II-B)" |

Examples tables are checked by `scripts/check_prototype_sync.py`: each `File` + `Path` must resolve to `Value`.

## Story TA-1 — See the LIVE package and its versions (F1b Configure mapping)

As a template admin I want to see which package version is LIVE and which is waiting, so that I know what new trades will use.

```gherkin
Given the template admin u.admin.lee is signed in
When they open Templates and select package TB-FXO-DEL-2026-001
Then GET /templates/{id} returns the package with version 1.1.0 LIVE
And the versions list shows 1.0.0 RETIRED, 1.1.0 LIVE and 1.2.0 DRAFT
And the Bindings tab shows selection rule PSR-FXO-DEL-2026-001 and the II-B field paths
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| package name | `prototype/data/templates/fxo-deliverable-2026/package.json` | `packageName` | `2026 FXO Deliverable (II-B)` |
| LIVE version | `prototype/data/templates/fxo-deliverable-2026/package.json` | `version` | `1.1.0` |
| row 1 | `prototype/data/templates/fxo-deliverable-2026/package.json` | `versions[0].status` | `RETIRED` |
| row 2 | `prototype/data/templates/fxo-deliverable-2026/package.json` | `versions[1].status` | `LIVE` |
| row 3 | `prototype/data/templates/fxo-deliverable-2026/package.json` | `versions[2].status` | `DRAFT` |
| one package for both MCA paths | `prototype/data/templates/fxo-deliverable-2026/package.json` | `mcaRequired` | `false` |
| selection rule | `prototype/data/templates/fxo-deliverable-2026/selection-rules.json` | `items[0].businessEvent` | `NEW_TRADE` |
| II-B premium path | `prototype/data/templates/fxo-deliverable-2026/exhibit-ii-b-product.json` | `fields[15].tpsJsonPath` | `trade.economics.premiumAmount` |

## Story TA-2 — Review a validated DRAFT version (F1a Draft version)

As a template admin I want to see what changed in DRAFT 1.2.0 and that it passed validation, so that I can activate it with confidence.

```gherkin
Given DRAFT 1.2.0 was added with PUT /templates/{id}/versions on 2027-11-28 (audit AUD-0005)
And CDU-PS validated it (audit AUD-0006)
When the admin selects version 1.2.0
Then GET /templates/{id}/versions/{version} shows one change to the Party A notice line
And validation status is PASSED
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| request change log | `prototype/data/inbound/ui/TB-FXO-DEL-2026-001.put-version-1.2.0.json` | `changeLog` | `Exhibit I notices: add SmartDX Docbox as Party A notice channel` |
| created as DRAFT | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/01-put-versions.201.json` | `status` | `DRAFT` |
| create audit | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/01-put-versions.201.json` | `auditId` | `AUD-0005` |
| change attribute | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `changes[0].attribute` | `Contact details for notice Party A` |
| change after | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `changes[0].after` | `ops-fx@scb.example; SmartDX Docbox SCB-SG` |
| validation | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `validation.status` | `PASSED` |
| new Exhibit I layer | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `layers[0].templateVersionId` | `TV-I-2026-1.2.0` |
| II-B layer unchanged | `prototype/data/templates/fxo-deliverable-2026/versions/1.2.0.json` | `layers[1].templateVersionId` | `TV-IIB-2026-1.1.0` |

## Story TA-3 — Activate DRAFT 1.2.0 with an audit trail (F1c Audit activate)

As a template admin I want to activate 1.2.0 with a reason, so that new trades use it and the change is audited.

```gherkin
Given package TB-FXO-DEL-2026-001 has 1.1.0 LIVE and 1.2.0 DRAFT with validation PASSED
When the admin confirms POST /templates/{id}/activate for 1.2.0 with reason PLANNED_RELEASE at 2027-12-01T16:00:00Z
Then 1.2.0 becomes LIVE and 1.1.0 becomes RETIRED and the rollback target
And GET /templates/{id}/audit gains AUD-0007 template.activated 1.1.0 → 1.2.0
And trades booked before 16:00Z keep version 1.1.0
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| request version | `prototype/data/inbound/ui/TB-FXO-DEL-2026-001.activate-1.2.0.json` | `version` | `1.2.0` |
| request reason | `prototype/data/inbound/ui/TB-FXO-DEL-2026-001.activate-1.2.0.json` | `reason` | `PLANNED_RELEASE` |
| new LIVE | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` | `status` | `LIVE` |
| previous LIVE | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` | `previousLiveVersion` | `1.1.0` |
| rollback target | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` | `rollbackTargetVersion` | `1.1.0` |
| audit id | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/02-post-activate.200.json` | `auditId` | `AUD-0007` |
| after: 1.1.0 | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/03-get-template.after-activate.200.json` | `versions[1].status` | `RETIRED` |
| after: 1.2.0 | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/03-get-template.after-activate.200.json` | `versions[2].status` | `LIVE` |
| audit action | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/04-get-template-audit.after-activate.200.json` | `items[6].action` | `template.activated` |
| audit after version | `prototype/data/outbound/api-responses/TB-FXO-DEL-2026-001/04-get-template-audit.after-activate.200.json` | `items[6].afterVersion` | `1.2.0` |
| TR-FXO-001 stays pinned | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `template.templateVersion` | `1.1.0` |

## Out of scope (EDGE / STUB)

Create package, rollback (`POST /templates/{id}/rollback`), hot-swap + resend ([`specs/scenarios/hot-swap-resend.md`](../scenarios/hot-swap-resend.md)), four-eyes approval.

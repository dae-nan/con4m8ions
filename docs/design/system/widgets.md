# Widgets — composite patterns

| Item | Value |
| --- | --- |
| Status | Phase 2 design pack — draft for review |
| Depends on | [`tokens.md`](tokens.md) · [`components.md`](components.md) |
| Class names | [`stylesheet.md`](stylesheet.md) §3 |

Widgets are built only from [`components.md`](components.md) glyphs. Each lists the data shape it reads; shapes are defined by [`specs/api/openapi.md`](../../../specs/api/openapi.md) and sample files under [`prototype/data/`](../../../prototype/data/).

## W1. Queue strip

Status counts across the top of the ops desk. Click a segment to filter the trade table.

```text
┌──────────┬───────────┬────────────┬──────────┬───────────────┬──────────┐
│ Received │ Composing │ ManualDraft│ Sent     │ AffirmPending │ Affirmed │
│    1     │     1     │     1      │    0     │       1       │    2     │
└──────────┴───────────┴────────────┴──────────┴───────────────┴──────────┘
```

- Reads `GET /trades` → `counts` object (keys are trade status enums, PRD §13.2).
- Segment underline uses the status tone. Zero counts stay visible (ideal path: no hidden states).
- Below `md`: horizontal scroll strip. Class `.cdu-queue-strip`.

## W2. Package card

Summary of one TemplatePackage; used in template list and in trade detail ("which package?").

```text
┌──────────────────────────────────────────────────────────┐
│ 2026 FXO Deliverable (II-B)               (● LIVE 1.1.0) │
│ TB-FXO-DEL-2026-001                                      │
│ Exhibit I EXH-I-2026-v1 + II-B · Supplements none        │
│ Defs 2026 · MCA optional · Resend MANUAL · Hot reload on │
│ Draft waiting: 1.2.0                          → Open     │
└──────────────────────────────────────────────────────────┘
```

- Reads `GET /templates/{id}` (TemplatePackage). Class `.cdu-package-card`.

## W3. Timeline rail (per-trade swimlane)

SmartDX-inspired horizontal swimlane; one lane per actor; one node per TimelineEvent.

```text
           10:00:00    10:00:01    10:00:02    10:00:03    10:00:04    10:00:05        15:04:05   15:04:06
TPs        ●─────────────────────────────────────────────────────────────── ● ack ─────────────────── ● ack
CDU-PS                 ● DQ ──────● legal ── ● package ── ● assembled
                                    ● ──────────────────────────────── ● sent
SmartDX                                                                ● generated
Counterpty                                                                               ● affirmed
```

- Reads `GET /trades/{id}/timeline` → `events[]` with `lane`, `at`, `action`, `status`, `documentId`, `templateVersion`.
- Node tone = tone of `status` after the event. Hover/focus node → tooltip with `actor`, `auditId`.
- Below `md`: rotates to a **vertical** list (one row per event, lane as a chip). Class `.cdu-timeline`.

## W4. Letter canvas

Exhibit I letter (“tops and tails”) with the II-B insert, block by block (PRD §4).

```text
┌─ Letter canvas ─ DOC-001 · TB-FXO-DEL-2026-001 v1.1.0 ─────────────────────┐
│ ▸ Heading       Standard Chartered Bank Sample Desk · 2027-12-01           │
│                 ACME Corp Treasury, 1 Example Street, London EC2N 1HQ      │
│ ▸ Definitions   2026 FX Definitions Main Book Version 1.0                  │
│ ▸ Agreement     ISDA Master Agreement dated 15 January 2026 (MCA …)        │
│ ┌ Insert ─ Exhibit II-B ──────────────────────────────────────────────┐    │
│ │ Option Style European · Option Type EUR Call / USD Put             │    │
│ │ Call EUR 1,000,000 · Strike 1.0850 · Expiry 2027-12-31 10:00 NY     │    │
│ └──────────────────────────────────────────────────────────────────────┘    │
│ ▸ Elections     LEI A 5493001KJTIIGC8Y1R12 · LEI B 549300ABCDEFGH123456    │
│ ▸ Closing       Supersession + please confirm                              │
└────────────────────────────────────────────────────────────────────────────┘
```

- Read mode: reads `exhibitILetter.blocks` (SmartDX payload / `GET /documents/{id}`).
- Edit mode (manual draft): each `▸` block becomes an editable region `✎`; reads `GET /assemblies/{id}/shell`.
- Font `letter-body`; gutter `layer-02`. Class `.cdu-letter`.

## W5. KPI tile

```text
┌──────────────────────┐
│ Affirm rate (FXO)    │
│ 66.7%                │   value: heading-04
│ 2 of 3 sent          │   context: label-01
└──────────────────────┘
```

- Reads `GET /analytics/summary`. `brand-secondary` 4px top bar. Class `.cdu-kpi`.

## W6. Aging bars

```text
AffirmPending age   0-1h            0
                    1-4h  ██████████ 1
                    4-24h           0
                    >24h            0
```

- Reads `GET /analytics/aging` → `buckets[]`. Bar tone = `progress`. Class `.cdu-aging`.

## W7. Audit list

```text
┌─────────────────────┬──────────────┬───────────────────────────┬─────────────┐
│ At (UTC)            │ Actor        │ Action                    │ Version     │
├─────────────────────┼──────────────┼───────────────────────────┼─────────────┤
│ 2027-11-28 09:00:00 │ u.admin.lee  │ template.version_added    │ — → 1.2.0   │
└─────────────────────┴──────────────┴───────────────────────────┴─────────────┘
```

- Reads `GET /templates/{id}/audit` or `GET /audit?tradeId=` → AuditEvent rows (PRD §7 minimum fields). Class `.cdu-audit`.

## W8. Field palette (manual entry — STUB)

Drag-drop AttributeDefinition list for manual mode (b). Named here so screens can reference it; **not drawn** in this PR (EDGE/STUB in [`03-manual-draft.md`](../screens/03-manual-draft.md)).

## EDGE / STUB

- W3 exception markers (Unmatched, ChannelError, Compare X gate) — STUB.
- W4 diff view (Compare X side-by-side) — STUB.
- W8 field palette — STUB.

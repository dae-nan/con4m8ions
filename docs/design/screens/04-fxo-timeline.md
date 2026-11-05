# 04 — FXO trade timeline

| Item | Value |
| --- | --- |
| Status | Phase 2 wireframe — ideal path — draft for review |
| Design system | [`components`](../system/components.md) §3, §4, §6, §9 · [`widgets`](../system/widgets.md) W3, W7 |
| Story map (PRD §9.3) | **K5 Observe** → S5 Timeline and queues → F5a Per-trade timeline · shows markers for **K2** F2a Locate package, F2b Prepare MCA and DQ, F2c Auto or manual draft and **K3** F3a Channel send, F3b Callback TPs, F3c Affirm webhook |
| Data | `prototype/data/timeline/TR-FXO-001.json` · `prototype/data/timeline/TR-FXO-005.json` · `prototype/data/timeline/audit-events.json` · `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` · `prototype/data/outbound/api-responses/book/get-trades.200.json` (picker, `timelineAvailable`) |
| APIs | `GET /trades/{id}/timeline` · `GET /trades/{id}` · `GET /trades` · `GET /audit` |
| PRD | §12.1 per-trade timeline, §7 audit |
| Flow | [`../flows/fxo-ideal-path.md`](../flows/fxo-ideal-path.md) flow B |

## 1. Goal

Answer "where is this confirm and who touched it?" in one view: SmartDX-inspired swimlanes from TPs receipt to affirm callback, every node backed by an AuditEvent.

**Non-goals:** cross-trade timelines (see MIS), editing anything, exception overlays.

## 2. Actors

Ops confirm analyst · Ops lead · (Phase 3: agent tool reads the same API).

## 3. Entry / exit

| From | To | Trigger |
| --- | --- | --- |
| Shell **Timeline** ([`00`](00-shell-nav.md)) | this screen, last trade (default `TR-FXO-001`) | nav |
| Ops desk drawer **Open timeline** ([`01`](01-ops-desk.md)) | this screen for that trade | click |
| Manual draft **View timeline** ([`03`](03-manual-draft.md)) | this screen for `TR-FXO-005` | link |
| Node `documentId` link | letter modal (W4 read mode) | click |
| Header **Back to trades** | [`01-ops-desk.md`](01-ops-desk.md) | click |

## 4. Layout — desktop

```text
 Timeline / TR-FXO-001                           Trade [TR-FXO-001 ▾]                         ‹ Back to trades ›
 TR-FXO-001 · ACME Corp Treasury · EUR Call / USD Put · EUR 1,000,000      (● Affirmed)
 TB-FXO-DEL-2026-001 v1.1.0 · DOC-001 · SDX-DOC-001 · With_MCA MCA-SCB-ACME-2026-001

┌─ Swimlanes ── 2027-12-01 (UTC) ───────────────────────────────────────────────────────────────────────────────┐
│             10:00:00   :01      :02       :02       :03        :04       :04       :05     ┊  15:04:05  15:04:06 │
│ TPs         ●Received ───────────────────────────────────────────────────────────── ●ack  ┊ ─────────── ●ack     │
│ CDU-PS                 ●DQ ── ●legal ── ●package ── ●assembled ── ●sent               ┊                     │
│ SmartDX                                                                   ●generated   ┊                     │
│ Counterparty                                                                           ┊  ●affirmed           │
│                                                                                 (time axis compressed at ┊)  │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────┬──────────────┬────────────────────┬────────────────┬─────────┬─────────┬──────────┐  ║ TL-01-09                [✕] ║
│ #        │ At (UTC)             │ Lane         │ Action             │ Status after   │ Doc     │ Version │ Audit    │  ║ affirm.affirmed             ║
├──────────┼──────────────────────┼──────────────┼────────────────────┼────────────────┼─────────┼─────────┼──────────┤  ║ (● Affirmed)                ║
│ TL-01-01 │ 2027-12-01 10:00:00  │ TPs          │ trade.received     │ (○ Received)   │ —       │ —       │ AUD-0101 │  ║ ─────────────────────────── ║
│ TL-01-02 │ 2027-12-01 10:00:01  │ CDU-PS       │ trade.dq_passed    │ (● Composing)  │ —       │ —       │ AUD-0102 │  ║ At      2027-12-01 15:04:05 ║
│ TL-01-03 │ 2027-12-01 10:00:02  │ CDU-PS       │ legal.resolved     │ (● Composing)  │ —       │ —       │ AUD-0103 │  ║ Actor   svc.affirm-webhook  ║
│ TL-01-04 │ 2027-12-01 10:00:02  │ CDU-PS       │ package.located    │ (● Composing)  │ —       │ 1.1.0   │ AUD-0104 │  ║ Lane    Counterparty        ║
│ TL-01-05 │ 2027-12-01 10:00:03  │ CDU-PS       │ assembly.completed │ (● Composing)  │ DOC-001 │ 1.1.0   │ AUD-0105 │  ║ Doc     DOC-001 →           ║
│ TL-01-06 │ 2027-12-01 10:00:04  │ CDU-PS       │ document.sent      │ (● Sent)       │ DOC-001 │ 1.1.0   │ AUD-0106 │  ║ Event   evt_1001            ║
│ TL-01-07 │ 2027-12-01 10:00:04  │ SmartDX      │ document.created   │ (● AffirmPend…)│ DOC-001 │ 1.1.0   │ AUD-0107 │  ║ Audit   AUD-0109            ║
│ TL-01-08 │ 2027-12-01 10:00:05  │ TPs          │ callback.sent      │ (● AffirmPend…)│ DOC-001 │ 1.1.0   │ AUD-0108 │  ║ Detail  Affirmed, 0         ║
│▌TL-01-09 │ 2027-12-01 15:04:05  │ Counterparty │ affirm.affirmed    │ (● Affirmed)   │ DOC-001 │ 1.1.0   │ AUD-0109 │  ║         differences         ║
│ TL-01-10 │ 2027-12-01 15:04:06  │ TPs          │ callback.sent      │ (● Affirmed)   │ DOC-001 │ 1.1.0   │ AUD-0110 │  ║                             ║
└──────────┴──────────────────────┴──────────────┴────────────────────┴────────────────┴─────────┴─────────┴──────────┘
```

- Lanes come from `lanes[]`; nodes are placed by `at`; gaps over 1 hour collapse to `┊` with the real times shown.
- Selecting a node or a row opens the event drawer; both stay in sync.
- `TR-FXO-005` renders the same way with `assembly.manual_started` / `manual_saved` / `manual_submitted` nodes in the `attention` tone.
- The header's MCA reads `documentation.masterConfirmation.masterConfirmationId` (derived path `mcaPath`).

### 4.1 Trade without a simulated timeline (picker, `timelineAvailable = false`)

The picker lists all six book trades and marks the two with a timeline with `◷`. Choosing any other trade shows the book row and a stub instead of lanes. No call is made to `GET /trades/{id}/timeline`, because the mock API would return 404.

```text
 Timeline / TR-FXO-006                           Trade [TR-FXO-006 ▾]                         ‹ Back to trades ›
   ◷ TR-FXO-001 · ◷ TR-FXO-005 · TR-FXO-002 · TR-FXO-003 · TR-FXO-004 · ▌TR-FXO-006        (picker list)
 TR-FXO-006 · Initech Treasury Ltd · USD Call / JPY Put · USD 5,000,000      (● Affirmed)
 TB-FXO-DEL-2026-001 v1.1.0 · DOC-106 · Without_MCA · sent 09:00:04Z · affirmed 11:30:00Z
┌ ◌ Timeline ───────────────────────────────────────────────────────────────── (◌ Coming soon) ┐
│ This trade has no simulated timeline in the prototype. Key times above come from the trade   │
│ book. Simulated timelines: TR-FXO-001, TR-FXO-005.            ‹ Open TR-FXO-001 timeline ›   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 5. Layout — iPhone (`sm`)

```text
┌──────────────────────────────┐
│ TR-FXO-001     (● Affirmed)  │
│ [TR-FXO-001 ▾]               │
├──────────────────────────────┤
│ 15:04:06 TPs                 │
│ callback.sent  (● Affirmed)  │
│ 15:04:05 Counterparty        │
│ affirm.affirmed (● Affirmed) │
│ 10:00:05 TPs                 │
│ callback.sent (● AffirmPend…)│
│ …                            │
└──────────────────────────────┘
```

Vertical list, newest first, lane shown as a label (widgets W3 small-screen rule).

## 6. Interaction (ideal path)

1. Opens with `GET /trades/TR-FXO-001` (header) and `GET /trades/TR-FXO-001/timeline` (lanes + events).
2. Analyst scans lanes: received → DQ → legal (With_MCA) → package v1.1.0 → assembled → sent → SmartDX generated → TPs ack → affirmed → affirm ack.
3. Clicks the affirm node → drawer with actor, audit id, detail.
4. Switches trade via the picker → `TR-FXO-005` shows the manual draft markers.

## 7. Component inventory

| Element | Component / widget | Class |
| --- | --- | --- |
| Page header + trade picker | components §9, §2 dropdown | `.cdu-page-header` |
| Swimlanes | W3 | `.cdu-timeline` |
| Event table | components §4 | `.cdu-table` |
| Event drawer | components §6 + §11 | `.cdu-drawer`, `.cdu-kv` |
| Status chips | components §3 | `.cdu-chip--{status}` |

## 8. Data bindings

| UI label | File | JSON path | Example |
| --- | --- | --- | --- |
| Lanes | `prototype/data/timeline/TR-FXO-001.json` | `lanes[3]` | `Counterparty` |
| Header status | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `status` | `Affirmed` |
| Header doc | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `currentDocumentId` | `DOC-001` |
| Row 1 action | `prototype/data/timeline/TR-FXO-001.json` | `events[0].action` | `trade.received` |
| Row 4 version | `prototype/data/timeline/TR-FXO-001.json` | `events[3].templateVersion` | `1.1.0` |
| Row 6 status | `prototype/data/timeline/TR-FXO-001.json` | `events[5].status` | `Sent` |
| Row 7 lane | `prototype/data/timeline/TR-FXO-001.json` | `events[6].lane` | `SmartDX` |
| Drawer id | `prototype/data/timeline/TR-FXO-001.json` | `events[8].timelineEventId` | `TL-01-09` |
| Drawer actor | `prototype/data/timeline/TR-FXO-001.json` | `events[8].actor` | `svc.affirm-webhook` |
| Drawer audit | `prototype/data/timeline/TR-FXO-001.json` | `events[8].auditId` | `AUD-0109` |
| Drawer detail | `prototype/data/timeline/TR-FXO-001.json` | `events[8].detail` | `Affirmed, 0 differences` |
| Last row action | `prototype/data/timeline/TR-FXO-001.json` | `events[9].action` | `callback.sent` |
| TR-FXO-005 manual marker | `prototype/data/timeline/TR-FXO-005.json` | `events[4].action` | `assembly.manual_started` |
| TR-FXO-005 manual saved by | `prototype/data/timeline/TR-FXO-005.json` | `events[5].actor` | `u.ops.tan` |
| Header MCA | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `documentation.masterConfirmation.masterConfirmationId` | `MCA-SCB-ACME-2026-001` |
| Picker TR-FXO-006 has timeline | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[5].timelineAvailable` | `false` |
| Stub TR-FXO-006 sent at | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[5].sentAt` | `2027-12-01T09:00:04Z` |
| Stub TR-FXO-006 affirmed at | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[5].affirmedAt` | `2027-12-01T11:30:00Z` |

## 9. API calls

| When | Call | File |
| --- | --- | --- |
| Open | `GET /trades/TR-FXO-001` | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` |
| Open | `GET /trades/TR-FXO-001/timeline` | `prototype/data/timeline/TR-FXO-001.json` |
| Open (picker) | `GET /trades` | `prototype/data/outbound/api-responses/book/get-trades.200.json` |
| Switch trade | `GET /trades/TR-FXO-005/timeline` | `prototype/data/timeline/TR-FXO-005.json` |
| Drawer "full audit" | `GET /audit?tradeId=TR-FXO-001` | `prototype/data/timeline/audit-events.json` (filter client-side in the prototype) |

## EDGE / STUB

- Exception markers (Unmatched, Disputed, Compare X gate, ChannelError, Rejected) and retry nodes — STUB (E3, E4, E7, E8).
- Later lifecycle events (AMEND, NOVATION, EXERCISE) and supersession chains (`priorDocumentId`) — STUB.
- Timelines for `TR-FXO-002`, `-003`, `-004`, `-006` — not simulated (`timelineAvailable = false`); the screen shows the §4.1 `(◌ Coming soon)` stub with book times.
- Export timeline as PDF — STUB.

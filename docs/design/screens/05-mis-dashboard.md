# 05 — MIS dashboard

| Item | Value |
| --- | --- |
| Status | Phase 2 wireframe — ideal path — draft for review |
| Design system | [`components`](../system/components.md) §3, §4, §9, §10 · [`widgets`](../system/widgets.md) W1, W5, W6 |
| Story map (PRD §9.3) | **K5 Observe** → S5 Timeline and queues → F5b Aging contagion errors · links to F5a Per-trade timeline |
| Data | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` · `prototype/data/outbound/api-responses/analytics/get-aging.200.json` · `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` · `prototype/data/outbound/api-responses/analytics/get-errors.200.json` · `prototype/data/outbound/api-responses/book/get-trades.200.json` |
| APIs | `GET /analytics/summary` · `GET /analytics/aging` · `GET /analytics/contagion` · `GET /analytics/queues/errors` · `GET /trades` |
| PRD | §12 MIS and observability, §12.2 contagion |
| Flow | [`../flows/fxo-ideal-path.md`](../flows/fxo-ideal-path.md) flow D |

## 1. Goal

The ops lead sees, for the FXO book today, how much came in, how much is affirmed, what is ageing and whether any counterparty is concentrating risk — and can drill from any number into the trades behind it.

**Non-goals:** custom report builder, multi-product rollups, historical trend charts.

## 2. Actors

Ops lead / MIS `u.mis.lead` · Ops confirm analyst (read).

## 3. Entry / exit

| From | To | Trigger |
| --- | --- | --- |
| Shell **MIS** ([`00`](00-shell-nav.md)) | this screen | nav |
| Queue strip / KPI click | [`01-ops-desk.md`](01-ops-desk.md) filtered by status | click |
| Aging bar click | [`01-ops-desk.md`](01-ops-desk.md) filtered AffirmPending | click |
| Contagion row click | [`01-ops-desk.md`](01-ops-desk.md) filtered by Party B | click |
| Median KPI ⓘ | [`04-fxo-timeline.md`](04-fxo-timeline.md) for `TR-FXO-001` (sample) | link |

All numbers are derived from the book (`scripts/prototype_sim.py` `analytics_from_book`), so the dashboard and the ops desk always agree.

## 4. Layout — desktop

```text
 MIS · Deliverable FX Option · 2027-12-01 00:00Z → 16:30Z                 Product [FXO ▾]  Window [Today ▾]
┌───────────────┬───────────────┬───────────────┬───────────────┬───────────────┬───────────────┐
│ Received      │ Sent          │ Affirmed      │ Affirm rate   │ Error rate    │ Median new →  │
│      6        │      3        │      2        │    66.7 %     │    0.0 %      │ affirmed      │
│               │               │               │ of sent       │               │  227 min  ⓘ   │
└───────────────┴───────────────┴───────────────┴───────────────┴───────────────┴───────────────┘
 Queue  Received 1 · Validating 0 · Composing 1 · ManualDraft 1 · Sent 0 · AffirmPending 1 · Affirmed 2

┌─ Aging (from sent) ─────────────────────────────┐ ┌─ Counterparty contagion · threshold 3 open ────────────────┐
│ AffirmPending                                   │ │ Party B               │ Trades │ Open │ Unm. │ Err │ Flag │
│   0-1h   ·                              0       │ ├───────────────────────┼────────┼──────┼──────┼─────┼──────┤
│   1-4h   ████████████████████           1       │ │ ACME Corp Treasury    │   2    │  1   │  0   │  0  │  —   │
│   4-24h  ·                              0       │ │ Globex Holdings Ltd   │   2    │  2   │  0   │  0  │  —   │
│   >24h   ·                              0       │ │ Initech Treasury Ltd  │   2    │  1   │  0   │  0  │  —   │
│ Unmatched                                       │ └────────────────────────────────────────────────────────────┘
│   all buckets                           0       │ ┌─ Error queue ──────────────────────────────────────────────┐
└─────────────────────────────────────────────────┘ │ ✓ No errors in window                                      │
                                                    └────────────────────────────────────────────────────────────┘
 As of 2027-12-01T16:30:00Z · refreshed with the book
```

## 5. Layout — iPhone (`sm`)

KPI tiles become a 2-column grid (6 tiles, 3 rows); queue strip scrolls horizontally; aging, contagion and errors stack as cards. Contagion table keeps Party B, Open, Flag columns only.

## 6. Interaction (ideal path)

1. Ops lead opens **MIS** from the shell; five calls load in parallel (`GET /analytics/summary`, `/aging`, `/contagion`, `/queues/errors`, `GET /trades` for counts).
2. Reads: 6 received, 3 sent, 2 affirmed (66.7 % of sent), 1 manual draft in progress, no errors.
3. Clicks the **1-4h** AffirmPending bar → ops desk filtered to `TR-FXO-002`.
4. Back to MIS, clicks **Globex Holdings Ltd** (2 open, below threshold 3) → ops desk filtered to `TR-FXO-005`, `TR-FXO-002`.

## 7. Component inventory

| Element | Component / widget | Class |
| --- | --- | --- |
| Header + filters | components §9, §2 | `.cdu-page-header` |
| KPI tiles | W5 | `.cdu-kpi` |
| Queue strip | W1 | `.cdu-queue-strip` |
| Aging bars | W6 | `.cdu-aging` |
| Contagion table | components §4 (compact) | `.cdu-table--compact` |
| Empty error queue | components §10 (empty state) | `.cdu-empty` |

## 8. Data bindings

| UI label | File | JSON path | Example |
| --- | --- | --- | --- |
| Window to | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `window.to` | `2027-12-01T16:30:00Z` |
| KPI Received | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `volumes.received` | `6` |
| KPI Sent | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `volumes.sent` | `3` |
| KPI Affirmed | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `volumes.affirmed` | `2` |
| KPI Affirm rate | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `affirmRate` | `0.6667` |
| KPI Error rate | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `errorRate` | `0.0` |
| KPI Median minutes | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `medianNewToAffirmedMinutes` | `227.0` |
| Queue ManualDraft | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.ManualDraft` | `1` |
| Queue Affirmed | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.Affirmed` | `2` |
| Aging AffirmPending 1-4h | `prototype/data/outbound/api-responses/analytics/get-aging.200.json` | `series[0].buckets[1].count` | `1` |
| Aging measured from | `prototype/data/outbound/api-responses/analytics/get-aging.200.json` | `series[0].measuredFrom` | `sentAt` |
| Contagion threshold | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` | `threshold` | `3` |
| Contagion row 2 name | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` | `items[1].partyBName` | `Globex Holdings Ltd` |
| Contagion row 2 open | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` | `items[1].open` | `2` |
| Contagion row 2 flag | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` | `items[1].flagged` | `false` |
| Error count | `prototype/data/outbound/api-responses/analytics/get-errors.200.json` | `count` | `0` |

Affirm rate renders as a percentage with one decimal (`0.6667` → `66.7 %`).

## 9. API calls

| When | Call | File |
| --- | --- | --- |
| Open | `GET /analytics/summary?productType=Deliverable_FX_Option` | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` |
| Open | `GET /analytics/aging` | `prototype/data/outbound/api-responses/analytics/get-aging.200.json` |
| Open | `GET /analytics/contagion` | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` |
| Open | `GET /analytics/queues/errors` | `prototype/data/outbound/api-responses/analytics/get-errors.200.json` |
| Open | `GET /trades` | `prototype/data/outbound/api-responses/book/get-trades.200.json` |

## EDGE / STUB

- Flagged contagion state (open ≥ threshold) and alerting — STUB; no counterparty reaches 3 in the sample book.
- Non-empty error queue (ChannelError, DQ failures) — STUB (E7, E8).
- Unmatched / Disputed aging with real counts — STUB (E3, E4).
- Window picker beyond Today, CSV export, multi-product — STUB.
- Agent "explain this number" panel — Phase 3.

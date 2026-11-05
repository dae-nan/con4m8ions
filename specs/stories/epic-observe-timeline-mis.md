# Epic: Observe — per-trade timeline and MIS

| Item | Value |
| --- | --- |
| Story map | PRD §9.3 K5 Observe → S5 Timeline and queues → F5a Per-trade timeline, F5b Aging contagion errors |
| PRD | §12 MIS and observability |
| Screens | [`00-shell-nav`](../../docs/design/screens/00-shell-nav.md) · [`01-ops-desk`](../../docs/design/screens/01-ops-desk.md) · [`04-fxo-timeline`](../../docs/design/screens/04-fxo-timeline.md) · [`05-mis-dashboard`](../../docs/design/screens/05-mis-dashboard.md) |
| Simulation | flow B step B15, flow C step C11, flow D steps D01–D06; book = Excel `Prototype_Trade_Book` at 2027-12-01T16:30:00Z |

Examples tables are checked by `scripts/check_prototype_sync.py`: each `File` + `Path` must resolve to `Value`.

## Story OB-1 — Find any trade from the shell (entry points)

As an ops analyst I want Trades, Timeline and MIS one click from anywhere, so that I never hunt for a view.

```gherkin
Given u.ops.tan is on any CDU-PS screen
When they open Trades from the shell
Then GET /trades lists 6 FXO trades with counts per status
And Timeline and MIS are first-level nav items
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| trade count | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `count` | `6` |
| first row | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[0].tradeId` | `TR-FXO-004` |
| Received | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.Received` | `1` |
| Composing | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.Composing` | `1` |
| ManualDraft | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.ManualDraft` | `1` |
| AffirmPending | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.AffirmPending` | `1` |
| Affirmed | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.Affirmed` | `2` |

## Story OB-2 — See one trade's journey across systems (F5a Per-trade timeline)

As an ops analyst I want a swimlane timeline for a trade, with every node tied to an audit event, so that I can answer "where is it and who touched it?".

```gherkin
Given TR-FXO-001 has been affirmed
When the analyst opens GET /trades/{id}/timeline for TR-FXO-001
Then lanes are TPs, CDU-PS, SmartDX and Counterparty
And 10 events run from trade.received at 10:00:00Z to callback.sent at 15:04:06Z
And each event carries the audit id recorded by GET /audit
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| lane 1 | `prototype/data/timeline/TR-FXO-001.json` | `lanes[0]` | `TPs` |
| lane 3 | `prototype/data/timeline/TR-FXO-001.json` | `lanes[2]` | `SmartDX` |
| first event | `prototype/data/timeline/TR-FXO-001.json` | `events[0].action` | `trade.received` |
| first event at | `prototype/data/timeline/TR-FXO-001.json` | `events[0].at` | `2027-12-01T10:00:00Z` |
| package node version | `prototype/data/timeline/TR-FXO-001.json` | `events[3].templateVersion` | `1.1.0` |
| affirm node lane | `prototype/data/timeline/TR-FXO-001.json` | `events[8].lane` | `Counterparty` |
| affirm node audit | `prototype/data/timeline/TR-FXO-001.json` | `events[8].auditId` | `AUD-0109` |
| last event at | `prototype/data/timeline/TR-FXO-001.json` | `events[9].at` | `2027-12-01T15:04:06Z` |

```gherkin
Given TR-FXO-005 was finished by manual draft
When the analyst opens its timeline
Then the manual draft nodes appear between package.located and document.sent
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| manual start | `prototype/data/timeline/TR-FXO-005.json` | `events[4].action` | `assembly.manual_started` |
| manual start status | `prototype/data/timeline/TR-FXO-005.json` | `events[4].status` | `ManualDraft` |
| saved | `prototype/data/timeline/TR-FXO-005.json` | `events[5].action` | `assembly.manual_saved` |
| submitted | `prototype/data/timeline/TR-FXO-005.json` | `events[6].action` | `assembly.manual_submitted` |
| sent | `prototype/data/timeline/TR-FXO-005.json` | `events[7].action` | `document.sent` |

## Story OB-3 — Read today's FXO numbers (F5b Aging contagion errors)

As an ops lead I want volumes, affirm rate, aging and counterparty concentration from the same book the desk sees, so that I can act before cut-off.

```gherkin
Given the FXO book at 2027-12-01T16:30:00Z holds 6 trades
When u.mis.lead opens MIS
Then GET /analytics/summary shows 6 received, 3 sent, 2 affirmed, affirm rate 0.6667 and median 227 minutes new → affirmed
And GET /analytics/aging shows 1 AffirmPending trade in the 1-4h bucket
And GET /analytics/contagion flags no counterparty at threshold 3
And GET /analytics/queues/errors is empty
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| received | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `volumes.received` | `6` |
| sent | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `volumes.sent` | `3` |
| affirmed | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `volumes.affirmed` | `2` |
| manual draft | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `volumes.manualDraft` | `1` |
| affirm rate | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `affirmRate` | `0.6667` |
| median minutes | `prototype/data/outbound/api-responses/analytics/get-summary.200.json` | `medianNewToAffirmedMinutes` | `227.0` |
| aging 1-4h | `prototype/data/outbound/api-responses/analytics/get-aging.200.json` | `series[0].buckets[1].count` | `1` |
| threshold | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` | `threshold` | `3` |
| Globex open | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` | `items[1].open` | `2` |
| Globex flagged | `prototype/data/outbound/api-responses/analytics/get-contagion.200.json` | `items[1].flagged` | `false` |
| errors | `prototype/data/outbound/api-responses/analytics/get-errors.200.json` | `count` | `0` |

MIS numbers are derived from the book by `analytics_from_book` in `scripts/prototype_sim.py`; the sync check fails if they drift from the book.

## Out of scope (EDGE / STUB)

Flagged contagion and alerts, non-empty error queues, Unmatched / Disputed aging, history windows and export, agent explanations (Phase 3).

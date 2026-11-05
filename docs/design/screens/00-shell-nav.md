# 00 — Shell and navigation

| Item | Value |
| --- | --- |
| Status | Phase 2 wireframe — ideal path — draft for review |
| Design system | [`tokens`](../system/tokens.md) · [`components`](../system/components.md) · [`widgets`](../system/widgets.md) · [`stylesheet`](../system/stylesheet.md) |
| Story map (PRD §9.3) | Entry points for every kite: K1 Define templates · K2 Book and assemble · K3 Send and match · **K5 Observe** (S5 Timeline and queues → F5a Per-trade timeline, F5b Aging contagion errors) |
| Data | `prototype/data/outbound/api-responses/book/get-trades.200.json` · `prototype/data/templates/index.json` |
| APIs | `GET /trades` · `GET /templates` |

## 1. Goal

One frame that makes every job reachable in one click: the **Trades** desk (default), **Timeline**, **MIS**, and **Templates** admin. Timeline and MIS must be first-class nav items, not buried inside a trade.

**Non-goals:** user/role admin, notifications centre, Phase 3 assistant.

## 2. Actors

Ops confirm analyst (default landing: Trades) · Template admin (Templates) · MIS lead (MIS) · Ops lead (Timeline).

## 3. Entry / exit

| From | To | Trigger |
| --- | --- | --- |
| App load | [`01-ops-desk.md`](01-ops-desk.md) | Default route `/trades` |
| Nav **Timeline** | [`04-fxo-timeline.md`](04-fxo-timeline.md) | Opens last viewed trade, default `TR-FXO-001`; trade picker in page header |
| Nav **MIS** | [`05-mis-dashboard.md`](05-mis-dashboard.md) | Route `/mis` |
| Nav **Templates** | [`02-template-admin.md`](02-template-admin.md) | Route `/templates` |
| Global search hit on a trade id | 01 with drawer open | Enter in search |

## 4. Layout — desktop (`lg` and up)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ▣ CDU-PS  Confirmations      [⌕ Search trade, doc, counterparty_______]   SIMULATION · as of 16:30Z  ◐  (UT) │  header (brand-navy)
├────────────────┬─────────────────────────────────────────────────────────────────────────────────────┤
│ ═ Trades     6 │                                                                                     │
│   Timeline     │                                                                                     │
│   MIS          │                   page content (01–05)                                              │
│ ────────────── │                                                                                     │
│   Templates  1 │                                                                                     │
│                │                                                                                     │
│                │                                                                                     │
│ ────────────── │                                                                                     │
│ ? Help         │                                                                                     │
└────────────────┴─────────────────────────────────────────────────────────────────────────────────────┘
```

- `═` marks the active nav item. Badge on **Trades** = trade count; badge on **Templates** = versions waiting in DRAFT.
- `◐` theme toggle (light/dark, [`tokens.md`](../system/tokens.md) §7). `(UT)` user menu.
- `SIMULATION · as of …` banner always visible while the prototype replays `prototype/data/`.

## 5. Layout — iPhone (`sm`, < 672px)

```text
┌──────────────────────────────┐
│ ▣ CDU-PS          ⌕   ◐  (UT)│
│ SIMULATION · as of 16:30Z    │
├──────────────────────────────┤
│                              │
│      page content            │
│      (single column)         │
│                              │
├──────────────────────────────┤
│ ═Trades  Timeline  MIS  Tmpl │  bottom tab bar (.cdu-shell__tabbar)
│   6                      1   │
└──────────────────────────────┘
```

## 6. Interaction (ideal path)

1. Analyst lands on **Trades** (01) with queue strip and table.
2. Clicks **Timeline** → 04 opens `TR-FXO-001`; the page-header trade picker switches trade.
3. Clicks **MIS** → 05; any tile or bar links back to 01 with that filter applied.
4. Admin clicks **Templates** → 02 package list.

## 7. Component inventory

| Element | Component / widget | Class |
| --- | --- | --- |
| Header | components §9 (page header) on navy bar | `.cdu-shell__header` |
| Global search | components §10 | `.cdu-filter-bar` |
| Side nav | Carbon `SideNav` rail | `.cdu-shell__nav` |
| Bottom tab bar | custom | `.cdu-shell__tabbar` |
| Badges | Carbon `Tag` size `sm`, tone `neutral` | `.cdu-chip--received` (neutral) |

## 8. Data bindings

| UI label | File | JSON path | Example |
| --- | --- | --- | --- |
| Trades badge | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `count` | `6` |
| Simulation as-of | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `asOf` | `2027-12-01T16:30:00Z` |
| Templates badge (DRAFT versions) | `prototype/data/templates/index.json` | `items[0].versions[2].status` | `DRAFT` |
| Timeline default trade | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[4].tradeId` | `TR-FXO-001` |

## 9. API calls

| When | Call |
| --- | --- |
| Shell mount | `GET /trades` (badge, as-of) · `GET /templates` (DRAFT badge) |

## EDGE / STUB

- Error badge on **Trades** for Rejected / ChannelError counts — STUB (E4, E8).
- Session expiry, role-based nav hiding — STUB.
- Phase 3 assistant entry — out of scope.

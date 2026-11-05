# 01 — Ops desk (trade queue)

| Item | Value |
| --- | --- |
| Status | Phase 2 wireframe — ideal path — draft for review |
| Design system | [`components`](../system/components.md) §3–§6, §10–§11 · [`widgets`](../system/widgets.md) W1, W2, W3 |
| Story map (PRD §9.3) | **K2 Book and assemble** → S2 Assemble FXO letter → F2a Locate package, F2b Prepare MCA and DQ, F2c Auto or manual draft · **K3 Send and match** → S3 SmartDX then affirm → F3a Channel send, F3b Callback TPs, F3c Affirm webhook (status only) |
| Data | `prototype/data/outbound/api-responses/book/get-trades.200.json` · `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` · `prototype/data/outbound/api-responses/TR-FXO-001/07-get-document.200.json` · `prototype/data/timeline/TR-FXO-001.json` |
| APIs | `GET /trades` · `GET /trades/{id}` · `GET /documents/{id}` · `GET /trades/{id}/timeline` |
| Flow | [`../flows/fxo-ideal-path.md`](../flows/fxo-ideal-path.md) flow B + D |

## 1. Goal

The analyst sees every FXO trade of the day by status, opens one, and confirms in seconds that the **right package** was used, the **letter went to SmartDX**, **TPs got the callback** and the counterparty **affirmed** — without opening another system.

**Non-goals:** editing trades (TPs owns them), channel controls (SmartDX is status-only here), exceptions.

## 2. Actors

Ops confirm analyst (primary) · Ops lead (read).

## 3. Entry / exit

| From | To | Trigger |
| --- | --- | --- |
| Shell **Trades** / app load ([`00`](00-shell-nav.md)) | this screen | — |
| MIS tile or bar ([`05`](05-mis-dashboard.md)) | this screen, filtered | click |
| Row `TR-FXO-005` (Manual draft) | [`03-manual-draft.md`](03-manual-draft.md) | drawer **Open draft** |
| Drawer **Open timeline** | [`04-fxo-timeline.md`](04-fxo-timeline.md) | click |
| Drawer **Package** link | [`02-template-admin.md`](02-template-admin.md) | click |

## 4. Layout — desktop (`xlg`, drawer docked)

```text
 Trades · Deliverable FX Options                                             as of 2027-12-01 16:30Z
┌──────────┬───────────┬────────────┬──────────┬───────────────┬──────────┐
│ Received │ Composing │ Manual draft│ Sent    │ Affirm pending│ Affirmed │      View MIS →
│    1     │     1     │     1      │    0     │       1       │    2     │
└──────────┴───────────┴────────────┴──────────┴───────────────┴──────────┘
 [⌕ Search trade, doc, counterparty___]  Status [All ▾]  MCA [All ▾]  Date [2027-12-01 ▾]

┌────────────┬──────────────────────┬─────────────┬────────────────────┬────────────┬────────────────┬─────────┬────┐  ║ TR-FXO-001                            [✕] ║
│ Trade ID   │ Counterparty         │ MCA         │ Option             │ Notional   │ Status         │ Doc     │ TL │  ║ ACME Corp Treasury · With MCA             ║
├────────────┼──────────────────────┼─────────────┼────────────────────┼────────────┼────────────────┼─────────┼────┤  ║ (● Affirmed)        affirmed 15:04:05Z    ║
│ TR-FXO-004 │ Initech Treasury Ltd │ Without MCA │ AUD Call / USD Put │ AUD 4.0m   │ (○ Received)   │ —       │    │  ║ ───────────────────────────────────────── ║
│ TR-FXO-003 │ ACME Corp Treasury   │ With MCA    │ EUR Put / USD Call │ EUR 3.0m   │ (● Composing)  │ —       │    │  ║ Package    TB-FXO-DEL-2026-001 v1.1.0 →   ║
│ TR-FXO-005 │ Globex Holdings Ltd  │ Without MCA │ EUR Call / USD Put │ EUR 2.5m   │ (● Manual draft)│ —       │ ◷  │  ║ Assembly   AR-FXO-001-01 · AUTOMATED      ║
│ TR-FXO-002 │ Globex Holdings Ltd  │ Without MCA │ GBP Call / USD Put │ GBP 2.0m   │ (● Affirm pending)│ DOC-102 │    │  ║ Document   DOC-001 · SmartDX SDX-DOC-001  ║
│▌TR-FXO-001 │ ACME Corp Treasury   │ With MCA    │ EUR Call / USD Put │ EUR 1.0m   │ (● Affirmed)      │ DOC-001 │ ◷  │  ║ MCA        MCA-SCB-ACME-2026-001          ║
│ TR-FXO-006 │ Initech Treasury Ltd │ Without MCA │ USD Call / JPY Put │ USD 5.0m   │ (● Affirmed)   │ DOC-106 │    │  ║ ───────────────────────────────────────── ║
└────────────┴──────────────────────┴─────────────┴────────────────────┴────────────┴────────────────┴─────────┴────┘  ║ Economics (II-B)                          ║
  1–6 of 6                                                                                      ‹ Prev  Next ›        ║ Strike 1.0850 · Expiry 2027-12-31 10:00 NY║
                                                                                                                        ║ Premium USD 15000 pay 2027-12-03          ║
                                                                                                                        ║ ───────────────────────────────────────── ║
                                                                                                                        ║ Journey  ●──●──●──●──●──●──●──● ── ●──●   ║
                                                                                                                        ║ Received  →  Sent 10:00:04  →  Affirmed   ║
                                                                                                                        ║ TPs ack 10:00:05 · affirm ack 15:04:06    ║
                                                                                                                        ║                                           ║
                                                                                                                        ║  ‹ View letter ›    [▶ Open timeline]     ║
```

- Below `xlg` the drawer overlays the table; below `md` it is a full-screen sheet with a back arrow.
- Default sort: `receivedAt` descending. Notional = `callCurrency` + `callCurrencyAmount` formatted (`1000000` → `1.0m`).
- **View letter** opens the letter canvas (widgets W4, read mode) in a modal from `GET /documents/{id}`.
- For a Manual draft row the drawer primary button reads **[▶ Open draft]** instead of Open timeline.
- Status and MCA chips use the [display-label map](../system/components.md#display-label-map-h2) (`ManualDraft` → "Manual draft", `With_MCA` → "With MCA"). Filter dropdown values stay as API codes.
- **TL** column: `◷` = the trade has a simulated timeline (`timelineAvailable = true`: `TR-FXO-001`, `TR-FXO-005`). Filter "Has timeline" sits in the filter bar overflow `⋯`.
- Drawer **MCA** shows `documentation.masterConfirmation.masterConfirmationId`, or "None (long-form ISDA 2002)" when it is `null`. Party B and Buyer/Seller come from `parties[]` + `product` party references ([`modelling-decisions.md`](../modelling-decisions.md)).
- Drawer for a trade without a timeline (`TR-FXO-006` shown): the journey rail is replaced by a stub (components §12).

```text
 ║ TR-FXO-006 · Initech Treasury Ltd · Without MCA ║
 ║ (● Affirmed)           affirmed 11:30:00Z        ║
 ║ ─────────────────────────────────────────────── ║
 ║ ┌ ◌ Timeline ───────────── (◌ Coming soon) ┐    ║
 ║ │ No simulated timeline for this trade.    │    ║
 ║ │ Book fields only in this prototype.      │    ║
 ║ └──────────────────────────────────────────┘    ║
 ║  ‹ View letter › (◌ Coming soon)                ║
```

## 5. Layout — iPhone (`sm`)

```text
┌──────────────────────────────┐
│ Trades            16:30Z     │
│ ‹Rcv 1›‹Cmp 1›‹Man 1›‹Aff 2›→│  queue strip scrolls
│ [⌕ Search___________]        │
├──────────────────────────────┤
│ TR-FXO-001      (● Affirmed) │
│ ACME Corp Treasury · EUR 1.0m│
│ DOC-001 · 15:04Z             │
├──────────────────────────────┤
│ TR-FXO-005   (● Manual draft) │
│ Globex Holdings Ltd · EUR 2.5m│
└──────────────────────────────┘
```

## 6. Interaction (ideal path)

1. Screen loads `GET /trades`; queue strip shows counts per status, table lists 6 trades.
2. Analyst clicks **Affirmed** in the strip (optional) → table filters to `TR-FXO-001`, `TR-FXO-006`.
3. Clicks `TR-FXO-001` → drawer loads `GET /trades/{id}` and `GET /documents/{id}`; journey mini-rail uses `GET /trades/{id}/timeline`.
4. Analyst checks package v1.1.0, DOC-001, both TPs callbacks → **Open timeline** for detail (04), or closes the drawer.
5. Analyst clicks `TR-FXO-005` → **Open draft** → 03.

## 7. Component inventory

| Element | Component / widget | Class |
| --- | --- | --- |
| Queue strip | W1 | `.cdu-queue-strip` |
| Filter bar | components §10 | `.cdu-filter-bar` |
| Trade table | components §4, compact | `.cdu-table` |
| Status chips | components §3 | `.cdu-chip--{status}` |
| Detail drawer | components §6 + §11 | `.cdu-drawer`, `.cdu-kv` |
| Journey mini-rail | W3 condensed (one lane) | `.cdu-timeline` |
| Letter modal | components §7 + W4 | `.cdu-modal`, `.cdu-letter` |

## 8. Data bindings

| UI label | File | JSON path | Example |
| --- | --- | --- | --- |
| Queue Received | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.Received` | `1` |
| Queue Composing | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.Composing` | `1` |
| Queue ManualDraft | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.ManualDraft` | `1` |
| Queue AffirmPending | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.AffirmPending` | `1` |
| Queue Affirmed | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `counts.Affirmed` | `2` |
| Row 5 Trade ID | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[4].tradeId` | `TR-FXO-001` |
| Row 5 Counterparty | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[4].partyBName` | `ACME Corp Treasury` |
| Row 5 Notional amount | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[4].callCurrencyAmount` | `1000000` |
| Row 5 Status | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[4].status` | `Affirmed` |
| Row 3 Status | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[2].status` | `ManualDraft` |
| Row 2 Template version | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[1].templateVersion` | `1.2.0` |
| Drawer Package | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `template.templateBundleId` | `TB-FXO-DEL-2026-001` |
| Drawer Package version | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `template.templateVersion` | `1.1.0` |
| Drawer Assembly | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `assemblyRunId` | `AR-FXO-001-01` |
| Drawer Document | `prototype/data/outbound/api-responses/TR-FXO-001/07-get-document.200.json` | `documentId` | `DOC-001` |
| Drawer SmartDX id | `prototype/data/outbound/api-responses/TR-FXO-001/07-get-document.200.json` | `smartdxDocumentId` | `SDX-DOC-001` |
| Drawer MCA | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `documentation.masterConfirmation.masterConfirmationId` | `MCA-SCB-ACME-2026-001` |
| Drawer MCA path (derived) | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `mcaPath` | `With_MCA` |
| Drawer Party B | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `parties[id=partyB].partyName` | `ACME Corp Treasury` |
| Drawer Buyer | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `product.buyerPartyReference.href` | `partyA` |
| Row 5 has timeline | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[4].timelineAvailable` | `true` |
| Row 6 has timeline | `prototype/data/outbound/api-responses/book/get-trades.200.json` | `items[5].timelineAvailable` | `false` |
| Drawer Strike | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `economics.strikePrice` | `1.0850` |
| Drawer Premium | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `economics.premiumAmount` | `15000` |
| Drawer Sent at | `prototype/data/timeline/TR-FXO-001.json` | `events[5].at` | `2027-12-01T10:00:04Z` |
| Drawer TPs ack | `prototype/data/timeline/TR-FXO-001.json` | `events[7].at` | `2027-12-01T10:00:05Z` |
| Drawer Affirmed at | `prototype/data/timeline/TR-FXO-001.json` | `events[8].at` | `2027-12-01T15:04:05Z` |

## 9. API calls

| When | Call | Response file |
| --- | --- | --- |
| Load | `GET /trades?from=2027-12-01` | `prototype/data/outbound/api-responses/book/get-trades.200.json` |
| Row click | `GET /trades/TR-FXO-001` | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` |
| Row click | `GET /documents/DOC-001` | `prototype/data/outbound/api-responses/TR-FXO-001/07-get-document.200.json` |
| Row click | `GET /trades/TR-FXO-001/timeline` | `prototype/data/timeline/TR-FXO-001.json` |

## EDGE / STUB

- Rejected / ChannelError / Unmatched / Disputed rows, error chips and retry actions — STUB (E3, E4, E7, E8).
- Resend / supersede action in drawer — STUB (E1 hot-swap resend).
- Bulk select, export CSV — STUB.
- Detail for trades without sim files (`TR-FXO-002`, `-003`, `-004`, `-006`) shows book fields only, a Timeline `(◌ Coming soon)` stub and a disabled View letter; full drawer data exists for `TR-FXO-001` and `TR-FXO-005`.

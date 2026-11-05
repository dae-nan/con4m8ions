# Components — ASCII glyph catalog

| Item | Value |
| --- | --- |
| Status | Phase 2 design pack — draft for review |
| Depends on | [`tokens.md`](tokens.md) |
| Class names | [`stylesheet.md`](stylesheet.md) §3 |

Every screen in [`../screens/`](../screens/) draws components **only** with the glyphs below, so a prototype agent can map each glyph to one Carbon component and one CSS class.

## 1. Buttons

```text
[▶ Activate 1.2.0]     primary      Carbon Button kind=primary     .cdu-btn--primary
[ Save draft ]         secondary    Carbon Button kind=secondary   .cdu-btn--secondary
‹ Cancel ›             ghost        Carbon Button kind=ghost       .cdu-btn--ghost
[⋯]                    overflow     Carbon OverflowMenu            .cdu-btn--icon
```

Rules: one primary per view region; primary sits right-most in a button group; destructive actions are EDGE (not drawn).

## 2. Fields

```text
Label                              read-only value (code-01 for ids)
Trade ID         TR-FXO-001

Label                              editable text input
Reason           [PLANNED_RELEASE_________]

Label                              dropdown
Status           [LIVE            ▾]

Label                              checkbox / toggle
Hot reload       [x] enabled      ( ●○ ) toggle on
```

- `____` = empty editable space; `▾` = dropdown; `[x]` / `[ ]` = checkbox.
- Label column width 16 chars in ASCII ≈ 128px. Required fields mark label with `*`.

## 3. Status chip and display-label map

```text
(● Affirmed)   (● Affirm pending)   (● Manual draft)   (● LIVE)   (○ DRAFT)
```

- `●` filled = current/terminal state; `○` hollow = not yet active (DRAFT, RETIRED).
- Tone comes from [`tokens.md`](tokens.md) §1.3. Carbon `Tag` size `sm`. Class `.cdu-chip--{kebab}` from the map below (never from a raw enum string).

### Display-label map (H2)

One shared map. **API / Excel keep the codes; the UI never prints a raw code.** Import as `labels.js` in the prototype. Trade-level headers always use the trade-status row; assembly status is secondary text only. Timeline table rows use the sentence; the code stays in the event drawer.

| Kind | Code (API) | Label | Tone | Chip class | Sentence (timeline / audit) |
| --- | --- | --- | --- | --- | --- |
| Trade status | `Received` | Received | neutral | `.cdu-chip--received` | Trade received |
| Trade status | `Validating` | Validating | info | `.cdu-chip--validating` | Validating |
| Trade status | `Composing` | Composing | info | `.cdu-chip--composing` | Composing |
| Trade status | `ManualDraft` | Manual draft | attention | `.cdu-chip--manual-draft` | Waiting for manual draft |
| Trade status | `Sent` | Sent | progress | `.cdu-chip--sent` | Sent |
| Trade status | `AffirmPending` | Affirm pending | progress | `.cdu-chip--affirm-pending` | Affirm pending |
| Trade status | `Affirmed` | Affirmed | success | `.cdu-chip--affirmed` | Affirmed |
| Assembly | `ASSEMBLING` | Assembling | info | `.cdu-chip--assembling` | Assembly in progress |
| Assembly | `PENDING_MANUAL_DRAFT` | Pending manual draft | attention | `.cdu-chip--pending-manual-draft` | Pending manual draft |
| Assembly | `COMPLETED` | Completed | success | `.cdu-chip--completed` | Assembly completed |
| Assembly mode | `AUTOMATED` | Automated | — | — | Automated |
| Assembly mode | `MANUAL_DRAFTING` | Manual drafting | — | — | Manual drafting |
| Template | `DRAFT` | DRAFT | neutral | `.cdu-chip--draft` | — |
| Template | `LIVE` | LIVE | success | `.cdu-chip--live` | — |
| Template | `RETIRED` | RETIRED | neutral | `.cdu-chip--retired` | — |
| Approval | `APPROVED` | APPROVED | success | `.cdu-chip--approved` | Template approved |
| Approval | `PENDING` | Pending approval | attention | `.cdu-chip--pending-approval` | Approval requested |
| MCA path | `With_MCA` | With MCA | — | — | — |
| MCA path | `Without_MCA` | Without MCA | — | — | — |
| Audit / timeline action | `trade.received` | — | — | — | Trade received |
| Audit / timeline action | `trade.dq_passed` | — | — | — | DQ passed |
| Audit / timeline action | `legal.resolved` | — | — | — | Legal resolved |
| Audit / timeline action | `package.located` | — | — | — | Package located |
| Audit / timeline action | `assembly.completed` | — | — | — | Assembly completed |
| Audit / timeline action | `assembly.manual_started` | — | — | — | Manual draft started |
| Audit / timeline action | `assembly.manual_saved` | — | — | — | Manual draft saved |
| Audit / timeline action | `assembly.manual_submitted` | — | — | — | Manual draft submitted |
| Audit / timeline action | `document.sent` | — | — | — | Document sent |
| Audit / timeline action | `document.created` | — | — | — | Document created in SmartDX |
| Audit / timeline action | `callback.sent` | — | — | — | Callback sent to TPs |
| Audit / timeline action | `affirm.affirmed` | — | — | — | Counterparty affirmed |
| Audit / timeline action | `template.approved` | — | — | — | Template approved |
| Audit / timeline action | `template.activated` | — | — | — | Template activated |
| Audit / timeline action | `template.validated` | — | — | — | Template validated |
| Audit / timeline action | `template.version_added` | — | — | — | Template version added |
| Audit / timeline action | `template.created` | — | — | — | Template created |

Rules: never show `partyA` / `partyB` ids (use party names, or "Party A" / "Party B" in letter text). Never show `PENDING_MANUAL_DRAFT` on a trade header — show **Manual draft**. Truncation is forbidden for Affirm pending and Manual draft; widen the column instead.

## 4. Data table

```text
┌────────────┬──────────────────────┬───────────────┬──────────┐
│ Trade ID ↓ │ Counterparty         │ Status        │ Doc      │   header: heading-compact-01, sortable ↓/↑
├────────────┼──────────────────────┼───────────────┼──────────┤
│ TR-FXO-001 │ ACME Corp Treasury   │ (● Affirmed)  │ DOC-001  │   row: compact 32px
│▌TR-FXO-005 │ Globex Holdings Ltd  │ (● ManualDra…)│ —        │   ▌ = selected row (brand-primary left bar)
└────────────┴──────────────────────┴───────────────┴──────────┘
  1–6 of 6                                       ‹ Prev  Next ›   pagination (Carbon Pagination)
```

Carbon `DataTable` with `size="sm"`, sticky header, row click opens detail drawer.

## 5. Tabs

```text
 Overview   Versions   Bindings   Audit
═════════                                   active tab underline (brand-primary)
```

Carbon `Tabs` (line). Class `.cdu-tabs`.

## 6. Drawer (detail side panel)

```text
                         ║ TR-FXO-001                          [✕] ║
                         ║ ─────────────────────────────────────── ║
                         ║ … content …                             ║
                         ║                                         ║
                         ║            ‹ Close ›  [▶ Open timeline] ║
```

`║` edges = drawer. Docks right at `xlg`; full-screen sheet below `md`. Class `.cdu-drawer`.

## 7. Modal (confirm step)

```text
        ╔══════════════════════════════════════════════╗
        ║ Activate version 1.2.0?                      ║
        ║ ──────────────────────────────────────────── ║
        ║ body text                                    ║
        ║                       ‹ Cancel ›  [▶ Confirm]║
        ╚══════════════════════════════════════════════╝
```

Carbon `Modal` size `sm`. Used only for activate and submit on the ideal path.

## 8. Notification

```text
 ┃ ✓ Version 1.2.0 is LIVE. New trades use it from 2027-12-01T16:00:00Z.   [✕]
```

`┃` left bar coloured by tone (`success` here). Carbon `InlineNotification` / `ToastNotification`. Error/warning variants are EDGE.

## 9. Breadcrumb and page header

```text
 Templates / 2026 FXO Deliverable (II-B)
 2026 FXO Deliverable (II-B)                    (● LIVE 1.1.0)   [▶ Activate 1.2.0]
 TB-FXO-DEL-2026-001 · Exhibit I + II-B · Defs 2026
```

## 10. Search and filter bar

```text
 [⌕ Search trade, doc, counterparty______]  Status [All ▾]  MCA [All ▾]  Date [2027-12-01 ▾]
```

## 11. Key–value list

```text
 Template version   1.1.0          Assembly mode   AUTOMATED
 Document           DOC-001        SmartDX doc     SDX-DOC-001
```

Two-column grid of §2 read-only fields; collapses to one column below `md`.

## 12. Coming soon stub

Marks a feature that is designed but not built in the prototype (approval workflow, unsimulated timelines, AI and future MIS features). It never pretends to work.

```text
 ┌ ◌ Explain this number ─────────────────────── (◌ Coming soon) ┐
 │ An assistant will explain how this KPI is derived from the     │
 │ trade book. Not available in this prototype.                   │
 └────────────────────────────────────────────────────────────────┘
 Inline form:   ‹ Request approval ›  (◌ Coming soon)
```

- The chip `(◌ Coming soon)` uses tone `neutral`, a dashed outline and no hover state.
- Controls inside the stub are rendered `disabled` with `aria-disabled="true"`, and the chip text is in the accessible name, e.g. "Request approval, coming soon".
- The panel form has a title, one sentence of what it will do, and no fake data.
- Carbon: `Tag` (type `outline`) for the chip and `Tile` for the panel.

## 13. Glyph legend (quick reference)

| Glyph | Meaning |
| --- | --- |
| `┌─┐ │ └─┘` | Container / card / table frame |
| `║` | Drawer edge |
| `╔═╗` | Modal |
| `▌` | Selected row |
| `═══` | Active tab / active nav item |
| `(● X)` `(○ X)` | Status chip |
| `[▶ X]` `[ X ]` `‹ X ›` | Primary / secondary / ghost button |
| `▾` | Dropdown |
| `⌕` | Search |
| `⋯` | Overflow menu |
| `→` | Navigation to another screen (target named next to it) |
| `{…}` | Value bound from prototype data (see each screen's Data bindings table) |
| `(◌ Coming soon)` · `┌ ◌ … ┐` | Coming soon chip / stub panel (§12) |
| `◷` | Trade has a simulated timeline (`timelineAvailable`) |

## EDGE / STUB

- Destructive button (`danger` kind), error notification, inline field error, skeleton loaders — STUB.
- Multi-select batch actions on tables — STUB.

# Design tokens — CDU-PS ops desk

| Item | Value |
| --- | --- |
| Status | Phase 2 design pack — draft for review |
| Basis | IBM Carbon v11 tokens (g10 light / g100 dark) + SCB-approximate accent |
| Used by | Every file in [`../screens/`](../screens/) · CSS variables in [`stylesheet.md`](stylesheet.md) |

> SCB colours below are **approximate** brand-like values for an internal prototype, not official brand assets.

## 1. Colour

### 1.1 Brand accent (SCB-approximate)

| Token | Light (g10) | Dark (g100) | Use |
| --- | --- | --- | --- |
| `brand-primary` | `#0473EA` | `#4C9BFF` | Primary buttons, active nav, links, focus ring |
| `brand-secondary` | `#38D200` | `#5FE033` | Positive accent bar on KPI tiles only (never text) |
| `brand-navy` | `#0F1F3D` | `#0F1F3D` | Shell header background (both themes) |

### 1.2 Carbon roles (unchanged names)

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `background` | `#F4F4F4` | `#161616` | Page |
| `layer-01` | `#FFFFFF` | `#262626` | Cards, tables, drawers |
| `layer-02` | `#F4F4F4` | `#393939` | Nested panels, letter canvas gutter |
| `border-subtle` | `#E0E0E0` | `#393939` | Table rules, dividers |
| `text-primary` | `#161616` | `#F4F4F4` | Body |
| `text-secondary` | `#525252` | `#C6C6C6` | Labels, meta |
| `text-on-color` | `#FFFFFF` | `#FFFFFF` | On brand / navy |
| `focus` | `brand-primary` | `#FFFFFF` | 2px focus outline |

### 1.3 Status tones

One tone per status. Chips, timeline nodes and MIS bars use the **same** mapping.

| Tone | Light fg / bg | Dark fg / bg | Statuses (trade · assembly · template) |
| --- | --- | --- | --- |
| `neutral` | `#525252` / `#E0E0E0` | `#C6C6C6` / `#393939` | `Received` · `DRAFT` · `RETIRED` |
| `info` | `#0043CE` / `#D0E2FF` | `#78A9FF` / `#002D9C` | `Validating` · `Composing` · `ASSEMBLING` |
| `attention` | `#8A3FFC` / `#E8DAFF` | `#BE95FF` / `#491D8B` | `ManualDraft` · `PENDING_MANUAL_DRAFT` · `PENDING_DATA_ENTRY` |
| `progress` | `#005D5D` / `#9EF0F0` | `#3DDBD9` / `#004144` | `Sent` · `AffirmPending` |
| `success` | `#0E6027` / `#A7F0BA` | `#42BE65` / `#044317` | `Affirmed` · `COMPLETED` · `LIVE` |
| `danger` (EDGE) | `#A2191F` / `#FFD7D9` | `#FF8389` / `#750E13` | `Rejected` · `ChannelError` · `FAILED` |
| `warning` (EDGE) | `#8E6A00` / `#FCF4D6` | `#F1C21B` / `#3D3100` | `Unmatched` · `Disputed` · `CompareXGate` |

Status names are exact enum values from PRD §13.2 (trade), Excel `Logical_Data_Model` `AssemblyRun.status`, and `Template_Admin_Utility.status`.

## 2. Type

IBM Plex Sans for UI, IBM Plex Mono for ids, JSON paths, amounts.

| Token | Size / line | Weight | Use |
| --- | --- | --- | --- |
| `heading-04` | 28 / 36 | 400 | Page title |
| `heading-03` | 20 / 28 | 400 | Section / drawer title |
| `heading-02` | 16 / 24 | 600 | Card title |
| `heading-compact-01` | 14 / 18 | 600 | Table header, field label |
| `body-compact-01` | 14 / 18 | 400 | Default body, table cells |
| `label-01` | 12 / 16 | 400 | Meta, timestamps, chip text |
| `code-01` | 12 / 16 | 400 mono | `TR-FXO-001`, `DOC-001`, JSON paths |
| `letter-body` | 15 / 24 | 400 serif (IBM Plex Serif) | Exhibit I letter canvas only |

## 3. Spacing (Carbon scale, px)

`spacing-01`=2 · `02`=4 · `03`=8 · `04`=12 · `05`=16 · `06`=24 · `07`=32 · `08`=40 · `09`=48

ASCII convention: one character column ≈ 8px, one line ≈ 16–24px. Wireframes are proportional, not pixel exact.

## 4. Density

| Mode | Row height | Where |
| --- | --- | --- |
| `compact` (default ops) | 32px (Carbon `sm`) | Trade queue, audit list, MIS tables |
| `default` | 48px (Carbon `lg`) | Template admin version table, forms |
| `touch` | 48px min target | Any viewport < 672px (iPhone) |

## 5. Breakpoints and layout grid

| Name | Min width | Columns | Shell behaviour |
| --- | --- | --- | --- |
| `sm` | 320 | 4 | Side nav hidden; bottom tab bar (see [`00-shell-nav.md`](../screens/00-shell-nav.md)) |
| `md` | 672 | 8 | Side nav as overlay (hamburger) |
| `lg` | 1056 | 16 | Side nav rail pinned (icons + labels) |
| `xlg` | 1312 | 16 | Detail drawer docks beside table |
| `max` | 1584 | 16 | Content max width; centred |

## 6. Elevation and motion

- Flat by default. Drawers and modals use Carbon `shadow` only in light theme; dark uses `layer-02` contrast.
- Motion: Carbon `productive` easing, 110ms for chips/toggles, 240ms for drawers. Respect `prefers-reduced-motion`.

## 7. Theme toggle

- `data-theme="light" | "dark"` on `<html>`; default follows `prefers-color-scheme`; user choice persists in `localStorage` key `cdu.theme`.
- Shell header stays `brand-navy` in both themes.

## EDGE / STUB

- High-contrast theme — STUB (Carbon g90 later).
- `danger` / `warning` tones exist for edge states (E3, E7, E8 in PRD §10.4) but no ideal-path screen renders them.
- Right-to-left layout — not in scope.

# Stylesheet — CSS variables and class map

| Item | Value |
| --- | --- |
| Status | Phase 2 design pack — draft for review |
| Depends on | [`tokens.md`](tokens.md) · [`components.md`](components.md) · [`widgets.md`](widgets.md) |
| Not in this PR | Full app CSS. The prototype copies §1–§2 into `prototype/web/styles/tokens.css` |

## 1. CSS variables

```css
:root,
[data-theme="light"] {
  --cdu-brand-primary: #0473EA;
  --cdu-brand-secondary: #38D200;
  --cdu-brand-navy: #0F1F3D;
  --cdu-background: #F4F4F4;
  --cdu-layer-01: #FFFFFF;
  --cdu-layer-02: #F4F4F4;
  --cdu-border-subtle: #E0E0E0;
  --cdu-text-primary: #161616;
  --cdu-text-secondary: #525252;
  --cdu-text-on-color: #FFFFFF;
  --cdu-focus: #0473EA;

  --cdu-tone-neutral-fg: #525252;   --cdu-tone-neutral-bg: #E0E0E0;
  --cdu-tone-info-fg: #0043CE;      --cdu-tone-info-bg: #D0E2FF;
  --cdu-tone-attention-fg: #8A3FFC; --cdu-tone-attention-bg: #E8DAFF;
  --cdu-tone-progress-fg: #005D5D;  --cdu-tone-progress-bg: #9EF0F0;
  --cdu-tone-success-fg: #0E6027;   --cdu-tone-success-bg: #A7F0BA;
  --cdu-tone-danger-fg: #A2191F;    --cdu-tone-danger-bg: #FFD7D9;
  --cdu-tone-warning-fg: #8E6A00;   --cdu-tone-warning-bg: #FCF4D6;

  --cdu-font-sans: "IBM Plex Sans", system-ui, sans-serif;
  --cdu-font-mono: "IBM Plex Mono", ui-monospace, monospace;
  --cdu-font-serif: "IBM Plex Serif", Georgia, serif;

  --cdu-space-01: 2px;  --cdu-space-02: 4px;  --cdu-space-03: 8px;
  --cdu-space-04: 12px; --cdu-space-05: 16px; --cdu-space-06: 24px;
  --cdu-space-07: 32px; --cdu-space-08: 40px; --cdu-space-09: 48px;

  --cdu-row-compact: 32px;
  --cdu-row-default: 48px;
  --cdu-motion-fast: 110ms;
  --cdu-motion-panel: 240ms;
}

[data-theme="dark"] {
  --cdu-brand-primary: #4C9BFF;
  --cdu-brand-secondary: #5FE033;
  --cdu-background: #161616;
  --cdu-layer-01: #262626;
  --cdu-layer-02: #393939;
  --cdu-border-subtle: #393939;
  --cdu-text-primary: #F4F4F4;
  --cdu-text-secondary: #C6C6C6;
  --cdu-focus: #FFFFFF;

  --cdu-tone-neutral-fg: #C6C6C6;   --cdu-tone-neutral-bg: #393939;
  --cdu-tone-info-fg: #78A9FF;      --cdu-tone-info-bg: #002D9C;
  --cdu-tone-attention-fg: #BE95FF; --cdu-tone-attention-bg: #491D8B;
  --cdu-tone-progress-fg: #3DDBD9;  --cdu-tone-progress-bg: #004144;
  --cdu-tone-success-fg: #42BE65;   --cdu-tone-success-bg: #044317;
  --cdu-tone-danger-fg: #FF8389;    --cdu-tone-danger-bg: #750E13;
  --cdu-tone-warning-fg: #F1C21B;   --cdu-tone-warning-bg: #3D3100;
}
```

## 2. Status → tone variables

```css
.cdu-chip--received, .cdu-chip--draft, .cdu-chip--retired          { --tone: neutral; }
.cdu-chip--validating, .cdu-chip--composing, .cdu-chip--assembling { --tone: info; }
.cdu-chip--manual-draft, .cdu-chip--pending-manual-draft,
.cdu-chip--pending-data-entry                                      { --tone: attention; }
.cdu-chip--sent, .cdu-chip--affirm-pending                         { --tone: progress; }
.cdu-chip--affirmed, .cdu-chip--completed, .cdu-chip--live         { --tone: success; }
.cdu-chip--approved                                                { --tone: success; }
.cdu-chip--coming-soon                                             { --tone: neutral; border-style: dashed; }
```

Implementation note for the prototype: resolve `--tone` to the `--cdu-tone-{tone}-fg/bg` pair with one rule per tone (CSS cannot interpolate variable names).

## 3. Class map

| Class | Component / widget | Carbon equivalent | Defined in |
| --- | --- | --- | --- |
| `.cdu-shell` | App frame (header + nav + content) | `UIShell` | [`00-shell-nav.md`](../screens/00-shell-nav.md) |
| `.cdu-shell__header` | Navy header bar | `Header` | 00 |
| `.cdu-shell__nav` | Side nav rail | `SideNav` | 00 |
| `.cdu-shell__tabbar` | Bottom tab bar (`sm`) | — (custom) | 00 |
| `.cdu-btn--primary` / `--secondary` / `--ghost` / `--icon` | Buttons | `Button` | components §1 |
| `.cdu-field` | Label + value / input | `TextInput`, `Dropdown` | components §2 |
| `.cdu-chip--{status}` | Status chip | `Tag` | components §3 |
| `.cdu-table` | Data table | `DataTable` | components §4 |
| `.cdu-tabs` | Tabs | `Tabs` | components §5 |
| `.cdu-drawer` | Detail side panel | — (custom panel) | components §6 |
| `.cdu-modal` | Confirm modal | `Modal` | components §7 |
| `.cdu-notice--{tone}` | Notification | `InlineNotification` | components §8 |
| `.cdu-page-header` | Breadcrumb + title | `Breadcrumb` | components §9 |
| `.cdu-filter-bar` | Search + filters | `Search`, `Dropdown` | components §10 |
| `.cdu-kv` | Key–value grid | `StructuredList` | components §11 |
| `.cdu-queue-strip` | Queue strip | — | widgets W1 |
| `.cdu-package-card` | Package card | `Tile` | widgets W2 |
| `.cdu-timeline` | Timeline rail | — | widgets W3 |
| `.cdu-letter` | Letter canvas | — | widgets W4 |
| `.cdu-kpi` | KPI tile | `Tile` | widgets W5 |
| `.cdu-aging` | Aging bars | — (simple bars) | widgets W6 |
| `.cdu-audit` | Audit list | `DataTable` | widgets W7 |
| `.cdu-coming-soon` | Coming soon stub panel (dashed border, muted text, disabled controls) | `Tile` | components §12 |
| `.cdu-chip--coming-soon` | Coming soon chip `(◌ Coming soon)` | `Tag` (outline) | components §12 |

## 4. Responsive rules

```css
@media (max-width: 671px) {   /* sm: iPhone */
  .cdu-shell__nav { display: none; }
  .cdu-shell__tabbar { display: flex; }
  .cdu-drawer { inset: 0; width: 100%; }
  .cdu-timeline { flex-direction: column; }
  .cdu-kv { grid-template-columns: 1fr; }
}
@media (min-width: 1312px) {  /* xlg: drawer docks */
  .cdu-drawer { position: static; width: 400px; }
}
```

## EDGE / STUB

- Print stylesheet for letter canvas — STUB.
- `.cdu-chip--rejected`, `--channel-error`, `--unmatched`, `--disputed` exist in tokens but are EDGE only.

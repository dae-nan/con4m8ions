# CDU-PS design pack (Phase 2)

ASCII wireframes, design system and simulation data for the FXO ideal path. No app code lives here; Phase 3 prototype agents build from these files.

## Sources of truth

| What | Canonical source | Derived files |
| --- | --- | --- |
| Data model, examples, simulation steps | `docs/mappings/*.xlsx` (sheets `Prototype_Trade_Book`, `Prototype_Sim`, `Attribute_Product_Map`, `LDM`, …) | `prototype/data/**` via `scripts/build_prototype_data.py` |
| API contract | [`specs/api/openapi.md`](../../specs/api/openapi.md) | request/response files under `prototype/data/` |
| Screens, bindings, stories | this folder + [`specs/stories/`](../../specs/stories/) | checked against the two sources above |

Rebuild and check:

```bash
.venv/bin/python scripts/build_prototype_data.py   # Excel → prototype/data
.venv/bin/python scripts/check_prototype_sync.py   # must print OK
```

## Index

| Area | File | Purpose |
| --- | --- | --- |
| Architecture | [`architecture.md`](architecture.md) | Components, simulated clock, replay model, status mapping |
| Design system | [`system/tokens.md`](system/tokens.md) | Colour, type, spacing, status tones |
| | [`system/components.md`](system/components.md) | Buttons, inputs, chips, tables, tabs, drawer, modal, notices, ASCII glyph legend |
| | [`system/widgets.md`](system/widgets.md) | W1 queue strip … W8 field palette |
| | [`system/stylesheet.md`](system/stylesheet.md) | `.cdu-*` class contract for the prototype CSS |
| Screens | [`screens/00-shell-nav.md`](screens/00-shell-nav.md) | App shell, nav, entry points to Timeline and MIS |
| | [`screens/01-ops-desk.md`](screens/01-ops-desk.md) | Trade book + trade drawer |
| | [`screens/02-template-admin.md`](screens/02-template-admin.md) | LIVE package view, activate DRAFT 1.2.0 |
| | [`screens/03-manual-draft.md`](screens/03-manual-draft.md) | TR-FXO-005 load template → edit → submit |
| | [`screens/04-fxo-timeline.md`](screens/04-fxo-timeline.md) | Per-trade swimlane timeline |
| | [`screens/05-mis-dashboard.md`](screens/05-mis-dashboard.md) | KPIs, aging, contagion, errors |
| Flow | [`flows/fxo-ideal-path.md`](flows/fxo-ideal-path.md) | Story map → screens → sim steps → files |
| Stories | [`../../specs/stories/`](../../specs/stories/) | BDD epics citing prototype data |
| Data | [`../../prototype/README.md`](../../prototype/README.md) | Folder layout, flow tables, rebuild rules |

## Load order for a prototype agent

Give an agent only what one screen needs:

1. `docs/design/system/tokens.md`, `components.md`, `widgets.md`, `stylesheet.md` (once per session).
2. `docs/design/architecture.md` §§ replay model and simulated clock.
3. One screen file from `docs/design/screens/`.
4. The files listed in that screen's **Data** row and its **Data bindings** table (paths under `prototype/data/`).
5. The matching endpoints in `specs/api/openapi.md` (screen **APIs** row).
6. The matching epic in `specs/stories/` as acceptance tests.

## Story map ↔ screen matrix

| Screen | K1 | K2 | K3 | K4 | K5 |
| --- | --- | --- | --- | --- | --- |
| 00 Shell | entry | entry | entry | — | entry (Timeline, MIS) |
| 01 Ops desk | — | F2a F2b F2c | F3a F3b F3c (status) | — | — |
| 02 Template admin | F1a F1b F1c | — | — | — | — |
| 03 Manual draft | — | F2c (manual) | F3a (submit) | — | — |
| 04 Timeline | — | markers | markers | — | F5a |
| 05 MIS | — | — | — | — | F5b |

## Conventions

- Ideal path only; every design file ends with `## EDGE / STUB`.
- Every value shown in a wireframe comes from `prototype/data/`; binding tables (`UI label | File | JSON path | Example`) are machine-checked.
- Ids are the same everywhere: package `TB-FXO-DEL-2026-001`, trades `TR-FXO-001`…`TR-FXO-006`, documents `DOC-001`, `DOC-105`, audit `AUD-…`, timeline `TL-…`.
- Times are UTC; the simulated "now" for the book and MIS is 2027-12-01T16:30:00Z.

## EDGE / STUB

| Area | Stubbed | Where noted |
| --- | --- | --- |
| K4 Change and recover | Amend, novation, exercise, hot-swap + resend (E1), rollback (E10) | 02, 04, flow |
| Exceptions | Unmatched/Disputed (E3/E4), Compare X gate, channel errors (E7/E8), abandon (E11) | 01, 03, 04, 05 |
| Authoring | New package, version text editing, supplements, SRO pins, field palette W8 | 02, 03 |
| Security | Real auth, roles, four-eyes approval | 00, 02 |
| MIS | Flagged contagion, non-empty error queue, history windows, export | 05 |

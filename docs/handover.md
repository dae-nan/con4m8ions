# CDU-PS handover — Phase 1 and Phase 2

Use this when cloning onto a new machine or opening a new Cursor workspace. Repo: [github.com/dae-nan/con4m8ions](https://github.com/dae-nan/con4m8ions). Work from **`main`**.

Related: [prototype-status.md](prototype-status.md) · [phase-2-handoff.md](phase-2-handoff.md) · [ux-review.md](ux-review.md)

---

## 1. What this project is

**CDU-PS** (Confirmation Document Utility — Product Spec) helps ops turn a booked **Deliverable FX Option** into an ISDA 2026 confirmation letter, get it affirmed, and watch the trade on a timeline and MIS desk.

**TPs** = Transaction Processing systems. **SmartDX** = vendor that produces the letter (mocked in the prototype).

---

## 2. Git state (as of this handover)

| PR | Title | State |
| --- | --- | --- |
| [#1](https://github.com/dae-nan/con4m8ions/pull/1) | Phase 1: PRD, Excel mapping, light specs | **Merged** 5 Nov 2026, 15:42 SGT (`e7e7c77`) |
| [#2](https://github.com/dae-nan/con4m8ions/pull/2) | Phase 2 design pack, rebuild, FpML-style model, scenario clock | **Merged** 5 Nov 2026, 18:30 SGT (`52482f7`) |
| [#3](https://github.com/dae-nan/con4m8ions/pull/3) | Phase 2 static HTML + Carbon prototype | **Merged** 5 Nov 2026 (`184e5ee`) |

Merged GitHub PRs stay in **Merged** (they cannot be “closed” further). Leftover feature branches are deleted after merge so day-to-day work is **`main` only**.

Clone:

```bash
git clone https://github.com/dae-nan/con4m8ions.git
cd con4m8ions
git checkout main
git pull
```

Python helpers (rebuild + sync check):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

---

## 3. Phase 1 (complete, on main)

Docs and specs only. No running UI.

| Artifact | Path |
| --- | --- |
| PRD v1.4 | `docs/prd-cdu-ps-v1.md` |
| Basics / phase split | `docs/explainer-basics.md` |
| Party A/B one-pager | `docs/party-ab-fxo-one-pager.md` |
| Attribute + LDM Excel | `docs/mappings/cdu-ps-isda-2026-mapping.xlsx` |
| FXO payload mocks Excel | `docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx` |
| Feature / scenario / API specs | `specs/` (OpenAPI later moved to v1.6 in Phase 2) |
| ISDA PDFs + text extracts | `docs/reference/isda/` and `docs/reference/isda/text/` |
| SmartDX screenshots | `docs/reference/smartdx/` |

Locked: FXO Deliverable (Exhibit II-B) is the deep product; dual MCA paths; light OpenSpec only; Phase 2 starts with wireframes then a Mac-first prototype.

---

## 4. Phase 2 — design pack (complete, on main via PR #2)

- Shared design system: `docs/design/system/` (tokens, components, widgets, stylesheet, display-label map).
- ASCII screens (ideal path): `docs/design/screens/00`–`05` plus `docs/design/flows/fxo-ideal-path.md`.
- Architecture, IA, modelling: `docs/design/architecture.md`, `information-architecture.md`, `modelling-decisions.md`.
- Simulation JSON: `prototype/data/` and `prototype/routes.json` (scenarios A–D).
- Stories: `specs/stories/epic-*.md`.
- Single rebuild: `scripts/build.py` from committed ISDA text. Sync: `scripts/check_prototype_sync.py`.

Modelling (extends beyond FX): one `parties[]` list; trade-level `documentation`; `productInsert`; `MasterConfirmation`; derived `mcaPath`.

---

## 5. Phase 2 — prototype (on main via PR #3)

Static **HTML + Carbon-inspired CSS**. No app server. An in-browser mock API replays `prototype/data` on the `/v1` OpenAPI paths.

### How to start it

From the repo root:

```bash
cd prototype
python3 -m http.server 8080 --bind 127.0.0.1
```

Open **http://127.0.0.1:8080/#/trades**

Default scenario is **D** (book + MIS, clock 16:30Z). Change scenario with `?scenario=A|B|C` on the URL, or the picker in the shell banner.

Optional check that data still matches Excel + OpenAPI:

```bash
cd ..   # repo root
.venv/bin/python scripts/check_prototype_sync.py
```

Do **not** hand-edit the Excel or `prototype/data`. Change `scripts/build.py` / `scripts/build_prototype_data.py` and run `scripts/build.py`.

### Screens implemented

| Route | Screen |
| --- | --- |
| `#/trades` | Ops desk (queue + drawer) |
| `#/timeline` | Per-trade FXO timeline |
| `#/mis` | MIS dashboard |
| `#/templates/...` | Template admin (view + activate) |
| `#/manual-draft?trade=TR-FXO-005` | Manual draft |

Dark-mode toggle and a compact/iPhone layout are in the CSS.

### Pathways / use cases implemented (ideal path)

Mapped to PRD §9.3 kite → sea.

| Scenario | Clock | Use case | What you do |
| --- | --- | --- | --- |
| **A** Template release | 15:59Z | Define templates — activate LIVE package | Open Templates, see LIVE 1.1.0 + DRAFT 1.2.0 already four-eyes approved, activate 1.2.0 |
| **B** TR-FXO-001 journey | scripted | Book → send → match | Timeline: **Run TR-FXO-001 journey** (NEW_TRADE → assemble → mock SmartDX → affirm → TPs callbacks) |
| **C** Manual draft | 16:40Z | Book — manual draft | Open TR-FXO-005, edit, save, submit to SmartDX; desk then shows Affirm pending |
| **D** Book & MIS (default) | 16:30Z | Observe | Six-trade ops desk + MIS (aging, contagion). TR-FXO-001 and TR-FXO-005 have timelines; other trades show a stub |

Four-eyes approval is **mocked as already done** (audit `AUD-0007` / `AUD-0008`). The real approval workflow is “Coming soon”.

---

## 6. Pending from Phase 2

**Not started / stubs (by design)**

- Kite **Change and recover** (amend, novation, exercise, hot-swap, Compare X, Swoosh).
- Real four-eyes approval UI and auth.
- Template authoring (Bindings tab is a stub).
- Full timeline swimlane (table + lane summary only).
- Timelines for TR-FXO-002 / 003 / 004 / 006 (UI stubs only).
- FastAPI swap-in; live SmartDX / SWIFT.
- Official `@carbon/web-components` (CSS-only Carbon look).
- Phase 3 AI (MIS Explain / Anomalies / Alerts / Export and the shell assistant = “Coming soon”).

**Known defects to fix on the next machine**

- Invalid Globex LEI `549300TRANSFeree0001` (fix in the generator, then rebuild).
- UX review **Medium / Low** items still open (see [ux-review.md](ux-review.md)): MIS “Sent” meaning, time-in-status polish, cutover loop for 1.2.0, version/layer numbering, too many disabled buttons.

**Do not rerun** the old Phase 1 scripts `generate_phase1_mapping.py` / `generate_fxo_payload_mocks.py` as the daily path. Use `scripts/build.py`. Re-extract ISDA text (`scripts/extract_isda_text.py`) only when a PDF changes.

---

## 7. Suggested next work (new workspace)

1. Pull `main`, run the prototype, walk scenarios A–D.
2. Fix the Globex LEI + remaining Medium UX items on a new branch.
3. Optionally swap Carbon web components, or add FastAPI later on the same `/v1` contract.
4. Phase 3 only when the ideal-path prototype is signed off.

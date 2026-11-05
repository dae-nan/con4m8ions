# Prototype simulation data (Phase 2)

## Running the prototype locally

From this directory (`prototype/`), start a static file server (required so `fetch()` can load `routes.json` and `data/`):

```bash
cd prototype
python3 -m http.server 8080 --bind 127.0.0.1
```

Open [http://127.0.0.1:8080/](http://127.0.0.1:8080/) in a browser. Default hash route is `#/trades` (scenario **D · Book & MIS**).

| Scenario | Use for |
| --- | --- |
| A | Template admin — activate DRAFT 1.2.0 |
| B | TR-FXO-001 journey — **Run journey** on Timeline |
| C | Manual draft TR-FXO-005 — Save / Submit |
| D | Ops desk + MIS (default) |

App code lives under `web/` (`api.js` mock layer, `labels.js` display map, screen modules, Carbon-inspired `.cdu-*` CSS).


## 1. Rules

- **Excel is canonical.** Every file under `data/` is one row of sheet `Prototype_Sim` in [`docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx`](../docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx). Rows may `$ref` the Phase 1 mock rows (`With_MCA` / `Without_MCA`), so `TR-FXO-001` payloads are the Phase 1 mocks verbatim.
- **Do not hand-edit `data/`, `routes.json` or the workbooks.** There is one rebuild path. It regenerates every sheet of both workbooks from the committed ISDA text extract (`docs/reference/isda/text/`) and the tables in `scripts/`, then exports `data/` and `routes.json`. The output is byte-identical for the same inputs.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py                   # workbooks + data/ + routes.json
.venv/bin/python scripts/check_prototype_sync.py    # must print OK (includes workbooks == fresh build)
```

  Only when an ISDA PDF changes: `.venv/bin/python scripts/extract_isda_text.py` (needs poppler `pdftotext`), then rebuild.
- **Trade shape** is FpML-style: `trade.parties[]`, `trade.product` (buyer/seller party references), `trade.economics`, `trade.documentation`. See [`docs/design/modelling-decisions.md`](../docs/design/modelling-decisions.md).
- **Assumed state:**
  - One LIVE package, `TB-FXO-DEL-2026-001` "2026 FXO Deliverable (II-B)" v1.1.0.
  - DRAFT v1.2.0 already approved (four-eyes) by `u.ctrl.ng` at 15:30 (`AUD-0007`).
  - Trade date 2027-12-01; book snapshot `asOf` 2027-12-01T16:30:00Z.
  - Only `TR-FXO-001` and `TR-FXO-005` have timelines (`timelineAvailable`).

## 1a. Mock API (`routes.json`)

`routes.json` has `scenarios[]` (A–D), `defaultScenario` (`D`), and one entry per `Prototype_Sim` row: `{step, scenario, at, method, path, url, contract, file, listFilter}`.
- The shell scenario picker sets the starting clock from `scenarios[].clock` (see [`docs/design/architecture.md`](../docs/design/architecture.md) §5).
- The browser layer answers `method` + `url` (under `/v1`) with `data/<file>`.
- A GET returns the latest entry at or before the sim clock. If `listFilter` is set (`events` or `items`), keep only array elements with `at` ≤ clock and adjust `count` / `asOf`.
- A POST/PUT returns its `response-*` entry and moves the clock to that entry's `at`. After manual submit (16:55:02Z), `GET /trades` resolves to `book/get-trades.after-submit.200.json`.
- Unknown calls return 404 `NOT_FOUND`, and the screen shows its stub.
- UI labels come from the [display-label map](../docs/design/system/components.md#display-label-map-h2); API payloads keep the codes.

## 2. Folders

```text
data/
  inbound/trades/        TPs NEW_TRADE events (POST /events)
  inbound/webhooks/      affirm / match webhooks (POST /webhooks/affirmation)
  inbound/ui/            requests sent by the ops desk UI (admin activate, manual draft save/submit)
  templates/             template store: package, versions, Exhibit I / II-B bodies, selection rules, audit
  outbound/api-responses/<entity>/NN-<call>.<http>.json   CDU-PS responses in call order
  outbound/smartdx/      packages sent to mock SmartDX + its replies
  outbound/tps-callbacks/ callbacks CDU-PS returns to TPs
  timeline/              per-trade timeline (GET /trades/{id}/timeline) + all audit events (GET /audit)
```

## 3. Flow A — template admin / view (`TB-FXO-DEL-2026-001`)

| Step | Call | File |
| --- | --- | --- |
| A01 | `GET /templates` | `data/templates/index.json` |
| A02 | `GET /templates/{id}` | `data/templates/fxo-deliverable-2026/package.json` |
| A03 | `GET /templates/{id}/versions/{version}` | `data/templates/fxo-deliverable-2026/versions/1.0.0.json` · `1.1.0.json` · `1.2.0.json` |
| A04 | `GET /templates/{id}/layers/{templateVersionId}` | `data/templates/fxo-deliverable-2026/exhibit-i-master.json` · `exhibit-ii-b-product.json` |
| A05 | `GET /templates/selection-rules` | `data/templates/fxo-deliverable-2026/selection-rules.json` |
| A06 | `GET /templates/{id}/audit` | `data/templates/fxo-deliverable-2026/audit.json` |
| A07–A08 | `PUT /templates/{id}/versions` (history, 2027-11-28) | `data/inbound/ui/TB-FXO-DEL-2026-001.put-version-1.2.0.json` → `data/outbound/api-responses/TB-FXO-DEL-2026-001/01-put-versions.201.json` |
| A09–A10 | `POST /templates/{id}/activate` (1.2.0 already approved, `AUD-0007`; activation `AUD-0008`) | `data/inbound/ui/TB-FXO-DEL-2026-001.activate-1.2.0.json` → `…/02-post-activate.200.json` |
| A11–A12 | re-read package + audit | `…/03-get-template.after-activate.200.json` · `…/04-get-template-audit.after-activate.200.json` |

## 4. Flow B — new trade `TR-FXO-001` → confirmed → affirmed → callback

| Step | Call | File |
| --- | --- | --- |
| B01–B02 | `POST /events` | `data/inbound/trades/TR-FXO-001.new-trade.json` → `data/outbound/api-responses/TR-FXO-001/01-post-events.202.json` |
| B03–B05 | `GET /assemblies/{id}` (legal → package → completed) | `…/TR-FXO-001/02-get-assembly.legal-resolved.200.json` · `03-…package-located` · `04-…completed` |
| B06–B07 | `POST /mock/smartdx/documents` | `data/outbound/smartdx/DOC-001.send.json` → `DOC-001.generated.json` |
| B08 | `POST /callbacks/tps` (generated) | `data/outbound/tps-callbacks/TR-FXO-001.01-generated.json` |
| B09–B10 | `POST /webhooks/affirmation` | `data/inbound/webhooks/DOC-001.affirmed.json` → `…/TR-FXO-001/05-post-webhooks-affirmation.200.json` |
| B11 | `POST /mock/smartdx/documents/{id}/status` | `data/outbound/smartdx/DOC-001.status-affirmed.json` |
| B12 | `POST /callbacks/tps` (affirm) | `data/outbound/tps-callbacks/TR-FXO-001.02-affirmed.json` |
| B13–B15 | `GET /trades/{id}`, `GET /documents/{id}`, `GET /trades/{id}/timeline` | `…/06-get-trade.200.json` · `07-get-document.200.json` · `data/timeline/TR-FXO-001.json` |

Flow C (manual draft `TR-FXO-005`, steps C01–C11) and flow D (book + MIS, D01–D06) are listed in Excel `Prototype_Sim` and [`docs/design/flows/fxo-ideal-path.md`](../docs/design/flows/fxo-ideal-path.md).

## 5. EDGE / STUB (no files yet)

| PRD id | Edge | Status it would show |
| --- | --- | --- |
| E1 | Wrong template → hot-swap → `POST /documents/{id}/resend` (mock rows `HOT_SWAP`, `RESEND` exist in Excel) | WrongTemplate → Superseded |
| E3 / 9a | Affirm fail, Unmatched, Disputed → Compare X gate | Unmatched · Disputed · CompareXGate |
| E4 | DQ reject (Excel `Errors` sheet) | Rejected |
| E6 | Swoosh inbound PDF + OCR | — |
| E8 | SmartDX down (`CHANNEL_UNAVAILABLE`) | ChannelError |
| E9 | Idempotency clash | 409 |
| E10 | Rollback package | — |
| E11 | Manual draft abandoned | FAILED / SUPPRESSED |
| — | Manual entry mode (b) `PUT /assemblies/{id}/manual-entries` | PENDING_DATA_ENTRY |
| — | AMEND, NOVATION, EXERCISE, TERMINATE payloads (Excel only) | Amended · Novated · Exercised |
| — | Four-eyes approval workflow `POST /templates/{id}/versions/{version}/approval` (approval mocked as given) | Coming soon |
| — | Timelines for `TR-FXO-002`, `TR-FXO-003`, `TR-FXO-004`, `TR-FXO-006` (`timelineAvailable = false`) | Coming soon |

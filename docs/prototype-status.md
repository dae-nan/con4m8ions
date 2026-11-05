# Prototype status — CDU-PS Phase 2

**Date:** 5 Nov 2026, Asia/Singapore  
**PR:** [dae-nan/con4m8ions#3](https://github.com/dae-nan/con4m8ions/pull/3) — **merged** to `main` (`184e5ee`)  
**Stack:** static HTML + Carbon-inspired CSS, in-browser mock API, no app server  
**Sync:** `scripts/check_prototype_sync.py` → OK (3,442 checks at last run)

Full Phase 1 + 2 context: [handover.md](handover.md).

## Completed

- Mock API (`prototype/web/js/api.js`) replays `prototype/routes.json` on `/v1` paths with scenario clock A–D and `listFilter`.
- Display-label map (`prototype/web/js/labels.js`) — no raw enums on screen.
- Shell / nav with scenario picker, dark-mode toggle, Trades / Timeline / MIS / Templates.
- Ops desk: six-trade book, filters, “in status”, drawer; timeline glyph only where `timelineAvailable`.
- FXO timeline for TR-FXO-001 (and TR-FXO-005); other trades stubbed.
- MIS dashboard with book-derived KPIs; AI / export / alerts = Coming soon.
- Template admin: view LIVE 2026 FXO Deliverable package; activate 1.2.0 under scenario A; four-eyes shown as already approved.
- Manual draft for TR-FXO-005 (scenario C); submit advances clock and refreshes the book.

## Demo map

| Scenario | Implemented use case |
| --- | --- |
| A | Activate template 1.2.0 |
| B | TR-FXO-001 NEW → SmartDX mock → affirmed → TPs callback |
| C | TR-FXO-005 manual draft → submit |
| D | Desk + MIS (default) |

## Run

```bash
cd prototype
python3 -m http.server 8080 --bind 127.0.0.1
# http://127.0.0.1:8080/#/trades
```

## Not done (Phase 2 remainder)

Change/recover flows; real four-eyes; Bindings tab; full swimlane; FastAPI; Carbon web components; Phase 3 AI; generator fix for invalid Globex LEI; UX Medium/Low polish.

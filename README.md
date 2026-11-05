# con4m8ions (CDU-PS)

Confirmation Document Utility — Product Spec for ISDA/EMTA **2026 FX Definitions** confirmation templates.

## Phase 1 (current)

Docs + Excel mapping + payload mocks only. No running UI or API. **Phase 3 AI/chatbot is thinking-only** in the API/PRD stubs.

| Artifact | Path |
| --- | --- |
| **PRD** | [`docs/prd-cdu-ps-v1.md`](docs/prd-cdu-ps-v1.md) |
| **Attribute Excel** | [`docs/mappings/cdu-ps-isda-2026-mapping.xlsx`](docs/mappings/cdu-ps-isda-2026-mapping.xlsx) |
| **FXO payload mocks** | [`docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx`](docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx) |
| **Phase 1 plan** | [`docs/phase-1-plan.md`](docs/phase-1-plan.md) |
| **Feature specs** | [`specs/features/`](specs/features/) (incl. Exhibit I letter) |
| **Scenarios** | [`specs/scenarios/`](specs/scenarios/) |
| **API contract** | [`specs/api/openapi.md`](specs/api/openapi.md) — grouped Templates / Trades / Documents / Affirm / MIS / Agent stubs |
| **Reference PDFs** | [`docs/reference/isda/`](docs/reference/isda/) |

### PRD highlights (v1.2)

- Ops/intern plain language + explainers (affirm vs confirm, MCA, matrices vs III, why FX often has no CSA)
- Ontology + composition visuals; Use Case 2.0 + edge cases
- Sequences **split** (Template Admin vs Trade); **state diagrams** for trade / FXO / template versioning
- Exhibit I letter modeled + mocked; LDM aligned to Excel (`Attribute type`, `Domain`, `LDM entity`)
- Archetypes / JTBD / Impact Map / User Story Map

### Regenerate

```bash
python3 scripts/generate_phase1_mapping.py      # attribute workbook (needs store PDF extract)
python3 scripts/generate_fxo_payload_mocks.py   # FXO payload mocks
```

## Phase 2 / 3 (deferred)

- **Phase 2:** HTML5 ops desk + Python FastAPI — Mac-first  
- **Phase 3:** AI / chatbot / MCP agents — not started

## ISDA / EMTA license

PDF materials under `docs/reference/isda/` are under license from ISDA and EMTA. **Internal use only.** See `LICENSE-NOTICE.md` and PDF title pages.

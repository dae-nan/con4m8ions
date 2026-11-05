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

### PRD highlights (v1.1)

- Ontology **diagram** + MASTER/PRODUCT/SUPPLEMENT/MATRIX/MCA **composition visual**
- Use Case 2.0 (Cockburn + Jacobson) for Deliverable FX Option + **Edge cases**
- Sequences **split**: Template Admin lifecycle vs Trade lifecycle vs recovery
- Exhibit I **confirmation letter** modeled and mocked
- Archetypes / JTBD / Impact Map / User Story Map
- FXO worked ontology + process flow

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

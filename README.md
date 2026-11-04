# con4m8ions (CDU-PS)

Confirmation Document Utility — Product Spec for ISDA/EMTA **2026 FX Definitions** confirmation templates.

## Phase 1 (current)

Docs + Excel mapping only. No running UI or API.

| Artifact | Path |
| --- | --- |
| **PRD** | [`docs/prd-cdu-ps-v1.md`](docs/prd-cdu-ps-v1.md) |
| **Excel mapping** | [`docs/mappings/cdu-ps-isda-2026-mapping.xlsx`](docs/mappings/cdu-ps-isda-2026-mapping.xlsx) |
| **Phase 1 plan** | [`docs/phase-1-plan.md`](docs/phase-1-plan.md) |
| **Feature specs** | [`specs/features/`](specs/features/) |
| **Scenarios** | [`specs/scenarios/`](specs/scenarios/) |
| **API contract** | [`specs/api/openapi.md`](specs/api/openapi.md) |
| **Reference PDFs** | [`docs/reference/isda/`](docs/reference/isda/) |

### Excel sheets

1. `Attribute_Product_Map` — field inventory (II-B deepest)  
2. `Template_Admin_Utility` — versioning / binding  
3. `Logical_Data_Model` — entities / relationships  
4. `Rules_DQ` — DQ + mapping rules  
5. `FXO_Deliverable_Lifecycle` — Deliverable FX Option event × systems  
6. `Legend_Assumptions` — keys + Assumed MCA + sources  

Regenerate workbook: `python3 scripts/generate_phase1_mapping.py` (requires `openpyxl`; reads Project store PDF text extract when present).

## Phase 2 (deferred)

HTML5 ops desk (Carbon principles, SCB-approx palette, dark mode, responsive) + Python FastAPI implementing `specs/api` — **Mac-first**, then cloud / Vercel. Mock SmartDX/SWIFT first.

## ISDA / EMTA license

PDF materials under `docs/reference/isda/` were created under license from ISDA and EMTA. **Internal use only** — do not copy or disseminate except as permitted by that license. See notices on the PDF title pages.

## Modeling cheat-sheet

- **MASTER** = Exhibit I · **PRODUCT** = Exhibit II-* · **SUPPLEMENT** = Exhibit III-*  
- Groups: `COMMON` / `PRODUCT` / `SUPPLEMENT` / `MATRIX` / `MCA` / `PLATFORM` / `LIFECYCLE`  
- MCA: dual paths `With_MCA` (Assumed sample) and `Without_MCA`  
- 2026 FX Definitions effective **22 Nov 2027**

# CDU-PS Phase 1 Plan

**Status:** Awaiting confirmation (revised)  
**Outcome:** Rewritten PRD (incl. ontology + logical data model + sequence diagrams) + light feature/API specs + multi-sheet Excel mapping workbook  
**Repo:** [dae-nan/con4m8ions](https://github.com/dae-nan/con4m8ions) (git push available; local Mac is Phase 2 run target)

---

## Locked decisions

| Topic | Decision |
| --- | --- |
| Mapping breadth | Every product/template in the 2026 colour-coded consolidated confirmation templates PDF; **Deliverable FX Option (Exhibit II-B) filled deepest** |
| MCA | Dual paths: **with MCA** and **without MCA**. Sample MCA invented and rows marked **Assumed** |
| OpenSpec | **Light only**: `specs/` feature + scenario + **API contract** markdown. No OpenSpec CLI/CI tooling |
| Phase 1 finish line | Docs + Excel + diagrams as **spec artifacts**. No running UI/API code yet |
| Phase 2 stack (deferred) | HTML5 + Carbon Design System principles; SCB approximate palette; dark-mode toggle with contrast; responsive incl. iPhone; Python APIs implementing the Phase 1 contracts; **run on your Mac first**, later cloud + Vercel |
| Sources | Uploaded ISDA PDFs + your draft PRD |

---

## ISDA template structure → how we model it

Yes — the 2026 annotated confirmation set is already a **master + product + supplement** stack:

| Layer | ISDA source | Role | CDU-PS model |
| --- | --- | --- | --- |
| **Master / common** | **Exhibit I** | Intro, standard paragraphs, closing; shared elections (LEI, Calculation Agent, accounts, offices, governing law, notices) | `TemplateLayer = MASTER` · attribute group `COMMON` |
| **Product confirmation** | **Exhibit II-A … II-K** | Product-specific economic terms (e.g. II-B Deliverable FX Option) | `TemplateLayer = PRODUCT` · one `ProductType` per exhibit · attribute group `PRODUCT` |
| **Product supplements / add-ons** | **Exhibit III-A …** | Optional overlays: disruption, early termination, averaging, barrier, etc. | `TemplateLayer = SUPPLEMENT` · attached via `supplementRefs[]` · attribute group `SUPPLEMENT` |
| **Matrix overlays** | SRO Matrix / EM Currency Matrix version pins on applicable II exhibits | Versioned reference data, not a separate confirmation body | `MatrixBinding` entity · attribute group `MATRIX` |
| **MCA overlay (optional)** | Bilateral Master Confirmation (sample Assumed) | Elects defs year, product elections, notice/CA defaults — increasingly absorbed into 2026 main book for EM | `McaProfile` · attribute group `MCA` · path `With_MCA` / `Without_MCA` |

**Logical grouping of attributes (used in Excel + LDM):**

1. `COMMON` — Exhibit I  
2. `PRODUCT` — Exhibit II fields for that product  
3. `SUPPLEMENT` — Exhibit III fields when elected  
4. `MATRIX` — SRO / EM matrix version + resolved matrix terms  
5. `MCA` — Assumed MCA elections (when path = With_MCA)  
6. `PLATFORM` — CDU-PS / TPS / SmartDX / SWIFT operational fields (not ISDA legal text)  
7. `LIFECYCLE` — novation parties, event ids, affirmation status, template version used at generation time  

Composition rule for a live confirmation instance:

```text
ConfirmationInstance =
  MASTER(Exhibit I)
  + PRODUCT(Exhibit II-*)
  + Σ elected SUPPLEMENT(Exhibit III-*)
  + MATRIX bindings (if applicable)
  + optional MCA profile
  + PLATFORM runtime metadata
```

---

## Source exhibits (mapping universe)

From *Annotated Confirmation Templates — 2026 FX Definitions* (8 Jul 2026):

**Exhibit I** — Introduction, standard paragraphs, closing (shared confirmation wrapper)

**Exhibit II product confirmations**

- II-A Deliverable FX Transaction  
- II-B Deliverable FX Option Transaction *(deepest)*  
- II-C Non-Deliverable FX Transaction  
- II-D Non-Deliverable FX Option Transaction  
- II-E Non-Deliverable FX Transaction (EM Currency Matrix)  
- II-F Non-Deliverable FX Option Transaction (EM Currency Matrix)  
- II-G Non-Deliverable Cross-Currency FX Transaction (EM Currency Matrix)  
- II-H Non-Deliverable Cross-Currency FX Option Transaction (EM Currency Matrix)  
- II-I Variance / Volatility Swap  
- II-J Correlation Swap  
- II-K Deliverable Delta Neutral Forward Volatility Agreement  

**Exhibit III additional provisions**

- III-A Deliverable disruption  
- III-B Non-deliverable disruption  
- III-C Mandatory early termination  
- III-D Optional early termination  
- III-E Averaging forward rate  
- III-F Averaging settlement rate  
- III-G Averaging strike price  
- III-H Barrier transaction *(plus any further III exhibits present in the PDF after contents)*

**Cross-refs:** 1998 FX Definitions, Annex A (1998), Introduction to 2026 FX Definitions (effective **Nov 22, 2027**; MCA consolidation; matrix versioning).

**Lifecycle events:** `NEW_TRADE`, `AMEND`, `TERMINATE`, `EXERCISE`, `NOVATION`, `AFFIRM` / match, template admin (`HOT_SWAP`, `ROLLBACK`, `RESEND`).

---

## Phase 1 vs Phase 2 — what goes where

| Artifact | Phase 1 (now) | Phase 2 (after Excel sign-off) |
| --- | --- | --- |
| PRD ontology + conceptual/logical data model | **Yes** — full prose + mermaid class/ER in PRD | Refine if implementation teaches gaps |
| Master / Product / Supplement composition model | **Yes** — PRD + Excel columns + LDM sheet | Enforce in Python template engine |
| Attribute lineage (source PDF / exhibit / annotation) | **Yes** — Excel columns | Surface in UI “field inspector” |
| Data quality + mapping rules catalog | **Yes** — Excel `Rules_DQ` sheet + light rules spec | Implement validators in Python |
| E2E sequence / event-flow diagram | **Yes** — mermaid in PRD | Optional interactive playback in UI |
| FXO deep-dive sequence (all events × systems) | **Yes** — mermaid in PRD + FXO lifecycle spec | Wire to live demo timeline in ops desk |
| API specification (endpoints, payloads, errors) | **Yes** — OpenAPI-style markdown under `specs/api/` | Implement FastAPI against that contract |
| Running HTML5 UI + Python services | No | **Yes** — Mac-first |
| Live SmartDX / SWIFT | No | Mock first; live later if needed |

**Rule of thumb:** Phase 1 = *what* and *how it should behave* (models, maps, contracts, diagrams). Phase 2 = *make it run*.

---

## Deliverables

### A. Rewritten PRD (`docs/prd-cdu-ps-v1.md`)

Must include:

1. Executive summary, Phase 1/2 scope split  
2. **Domain ontology** — FinancialProduct, LegalFramework / MCA / ISDA defs year, DynamicTemplate (Master/Product/Supplement layers), DocumentArtifact, LifecycleEvent, MatrixBinding  
3. **Logical data model** — entities, keys, relationships (ConfirmationInstance composition; TemplateVersion; AttributeDefinition; MappingRule; DQRule; NovationTransfer)  
4. MCA with/without; 1998 vs 2026 election  
5. **E2E sequence / event-flow diagram** (mermaid) — TPS → Ingest → Legal Resolver → Template Engine → SmartDX + SWIFT → Affirm webhook → TPS callback; parallel Template Admin hot-swap path  
6. **FXO Deliverable deep-dive sequence** (mermaid) — NEW → (wrong template) → HOT_SWAP/RESEND → AFFIRM → AMEND → NOVATION → EXERCISE/SETTLE (and disruption edge where relevant), naming systems/services on each message  
7. NFRs: prototype-realistic targets; draft PRD five-nines numbers as aspirational appendix only  
8. Acceptance criteria tied to Excel + Phase 2 demo readiness  

### B. Light specs (`specs/`)

**Features**

- `specs/features/attribute-product-mapping.md` — groups, composition, MCA paths  
- `specs/features/template-admin.md` — versioning, hot-swap, rollback, resend  
- `specs/features/fxo-deliverable-lifecycle.md` — deep dive + sequence reference  

**Scenarios**

- hot-swap wrong→amend→resend; novation; MCA vs no-MCA; affirm callback; supplement election (e.g. barrier / averaging)  

**API contract (Phase 1 spec only)** — `specs/api/openapi.md` (or split files):

- `POST /events` — ingest lifecycle event  
- `GET /trades/{id}` / timeline  
- `POST /templates` · `PUT /templates/{id}/versions` · `POST /templates/{id}/activate` · `POST /templates/{id}/rollback`  
- `POST /documents/{id}/resend`  
- `POST /webhooks/affirmation`  
- `POST /callbacks/tps` (outbound shape)  
- Error model, idempotency keys, example JSON aligned to Excel TPS paths  

No server implementation in Phase 1.

### C. Excel workbook (`docs/mappings/cdu-ps-isda-2026-mapping.xlsx`)

**Sheet 1 — `Attribute_Product_Map`**

| # | Column |
| --- | --- |
| 1 | Attribute / field name |
| 2 | Attribute group (`COMMON` / `PRODUCT` / `SUPPLEMENT` / `MATRIX` / `MCA` / `PLATFORM` / `LIFECYCLE`) |
| 3 | Template layer (`MASTER` / `PRODUCT` / `SUPPLEMENT`) |
| 4 | Exhibit / template ID (`I`, `II-B`, `III-H`, …) |
| 5 | Matrix / version hooks |
| 6 | ISDA 2026 section / annotation note |
| 7 | **Lineage** — source PDF + page/exhibit anchor |
| 8 | Product type(s) |
| 9 | Depth (`Deep` II-B / `Standard`) |
| 10 | Lifecycle events material to |
| 11 | MCA path (`With_MCA` / `Without_MCA` / `Both`) |
| 12 | MCA sample field (Assumed if invented) |
| 13 | TPS JSON path |
| 14 | Downstream SmartDX / SWIFT target |
| 15 | DQ rule IDs (FK to Rules_DQ) |
| 16 | Mapping / transform rule IDs |
| 17 | Notes / Assumed flag |

**Sheet 2 — `Template_Admin_Utility`**

Admin fields for Master/Product/Supplement binding, product routing, versioning (`DRAFT`/`LIVE`/`RETIRED`), hot-reload, rollback, audit. Includes `masterTemplateId`, `productExhibitId`, `supplementExhibitIds[]`, `matrixBindings`, `mcaRequired`.

**Sheet 3 — `Logical_Data_Model`**

Entity list, attributes, PK/FK, relationships (textual + simple adjacency). Mirrors PRD mermaid; Excel is the working table ops can filter.

**Sheet 4 — `Rules_DQ`**

Rule ID, type (`REQUIRED`, `FORMAT`, `CROSS_FIELD`, `CALENDAR`, `LEGAL_ELECTION`, `LINEAGE_PRESENT`), severity, applies-to attribute/group/product/lifecycle, expression/description, Assumed vs ISDA-derived.

**Sheet 5 — `FXO_Deliverable_Lifecycle`**

Sample Deliverable FX Option across NEW / AFFIRM / AMEND / NOVATION / edges / template admin wrong→fix→resend; columns for system/service touched and template version used. Cross-references the PRD FXO sequence diagram.

**Sheet 6 — `Legend_Assumptions`**

Colour/group key, Assumed MCA inventory, source PDFs, effective-date note.

### D. Repo hygiene

- Commit Phase 1 artifacts to `con4m8ions`  
- Copy reference PDFs under `docs/reference/isda/` (license notice retained)  
- README indexes PRD, specs, Excel, diagrams  

---

## Approach

1. Extract Exhibit I/II/III field inventories from PDFs → working CSV in Project `internal/`.  
2. Tag each field with **group + template layer + lineage**.  
3. Enrich II-B deepest; attach III supplements that can overlay FXO.  
4. Overlay MCA Assumed + Without_MCA paths.  
5. Author `Rules_DQ` + mapping rule IDs referenced from the attribute sheet.  
6. Build Excel (`openpyxl`) with the six sheets.  
7. Rewrite PRD (ontology, LDM, both sequence diagrams) + light feature/API specs using the same vocabulary.  
8. Push branch + PR; mirror Excel + plan in Project Context.

---

## Out of scope (Phase 1)

- Running HTML5 / Carbon / SCB UI  
- Running Python FastAPI (spec only)  
- Live SmartDX or SWIFT  
- Full OpenSpec toolchain  
- Interactive diagram playback in the ops desk (Phase 2)  
- Production five-nines NFR enforcement  

---

## Phase 2 preview (after Excel + PRD/API sign-off)

Local Mac first: HTML5 ops desk implementing Carbon principles + SCB tokens + dark mode + responsive layouts; Python services implementing `specs/api`; load mappings/rules from Excel→JSON; mock SmartDX/SWIFT; demo FXO lifecycle (incl. novation + template admin) with UI timeline matching the Phase 1 sequence diagrams. Then sync to cloud agent and Vercel.

---

## Acceptance for Phase 1

- [ ] PRD includes ontology, logical data model, E2E sequence, and FXO deep-dive sequence (systems named)  
- [ ] Specs cover mapping, template admin, FXO lifecycle scenarios, and API contract  
- [ ] Excel has six sheets; Master/Product/Supplement groups explicit; II-B deepest  
- [ ] Lineage + DQ/mapping rule IDs populated for Deep rows; Standard rows have lineage at exhibit level minimum  
- [ ] MCA Assumed rows flagged; Without_MCA path present  
- [ ] Workbook openable; committed and linked from Context  

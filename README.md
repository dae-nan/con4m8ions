# con4m8ions (CDU-PS)

Confirmation Document Utility — Product Spec for ISDA/EMTA **2026 FX Definitions** confirmation templates.

## Phase 1 (current)

Docs + Excel mapping + payload mocks only. No running UI or API.  
**TPs** = Transaction Processing systems. **SmartDX** = external vendor for ISDA confirmation letters.

| Artifact | Path |
| --- | --- |
| **PRD (v1.4)** | [`docs/prd-cdu-ps-v1.md`](docs/prd-cdu-ps-v1.md) |
| **Basics + phase explainer** | [`docs/explainer-basics.md`](docs/explainer-basics.md) |
| **Party A/B one-pager** | [`docs/party-ab-fxo-one-pager.md`](docs/party-ab-fxo-one-pager.md) |
| **Attribute Excel** | [`docs/mappings/cdu-ps-isda-2026-mapping.xlsx`](docs/mappings/cdu-ps-isda-2026-mapping.xlsx) |
| **FXO payload mocks** | [`docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx`](docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx) |
| **Feature / scenario / API specs** | [`specs/`](specs/) |
| **ISDA PDFs** | [`docs/reference/isda/`](docs/reference/isda/) |
| **SmartDX reference images** | [`docs/reference/smartdx/`](docs/reference/smartdx/) |

### PRD v1.4 highlights

- Explainers in `explainer-basics.md`; story map mermaid (kite → sea → fish)  
- Manual drafting first-class (load+edit / drag-drop fields); audit trail across template/assembly/docs  
- ER Mermaid fixed; Phase 2 starts with ASCII wireframes (not drawn in Phase 1)  
- Prior v1.3: TPs/SmartDX arch, Swoosh/Compare X, TemplatePackage/AssemblyRun, DDD APIs  


`scripts/generate_phase1_mapping.py` and `scripts/generate_fxo_payload_mocks.py` record how Phase 1 built the workbooks. Do not rerun them: they need the ISDA PDF extract and would drop sheets added afterwards. Change the workbooks through `scripts/build_prototype_data.py` (below).

## Phase 2 — design pack

ASCII wireframes, design system and simulation data for the FXO ideal path. Still no app code.

| Artifact | Path |
| --- | --- |
| **Design pack index + load order** | [`docs/design/README.md`](docs/design/README.md) |
| **Prototype architecture** | [`docs/design/architecture.md`](docs/design/architecture.md) |
| **Screens (ASCII)** | [`docs/design/screens/`](docs/design/screens/) |
| **Ideal-path flow** | [`docs/design/flows/fxo-ideal-path.md`](docs/design/flows/fxo-ideal-path.md) |
| **Simulation data** | [`prototype/`](prototype/) |
| **BDD stories** | [`specs/stories/`](specs/stories/) |
| **API contract (v1.5)** | [`specs/api/openapi.md`](specs/api/openapi.md) |

Excel (`docs/mappings/`) and `specs/api/openapi.md` are canonical; `prototype/data/` is generated from them.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_prototype_data.py   # patch workbooks, export prototype/data
.venv/bin/python scripts/check_prototype_sync.py   # Excel ↔ OpenAPI ↔ data ↔ docs; must print OK
```

## Phase 3

See [`docs/explainer-phase-split.md`](docs/explainer-phase-split.md).

## License

ISDA/EMTA PDFs: internal use per license. SmartDX screenshots: internal reference only.

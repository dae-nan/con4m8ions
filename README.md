# con4m8ions (CDU-PS)

Confirmation Document Utility — Product Spec for ISDA/EMTA **2026 FX Definitions** confirmation templates.

## Phase 1 (current)

Docs + Excel mapping + payload mocks only. No running UI or API.  
**TPs** = Transaction Processing systems. **SmartDX** = external vendor for ISDA confirmation letters.

| Artifact | Path |
| --- | --- |
| **PRD (v1.3)** | [`docs/prd-cdu-ps-v1.md`](docs/prd-cdu-ps-v1.md) |
| **Phase split explainer** | [`docs/explainer-phase-split.md`](docs/explainer-phase-split.md) |
| **Party A/B one-pager** | [`docs/party-ab-fxo-one-pager.md`](docs/party-ab-fxo-one-pager.md) |
| **Attribute Excel** | [`docs/mappings/cdu-ps-isda-2026-mapping.xlsx`](docs/mappings/cdu-ps-isda-2026-mapping.xlsx) |
| **FXO payload mocks** | [`docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx`](docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx) |
| **Feature / scenario / API specs** | [`specs/`](specs/) |
| **ISDA PDFs** | [`docs/reference/isda/`](docs/reference/isda/) |
| **SmartDX reference images** | [`docs/reference/smartdx/`](docs/reference/smartdx/) |

### PRD v1.3 highlights

- Plain-words story + MCA utility; phase split moved to explainer  
- Ontology with dotted optional lines; TemplatePackage / AssemblyRun borrowed into LDM  
- Target architecture: TPs → CDU-PS → SmartDX → CDU-PS → TPs; Swoosh + Compare X exception gates  
- Story map with triggers, altitudes, metrics, emotional JTBD; UC diagram + numbered edges  
- Timeline (per-trade + simple aggregates, FXO seed); Party A/B one-pager; ER + class LDM  
- DDD bounded contexts aligned to API groups  

### Regenerate (optional)

```bash
python3 scripts/generate_phase1_mapping.py
python3 scripts/generate_fxo_payload_mocks.py
```

## Phase 2 / 3

See [`docs/explainer-phase-split.md`](docs/explainer-phase-split.md).

## License

ISDA/EMTA PDFs: internal use per license. SmartDX screenshots: internal reference only.

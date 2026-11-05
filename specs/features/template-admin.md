# Feature: Template Admin Utility

## Intent

Version and bind **TemplatePackage** (MASTER tops-and-tails / Exhibit I + PRODUCT / Exhibit II-* + optional SUPPLEMENT); activate LIVE versions; hot-swap and rollback; trigger resend. Letter generation on the trade path is **AssemblyRun → SmartDX** (TPs → CDU-PS → SmartDX → CDU-PS → TPs).

## Core fields

See Excel `Template_Admin_Utility`.

| Field | Role |
| --- | --- |
| `templateBundleId` | Composite binding id |
| `masterTemplateId` | Exhibit I |
| `productExhibitId` / `productType` | Exhibit II-* routing |
| `supplementExhibitIds[]` | Elected III-* |
| `matrixBindings` | Version pins JSON |
| `mcaRequired` / `mcaProfileId` | MCA path |
| `version` / `status` | `DRAFT` \| `LIVE` \| `RETIRED` |
| `hotReloadEnabled` | Allow HOT_SWAP without redeploy |
| `rollbackTargetVersion` | Prior LIVE |
| `resendPolicy` | `AUTO` \| `MANUAL` after swap |
| `legalDefsYear` | `1998` \| `2026` |

## Behaviours

1. **Create version** — `POST /templates`, `PUT /templates/{id}/versions` → `DRAFT`  
2. **Activate** — `POST /templates/{id}/activate` → status `LIVE`; previous LIVE → `RETIRED` or retained as rollback target  
3. **Hot-swap** — change LIVE binding used by Template Engine for new composes; optionally auto-`RESEND` open docs  
4. **Rollback** — `POST /templates/{id}/rollback` to prior version  
5. **Audit** — `lastChangedBy` / `lastChangedAt` mandatory  

## Wrong → hot-swap → resend

Operational edge for FXO demo: wrong PRODUCT exhibit or version detected → activate correct LIVE → `POST /documents/{id}/resend` with `priorDocumentId` linkage and supersession language from Exhibit I closing.

## Acceptance

- Admin field inventory in Excel  
- API contract covers create / version / activate / rollback / resend  
- Scenario `specs/scenarios/hot-swap-resend.md` walks the edge

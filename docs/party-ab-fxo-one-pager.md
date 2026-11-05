# Party A vs Party B — Deliverable FX Option one-pager

Columnar attributes from LDM `Party` (+ letter elections). Seed trade `TR-FXO-001` (With_MCA sample). Mirror of Excel sheet `PartyAB_Attributes`.

| Attribute | LDM entity | Party A (us / sender) | Party B (counterparty) | Notes |
| --- | --- | --- | --- | --- |
| Role on confirm | Party.role | Party A | Party B | Exhibit I names |
| Buyer / Seller | FxOptionEconomics | Buyer = Party A | Seller = Party B | Sample FXO |
| Legal name | Party.name | Standard Chartered Bank Sample Desk | ACME Corp Treasury | Assumed sample |
| LEI | Party.lei | 5493001KJTIIGC8Y1R12 | 549300ABCDEFGH123456 | Format DQ |
| Address | Party.address | (desk letterhead) | 1 Example Street, London EC2N 1HQ | Exhibit I heading |
| City / postcode | Party (extended) | — | London / EC2N 1HQ | Optional enrich |
| Office | Party.office | Singapore | London | Exhibit I Offices |
| Notice contact | ExhibitILetter.elections | ops-fx@scb.example | fxconfirm@acme.example | New 2026 optional |
| Account / SSI | SettlementInstructions | Assumed SSI A | Assumed SSI B | With_MCA defaults |
| Calc agent election | ExhibitILetter / MasterConfirmation | Party A (Assumed MCA default) | — | Without_MCA: explicit |
| Master agreement date | LegalFramework / MCA | 2026-01-15 (Assumed) | same bilateral | With_MCA path |
| On novation | NovationTransfer | Remaining Party A | Transferor B → Transferee C | Regen letter parties |

**Sources:** LDM Excel; SmartDX-style Party A/B extractable fields in `docs/reference/smartdx/` (pattern only — FXO seed values are Assumed).

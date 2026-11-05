# Modelling decisions — trade, documentation, parties, product insert

| Item | Value |
| --- | --- |
| Status | Phase 2 — decided (user answers to handoff items 3–5) |
| Applies to | Excel `Attribute_Product_Map`, `Logical_Data_Model`, `PartyAB_Attributes`, payload mocks, [`specs/api/openapi.md`](../../specs/api/openapi.md) v1.6, `prototype/data/`, screens, stories |
| Grounding | ISDA/EMTA 2026 FX Definitions confirmation templates (Exhibit I, II-B, III) in [`docs/reference/isda/`](../reference/isda/) (text extract under `text/`); FpML `trade` / `party` / `documentation` conventions |
| Goal | One product-agnostic trade shape, so II-A … II-K and non-FX products reuse everything except `economics` |

## Trade shape

```text
trade
├── parties[]                {id, partyName, lei, address, office, noticeContact, settlementAccount}
├── product                  {productType, transactionType, buyerPartyReference.href, sellerPartyReference.href}
├── economics                product-specific terms only (II-B: strike, currencies, expiry, premium, …)
├── documentation
│   ├── masterAgreement      {masterAgreementType, masterAgreementDate, longFormFallback, governingLaw, terminationCurrency}
│   ├── masterConfirmation   {masterConfirmationId, masterConfirmationType, masterConfirmationDate} | null
│   ├── contractualDefinitions[]  {definitions, publisher, book, version}
│   └── contractualMatrix[]  {matrixType, version}   (empty = each matrix as at the Trade Date)
├── calculationAgent         {calculationAgentPartyReference.href, jointDisputeResolution}
└── brokerPartyReference     {href}
```

## Decisions

| # | Decision | Rationale |
| --- | --- | --- |
| MD-1 | Legal and documentation terms live in one trade-level `documentation` block: master agreement, master confirmation (MCA), contractual definitions, contractual matrix, plus the confirmation's own `governingLaw` and `acknowledgmentsAndRepresentations`. | FpML keeps these under `documentation`, outside the product, so every product shares them. Exhibit I treats them as wrapper terms: it incorporates "Version 1.0 of the Main Book of the 2026 FX Definitions" and has one agreement clause for an executed ISDA Master Agreement and another for the deemed long-form ISDA 2002. |
| MD-2 | Matrices are `contractualMatrix[] {matrixType, version}`. An empty list means each matrix applies as at the Trade Date. | The Exhibit I footnote says the Main Book and each Matrix are versioned separately, with matrices taken as at the Trade Date unless the parties pin a version. |
| MD-3 | `mcaPath` is derived and is never sent inbound. It is `With_MCA` exactly when `documentation.masterConfirmation` is set. It stays as a read-model field (book, trade snapshot, assembly `legal`, letter `path`). | Two inbound flags that can disagree are a data-quality trap. The master confirmation is the fact; the path is a projection of it. |
| MD-4 | There is one `parties[]` list. Each entry's `id` (`partyA`, `partyB`, `partyC`) is the target of every `…PartyReference.href`: buyer and seller in `product`, the calculation agent, the broker, and novation transferor, transferee and remaining party. Notice contact and settlement account live on the party. | This is FpML `party` / `partyReference`. The ISDA templates name Party A and Party B once in Exhibit I and then only elect roles (Buyer, Seller, Calculation Agent). Holding one record per party means LEI, office and notices cannot drift. |
| MD-5 | `product` holds identity and roles (`productType`, `transactionType` and the party references). `economics` holds product terms only, with no party data and no transaction type. | A new product (II-A … II-K or a non-FX product) only swaps `economics`. Routing and DQ rules on `product` stay generic. |
| MD-6 | The product insert has one name, `productInsert` = `{exhibitId, title, additionalProvisionExhibitIds}`. It is used for the Exhibit I template block, the letter's `blocks.productInsert` and the LDM `ExhibitILetter.productInsert`. | ISDA's Exhibit I placeholder reads "[Insert the relevant form of Confirmation from one of the templates in Exhibit II and, if applicable, the relevant Additional Provisions from one or more of the templates in Exhibit III.]" The name follows that wording and covers both halves (Exhibit II form plus Exhibit III Additional Provisions). It replaces `productInsertRef` and the block-level `productExhibitId`. |
| MD-7 | `masterConfirmationId` replaces `mcaProfileId`, and the LDM entity `McaProfile` becomes `MasterConfirmation`. | This aligns with FpML `masterConfirmation` and with ISDA "Master Confirmation Agreement" wording. |
| MD-8 | The assembly `legal` block is the Legal Resolver's result only: `{frameworkId, mcaPath, masterConfirmationId, longFormFallback}`. | The terms stay in `trade.documentation`, so nothing is copied that could go stale. |
| MD-9 | Attribute paths address list items by key, for example `trade.parties[id=partyA].lei` or `trade.documentation.contractualMatrix[matrixType=SRO].version`. | Paths stay stable when list order changes. The sync check and Excel use the same selector syntax. |

**Kept as is (noted):**
- Template config keeps `supplementExhibitIds` for Exhibit III (ISDA calls these "Additional Provisions"; the letter uses `additionalProvisionExhibitIds`).
- Package-level `matrixBindings` remains the template default, used when a trade has no `contractualMatrix` entry.
- Package `productExhibitId` remains the routing key.
- `general_terms` in `productBody.generalTerms` is the rendered II-B "General Terms" section (Buyer: "Party A"). It is rendered output, not trade data.

## Old → new paths

| Old (Phase 1) | New |
| --- | --- |
| `mcaPath`, `mcaProfileId`, top-level `legal.*` on `POST /events` | `trade.documentation.*`; `mcaPath` derived |
| `trade.legal.fxDefinitionsVersion` | `trade.documentation.contractualDefinitions[0].version` |
| `trade.legal.isdaMaster.date` | `trade.documentation.masterAgreement.masterAgreementDate` |
| `trade.legal.longFormFallback` / `governingLaw` / `terminationCurrency` | `trade.documentation.masterAgreement.*` |
| `trade.legal.governingLawConfirm` | `trade.documentation.governingLaw` |
| `trade.legal.matrix.sroVersion` | `trade.documentation.contractualMatrix[matrixType=SRO].version` |
| `trade.legal.mca.*` | `trade.documentation.masterConfirmation.*` |
| `trade.legal.calculationAgent` | `trade.calculationAgent.calculationAgentPartyReference.href` |
| `trade.parties.partyA.name` / `.lei` / `.office` | `trade.parties[id=partyA].partyName` / `.lei` / `.office` |
| `trade.parties.buyer` / `.seller` | `trade.product.buyerPartyReference.href` / `sellerPartyReference.href` |
| `trade.economics.buyer` / `.seller` / `.transactionType` | removed / `trade.product.*` |
| `trade.notices.partyA` | `trade.parties[id=partyA].noticeContact` |
| `trade.settlement.accountPartyA` | `trade.parties[id=partyA].settlementAccount` |
| `trade.parties.brokerArranger` | `trade.brokerPartyReference.href` |
| `novation.transferee` (party data) | `transfereePartyReference.href` (party in `trade.parties`) |
| `ExhibitILetter.productInsertRef`, block `productExhibitId` | `productInsert` |

## Examples

| Field | File | Path | Value |
| --- | --- | --- | --- |
| Party B name | `prototype/data/inbound/trades/TR-FXO-001.new-trade.json` | `trade.parties[id=partyB].partyName` | `ACME Corp Treasury` |
| Buyer reference | `prototype/data/inbound/trades/TR-FXO-001.new-trade.json` | `trade.product.buyerPartyReference.href` | `partyA` |
| Master agreement | `prototype/data/inbound/trades/TR-FXO-001.new-trade.json` | `trade.documentation.masterAgreement.masterAgreementType` | `ISDA2002` |
| Master confirmation | `prototype/data/inbound/trades/TR-FXO-001.new-trade.json` | `trade.documentation.masterConfirmation.masterConfirmationId` | `MCA-SCB-ACME-2026-001` |
| Definitions | `prototype/data/inbound/trades/TR-FXO-001.new-trade.json` | `trade.documentation.contractualDefinitions[0].definitions` | `2026 FX Definitions` |
| Without MCA | `prototype/data/inbound/trades/TR-FXO-005.new-trade.json` | `trade.documentation.masterConfirmation` | `null` |
| Long-form fallback | `prototype/data/inbound/trades/TR-FXO-005.new-trade.json` | `trade.documentation.masterAgreement.longFormFallback` | `true` |
| Party B (TR-FXO-005) | `prototype/data/inbound/trades/TR-FXO-005.new-trade.json` | `trade.parties[id=partyB].partyName` | `Globex Holdings Ltd` |
| Derived MCA path | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `mcaPath` | `With_MCA` |
| Resolver result | `prototype/data/outbound/api-responses/TR-FXO-001/02-get-assembly.legal-resolved.200.json` | `legal.masterConfirmationId` | `MCA-SCB-ACME-2026-001` |
| Template insert | `prototype/data/templates/fxo-deliverable-2026/exhibit-i-master.json` | `blocks[4].productInsert.exhibitId` | `II-B` |
| Letter insert | `prototype/data/outbound/smartdx/DOC-001.send.json` | `exhibitILetter.blocks.productInsert.title` | `Confirmation of a Deliverable FX Option Transaction` |

## EDGE / STUB

- Only II-B economics are deep-modelled. Other products keep exhibit-level rows in `Attribute_Product_Map` with `ProductEconomics`.
- `settlementAccount`, `calculationAgent` and `brokerPartyReference` are mapped, but the sample trades do not populate them. The letter prints placeholders.
- Pinned matrix versions (non-empty `contractualMatrix`) and Exhibit III Additional Provisions are not simulated.
- Novation uses party references in the payload-mocks workbook only. No novation flow is simulated.

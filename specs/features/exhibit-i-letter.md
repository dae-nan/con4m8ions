# Feature: Exhibit I Confirmation Letter (MASTER)

## Intent

Model Exhibit I as the **ISDA confirmation letter wrapper** — not a thin header. The letter introduces the trade, incorporates the 2026 FX Definitions, subjects the trade to the Master Agreement (or long-form fallback), carries shared elections, inserts the Product/Supplement body, and closes with supersession + signatures.

## Letter blocks → fields

| Block | Key fields | TPS / compose path examples |
| --- | --- | --- |
| Heading | Party A letterhead, Confirmation Date, Party B name & address | `confirmation.header.*` |
| Intro | Purpose paragraph; Trade Date reference | composed text |
| Definitions | FX Definitions version election | `trade.legal.fxDefinitionsVersion` |
| Agreement | ISDA Master date (With_MCA) **or** long-form fallback (Without_MCA) | `trade.legal.isdaMaster.date` / `trade.legal.longFormFallback` |
| **Insert point** | Exhibit II-* (+ III-*) body | Template Engine splice |
| Elections | LEI A/B, Fallback Benchmark, Acks/Reps, Calculation Agent, Joint CA dispute | `trade.parties.*.lei`, `trade.legal.calculationAgent`, … |
| Accounts | Account Party A/B | `trade.settlement.accountParty*` |
| Offices / Broker | Offices, Broker/Arranger | `trade.parties.*.office` |
| Law / Notices | Governing law (if no Master), notice contacts | `trade.legal.governingLawConfirm`, `trade.notices.*` |
| Closing | Supersession; please confirm… | `confirmation.closing.supersession` |
| Signatures | Party A; Party B confirm-as-of | `confirmation.signatures.*` |

## Wrap rule for II-B

```text
Exhibit I [Heading … Agreement]
  + II-B product economics
  + Σ elected III-*
Exhibit I [Additional elections … Closing … Signatures]
```

## MCA impact on letter

| Path | Letter behaviour |
| --- | --- |
| With_MCA | Short-form Master subject clause; CA/notices/SSI may default from Assumed MCA |
| Without_MCA | Long-form binding agreement language; explicit governing law / termination currency |

## Mocks

See `docs/mappings/cdu-ps-fxo-deliverable-payload-mocks.xlsx` sheets `With_MCA` / `Without_MCA` columns for `smartdx.exhibitILetter` text and structured blocks.

## Acceptance

- PRD §5 documents structure  
- Attribute_Product_Map retains Exhibit I COMMON rows  
- Payload mocks include full letter draft for NEW_TRADE (both MCA paths)

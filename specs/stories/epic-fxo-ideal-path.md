# Epic: FXO ideal path — new trade to affirmed, with TPs callbacks

| Item | Value |
| --- | --- |
| Story map | PRD §9.3 K2 Book and assemble → S2 Assemble FXO letter · K3 Send and match → S3 SmartDX then affirm |
| Feature specs | [`specs/features/fxo-deliverable-lifecycle.md`](../features/fxo-deliverable-lifecycle.md) · [`specs/features/exhibit-i-letter.md`](../features/exhibit-i-letter.md) · [`specs/features/attribute-product-mapping.md`](../features/attribute-product-mapping.md) |
| Scenarios | [`specs/scenarios/affirm-callback.md`](../scenarios/affirm-callback.md) · [`specs/scenarios/mca-vs-no-mca.md`](../scenarios/mca-vs-no-mca.md) |
| Screens | [`01-ops-desk`](../../docs/design/screens/01-ops-desk.md) · [`03-manual-draft`](../../docs/design/screens/03-manual-draft.md) · [`04-fxo-timeline`](../../docs/design/screens/04-fxo-timeline.md) |
| Simulation | flow B (TR-FXO-001, steps B01–B15) and flow C (TR-FXO-005, steps C01–C11) |

Examples tables are checked by `scripts/check_prototype_sync.py`: each `File` + `Path` must resolve to `Value`.

## Story FX-1 — Accept a NEW_TRADE from TPs (F2b Prepare MCA and DQ)

As TPs I want CDU-PS to accept a NEW_TRADE event and tell me where to follow it, so that booking is not blocked on document work.

```gherkin
Given package TB-FXO-DEL-2026-001 version 1.1.0 is LIVE
When TPs sends POST /events with NEW_TRADE evt_1001 for TR-FXO-001 on the With_MCA path
Then CDU-PS replies 202 ACCEPTED with trade status Received and assembly run AR-FXO-001-01
And DQ passes and the Legal Resolver picks With_MCA profile MCA-SCB-ACME-2026-001
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| event type | `prototype/data/inbound/trades/TR-FXO-001.new-trade.json` | `eventType` | `NEW_TRADE` |
| MCA path in | `prototype/data/inbound/trades/TR-FXO-001.new-trade.json` | `mcaPath` | `With_MCA` |
| 202 status | `prototype/data/outbound/api-responses/TR-FXO-001/01-post-events.202.json` | `status` | `ACCEPTED` |
| trade status | `prototype/data/outbound/api-responses/TR-FXO-001/01-post-events.202.json` | `tradeStatus` | `Received` |
| assembly run | `prototype/data/outbound/api-responses/TR-FXO-001/01-post-events.202.json` | `assemblyRunId` | `AR-FXO-001-01` |
| DQ | `prototype/data/outbound/api-responses/TR-FXO-001/02-get-assembly.legal-resolved.200.json` | `dq.status` | `PASSED` |
| MCA profile | `prototype/data/outbound/api-responses/TR-FXO-001/02-get-assembly.legal-resolved.200.json` | `legal.mcaProfileId` | `MCA-SCB-ACME-2026-001` |

## Story FX-2 — Locate the LIVE package and assemble the letter (F2a Locate package, F2c Auto or manual draft)

As CDU-PS I want to pick the LIVE FXO package by selection rule and assemble Exhibit I + II-B automatically, so that the letter needs no human touch.

```gherkin
Given TR-FXO-001 passed DQ and legal resolution
When the Template Engine applies selection rule PSR-FXO-DEL-2026-001
Then package TB-FXO-DEL-2026-001 version 1.1.0 is pinned to the run
And GET /assemblies/{id} shows status COMPLETED with confirmation CONF-001 and document DOC-001
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| rule | `prototype/data/outbound/api-responses/TR-FXO-001/03-get-assembly.package-located.200.json` | `package.ruleId` | `PSR-FXO-DEL-2026-001` |
| pinned version | `prototype/data/outbound/api-responses/TR-FXO-001/03-get-assembly.package-located.200.json` | `templateVersion` | `1.1.0` |
| mode | `prototype/data/outbound/api-responses/TR-FXO-001/04-get-assembly.completed.200.json` | `assemblyMode` | `AUTOMATED` |
| status | `prototype/data/outbound/api-responses/TR-FXO-001/04-get-assembly.completed.200.json` | `status` | `COMPLETED` |
| confirmation | `prototype/data/outbound/api-responses/TR-FXO-001/04-get-assembly.completed.200.json` | `confirmationId` | `CONF-001` |
| document | `prototype/data/outbound/api-responses/TR-FXO-001/04-get-assembly.completed.200.json` | `documentId` | `DOC-001` |

## Story FX-3 — Send to SmartDX and tell TPs (F3a Channel send, F3b Callback TPs)

As TPs I want a callback when the confirmation is generated, so that the trade record shows the document reference.

```gherkin
Given DOC-001 is assembled for TR-FXO-001
When CDU-PS sends it with POST /mock/smartdx/documents
Then the SmartDX mock returns GENERATED with SDX-DOC-001
And CDU-PS calls POST /callbacks/tps with status GENERATED and template version 1.1.0
And the trade moves Sent → AffirmPending
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| channel | `prototype/data/outbound/smartdx/DOC-001.send.json` | `channel` | `SmartDX` |
| letter Party B | `prototype/data/outbound/smartdx/DOC-001.send.json` | `exhibitILetter.blocks.heading.partyBName` | `ACME Corp Treasury` |
| SmartDX status | `prototype/data/outbound/smartdx/DOC-001.generated.json` | `status` | `GENERATED` |
| SmartDX id | `prototype/data/outbound/smartdx/DOC-001.generated.json` | `smartdxDocumentId` | `SDX-DOC-001` |
| callback status | `prototype/data/outbound/tps-callbacks/TR-FXO-001.01-generated.json` | `status` | `GENERATED` |
| callback version | `prototype/data/outbound/tps-callbacks/TR-FXO-001.01-generated.json` | `templateVersion` | `1.1.0` |
| timeline after send | `prototype/data/timeline/TR-FXO-001.json` | `events[6].status` | `AffirmPending` |

## Story FX-4 — Record the affirmation and tell TPs (F3c Affirm webhook, F3b Callback TPs)

As TPs I want to hear when the counterparty affirms, so that the trade can close its confirmation obligation.

```gherkin
Given TR-FXO-001 is AffirmPending on DOC-001
When the affirmation webhook POST /webhooks/affirmation reports Affirmed with no differences at 15:04:05Z
Then CDU-PS marks the trade Affirmed, updates SmartDX status, and calls POST /callbacks/tps with AFFIRM Affirmed
And GET /trades/{id} shows status Affirmed
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| webhook status | `prototype/data/inbound/webhooks/DOC-001.affirmed.json` | `status` | `Affirmed` |
| webhook response | `prototype/data/outbound/api-responses/TR-FXO-001/05-post-webhooks-affirmation.200.json` | `tradeStatus` | `Affirmed` |
| not a duplicate | `prototype/data/outbound/api-responses/TR-FXO-001/05-post-webhooks-affirmation.200.json` | `duplicate` | `false` |
| SmartDX update | `prototype/data/outbound/smartdx/DOC-001.status-affirmed.json` | `affirmationStatus` | `Affirmed` |
| callback event | `prototype/data/outbound/tps-callbacks/TR-FXO-001.02-affirmed.json` | `eventType` | `AFFIRM` |
| callback status | `prototype/data/outbound/tps-callbacks/TR-FXO-001.02-affirmed.json` | `affirmationStatus` | `Affirmed` |
| trade status | `prototype/data/outbound/api-responses/TR-FXO-001/06-get-trade.200.json` | `status` | `Affirmed` |

## Story FX-5 — Finish a letter by manual draft (F2c Auto or manual draft, mode a)

As an ops analyst I want to load the LIVE template filled with trade data, edit the one block the counterparty asked about, and submit, so that bespoke wording still goes through CDU-PS.

```gherkin
Given TPs sent TR-FXO-005 for Globex Holdings Ltd with requested mode MANUAL_DRAFTING
And the assembly run AR-FXO-005-01 is PENDING_MANUAL_DRAFT on version 1.1.0
When u.ops.tan loads GET /assemblies/{id}/shell, edits the Calculation Agent in block elections and saves with PUT /assemblies/{id}/manual-draft
And submits with POST /assemblies/{id}/submit
Then draft MDC-005-01 is audited, the run completes with DOC-105, SmartDX receives the edited letter and TPs gets a GENERATED callback
```

| Then | File | Path | Value |
| --- | --- | --- | --- |
| requested mode | `prototype/data/inbound/trades/TR-FXO-005.new-trade.json` | `assembly.requestedMode` | `MANUAL_DRAFTING` |
| run status | `prototype/data/outbound/api-responses/TR-FXO-005/02-get-assembly.pending-manual-draft.200.json` | `status` | `PENDING_MANUAL_DRAFT` |
| editable block | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `editableBlocks[0]` | `elections` |
| CA before | `prototype/data/outbound/api-responses/TR-FXO-005/03-get-assembly-shell.200.json` | `exhibitILetter.blocks.elections.calculationAgent` | `Party A` |
| draft id | `prototype/data/outbound/api-responses/TR-FXO-005/04-put-manual-draft.200.json` | `id` | `MDC-005-01` |
| drafted by | `prototype/data/outbound/api-responses/TR-FXO-005/04-put-manual-draft.200.json` | `draftedBy` | `u.ops.tan` |
| submit status | `prototype/data/outbound/api-responses/TR-FXO-005/05-post-submit.200.json` | `status` | `COMPLETED` |
| document | `prototype/data/outbound/api-responses/TR-FXO-005/05-post-submit.200.json` | `documentId` | `DOC-105` |
| SmartDX letter CA | `prototype/data/outbound/smartdx/DOC-105.send.json` | `exhibitILetter.blocks.elections.calculationAgent` | `Party A; provided that if an Event of Default has occurred with respect to Party A, Party B may appoint a leading dealer as Calculation Agent` |
| callback status | `prototype/data/outbound/tps-callbacks/TR-FXO-005.01-generated.json` | `status` | `GENERATED` |

## Out of scope (EDGE / STUB)

Unmatched / Disputed affirmations, Compare X gate, SWIFT and paper channels, channel errors, AMEND / NOVATION / EXERCISE ([`specs/scenarios/novation.md`](../scenarios/novation.md)), manual mode (b) data entry.

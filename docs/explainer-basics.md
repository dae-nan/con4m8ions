# CDU-PS basics explainer

Plain-language notes for ops analysts and interns. Kept **out of** the early PRD story so the job comes first.  
PRD pointer: [`docs/prd-cdu-ps-v1.md`](prd-cdu-ps-v1.md). Phase table also mirrored from the old phase-split note.

**Naming:** **TPs** = Transaction Processing systems. **SmartDX** = external vendor that generates the ISDA confirmation letter.

---

## 1. Affirmation vs confirmation

| Word | Meaning |
| --- | --- |
| **Confirmation** | The letter **we send** that states the deal (Exhibit I + product body). |
| **Affirmation** | The **other side’s reply**: matches / unmatched / disputed. |

Sending is not the finish line. Affirmed is.

---

## 2. Termsheet vs confirmation vs settlement

| Artifact | Job |
| --- | --- |
| Termsheet | Short commercial summary while negotiating. |
| Confirmation | Formal ISDA-style record of trade terms. |
| Settlement | Later cash/currency move when the deal pays or delivers. |

A confirm can describe settlement dates and accounts. Settlement systems still do the actual pay.

---

## 3. MCA (Master Confirmation Agreement)

| Idea | Meaning |
| --- | --- |
| MCA | Side agreement with default elections for many FX confirms. |
| With MCA | Short letter; defaults from MCA profile (**Assumed** sample in Excel). |
| Without MCA | Long-form Exhibit I; fill elections yourself. |

**Utility:** shared MCA → each confirm stays shorter. CDU-PS supports **both** paths.

---

## 4. Why FX often has no CSA

A **CSA** (Credit Support Annex) is about posting collateral under an ISDA. Many short-dated FX flows settle fast (or via CLS), so desks often skip CSA for those trades. Credit still exists; the docs pack differs. FXO happy path does not require CSA fields.

---

## 5. Matrices vs Exhibit III supplements

| Thing | Is | Is not |
| --- | --- | --- |
| **Matrix** (SRO / EM Currency) | Versioned lookup table; pin a version | Letter body |
| **Exhibit III** | Optional extra confirm clauses (barrier, averaging, disruption…) | A matrix |

Matrix = lookup data. Supplement = extra clauses on the confirm.

---

## 6. Phase split

| Thing | Phase 1 | Phase 2 | Phase 3 |
| --- | --- | --- | --- |
| PRD, Excel maps, light API/feature specs, payload mocks | Yes | Tweak from build learnings | — |
| **ASCII wireframes** (ops desk screens) | Plan only — **not drawn in Phase 1** | **Start here** before coding UI | — |
| HTML5 ops desk + Python services (Mac-first) | No | Yes (after wireframes) | — |
| Live SmartDX / SWIFT / Swoosh / Compare X | Spec + mocks | Mock first, then wire | — |
| AI / chatbot / MCP agents | Thinking + stubs only | Empty stubs OK | Build |

**Rule:** Phase 1 = what and how it should behave. Phase 2 = wireframes first, then make it run. Phase 3 = agent helpers.

### Phase 2 kickoff (locked plan)

Phase 2 **starts** with a short re-read of this PRD pack, then **ASCII wireframes** for the main ops journeys (template admin, assemble/send FXO, timeline, manual draft, exception queues) **before** HTML/Python implementation. Full wireframe drawing is **not** a Phase 1 deliverable.

---

## 7. Related docs

- PRD: `docs/prd-cdu-ps-v1.md`  
- Party A/B one-pager: `docs/party-ab-fxo-one-pager.md`  
- Legacy pointer: `docs/explainer-phase-split.md` → this file  

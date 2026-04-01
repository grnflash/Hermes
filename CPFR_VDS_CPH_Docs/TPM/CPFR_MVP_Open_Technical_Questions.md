# CPFR in CPH — MVP Open Technical Questions (LOE spike)

**Companion to:** `CPFR_User_Stories-MVP_R2.2.docx`  
**Purpose:** Track open technical items without embedding them in the main user-stories document. Update section numbers if the main document structure changes.

---

## OQ-1 — Vendor identity handoff to Tableau iframe

| Field | Detail |
|--------|--------|
| **Question** | How does CPH pass `vendor_id` (or equivalent) to the embedded Tableau workbook so row-level security / filtering is correct? Does the existing VC module already resolve vendor identity from the logged-in session such that CPFR can reuse the same pattern? |
| **Owner** | Harish + Stefan (SC-BIE as needed); Nathan to facilitate |
| **References** | Main doc §2 **V-1** — Acceptance Criteria (vendor isolation / single-vendor data) |
| **If unresolved** | V-1 isolation AC is hard to estimate |

---

## OQ-2 — Tableau iframe configuration

| Field | Detail |
|--------|--------|
| **Question** | SC-BIE publishes the CPFR Tableau workbook; CPH embeds via iframe. What are the concrete config requirements (URL parameters, token handoff, allowed origins, sizing)? |
| **Owner** | Harish + SC-BIE |
| **References** | Main doc §2 **V-1**, **V-3**, **V-5**; Figure 2 (viewport) |
| **If unresolved** | Iframe integration scope for viewer stories is unclear |

---

## OQ-3 — Role-based provisioning / CPFR subscription type

| Field | Detail |
|--------|--------|
| **Question** | What is the LOE to extend CPH provisioning so the CPFR subscription checkbox (production may still label it "Demand Forecast") correctly gates CPFR viewer access and email triggers? |
| **Owner** | Harish / Gangi |
| **References** | Main doc §2 **V-4** — Enable reports / Edit User modal; Figure 3 |
| **If unresolved** | V-4 contact/subscription ACs are hard to estimate |

---

## OQ-4 — TM-1 RBAC and surface location

| Field | Detail |
|--------|--------|
| **Question** | Exact CPH role names, navigation entry point, and guardrails for TM-1 (who may edit which vendors' tier/contacts). |
| **Owner** | Harish + Replen Tech / CPH PM |
| **References** | Main doc §2 **TM-1** |
| **If unresolved** | TM-1 LOE range stays wide |

---

*Document generated to support R2.2 package. Renumber references if §2 story order or main-doc section titles change.*

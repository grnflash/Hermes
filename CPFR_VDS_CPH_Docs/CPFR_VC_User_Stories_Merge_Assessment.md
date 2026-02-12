# CPFR & Vendor Compliance User Stories: Merge Assessment

**Document Type:** Working assessment for review before drafting merged user stories  
**Last Updated:** 2026-02-04  
**Purpose:** Identify which user stories from the CPFR Platform & Portal User Stories and the Vendor Compliance (CPH) User Stories can be merged (with dual applicability) vs. kept separate, aligned with the merged BRD and BRD merge assessment.

**Source Documents:**
- *CPFR Plat & Port - User Stories* (Problem Definition & User Needs): Vendor (V-1–V-5), ISM (I-1–I-4), CPFR Team (P-1–P-3), BIE (B-1–B-2), Cross-Team (C-1)
- *Vendor Compliance - User Stories*: 10 themes with sub-stories (Vendor, Category Manager, Compliance Manager, Manager personas)

**Reference Context:** CPH Portal Platform BRD CPFR VC Merged Draft; CPFR_VC_BRD_Merge_Step1_Assessment (combine vs. keep separate).

---

## Summary for Review

| Category | Count | Approach |
|----------|--------|----------|
| **Merge (dual applicability)** | 5 groupings | Single story or paired internal/vendor story with "(Applies to CPFR and Vendor Compliance)" or equivalent; reduces duplication and supports one CPH experience. |
| **Keep separate — CPFR-only** | 10 stories | Platform scale, data consistency, analytical depth, historical data, governance, BIE/CPFR team; no VC analogue. |
| **Keep separate — VC-only** | 4 groupings | Chargeback/violation access, dispute resolution, scalability ($21M), Compliance Manager table outputs / Tableau. |
| **Stand apart (different persona or scope)** | 2 | Cross-team extensibility (C-1); VC proof-of-delivery / manager accountability (can be one VC-flavored story that references shared email capability). |

---

## 1. Stories to MERGE (Complementary or Redundant — Dual Applicability)

These describe the same capability from CPFR vs. VC perspective. The merged BRD already combines Vendor Administration, Communication & Email, Data Isolation, and CPH Integration; user stories should mirror that with explicit dual applicability where appropriate.

### 1.1 Single Location for Reports / On-Demand Access (Vendor)

| Source | Story | Merge rationale |
|--------|------|-----------------|
| **CPFR** V-1 | Access CPFR data on-demand, 24/7, via portal, email, or both; proactively address issues without waiting for scheduled reports | Same need: one place to get data/reports, on-demand, preferred modality. |
| **VC** #1a | As a Vendor, single consistent location to access reports/insights without sorting through dozens of emails | Same need. |
| **VC** #2a | As a Vendor, access historical chargeback data and documentation in CPH (VC-specific *content*, same *capability*: centralized access) | Centralized access; content (chargeback) is VC; capability (single location in CPH) is shared. |

**Proposed merged story (dual applicability):**

- **As a vendor**, I need **a single, consistent location in CPH** where I can access the reports and data that matter to me (**CPFR and/or chargeback/compliance**) on-demand, 24/7, via my preferred method (portal, email, or both), **so that** I can manage my business and address issues without sorting through dozens of emails or waiting for scheduled reports.  
- **Note:** VC-specific variant can add: “including historical chargeback/compliance data and documentation when applicable.”

**Recommendation:** One primary merged vendor story; optional short bullet under “Acceptance / Scope” that CPFR content includes forecast/inventory/etc., and VC content includes chargeback/violation reports and history.

---

### 1.2 Contact Information & Report Distribution Preferences (Vendor + Internal)

| Source | Story | Merge rationale |
|--------|------|-----------------|
| **CPFR** V-4 | Manage contact information, notification preferences, data recipients; data secure and only to own staff; no ISM intervention for admin changes | Same capability: self-service contact and distribution. |
| **VC** #6a | Vendor manage contact and distribution preferences; self-manage in one place; grant access based on admin credentials | Same capability. |
| **VC** #6b | Manager: multiple tables, overwriting risk, confirm which reports vendors refer to | Same problem: fragmented contact/distribution; combined admin fixes it. |
| **VC** #4a | Category Manager: control which vendors have access to which reports; add/remove from distributions | Same capability as internal side of CPFR REQ-5.3 / BRD REQ-1.1 (assign/remove report access by vendor). |

**Proposed merged stories:**

- **Vendor (dual):** As a vendor, I need to **manage my contact information and report distribution preferences** (for **CPFR and/or chargeback/compliance**) in one place in CPH, **so that** the right people receive the right reports and I can make changes without tickets or ISM intervention. *(Acknowledge dual applicability: CPFR and VC contact/recipient lists remain manageable as separate elements per merged BRD.)*
- **Internal (dual):** As a Category Manager / In-Stock Manager, I need **one interface in CPH** to assign or remove report access by vendor and to manage which reports go to which stakeholders, with **CPFR report tier/config and VC report config as distinct, configurable elements**, **so that** each partner receives only the information aligned to their strategy and we avoid overwrites and confusion across systems.

**Recommendation:** Two merged stories (vendor + internal); acceptance criteria reference “CPFR and VC contact/recipient lists manageable as separate elements” and “use/expand CPH’s existing user self-service admin facility” per merged BRD.

---

### 1.3 Internal Visibility: Same Reports/Data as Vendors (Category Manager / ISM)

| Source | Story | Merge rationale |
|--------|------|-----------------|
| **CPFR** I-1 | ISM reference same data as vendors; consistent interface; productive conversations without data reconciliation | Same outcome: internal sees what vendor sees. |
| **VC** #2b | Category Manager: visibility into all vendor reports in CPH; quick reference, validate performance, no manual file sharing | Same outcome. |
| **VC** #7a | Category and In-Stock Manager: access to reports vendors receive; visibility for effective engagement when vendor references data | Same outcome. |

**Proposed merged story (dual applicability):**

- **As a Category Manager / In-Stock Manager**, I need **access within CPH to the same reports and data that vendors receive** (for **CPFR and/or chargeback/compliance**), **so that** I can reference them, validate performance, and engage effectively when vendors reference the data or request follow-up, without relying on manual file sharing or conflicting sources.

**Recommendation:** One merged internal story; applies to both CPFR and VC content in CPH.

---

### 1.4 Email Reports / Modalities and Control (Vendor + Manager)

| Source | Story | Merge rationale |
|--------|------|-----------------|
| **CPFR** V-1, NFR | Portal + email modalities; vendor preference | Same system: email driven from CPH contact/distribution. |
| **VC** #10a | Vendor: control which reports are emailed to which team members; different functions need different reports | Same capability; VC emphasizes per-report, per-recipient control. |
| **VC** #10b | Manager: vendors engaged with reports; proactive notifications; **proof of delivery** | Proof of delivery is VC-specified but can apply to both if email is unified. |

**Proposed merged stories:**

- **Vendor (dual):** As a vendor, I need to **choose how I receive reports** (portal, email, or both) and **control which reports are emailed to which team members** (for **CPFR and/or chargeback/compliance**), **so that** each of my teams (catalog, production, replenishment, etc.) gets the right information and I can use automated systems that consume emailed reports where needed.
- **Manager (VC-led, shared capability):** As a Manager, I need vendors to remain engaged with performance reports and receive proactive notifications, and I need **proof of delivery** where reports are emailed, **so that** I can hold them accountable for metrics and ensure timely action. *(Label as “Applies to CPFR and Vendor Compliance” where the same email system is used.)*

**Recommendation:** One merged vendor story; one manager story that explicitly applies to both CPFR and VC when the same CPH-driven email and contact management is used.

---

### 1.5 Report Distribution / Access Control (Internal) — Already Covered

Report distribution and “who gets which reports” are already merged under **1.2 Internal (Category Manager / ISM)**. VC #4 and CPFR REQ-5.3 / BRD REQ-1.1 are the same requirement: one combined internal story suffices (see 1.2).

---

## 2. Stories to KEEP SEPARATE — CPFR-Only

These reflect platform scale, data governance, analytical depth, historical CPFR data, or CPFR-specific roles. No VC analogue; keep as distinct CPFR user stories.

| ID | Story | Rationale |
|----|-------|-----------|
| **V-2** | View Consistent Data with ISM (same data when we discuss performance) | CPFR data consistency / single source of truth; VC has different content (chargeback reports), not “same calculation view.” |
| **V-3** | Access Appropriate Analytical Depth (tier, planning needs) | CPFR tier structure and analytical depth; VC reports are not tiered in the same way. |
| **V-5** | Access Historical Data (2 years, daily granularity, trends, forecast accuracy) | CPFR historical data retention; VC has “historical repository” but different grain and purpose. |
| **I-2** | Access Cross-Vendor Analytics with Flexible Scope | ISM cross-vendor CPFR analytics; internal override; CPFR platform scope. |
| **I-3** | Reduce Time on Routine Data Work | ISM capacity reallocation; CPFR-specific (prep, validation, report delivery). |
| **I-4** | Customize Vendor Data Views (metrics, high-touch) | CPFR metric-level customization; VC report types are configured but not “analytical depth” in same sense. |
| **P-1** | Establish Single Source of Truth with Governance | CPFR platform governance; daily snapshots, lineage. |
| **P-2** | Provide Definitive Audit Trails | CPFR data lineage and access logs. |
| **P-3** | Support Advanced Analytics and Cross-Team Sharing | CPFR AI/ML, shared definitions; platform extensibility. |
| **B-1** | Scale Data Access Without Proportional Overhead | CPFR scale (3K–5K vendors, 6.6K+ reads); VC scale is different (123 → thousands). |
| **B-2** | Provide Unified Data Access Layer | CPFR unified data layer; internal tools, shadow tools. |

**Recommendation:** Keep these 10 stories in a **CPFR-only** section of the merged document; no merging with VC stories.

---

## 3. Stories to KEEP SEPARATE — VC-Only

These reflect chargeback/violation content, dispute resolution, Compliance Manager persona, or VC program scalability. No CPFR analogue.

### 3.1 Centralized Chargeback/Compliance Access and Historical Repository (Vendor + Internal)

| Source | Story | Rationale |
|--------|------|------------|
| **VC** #2a | Vendor: historical chargeback data and documentation in CPH; analyze issues, resolve disputes, track trends | *Capability* merged in 1.1 (single location); *content* (chargeback, disputes) is VC-only. Optional VC-specific acceptance criterion under 1.1 or a short VC-only story: “As a vendor, I need to access my historical chargeback/compliance data and documentation in CPH so that I can analyze issues, resolve disputes, and track trends without searching old emails.” |
| **VC** #2b | Category Manager: visibility into all vendor reports | Merged in 1.3 (internal visibility). |

**Recommendation:** If 1.1’s acceptance criteria explicitly call out “historical chargeback/compliance data and documentation,” a separate VC #2a story may be redundant; otherwise one short **VC-only** story for “historical chargeback/compliance repository and self-service retrieval” keeps VC scope clear.

---

### 3.2 Time to Resolution / Dispute Process (Vendor + Compliance Manager)

| Source | Story | Rationale |
|--------|------|------------|
| **VC** #3 | Vendor: resolving chargebacks takes too long; multiple emails, Oracle CRM, reattach docs; want fewer clicks and less time | VC-only: dispute workflow. |
| **VC** #8a | Vendor: view all chargebacks and file disputes in one platform; no redirect to another portal; no duplicate uploads | VC-only: dispute UX. |
| **VC** #8b | Compliance Manager: ~30% efficiency gain if supporting documents and case details in one platform | VC-only: dispute resolution efficiency. |

**Proposed (keep as VC-only, can be two stories or one vendor + one internal):**

- **Vendor:** As a vendor, I need to **view all my chargebacks and file disputes in a single interface within CPH** (without being redirected to Oracle CRM or re-uploading documentation), **so that** I can resolve issues in fewer steps and less time (target: fewer than 5 clicks and 5 minutes).
- **Compliance Manager:** As a Compliance Manager, I need **all dispute supporting documents and case details in one platform**, **so that** dispute resolution efficiency can improve (e.g., ~30%) and we can reduce Oracle CRM ticket volume.

**Recommendation:** Keep **VC-only**; no CPFR equivalent. Optionally reference merged BRD REQ-12.x (Dispute Resolution).

---

### 3.3 Report Distribution / Access Control — Scalability and Program Expansion

| Source | Story | Rationale |
|--------|------|------------|
| **VC** #5 | Compliance Manager: scalable framework for chargeback defects; expand program without proportional manual workload; capture $21M entitlement | VC program scalability (123 → thousands); CPFR scale is platform/concurrent users, not “chargeback program expansion.” |

**Proposed (VC-only):**

- **As a Compliance Manager**, I need a **scalable framework in CPH** to manage chargeback/compliance reporting and defects across the company, **so that** we can expand the program (e.g., toward the $21M entitlement opportunity) without increasing manual workload proportionally.

**Recommendation:** **VC-only**; CPFR has B-1 (platform scale) but not “chargeback program expansion.”

---

### 3.4 Data Structures, Table Outputs, and Cross-Team Visibility (Internal — VC)

| Source | Story | Rationale |
|--------|------|------------|
| **VC** #9a | Category Manager: understand data sharing level with a vendor without logging into CPH; Tableau view or data output across vendor base | VC/chargeback reporting and analytics; internal table outputs. |
| **VC** #9b | Compliance Manager: table outputs from CPH (disputes, vendor feedback, ticket dispositions, usage, program performance) | VC program performance and dispute analytics. |

**Proposed (VC-only, can be one or two stories):**

- **As a Category Manager**, I need **Tableau views or data outputs** that show data-sharing levels across the vendor base (without requiring CPH login where specified), **so that** I can understand vendor engagement and sharing at a glance.
- **As a Compliance Manager**, I need **table outputs from CPH** (e.g., chargeback disputes, vendor feedback, ticket dispositions, usage, program performance), **so that** I can build tools to measure and evaluate program performance.

**Recommendation:** **VC-only**; CPFR has internal tools (Tableau, Plotly) but for CPFR data, not chargeback/dispute/usage metrics.

---

## 4. Stories to STAND APART (Different Persona or Cross-Cutting)

| Source | Story | Recommendation |
|--------|------|----------------|
| **CPFR** C-1 | As a member of Vendor Compliance or other teams, extend CPFR platform architecture to other vendor-related data (unified vendor data environment) | **Keep as CPFR cross-team / extensibility story.** Place in merged doc under “CPFR” or “Cross-program”; acknowledges VC as consumer of platform patterns (per merged BRD NFR-4, future integration). No merge with a specific VC story. |
| **VC** #10b (proof of delivery) | Manager: proof of delivery for emailed reports; hold vendors accountable | Treated in **1.4** as manager story with dual applicability when same email system is used; no separate section needed unless you want a short “VC success criterion: proof of delivery” callout. |

---

## 5. Suggested Structure for Merged User Stories Document

1. **Introduction / Document Purpose**  
   - Merged CPFR + VC user stories for CPH; aligned to CPH Portal Platform BRD (CPFR & VC).

2. **Combined (Dual Applicability)**  
   - 1.1 Single location / on-demand access (Vendor)  
   - 1.2 Contact & report distribution (Vendor)  
   - 1.2 Internal: Report access control & distribution (Category Manager / ISM)  
   - 1.3 Internal visibility to vendor reports (Category Manager / ISM)  
   - 1.4 Email modalities and control (Vendor)  
   - 1.4 Manager: Engagement and proof of delivery (Manager) — optional; can be folded into 1.4

3. **CPFR-Only**  
   - Problem statements (scale, data consistency, manual overhead, self-service) — abbreviated if desired  
   - Vendor: V-2, V-3, V-5  
   - ISM: I-2, I-3, I-4  
   - CPFR Team: P-1, P-2, P-3  
   - BIE: B-1, B-2  
   - Cross-team: C-1  

4. **Vendor Compliance–Only**  
   - Optional: Short problem context (too many touchpoints, dispute friction, scalability)  
   - Centralized chargeback/compliance access and historical repository (if not fully covered in 1.1)  
   - Dispute resolution (Vendor + Compliance Manager)  
   - Scalability / program expansion (Compliance Manager)  
   - Data structures & table outputs (Category Manager + Compliance Manager)  

5. **Version / Phasing**  
   - Align to merged BRD: Version 1 (Chargebacks), Version 2 (Violations), Version 3 (CPFR) and “VC Phase 3 = CPFR Phase 2.”

6. **Document Maintenance**  
   - When to update; preserve problem/user need vs. solution.

---

## 6. Checklist Before Drafting Merged Document

- [ ] Confirm merged vendor story 1.1 explicitly includes “CPFR and/or chargeback/compliance” and optional VC historical repository.
- [ ] Confirm 1.2 vendor + internal stories reference “CPFR and VC contact/recipient lists as separate manageable elements.”
- [ ] Confirm 1.4 manager story is labeled as applying to both CPFR and VC where same email/contact system is used.
- [ ] All 10 CPFR-only stories (V-2, V-3, V-5, I-2, I-3, I-4, P-1, P-2, P-3, B-1, B-2) retained without merging into VC.
- [ ] VC-only: dispute resolution (vendor + Compliance Manager), scalability, table outputs / Tableau clearly in VC-only section.
- [ ] C-1 (extend platform to other data types) retained as CPFR cross-team; no merge with VC story.
- [ ] Phasing / version releases aligned to merged BRD (Chargebacks → Violations → CPFR; VC Phase 3 = CPFR Phase 2).

---

*End of assessment. Ready for your review; draft merged user stories document can follow once you approve or adjust this plan.*

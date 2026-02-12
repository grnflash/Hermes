# Step 1: Combine vs. Keep Separate — Assessment

**Purpose:** Before merging the CPFR and VC BRDs, this document classifies each requirement area as **Combine** (single feature/section with CPFR and VC elements) or **Keep Separate** (CPFR-only or VC-only). Combined items will be rendered as unified requirements in the merged BRD with CPFR/VC called out where relevant; separate items retain distinct scope.

**Document type:** Working assessment for review before Step 2 (merge).  
**Last updated:** 2026-02-03

---

## Summary for Senior Readers

- **Combine:** Vendor administration (contacts, report distribution, email recipients—with CPFR and VC contact lists as **separate manageable elements**; **use and expand CPH’s existing user self-service admin facility**—roles, permissions, reporting—to encompass CPFR/VC, with **show/hide of certain config options** between Chewy TM visibility vs. vendor visibility), data isolation/security (vendor isolation; avoid prescriptive “RLS” at BRD level), CPH integration, usability, performance (single section with sub-points), and vendor experience cohesion. Resource availability (design/development) and transition of CPH capacity to CPFR module work are **shared** constraints/dependencies/risks; use “transition”/“sequencing” language, not “handoff.” These are shared CPH capabilities or cross-cutting concerns; one requirement or section with CPFR and VC elements avoids duplication and supports a single vendor experience.
- **Keep separate:** CPFR platform (scale, data governance, tiers, historical data, refresh, extensibility), CPFR portal (report viewer, tier selection), VC/Chargeback content (report access, dispute resolution, violations, scalability/entitlement metrics). These reflect distinct ownership, data, and workflows.
- **Phasing:** VC Phases 1 & 2 and CPFR Phase 1 (platform) are parallel; VC Phase 3 and CPFR Phase 2 are the same (CPFR module in CPH). The merged BRD will state this explicitly.

---

## 1. Functional Requirements — Detailed Classification

### 1.1 COMBINE — Vendor Administration & Report Distribution (lives in CPH)

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** FR-5 | REQ-5.1: Vendors access CPFR data on-demand (portal, email, etc.); REQ-5.2: Vendors manage contact info and notification preferences; REQ-5.3: ISMs customize vendor data views | Same capability as VC: who gets what, and how. |
| **VC** FR-1 (Access Control) | REQ-1.0: ISM/Category Manager assign or remove report access by vendor; REQ-1.1: Assign/remove contact info for email distribution; REQ-1.2: Unique email distribution per report type; REQ-1.3: Vendor self-service for contact and distribution preferences | Same capability: report access control + contact/distribution. |

**Merge approach:** One combined section, e.g. **FR-X: Vendor Administration & Report Distribution (CPH)**, with:
- One **internal (Chewy) interface** to assign/remove report access by vendor and to manage which reports go to which stakeholders (with CPFR report tier/config and VC report config as distinct elements).
- One **vendor self-service** experience: contact management and distribution preferences in a single place, with **distinct areas/sections** for (a) CPFR report recipients and preferences, (b) VC/Chargeback report recipients and preferences (e.g., two boxes/sections on one page or flow).
- **CPFR and VC contact/recipient lists must be manageable as separate elements.** They may appear on the same page together, and many recipients for a given vendor may receive both CPFR and VC content—but the BRD must require the ability to manage CPFR recipients and VC recipients as separate lists, so that a vendor can assign some contacts to CPFR only, some to VC only, or some to both, as needed.
- **Administrative visibility — use and expansion of CPH’s existing facility; show/hide of config options:** CPH already has a user self-service admin page: when opened by Chewy personnel it shows a view visible across all vendors; when opened by a vendor it shows only that vendor. It lists individuals, email address, and a role (e.g., EDI User, Warehouse User) via a pop-out menu; role drives visibility to links/pages, permissions, and triggers for reporting (including the outbound email module). It was agreed (N. Nelson and N. Miles) that **expanding this existing facility to logically encompass CPFR** (and by implication VC) would provide the needed administrative options—i.e., extend roles and this admin capability so CPFR and VC contact/distribution and reporting are managed through the same facility. Apart from describing this use and expansion, the BRD must still require the ability to **show or hide certain configuration options** between (a) **Chewy TM visibility (broader)** — e.g., which CPFR tier per vendor, which VC report types — and (b) **vendor visibility (narrower)** — e.g., contact emails, add/remove users, who receives CPFR/VC reports. How to achieve show/hide is implementation-agnostic (e.g., visibility labels in page HTML, additional sub-pages only for Chewy TMs, role-based visibility); the BRD should state the requirement without prescribing the mechanism.

**Recommended plan for merged BRD:** (1) Reference CPH’s existing user self-service admin page (roles such as EDI User, Warehouse User; visibility, permissions, reporting/email). (2) Require expansion of this facility to logically encompass CPFR (and VC) so that CPFR/VC contact, distribution, and reporting are managed through the same facility. (3) Require the ability to show or hide certain configuration options between Chewy TM visibility and vendor visibility; leave mechanism unspecified.
- Optional sub-reqs or bullets that call out CPFR vs. VC where needed for traceability.

---

### 1.2 COMBINE — Email & Communication (CPH-driven)

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** FR-5, NFR-3 | Email backup, modalities (portal + email) | Same system: email driven from CPH contact/distribution settings. |
| **VC** FR-4 | REQ-4.1: Reduce email volume; REQ-4.2: Email report functionality with vendor control over which reports go to which team members; REQ-4.3: Email system reads from CPH contact management and report distribution; REQ-4.4: Proof of delivery | Same capability: one email engine, one contact/distribution source. |

**Merge approach:** Single **Communication & Email** requirement (or sub-section under Vendor Administration): email report capability for both CPFR and VC, reading from unified CPH contact management and report distribution; vendor control over recipients per report type (CPFR vs. VC); proof of delivery where specified (VC). **Contact/recipient lists for CPFR and VC must be manageable as separate elements** (same page OK)—so that specific recipients for a given vendor can be assigned to CPFR only, VC only, or both, as required. Baseline/target (e.g., 65 emails/month) can remain VC-sourced but labeled as shared context.

---

### 1.3 COMBINE — Data Isolation & Security (vendor isolation in CPH + platform)

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** FR-3 | REQ-3.1: Strict data isolation, vendors only their SKUs, access logging; REQ-3.2: Multi-vendor entities; REQ-3.3: Internal user granular access | Same principle: vendor-scoped data; VC relies on same isolation. |
| **VC** NFR-2 | REQ-N2.1: Strict vendor data isolation; REQ-N2.2: vendor_id–based isolation; REQ-N2.3: CPH vendor isolation aligned with SC-BIE semantic layer for CPFR | Same principle; VC explicitly ties vendor isolation to CPH and future CPFR integration. |

**Merge approach:** One **Data Isolation & Security** section: enforce **vendor isolation** (vendors access only their own data) in CPH and in CPFR platform; alignment between CPH vendor isolation and SC-BIE semantic layer for CPFR integration. Avoid overly prescriptive implementation language (e.g., “RLS” or “RLS key mapping”) at BRD level—“vendor isolation” is sufficient to convey the requirement. Sub-bullets can distinguish CPFR (SKU/tier, internal override) vs. VC (chargeback/compliance scope).

---

### 1.4 COMBINE — CPH Integration & Cross-Module Experience

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** FR-7 | REQ-7.1: Integrate with CPH; REQ-7.4: Support future integration with VC data | Single integration target: CPH. |
| **VC** FR-5 | REQ-5.1–5.3: Unified vendor experience across VC, Chargeback, CPFR; consistent navigation, data access, UI; avoid fragmentation (Sr. Director) | Same outcome: one CPH, one experience. |
| **VC** NFR-3 | REQ-N3.1: Integrate with CPH; REQ-N3.3: Support future CPFR integration | Redundant with FR-5 and CPFR FR-7. |

**Merge approach:** One **CPH Integration & Vendor Experience Cohesion** requirement: seamless integration with existing CPH; unified vendor experience across VC, Chargeback, and CPFR modules; consistent navigation, data access patterns, and UI; avoid vendor experience fragmentation (cite Sr. Director). CPFR FR-7.2/7.3 (Tableau/Plotly, VDS) stay under CPFR-specific sections.

---

### 1.5 KEEP SEPARATE — CPFR Platform (scale, governance, data, refresh)

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** FR-1 | Scale: 3K–5K vendor users, 200+ internal, 6.6K+ daily reads, no proportional overhead | CPFR platform only; VC has different scale baselines. |
| **CPFR** FR-2 | Daily immutable snapshots, same version across methods, lineage/audit | CPFR data platform only. |
| **CPFR** FR-4 | Tier structure, analytical depth, metric-level customization | CPFR report structure only. |
| **CPFR** FR-6 | 2 years historical, daily granularity, time-series analysis | CPFR data only. |
| **CPFR** FR-8 | Daily refresh 2–3 AM, sequential base → materialized views | CPFR platform only. |

**Merge approach:** Keep as **CPFR-only** sections (e.g., Scale, Data Consistency & Governance, Analytical Depth, Historical Data, Data Refresh). No VC equivalent; no combination.

---

### 1.6 KEEP SEPARATE — CPFR Portal (viewer, tier selection)

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** FR-5.1, FR-7.2 | Vendor access to CPFR data via portal; Tableau/Plotly-style viewer; tier-based views | CPFR-specific: time-series, SKU/location, interactive viewer. |

**Merge approach:** **CPFR-only** requirement(s): vendor-facing CPFR module in CPH — access to CPFR reports (e.g., last 30 days), report selector, embedded viewer (Tableau or Plotly) for filtering and basic aggregation; tier/config set by Chewy (see combined admin section). No VC equivalent.

---

### 1.7 KEEP SEPARATE — VC/Chargeback Reporting & Dispute (VC-only)

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **VC** FR-1 (Data Access) | REQ-1.1–1.5: Single location for chargeback/compliance reports; historical repository; internal access; table outputs; Tableau/data sharing levels | VC/Chargeback content and UX; text-style reports, no CPFR viewer. |
| **VC** FR-2 | Dispute resolution in CPH; single interface for chargebacks/disputes; file disputes in-platform; store docs; <5 clicks, <5 minutes | Chargeback subset of VC; no CPFR equivalent. |
| **VC** FR-4 (partial) | REQ-4.5: Scale 123 → thousands; REQ-4.6: $21M entitlement opportunity | VC/Chargeback program scope. |

**Merge approach:** **VC-only** sections: (1) VC/Chargeback report access and repository in CPH; (2) Dispute resolution (lightweight issue/resolution tracker, CRM-like). Email reduction and scalability stay VC success criteria/context but can reference shared CPH communication (combined above).

---

## 2. Non-Functional Requirements — Classification

### 2.1 COMBINE — Performance

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** NFR-1 | Query <2 s (tier) / <10 s (cross-vendor); 200+ concurrent sessions; >99.5% availability | Same NFR category; different metrics. |
| **VC** NFR-1 | Support 123 → thousands; dispute <5 clicks, <5 min; historical retrieval self-service, no significant delay | Same category; VC-specific metrics. |

**Merge approach:** One **Performance** NFR section with sub-bullets: (a) CPFR: query times, concurrent sessions, availability; (b) VC: vendor scale, dispute UX, historical retrieval. Traceability preserved.

---

### 2.2 COMBINE — Usability

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** NFR-3 | Intuitive portal; multiple modalities (portal, email); self-service admin | Same intent. |
| **VC** NFR-4 | Intuitive portal; self-service contact/email preferences; multiple modalities | Same intent. |

**Merge approach:** One **Usability** NFR: intuitive portal for varying technical ability; self-service for contact and report distribution (CPFR + VC); multiple access modalities (portal, email). No need to duplicate.

---

### 2.3 KEEP SEPARATE — Data Governance (CPFR), Extensibility (CPFR)

| Source | Requirement | Rationale |
|--------|-------------|-----------|
| **CPFR** NFR-2 | Data definitions, lineage, audit, change management, centralized governance | CPFR platform governance only. |
| **CPFR** NFR-4 | AI/ML readiness; extension to other data types (e.g., VC) | CPFR platform only. |

**Merge approach:** Remain **CPFR-only** under a CPFR platform / governance section.

---

## 3. Success Criteria

| Source | Criterion | Combine or separate |
|--------|-----------|---------------------|
| **VC** SC-1–SC-5 | Email reduction, dispute efficiency, ticket reduction, scalability, adoption | **Keep VC subsection** — concrete, measurable; retain baselines and targets. |
| **CPFR** (inferred) | Scale (3K+ vendors, 200+ internal); performance (query, availability); data consistency; ISM capacity reallocation; vendor/portal adoption | **Add CPFR subsection** — directional and magnitude-oriented; traceable to FR/NFR. |

**Merge approach:** One **Success Criteria** section with two subsections: (1) **VC** — existing SC-1–SC-5 with baselines/targets; (2) **CPFR** — inferred criteria (scale, performance, consistency, capacity reallocation, adoption) with short rationale. Enables traceability without over-claiming.

---

## 4. Explored Solutions / Feasibility

| Content | Merge approach |
|---------|----------------|
| **CPFR** Platform (Snowflake, semantic layer, vendor isolation, materialized views, CPH portal) | **Shorten** to a few sentences; state that CPFR platform is Snowflake-based with semantic layer and vendor isolation; CPH hosts vendor-facing and admin features; reference CPFR BRD or technical specs for detail. |
| **VC** | No separate “explored solutions” section; VC requirements already imply CPH + dispute workflow. |

**Merge approach:** Single, succinct **Explored Solutions / Feasibility** subsection: CPFR platform (Snowflake, semantic layer, vendor isolation, daily refresh) and CPH integration (unified vendor experience, Replen Tech). External reference for full architecture.

---

## 5. Phasing

| Source | Phasing | Merge approach |
|--------|---------|----------------|
| **CPFR** | Phase 1: Platform (Snowflake, internal tools). Phase 2: CPFR portal in CPH. | **Combine** into one timeline. |
| **VC** | Phase 1: Chargebacks (File Access Control, 123 vendors). Phase 2: Violations. Phase 3: CPFR (see CPFR BRD). | **Combine** with explicit parallel/sequential. |

**Merge approach:** One **Phased Release** section that states:
- **Parallel:** CPFR Phase 1 (SC-BIE: CPFR data platform build) and VC Phases 1 & 2 (CPH: Chargebacks, then Violations) run in parallel. CPFR module development in CPH cannot start in earnest until the CPFR data platform is deployed (~3-month gap).
- **Sequential / transition of CPH capacity:** Once the CPFR data platform is deployed, CPH is free to move development capacity to CPFR module work—and should do so as close to that timeframe as possible. VC Phases 1 & 2 complete first so CPH team can pivot from VC work to CPFR module development. (Avoid “handoff” language: this is about *what CPH works on next*, not about SC-BIE transferring platform assets to CPH or CPH taking over platform maintenance.)
- **VC Phase 3 = CPFR Phase 2:** CPFR module in CPH (dependent on deployed CPFR data platform and alignment of vendor isolation between CPH and SC-BIE).

---

## 6. Constraints & Assumptions

| Source | Item | Combine or separate |
|--------|------|---------------------|
| **CPFR** C-1 | Snowflake & SQL standardization | CPFR-only. |
| **CPFR** C-2 | VDS complementarity | CPFR-only. |
| **CPFR** C-3, **VC** C-1 | CPH integration requirement | **Combine** — one constraint: portal integrates into CPH. |
| **VC** C-2 | Vendor experience cohesion (Sr. Director) | **Combine** — same constraint; can merge with C-1. |
| **VC** C-3 | Resource availability (design, approval) | **Combine** — shared constraint; CPFR will likely run into the same resource constraints if not addressed. Describe as shared (design/development resources subject to approval; affects both VC and CPFR). |
| **VC** C-4 | Sequencing / CPH capacity for CPFR module (CPFR depends on SC-BIE platform; VC can stage first) | **Combine** — single constraint: CPFR module work in CPH cannot start in earnest until CPFR data platform is deployed; once deployed, CPH should pivot to CPFR module development as close to that timeframe as possible. Describe as “transition of CPH development capacity” or “sequencing,” not “handoff” (no transfer of platform assets or maintenance to CPH). |
| **CPFR** A-1–A-3 | Daily snapshot, tier evolution, historical retention | CPFR-only. |
| **VC** A-1–A-3 | Email preference, dispute efficiency, $21M expansion | VC-only (or VC-labeled in a shared assumptions list). |

**Merge approach:** One **Constraints** list with combined CPH/Vendor Experience items, shared resource availability (C-3), and sequencing/transition of CPH capacity (C-4); one **Assumptions** list with CPFR-only and VC-only items clearly labeled.

---

## 7. Dependencies & Risks

| Source | Item | Combine or separate |
|--------|------|---------------------|
| **CPFR** D-1, **VC** D-1 | Replen Tech / CPH development | **Combine** — same dependency. |
| **CPFR** D-2, **VC** (implicit) | EDS security approval | **Combine** — same dependency. |
| **CPFR** D-3 | Data source availability | CPFR-only. |
| **CPFR** D-4, **VC** SC-5 | Vendor adoption | **Combine** — same dependency; mitigation (co-branded rollout, education, email backup) shared. |
| **VC** D-2 | Design resources (approval pending) | **Combine** — shared dependency; CPFR will likely face the same design resource constraints if not addressed. |
| **VC** D-3 | Transition of CPH development capacity to CPFR module | **Combine** with CPFR dependency on platform deployment — CPH team (developers/UX) will transition from VC work to CPFR module work once the CPFR data platform is deployed; plan for continuity so CPFR module development can start as close as possible to that timeframe. Describe as “transition of CPH capacity” or “sequencing,” not “handoff” (no transfer of platform ownership or maintenance). |
| **VC** D-4, **CPFR** (implicit) | Vendor isolation alignment (CPH and SC-BIE semantic layer for CPFR) | **Combine** — single dependency; critical for CPFR Phase 2. Describe as **vendor isolation** alignment between CPH and SC-BIE; avoid overly prescriptive “RLS” or “RLS key mapping” at BRD level. |
| **CPFR** R-1, **VC** R-1 | Data consistency / inter-team alignment; Vendor experience fragmentation | **Combine** — same theme: alignment and single experience; one risk with both angles. |
| **CPFR** R-2, **VC** R-2 | Vendor adoption | **Combine** — same risk. |
| **CPFR** R-3 | Platform sustainment | CPFR-only. |
| **CPFR** R-4, **VC** R-6 | Performance at scale / Scalability | **Combine** — “Performance and scalability at scale” with CPFR (3K+ users) and VC (123 → thousands) sub-points. |
| **VC** R-3 | Resource availability (design, development) | **Combine** — shared risk; affects both VC and CPFR if resources are not confirmed. |
| **VC** R-4 | Integration complexity | **Combine** — “Integration complexity across CPH, CPFR data, dispute, contact management” with shared mitigation. |
| **VC** R-5 | Vendor isolation alignment (CPH and SC-BIE for CPFR) | **Combine** with D-4. Describe as **vendor isolation** alignment; avoid “RLS key mapping” at BRD level. |

**Merge approach:** Single **Dependencies** list: combined where same (Replen Tech, EDS, vendor adoption); **shared** for design resources (D-2) and transition of CPH capacity to CPFR module (D-3); vendor isolation alignment (D-4) described without “RLS” at BRD level; CPFR-only (e.g., data sources) and VC-only labeled where applicable. Single **Risks** list: combined for shared themes; **shared** for resource availability (R-3) and vendor isolation alignment (R-5); CPFR-only and VC-only labeled where applicable.

---

## 8. Document-Level Elements

| Element | Merge approach |
|---------|----------------|
| **Title** | E.g., “CPH Portal & Platform: Business Requirements (CPFR & Vendor Compliance)” or similar. |
| **Purpose** | Single purpose statement: joint BRD for CPFR and VC modules in CPH; unified vendor experience; combined where shared, distinct where not. |
| **Table of contents** | Single TOC: Executive/headline (for sr. leaders), then Business Requirements (combined + CPFR-only + VC-only), Success Criteria (VC + CPFR), Phasing, Explored Solutions (short), Constraints, Dependencies & Risks, Document Maintenance. |
| **Headlining vs. drill-down** | Brief executive summary at top (outcomes, phasing, key risks); requirements and technical detail below for technicians. |

---

## 9. Checklist for Step 2 (Merge)

When drafting the merged BRD in Step 2:

- [ ] One **Vendor Administration & Report Distribution** section (CPH) with CPFR and VC recipient/preference elements; **CPFR and VC contact lists as separate manageable elements** (same page OK; ability to assign recipients to CPFR only, VC only, or both).
- [ ] **Administrative visibility:** Describe **use and expansion of CPH’s existing user self-service admin facility** (roles, permissions, reporting/email) to encompass CPFR (and VC). Require ability to **show or hide certain configuration options** between Chewy TM visibility (broader—e.g., CPFR tier, VC report types) and vendor visibility (narrower—e.g., contacts, add/remove users); implementation-agnostic (no prescribed mechanism).
- [ ] One **Communication & Email** requirement (or sub-section) referencing shared CPH contact/distribution; **CPFR and VC recipients manageable separately** (per above).
- [ ] One **Data Isolation & Security** section (**vendor isolation**; alignment CPH–SC-BIE for CPFR; avoid prescriptive “RLS”/“RLS key mapping” at BRD level).
- [ ] One **CPH Integration & Vendor Experience Cohesion** requirement (no fragmentation).
- [ ] **CPFR-only** sections: Scale, Data Consistency & Governance, Analytical Depth, Historical Data, Data Refresh, CPFR Portal (viewer, tier selection), Data Governance NFR, Extensibility NFR.
- [ ] **VC-only** sections: VC/Chargeback report access and repository, Dispute resolution.
- [ ] **Combined** NFRs: Performance, Usability.
- [ ] **Success criteria**: VC (concrete) + CPFR (inferred, directional) with traceability.
- [ ] **Phasing**: Parallel (CPFR Phase 1 | VC 1 & 2); **transition of CPH capacity** to CPFR module once platform deployed (not “handoff”); VC Phase 3 = CPFR Phase 2.
- [ ] **Explored solutions**: Short paragraph + external reference (vendor isolation, not RLS).
- [ ] **Constraints, Dependencies, Risks**: Resource availability (C-3, D-2, R-3) and transition of CPH capacity (C-4, D-3) described as **shared**; vendor isolation alignment (D-4, R-5) as “vendor isolation,” not RLS; combined where shared; CPFR-only and VC-only labeled.
- [ ] **Tone**: Headlines for sr. leaders; drill-down for technicians; concise; no bloat.

---

**End of Step 1 Assessment.**  
Ready for your review; Step 2 (draft merged BRD) will follow once you approve or adjust this classification.

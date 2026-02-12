# CPH Portal & Platform: Business Requirements (CPFR & Vendor Compliance)

**Document Type:** Business Requirements Document (Merged)  
**Last Updated:** 2026-02-03  
**Status:** Draft for Review  

**Document Purpose**  
This document captures business requirements, success criteria, constraints, dependencies, and risks for CPFR (Collaborative Planning, Forecasting & Replenishment) and Vendor Compliance (VC) / Chargeback modules within the Chewy Partner Hub (CPH). It merges requirements from the CPFR Platform & Portal BRD and the VC & Chargeback CPH Portal BRD to support a unified vendor experience and coherent delivery. Requirements are defined independently of specific technical approaches. Problem statements and user needs are documented in the source Problem Definition & User Stories and VC source documents.

**Joint Business Product Owners:** Nathan Miles (CPFR), Nathan Nelson (VC)

---

## Table of Contents

1. Executive Summary (for senior leaders)
2. Business Requirements
   - Combined (CPH-shared): Vendor Administration & Report Distribution; Communication & Email; Data Isolation & Security; CPH Integration & Vendor Experience Cohesion
   - CPFR-only: Platform (Scale, Data Consistency & Governance, Analytical Depth, Historical Data, Data Refresh); CPFR Portal (viewer, tier selection); Data Governance NFR; Extensibility NFR
   - VC-only: VC/Chargeback Data Access & Reporting; Dispute Resolution
3. Non-Functional Requirements (Performance, Usability; CPFR Data Governance & Extensibility)
4. Success Criteria (VC; CPFR)
5. Phased Release Plan
6. Explored Solutions (Feasibility Reference)
7. Constraints & Assumptions
8. Dependencies & Risks
9. Document Maintenance

---

## 1. Executive Summary (for senior leaders)

**Outcomes**  
- **Unified vendor experience:** One CPH with VC/Chargeback and CPFR modules—consistent navigation, data access, and UI. Avoiding vendor experience fragmentation is a critical requirement (Sr. Director of Retail I.T. Product Management).  
- **Shared administration in CPH:** Vendor administration and report distribution (contacts, who receives CPFR vs. VC reports, email preferences) are combined where they live in CPH, with CPFR and VC contact/recipient lists as separate manageable elements. CPH’s existing user self-service admin facility (roles, permissions, reporting/email) will be expanded to encompass CPFR and VC; certain configuration options will be visible only to Chewy personnel (e.g., CPFR tier, VC report types) vs. visible to vendors (contacts, add/remove users).  
- **CPFR:** A governed CPFR data platform (SC-BIE) plus a CPFR module in CPH (report viewer, tier-based access). CPFR module development in CPH cannot start in earnest until the CPFR data platform is deployed.  
- **VC/Chargeback:** Report access and repository in CPH, dispute resolution in-platform (lightweight issue/resolution tracker), scalability to thousands of vendors and $21M entitlement opportunity.

**Phasing**  
- **Parallel:** CPFR Phase 1 (SC-BIE: CPFR data platform build) and VC Phases 1 & 2 (CPH: Chargebacks, then Violations) run in parallel (~3-month gap before CPFR module work can start).  
- **Transition of CPH capacity:** Once the CPFR data platform is deployed, CPH development capacity moves to CPFR module work (no transfer of platform assets or maintenance to CPH). VC Phase 3 and CPFR Phase 2 are the same deliverable: the CPFR module in CPH.

**Key risks (shared)**  
- Vendor experience fragmentation; vendor adoption; resource availability (design/development) for both VC and CPFR; integration complexity; vendor isolation alignment between CPH and SC-BIE for CPFR.

---

## 2. Business Requirements

### 2.1 Combined Requirements (lives in CPH)

#### FR-1: Vendor Administration & Report Distribution (CPH)

- **REQ-1.1** Provide a single internal (Chewy) interface within CPH for ISMs or Category Managers to assign or remove report access by vendor and to manage which reports go to which stakeholders, with **CPFR report tier/config** and **VC report config** as distinct, configurable elements.
- **REQ-1.2** Provide a single vendor self-service experience for contact management and report distribution preferences, with **distinct areas or sections** for (a) CPFR report recipients and preferences, and (b) VC/Chargeback report recipients and preferences (e.g., separate boxes or sections on one page or flow).
- **REQ-1.3** Require that **CPFR and VC contact/recipient lists be manageable as separate elements**. They may appear on the same page. Many recipients for a given vendor may receive both CPFR and VC content; the system must support assigning specific contacts to CPFR only, VC only, or both, as needed.
- **REQ-1.4** **Use and expand CPH’s existing user self-service admin facility** to encompass CPFR (and VC). CPH already has a user self-service admin page that, when opened by Chewy personnel, shows a view across all vendors; when opened by a vendor, shows only that vendor. It lists individuals, email address, and role (e.g., EDI User, Warehouse User) via a pop-out menu; role drives visibility to links/pages, permissions, and triggers for reporting (including the outbound email module). The BRD requires expansion of this facility so that CPFR and VC contact, distribution, and reporting are managed through the same facility.
- **REQ-1.5** Require the ability to **show or hide certain configuration options** between (a) **Chewy TM visibility (broader)** — e.g., which CPFR tier is selected for a given vendor, which VC report types are enabled — and (b) **vendor visibility (narrower)** — e.g., contact emails, add/remove users, who receives CPFR/VC reports. The mechanism (e.g., visibility labels, sub-pages only for Chewy TMs, role-based visibility) is not prescribed at BRD level.
- **REQ-1.6** Enable ISMs to customize vendor data views and metric selections for CPFR (internal-only configuration).

#### FR-2: Communication & Email (CPH-driven)

- **REQ-2.1** Provide email report capability for both CPFR and VC, reading from unified CPH contact management and report distribution settings; vendor control over which reports are emailed to which team members, with **CPFR and VC recipients manageable as separate elements** (per FR-1.3).
- **REQ-2.2** Support multiple access modalities (web portal, email) based on vendor preferences; email backup for vendors unable or preferring not to use the portal.
- **REQ-2.3** Provide proof of delivery for emailed reports where specified (VC context).
- **REQ-2.4** Reduce email volume from current baseline (e.g., 65 emails per month per vendor from Chargebacks and CPFR/VC) through portal adoption and consolidated distribution; measurement via email volume tracking and portal usage analytics.

#### FR-3: Data Isolation & Security

- **REQ-3.1** Enforce **vendor isolation** so that vendors access only their own data in CPH and in the CPFR platform; complete access logging for security and compliance.
- **REQ-3.2** Support multi-vendor entities with separate vendor numbers and SKU groups (CPFR); align CPH vendor isolation with the SC-BIE semantic data layer for CPFR integration (vendor isolation alignment; implementation details in technical specifications).
- **REQ-3.3** Provide granular access controls for internal users (default scope with override capabilities for CPFR).

#### FR-4: CPH Integration & Vendor Experience Cohesion

- **REQ-4.1** Integrate all CPFR and VC capabilities seamlessly within existing Chewy Partner Hub (CPH) infrastructure; portal development must align with CPH architecture and Replen Tech resources.
- **REQ-4.2** Ensure a **unified vendor experience** across VC, Chargeback, and CPFR modules within CPH: consistent navigation, data access patterns, and user interface. **Avoid vendor experience fragmentation** (critical requirement established by Sr. Director of Retail I.T. Product Management).
- **REQ-4.3** Support future integration between CPFR and VC data where applicable.

---

### 2.2 CPFR-Only Requirements

#### FR-5: CPFR Platform — Scale

- **REQ-5.1** Support 3,000–5,000 concurrent vendor users and 200+ concurrent internal users (ISMs, analysts).
- **REQ-5.2** Handle 6,600+ daily read operations without performance degradation.
- **REQ-5.3** Scale vendor capacity without proportional infrastructure or support overhead increase.

#### FR-6: CPFR Platform — Data Consistency & Governance

- **REQ-6.1** Provide daily, immutable data snapshots that eliminate time-of-day drift.
- **REQ-6.2** Ensure all stakeholders (internal and external) reference the same data version across all access methods (portal, email, direct queries).
- **REQ-6.3** Provide definitive data lineage and audit trails for all data access.

#### FR-7: CPFR Platform — Analytical Depth

- **REQ-7.1** Support multiple analytical depth levels (tier structure) as templates with customization capability, accommodating different vendor needs from high-level forecasts to granular SKU/fulfillment-center/region breakdowns.
- **REQ-7.2** Enable metric-level customization for high-touch vendor relationships.

#### FR-8: CPFR Platform — Historical Data

- **REQ-8.1** Maintain 2 years of historical CPFR data with daily granularity.
- **REQ-8.2** Enable time-series analysis, trend identification, and historical comparison for forecast accuracy validation.

#### FR-9: CPFR Platform — Data Refresh

- **REQ-9.1** Refresh CPFR data daily during designated maintenance window (2–3 AM), completing refresh cycle within the window to ensure availability by business hours.
- **REQ-9.2** Provide sequential refresh of dependent data structures (base tables then materialized views).

#### FR-10: CPFR Portal (module in CPH)

- **REQ-10.1** Provide vendor-facing CPFR module within CPH: access to CPFR reports (e.g., last 30 days), report selector, and embedded viewer (Tableau- or Plotly-based) for filtering and basic real-time aggregation; CPFR data is time-based with many performance metrics at SKU and location grain.
- **REQ-10.2** CPFR tier/config per vendor is set by Chewy personnel via the combined administration capability (FR-1); not visible to vendors.
- **REQ-10.3** Enable vendors to access CPFR data on-demand, 24/7, without ISM intervention, via portal and email based on vendor preferences.
- **REQ-10.4** Maintain compatibility with existing VDS infrastructure (complementary, not replacement); provide data access compatible with existing internal tools (Tableau, Plotly, etc.) and future API exposure for vendors who are not VDS tenants.

---

### 2.3 VC-Only Requirements

#### FR-11: VC/Chargeback — Data Access & Reporting

- **REQ-11.1** Provide a single, consistent location within CPH where vendors can access designated chargeback and compliance reports without sorting through multiple emails, reducing errors and omissions.
- **REQ-11.2** Provide a centralized repository for historical chargeback and compliance data accessible through CPH with self-service retrieval.
- **REQ-11.3** Enable Category Managers and In-Stock teams to access all vendor compliance and chargeback reports within CPH for quick reference and decision-making.
- **REQ-11.4** Provide table outputs from the CPH platform for internal analysis (chargeback disputes, vendor feedback, ticket dispositions, usage, program performance data).
- **REQ-11.5** Provide Tableau views or data outputs showing data sharing levels across the vendor base (without requiring CPH login where specified).
- **REQ-11.6** Support expansion from current 123 vendors to thousands without proportional increase in manual workload; enable program expansion to capture estimated $21M entitlement opportunity.

#### FR-12: VC/Chargeback — Dispute Resolution

- **REQ-12.1** Integrate dispute functionality within CPH (eliminate redirect to Oracle CRM).
- **REQ-12.2** Display all chargebacks, charge types, and disputes in a single interface; enable vendors to file disputes directly within the platform without duplicate documentation uploads.
- **REQ-12.3** Store all supporting documents and case details in one platform.
- **REQ-12.4** Reduce dispute resolution time from current baseline (12 clicks, 20 minutes) to fewer than 5 clicks and fewer than 5 minutes.

---

## 3. Non-Functional Requirements

#### NFR-1: Performance (combined)

- **CPFR:** Query response time under 2 seconds for tier-specific vendor queries, under 10 seconds for complex cross-vendor analytics; support 200+ concurrent user sessions without performance degradation; system availability greater than 99.5% during business hours.
- **VC:** System must support current 123 vendors with capacity for expansion to thousands; dispute resolution process must complete in fewer than 5 clicks and fewer than 5 minutes; historical data retrieval must be self-service without significant delay.

#### NFR-2: Usability (combined)

- **REQ-N2.1** Portal interface must be intuitive for vendors with varying technical capabilities.
- **REQ-N2.2** Administrative tasks (contact management, report distribution preferences for CPFR and VC) must be self-service where visible to vendors; multiple access modalities (web portal, email) supported.

#### NFR-3: Data Governance (CPFR-only)

- **REQ-N3.1** Provide standardized data definitions, lineage documentation, and audit capabilities for data access and modifications.
- **REQ-N3.2** Support change management process for data structure modifications; enable centralized governance while maintaining team autonomy.

#### NFR-4: Extensibility (CPFR-only)

- **REQ-N4.1** Architecture must support future AI/ML-driven analytics initiatives and machine learning model training with normalized data cadence.
- **REQ-N4.2** Platform must support extension to other data types (e.g., VC data) and future enhancements without fundamental redesign.

---

## 4. Success Criteria

#### 4.1 VC (concrete, measurable)

- **SC-1 Communication efficiency:** Baseline 65 emails per month per vendor (45 from Chargebacks, 20 from CPFR/VC). Target: significant reduction through portal adoption. Measurement: email volume tracking and portal usage analytics.
- **SC-2 Dispute resolution efficiency:** Baseline 12 clicks and 20 minutes to reach dispute resolution. Target: fewer than 5 clicks and fewer than 5 minutes (aligned with competitor platforms); 30% improvement in dispute resolution efficiency. Measurement: user interaction tracking and time-to-resolution metrics.
- **SC-3 Support ticket reduction:** Baseline 90 tickets per month for contact list corrections/updates. Target: significant reduction through unified contact management. Measurement: support ticket volume tracking.
- **SC-4 Program scalability:** Baseline 123 vendors in Chargeback Program. Target: support expansion to capture $21M entitlement opportunity. Measurement: vendor onboarding capacity and system performance metrics.
- **SC-5 Vendor adoption:** Target high adoption rate of CPH portal for chargeback and compliance data access. Measurement: portal login rates, feature usage analytics, vendor feedback.

**ROI value drivers (VC context):** $10.8M annual chargeback-related data, $21M entitlement opportunity, 1,500 Oracle CRM tickets/year reduction, 30% dispute resolution efficiency improvement.

#### 4.2 CPFR (directional, magnitude-oriented)

- **Scale:** Support 3,000+ vendors and 200+ internal users; 6,600+ daily read operations without degradation.
- **Performance:** Query and availability targets per NFR-1 (CPFR).
- **Data consistency:** Single source of truth, daily immutable snapshots, definitive lineage and audit.
- **Capacity reallocation:** ISM and analyst capacity redirected from manual data prep and delivery to strategic vendor collaboration and analysis.
- **Vendor/portal adoption:** High adoption of CPFR module in CPH and self-service capabilities; measurement via portal usage and adoption metrics.

Traceability: these criteria map to FR-5 through FR-10 and NFR-1, NFR-3, NFR-4.

---

## 5. Phased Release Plan

- **Parallel track 1 — CPFR Phase 1:** SC-BIE builds and deploys the CPFR data platform (Snowflake, semantic layer, vendor isolation, daily refresh, internal tools). CPFR module development in CPH cannot start in earnest until this platform is deployed (~3-month gap).
- **Parallel track 2 — VC Phases 1 & 2:** CPH team delivers VC/Chargeback in CPH. Phase 1 (Chargebacks): File Access Control framework, chargeback data access, dispute process integration for 123 vendors. Metrics: POA Fill-Rate, ASN Fill-Rate, ASN On-Time, No Call No Show, Reschedules, Value Added Services, Pallet Damages, Refusals, PO On-Time (Weekly/Monthly). Phase 2 (Violations): Violation data access for all vendors. Metrics: Pkg/Pallet not securely wrapped, Pallet Improperly Built, Load Not Secured, Pallet Damages, Pallet Over Height, Mixed SKU Carton Not Labeled, Pallet Not Labeled Correctly, Carton Not Labeled Correctly, UPC Not Found On Item, UPC Does Not Scan, Refusal, EDI Expiration (Weekly/Monthly).
- **Transition of CPH capacity:** Once the CPFR data platform is deployed, CPH development capacity moves to CPFR module work—and should do so as close to that timeframe as possible. This is a transition of *what CPH works on next*, not a transfer of platform assets or maintenance from SC-BIE to CPH. Plan for developer and UX continuity so CPFR module development can start as soon as the platform is ready.
- **VC Phase 3 = CPFR Phase 2:** The CPFR module in CPH (vendor-facing CPFR reports, viewer, tier-based access) is the same deliverable as VC Phase 3. It is dependent on the deployed CPFR data platform and alignment of vendor isolation between CPH and the SC-BIE semantic layer.

---

## 6. Explored Solutions (Feasibility Reference)

*This section summarizes explored solutions to demonstrate feasibility. These are not final solution decisions; detailed architecture is documented in the CPFR Platform & Portal BRD and technical specifications.*

- **CPFR platform:** Snowflake-based data platform with a semantic layer, vendor isolation, daily refresh, and materialized views; scales to 3K+ vendors and supports daily immutable snapshots. CPH hosts the vendor-facing and administrative features that consume this platform.
- **CPH integration:** Vendor-facing interface within existing Chewy Partner Hub; self-service for data access, contact management, and report distribution (CPFR and VC); unified vendor experience across VC, Chargeback, and CPFR modules; Replen Tech engineering and EDS security alignment.

*For full platform architecture, ETL flow, and technical design, see the CPFR Platform & Portal BRD and related technical specifications.*

---

## 7. Constraints & Assumptions

#### Constraints

- **C-1 CPH integration:** Portal must integrate into existing Chewy Partner Hub infrastructure; development must align with CPH architecture and Replen Tech resources.
- **C-2 Vendor experience cohesion:** Avoidance of vendor experience fragmentation is a critical requirement (Sr. Director of Retail I.T. Product Management). All CPH modules must maintain a unified vendor experience.
- **C-3 Resource availability (shared):** Design and development resources are subject to approval and availability for both VC and CPFR workstreams; timelines may require flexibility. If not addressed, CPFR will likely face the same resource constraints as VC.
- **C-4 Sequencing / CPH capacity for CPFR module:** CPFR module work in CPH cannot start in earnest until the CPFR data platform is deployed. Once deployed, CPH should pivot to CPFR module development as close to that timeframe as possible. This is described as transition of CPH development capacity or sequencing—not as a handoff of platform assets or maintenance from SC-BIE to CPH.
- **C-5 Snowflake & SQL (CPFR):** Enterprise has standardized on Snowflake; CPFR platform must leverage Snowflake infrastructure and SQL-based access patterns.
- **C-6 VDS complementarity (CPFR):** CPFR platform must complement, not replace, existing VDS infrastructure.

#### Assumptions

- **CPFR:** Daily immutable snapshots meet business needs for collaborative planning; tier structure serves as templates with customization capability; 2 years of historical data with daily granularity meets analytical needs.
- **VC:** Some vendors will continue to prefer email reports despite portal availability; 30% improvement in dispute resolution efficiency is achievable through platform consolidation; $21M entitlement opportunity is achievable through a scalable framework.

---

## 8. Dependencies & Risks

#### Dependencies

- **D-1 CPH / Replen Tech development:** Portal integration and CPH module development require Replen Tech (CPH) engineering resources. Mitigation: joint roadmap and defined requirements. Status: active collaboration in progress.
- **D-2 EDS security approval:** Portal and platform require EDS security review and approval. Mitigation: leverage existing Replen Tech EDS partnerships. Status: security review process initiated.
- **D-3 Design resources (shared):** UX/UI design resources are subject to approval and availability for both VC and CPFR. Mitigation: plan for outsourcing or shared design if dedicated resources cannot be confirmed. Status: approval pending where applicable.
- **D-4 Transition of CPH capacity to CPFR module:** CPH team (developers/UX) will transition from VC work to CPFR module work once the CPFR data platform is deployed. Mitigation: plan for continuity so CPFR module development can start as close as possible to that timeframe; describe as transition of CPH capacity, not handoff. Status: planning in progress.
- **D-5 Vendor isolation alignment:** Alignment of vendor isolation between CPH and the SC-BIE semantic data layer is required for CPFR module integration. Mitigation: early coordination between SC-BIE, CPH, and CPFR teams; configuration properties in line-of-sight early. Status: coordination required.
- **D-6 Vendor adoption:** Success requires vendor adoption of portal and self-service capabilities. Mitigation: co-branded rollout with VC and CPFR, vendor education, email backup option. Status: communication and transition planning in progress.
- **D-7 Data source availability (CPFR):** CPFR platform requires reliable, timely data sources for daily refresh. Mitigation: leverage existing ETL processes and data sources. Status: data sources identified and validated.

#### Risks

- **R-1 Vendor experience fragmentation / inter-team alignment:** Multiple CPH modules (VC, Chargeback, CPFR) could create a fragmented vendor experience if not coordinated; misalignment between CPFR, Replen Tech, and VC teams could delay implementation. Impact: critical (fragmentation); high (alignment). Mitigation: consistent design patterns, developer/UX continuity, regular coordination between VC and CPFR teams, centralized governance, joint roadmap.
- **R-2 Vendor adoption:** Vendors may not adopt the portal, limiting self-service benefits. Impact: high. Mitigation: co-branded rollout, vendor education, email backup option, gradual onboarding, monitor utilization.
- **R-3 Resource availability (shared):** Design and development resources may not be available as planned for VC or CPFR. Impact: medium. Mitigation: plan for outsourcing or shared resources, early resource planning, flexible timeline. Affects both workstreams.
- **R-4 Integration complexity:** Integrating dispute process, email systems, CPFR data, and contact management could be more complex than anticipated. Impact: medium. Mitigation: phased approach, early technical review, regular technical checkpoints.
- **R-5 Vendor isolation alignment:** CPH vendor isolation and SC-BIE semantic layer may not align, creating integration challenges for the CPFR module. Impact: medium (affects CPFR Phase 2). Mitigation: early coordination, document vendor isolation requirements, configuration in line-of-sight.
- **R-6 Performance / scalability at scale:** Platform performance may degrade with 3,000+ users (CPFR); VC scale from 123 to thousands may stress systems. Impact: high. Mitigation: architecture designed for scale, performance testing, scalability validation before expansion.
- **R-7 Platform sustainment (CPFR):** Long-term CPFR platform maintenance may not be adequately resourced. Impact: medium. Mitigation: clear ownership by Supply Chain B.I. team, ongoing Replen Tech and EDS support.

---

## 9. Document Maintenance

This document should be updated when:
- Requirements are refined through stakeholder feedback
- New constraints or dependencies are identified
- Phased release plans evolve

**Maintenance principles:**
- Preserve requirements even as solutions evolve
- Clearly distinguish between requirements and context/commentary
- Update the "Last Updated" date with each significant change

---

*End of merged BRD draft. Source assessment: CPFR_VC_BRD_Merge_Step1_Assessment.md. Source BRDs: CPFR Platform & CPH Portal - BRD; VC_CPH_BRD.*

# Vendor Compliance & Chargeback - CPH Portal BRD

**Document Type:** Business Requirements Document  
**Last Updated:** 2026-01-26  
**Status:** Draft for Review

## Document Purpose

This document captures business requirements, success criteria, constraints, dependencies, and risks for the Vendor Compliance (VC) and Chargeback CPH Portal initiative. Requirements are defined independently of specific technical approaches.

**Note:** This document focuses on what must be achieved (requirements). Problem statements and user needs are documented in the source VC document ("CPH and Vendor Compliance .pdf").

## Table of Contents

- [Business Requirements](#business-requirements)
- [Success Criteria](#success-criteria)
- [Constraints & Assumptions](#constraints--assumptions)
- [Dependencies & Risks](#dependencies--risks)
- [Document Maintenance](#document-maintenance)

---

## Business Requirements

### Functional Requirements

**FR-1: Data Access & Reporting Requirements**
- **REQ-1.1:** Provide single, consistent location within CPH where vendors can access all chargeback and compliance reports without sorting through multiple email messages
- **REQ-1.2:** Provide centralized repository for historical chargeback and compliance data accessible through CPH with self-service retrieval
- **REQ-1.3:** Enable Category Managers and In-Stock teams to access all vendor reports within CPH for quick reference and decision-making
- **REQ-1.4:** Provide table outputs from CPH platform for internal analysis (chargeback disputes, vendor feedback, ticket dispositions, usage, program performance data)
- **REQ-1.5:** Provide Tableau views or data outputs showing data sharing levels across vendor base (without requiring CPH login)

**FR-2: Dispute Resolution Requirements**
- **REQ-2.1:** Integrate dispute functionality within CPH (eliminate redirect to Oracle CRM)
- **REQ-2.2:** Display all chargebacks, charge types, and disputes in single interface
- **REQ-2.3:** Enable vendors to file disputes directly within platform without duplicate documentation uploads
- **REQ-2.4:** Store all supporting documents and case details in one platform
- **REQ-2.5:** Reduce dispute resolution time from current baseline (12 clicks, 20 minutes) to <5 clicks and <5 minutes

**FR-3: Access Control & Management Requirements**
- **REQ-3.1:** Provide Category Manager interface within CPH to assign or remove report access by vendor (File Access Control framework - critical first step)
- **REQ-3.2:** Enable Category Managers to control which vendors receive specific reports aligned to business strategy
- **REQ-3.3:** Consolidate vendor contact data management within CPH (eliminate three-table fragmentation across Chargebacks, VC, CPFR, Cognizant)
- **REQ-3.4:** Enable vendor self-service for contact and distribution preferences
- **REQ-3.5:** Enable vendors to grant access to external stakeholders based on admin credentials
- **REQ-3.6:** Reduce support tickets for contact updates from current baseline of 90 tickets per month

**FR-4: Communication & Scalability Requirements**
- **REQ-4.1:** Reduce email volume from current baseline of 65 emails per month per vendor (45 from Chargebacks, 20 from CPFR/VC)
- **REQ-4.2:** Maintain email report functionality for vendors who prefer email delivery, with vendor control over which reports are emailed to specific team members
- **REQ-4.3:** Consolidate email system to read directly from CPH contact management and report distribution settings (replace Python and SPARK-based processes)
- **REQ-4.4:** Provide proof of delivery for emailed reports
- **REQ-4.5:** Support expansion from current 123 vendors to thousands without proportional increase in manual workload
- **REQ-4.6:** Enable program expansion to capture estimated $21M entitlement opportunity

**FR-5: Vendor Experience Cohesion Requirements**
- **REQ-5.1:** Ensure unified vendor experience across VC, Chargeback, and future CPFR modules within CPH
- **REQ-5.2:** Maintain consistent navigation, data access patterns, and user interface across all CPH modules
- **REQ-5.3:** Avoid vendor experience fragmentation (critical requirement established by Sr. Director of Retail I.T. Product Management)

### Non-Functional Requirements

**NFR-1: Performance Requirements**
- **REQ-N1.1:** System must support current 123 vendors with capacity for expansion to thousands
- **REQ-N1.2:** Dispute resolution process must complete in <5 clicks and <5 minutes
- **REQ-N1.3:** Historical data retrieval must be self-service without significant delay

**NFR-2: Security & Data Isolation Requirements**
- **REQ-N2.1:** Enforce strict vendor data isolation ensuring vendors access only their own data
- **REQ-N2.2:** Implement Row-Level Security (RLS) with vendor_id matching for data isolation
- **REQ-N2.3:** RLS key mapping must support CPH vendor isolation framework and align with SC-BIE semantic data layer for future CPFR integration (reference requirement - detailed schemas in technical specifications)

**NFR-3: Integration Requirements**
- **REQ-N3.1:** Integrate seamlessly with existing Chewy Partner Hub (CPH) infrastructure
- **REQ-N3.2:** Maintain compatibility with existing internal tools (Tableau, reporting systems)
- **REQ-N3.3:** Support future integration with CPFR workstream (Version 3)

**NFR-4: Usability Requirements**
- **REQ-N4.1:** Portal interface must be intuitive for vendors with varying technical capabilities
- **REQ-N4.2:** Administrative tasks (contact management, email preferences) must be self-service
- **REQ-N4.3:** Support multiple access modalities (web portal, email) based on vendor preferences

---

## Success Criteria

**SC-1: Communication Efficiency**
- **Baseline:** 65 emails per month per vendor (45 from Chargebacks, 20 from CPFR/VC)
- **Target:** Significant reduction in email volume through portal adoption
- **Measurement:** Email volume tracking and portal usage analytics

**SC-2: Dispute Resolution Efficiency**
- **Baseline:** 12 clicks and 20 minutes to reach dispute resolution
- **Target:** <5 clicks and <5 minutes (aligned with competitor platforms)
- **Additional Target:** 30% improvement in dispute resolution efficiency
- **Measurement:** User interaction tracking and time-to-resolution metrics

**SC-3: Support Ticket Reduction**
- **Baseline:** 90 tickets per month for contact list corrections/updates
- **Target:** Significant reduction through unified contact management
- **Measurement:** Support ticket volume tracking

**SC-4: Program Scalability**
- **Baseline:** 123 vendors in Chargeback Program
- **Target:** Support expansion to capture $21M entitlement opportunity
- **Measurement:** Vendor onboarding capacity and system performance metrics

**SC-5: Vendor Adoption**
- **Target:** High adoption rate of CPH portal for chargeback and compliance data access
- **Measurement:** Portal login rates, feature usage analytics, vendor feedback

**ROI Value Drivers:** $10.8M annual chargeback-related data, $21M entitlement opportunity, 1,500 Oracle CRM tickets/year reduction, 30% dispute resolution efficiency improvement

**Version Release Plan:**
- **Version 1 (Chargebacks):** File Access Control framework, chargeback data access, dispute process integration for 123 vendors. Metrics: POA Fill-Rate, ASN Fill-Rate, ASN On-Time, No Call No Show, Reschedules, Value Added Services, Pallet Damages, Refusals, PO On-Time (Weekly/Monthly)
- **Version 2 (Violations):** Violation data access for all vendors. Metrics: Pkg/Pallet not securely wrapped, Pallet Improperly Built, Load Not Secured, Pallet Damages, Pallet Over Height, Mixed SKU Carton Not Labeled, Pallet Not Labeled Correctly, Carton Not Labeled Correctly, UPC Not Found On Item, UPC Does Not Scan, Refusal, EDI Expiration (Weekly/Monthly)
- **Version 3 (CPFR):** Subsequent workstream - see CPFR BRD. Dependencies: SC-BIE team completion of CPFR data platform, handoff of developers/UX designers, RLS key mapping alignment

---

## Constraints & Assumptions

### Enterprise Technology Constraints

**C-1: CPH Integration Requirement**
- **Constraint:** Portal must integrate into existing Chewy Partner Hub infrastructure
- **Implication:** Portal development must align with CPH architecture and Replen Tech resources
- **Rationale:** Leverages existing portal infrastructure and avoids duplication

**C-2: Vendor Experience Cohesion**
- **Constraint:** Avoidance of vendor experience fragmentation is critical requirement (established by Sr. Director of Retail I.T. Product Management)
- **Implication:** All CPH modules must maintain unified vendor experience
- **Rationale:** Ensures cohesive vendor experience across VC, Chargeback, and CPFR capabilities

### Organizational Constraints

**C-3: Resource Availability**
- **Constraint:** Design and development resources subject to approval and availability
- **Implication:** Timeline may require flexibility based on resource confirmation
- **Rationale:** Design team tentative buy-in for post-February start; formal approval from Richard pending

**C-4: Handoff Coordination**
- **Constraint:** CPFR workstream depends on SC-BIE team completion of CPFR data platform
- **Implication:** VC workstream can stage before CPFR, but handoff must be managed to avoid resource loss
- **Rationale:** Timing coordination required between VC, CPFR, and SC-BIE workstreams

### Business Assumptions

**A-1: Email Preference Retention**
- **Assumption:** Some vendors will continue to prefer email reports despite portal availability
- **Rationale:** Vendor outreach sessions indicate preference for email among some vendors with automated systems
- **Validation:** Email capability maintained while reducing overall email volume

**A-2: Dispute Resolution Efficiency**
- **Assumption:** 30% improvement in dispute resolution efficiency achievable through platform consolidation
- **Rationale:** Compliance Manager estimate based on consolidated documentation and workflow
- **Validation:** Target validated against competitor platform benchmarks (<5 clicks, <5 minutes)

**A-3: Program Expansion Opportunity**
- **Assumption:** $21M entitlement opportunity achievable through scalable framework
- **Rationale:** Current 123 vendors represent subset of potential program participants
- **Validation:** Business case supports expansion with scalable architecture

---

## Dependencies & Risks

### Dependencies

**D-1: CPH Development Team**
- **Dependency:** CPH development team resources for portal framework implementation
- **Mitigation:** Joint roadmap and defined requirements
- **Status:** Active collaboration in progress

**D-2: Design Resources**
- **Dependency:** UX/UI design resources (tentative buy-in for post-February start; formal approval from Richard pending)
- **Mitigation:** Plan for outsourcing if dedicated design stakeholder cannot be confirmed
- **Status:** Approval pending

**D-3: Handoff to CPFR Workstream**
- **Dependency:** Developer and UX designer continuity from VC workstream to CPFR workstream
- **Mitigation:** Ensure handoff protocols established to avoid "lost" resources
- **Status:** Planning in progress

**D-4: RLS Key Mapping Alignment**
- **Dependency:** SC-BIE team must have configuration properties in "line-of-sight" for RLS key mapping alignment
- **Mitigation:** Early coordination between SC-BIE, CPH, and CPFR teams
- **Status:** Coordination required

### Risks

**R-1: Vendor Experience Fragmentation**
- **Risk:** Multiple CPH modules (VC, Chargeback, CPFR) could create fragmented vendor experience if not properly coordinated
- **Impact:** Critical - Sr. Director of Retail I.T. Product Management has established this as critical hurdle
- **Mitigation:** Maintain consistent design patterns, ensure developer/UX continuity, establish clear handoff protocols, regular coordination between VC and CPFR teams
- **Probability:** Medium | **Impact:** Critical

**R-2: Vendor Adoption Challenges**
- **Risk:** Vendors may resist adopting new portal, preferring familiar email-based processes
- **Impact:** High - Could limit ROI realization and program expansion
- **Mitigation:** Maintain email report capability, provide vendor education and support, ensure clear value proposition, gradual migration approach
- **Probability:** Medium | **Impact:** High

**R-3: Resource Availability**
- **Risk:** Design and development resources may not be available as planned
- **Impact:** Medium - Could delay implementation timeline
- **Mitigation:** Plan for outsourcing, early resource planning, flexible timeline with buffer
- **Probability:** Medium | **Impact:** Medium

**R-4: Integration Complexity**
- **Risk:** Integrating dispute process, email systems, and contact management could be more complex than anticipated
- **Impact:** Medium - Could delay delivery or require scope adjustments
- **Mitigation:** Phased approach (Version 1, then Version 2), early technical review, regular technical checkpoints
- **Probability:** Medium | **Impact:** Medium

**R-5: RLS Key Mapping Alignment**
- **Risk:** SC-BIE semantic data layer and CPH vendor isolation may not align, creating integration challenges for CPFR workstream
- **Impact:** Medium - Affects future CPFR integration, not immediate VC delivery
- **Mitigation:** Ensure SC-BIE team has configuration properties in "line-of-sight" now, document RLS requirements, early coordination
- **Probability:** Low | **Impact:** Medium

**R-6: Scalability Limitations**
- **Risk:** System may not scale effectively from 123 vendors to thousands
- **Impact:** High - Limits ability to capture $21M entitlement opportunity
- **Mitigation:** Architecture designed for scalability from outset, performance testing, scalability validation before expansion
- **Probability:** Low | **Impact:** High

---

## Document Maintenance

This document should be updated as:
- Requirements are refined through stakeholder feedback
- New constraints or dependencies are identified
- Version release plans evolve

**Maintenance Principles:**
- Preserve requirements even as solutions evolve
- Clearly distinguish between requirements and context/commentary
- Update "Last Updated" date with each significant change

---

**End of Document**

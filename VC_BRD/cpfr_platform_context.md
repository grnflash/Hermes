# CPFR Platform & Portal: Context Document
## Living Record of Project Context, Decisions, and Evolution

**Last Updated:** 2025-01-XX  
**Purpose:** This document serves as a comprehensive, living record of the CPFR Platform & Portal initiative. It captures strategic context, organizational landscape, key decisions, terminology, and working principles that transcend any particular deliverable.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Organizational Context](#organizational-context)
3. [Current State Analysis](#current-state-analysis)
4. [Strategic Objectives](#strategic-objectives)
5. [Key Terminology](#key-terminology)
6. [Technical Context](#technical-context)
7. [Organizational Sensitivities & Constraints](#organizational-sensitivities--constraints)
8. [Value Framework](#value-framework)
9. [Decision History](#decision-history)
10. [Related Initiatives](#related-initiatives)

---

## Project Overview

### Initiative Purpose
The CPFR Platform & Portal initiative modernizes how Chewy shares supply-chain data with vendors and enables internal teams to collaborate effectively. The project delivers two complementary components:

1. **CPFR Data Platform** (Snowflake-based): A unified, governed source for CPFR data that replaces ad-hoc reporting workflows and fragmented data access patterns.
2. **CPFR Vendor Portal** (CPH Integration): A vendor-facing, self-service interface within Chewy Partner Hub that provides secure, 24/7 access to CPFR data.

### Origin Story
The project evolved from the CPFR team's need to modernize data sharing between Chewy and its vendors. Historically, CPFR data has been distributed via weekly emailed reports generated from fragmented queries, creating:
- Data inconsistencies across different systems and extracts
- Scalability limits (currently serving ~200 vendors via VDS, with business need for 3,000+)
- Excessive manual coordination work
- Time-of-day data drift issues
- Limited vendor self-service capabilities

### Evolution of Documentation
Early documentation was created when CPFR expected minimal outside support and had to justify feasibility to internal B.I. teams:
- **CPFR Platform – Executive Summary.pdf** – Initial rationale and architecture for Snowflake-based semantic layer
- **CPFR Semantic Platform – Specs and Reqs.pdf** – Technical deep dive on scalability, access control, and implementation
- **CPFR_VDS_CPH.pdf** – Comparative analysis between CPFR, VDS, and emerging CPH capabilities

These documents remain directionally valid but reflect a different organizational context than the current collaborative approach.

---

## Organizational Context

### Key Teams & Ownership

**CPFR Team (Supply Chain B.I.)**
- **Role:** Data platform ownership and long-term maintenance
- **Team Size:** ~8 Business Intelligence Engineers (BIE I through BIE III) under a new director
- **Capacity:** 30-50% allocation (equivalent to 2-4 FTE) for platform implementation
- **Expertise:** Semantic layers are core BIE competency

**Replenishment Technology (Replen Tech)**
- **Role:** Portal engineering, product management, and security integration
- **Leadership:** Ratna Ramani
- **Resources:** Software engineers, data engineer, product management, existing EDS partnerships
- **Ownership:** CPH portal development and vendor-facing interface

**Vendor Compliance (VC) Team**
- **Role:** Co-development partner for vendor portal capabilities
- **Relationship:** Parallel workstream developing vendor portal on CPH
- **Future Integration:** Architecture can be extended to include VC data

**Electronic Data Security (EDS)**
- **Role:** Security governance and compliance
- **Relationship:** Existing partnership through Replen Tech

**In-Stock Managers (ISMs)**
- **Role:** Primary internal users of CPFR data
- **Count:** ~200 ISMs across categories (Consumables, Health/Science, EFE, Hard Goods)
- **Usage Pattern:** Cross-vendor analysis, flexible querying, vendor collaboration

### Organizational Patterns
Chewy patterns many business processes after Amazon, including:
- **OP1/OP2 Process:** Annual planning and provisioning cycles
- **Documentation Style:** Amazon product management formats (PRFAQs, working backwards)
- **Cultural Influence:** Many former Amazonians in leadership roles

---

## Current State Analysis

### Data Distribution Methods

**Weekly Emailed Reports**
- **Scale:** 2,300+ vendors receiving weekly inventory and forecast reports
- **Process:** Manual coordination of data extraction, validation, and delivery
- **Issues:**
  - Time-consuming manual work
  - Risk of data inconsistencies when different systems produce conflicting results
  - Limited scalability
  - Time-of-day drift (data changes throughout the day)

**VDS (Vendor Data Services)**
- **Scale:** ~200 premium vendors via on-demand dashboards
- **Architecture:** Session-based design with API partition model
- **Strengths:**
  - Effective for deep exploration and infosec isolation
  - Real-time queryability for time-sensitive data
- **Limitations:**
  - Scales poorly to thousands of concurrent vendors
  - Complicates time-series comparisons
  - One-to-many vendor relationships create exponential scaling challenges

### Data Architecture Current State

**Primary Repository:** Snowflake (migration from multiple databases in progress)

**Current Access Patterns:**
- API-based services fetching from Snowflake
- Direct Snowflake queries from internal teams (creating "shadow organization" tools)
- Fragmented tool landscape with inconsistent data interpretations

**Data Tiers (Current Structure):**
- **Tier 4:** 3-month forecast (~12MB, single CSV equivalent) - *Note: Being deprecated due to improved 6-month forecast accuracy*
- **Tier 3:** 6-month forecast (~30MB, ~200K rows)
- **Tier 2:** Tier 3 + inventory metrics (on-hand, on-order, auto-ship backorders, days-of-supply)
- **Tier 1:** Tier 2 + OP/NOP placement metrics + granular SKU/fulfillment-center/region breakdowns
- **Tier 0 (VDS):** Tier 1 + real-time API queryability

**Data Dimensions:**
- Fulfillment Centers: Up to 30 per row (sparse distribution)
- Additional Columns: ~15 max for Tier 2/1
- Expansion Factor: 1x to 30x depending on SKU/vendor distribution
- Historical Requirement: 2 years retention desired

### Scale Requirements

**Current Capacity:**
- ~200 vendors actively supported through VDS
- ~200 ISMs (internal users)

**Business Target:**
- 3,000-5,000 vendors enrolled in CPFR processes
- Support for concurrent access patterns

**Query Volume:**
- ~6,600 reads/day (2x ISM + 2x Vendor average)
- 200+ concurrent users expected

**Data Refresh:**
- Daily refresh during 2-3 AM lockout window
- Snapshot consistency requirement (not real-time)

---

## Strategic Objectives

### Core Motivations

1. **Single Version of Truth**
   - Unify internal (ISM) and external (vendor) data sources
   - Eliminate conflicting numbers in vendor conversations
   - Provide definitive data lineage for audit and accountability

2. **Streamlined Access**
   - Enable vendors to self-serve data access
   - Enable ISMs to collaborate using shared metrics
   - Reduce manual coordination overhead

3. **Governance and Auditability**
   - Provide consistent, immutable daily snapshots
   - Eliminate time-of-day drift issues
   - Support audit requirements with definitive access control

4. **Scalability**
   - Serve 3,000-5,000 vendors concurrently
   - Support growth without proportional infrastructure overhead

5. **Future Readiness**
   - Create extensible foundation for AI/ML-driven analytics
   - Enable cross-team data sharing (CPFR, VC, Merch, others)
   - Support machine learning model training with normalized data cadence

### Value Themes

**A. Operational Cohesion & Efficiency**
- Eliminate redundant queries and reconciliations
- Free ISM and analyst time for proactive vendor and forecast work
- Redirect capacity from routine reporting to insight generation
- Estimated recurring value: ~$675k/year

**B. Vendor Enablement & Partnership Expansion**
- Always-available daily data (no time-of-day drift)
- Self-service management of notifications and contacts
- Scales to thousands of vendors with minimal overhead
- Estimated recurring value: ~$705k/year

**C. Enterprise Data Alignment & Future Readiness**
- Shared definitions and lineage across CPFR, VC, Merch, and others
- Immutable daily snapshots for audit and machine learning readiness
- Estimated recurring value: ~$450k/year

**D. Strategic Growth Enablement**
- Complements—not replaces—VDS; serves broader vendor cohort
- Architecture can be extended to include Vendor Compliance (VC) data
- Estimated recurring value: ~$650k/year

**Total Conservative Annual Entitlement:** ≈ **$2.5M recurring**

---

## Key Terminology

- **CPFR:** Collaborative Planning, Forecasting & Replenishment (Chewy's supply-chain vendor collaboration program)
- **VC:** Vendor Compliance team
- **CPH:** Chewy Partner Hub, the vendor-facing web portal
- **Replen Tech:** Replenishment Technology team within I.T., led by Ratna Ramani; owns portal engineering
- **EDS:** Electronic Data Security team
- **ISM:** In-Stock Manager (Chewy internal role responsible for vendor relationships and inventory management)
- **VDS:** Vendor Data Services; an older system optimized for premium, low-concurrency, on-demand analytics
- **BIE:** Business Intelligence Engineer
- **OP/NOP:** Order Placement / Network Optimization Program
- **ASBO:** Auto Ship Back Order
- **SKU:** Stock Keeping Unit
- **FC:** Fulfillment Center
- **RLS:** Row-Level Security (database feature for multi-tenant data isolation)

---

## Technical Context

### Platform Architecture (Explored Solution)

**Hybrid Approach:**
- **Semantic Layer (25% of VDS ecosystem):** CPFR data with snapshot consistency requirements
- **API Services (75% of VDS):** Real-time data with time-of-day relevance
- **Unified Access Layer (Future):** Abstraction enabling seamless transitions between architectures

**Core Semantic Layer Structure:**
```
Daily ETL → Snowflake Raw Tables → Base Semantic Table (RLS) → Materialized Views → User Access
```

**Base Table Design:**
- Single logical table with physical partitioning
- Clustering: snapshot_date, vendor_id, tier_level
- Estimated Size: <1GB per daily snapshot, ~730GB for 2-year retention
- Partitioning: Time-based with compound clustering for RLS performance

**Row-Level Security (RLS) Implementation:**
- Vendor Policy: Strict isolation via vendor_id matching
- ISM Policy: Broader scope with override capabilities
- Inheritance: Materialized views inherit RLS from base table
- Multi-vendor Support: User-vendor mapping table for complex relationships

**Materialized Views Strategy:**
- Purpose: Performance optimization for common query patterns
- Not Security Controls: RLS on base table provides all security
- Target Patterns: Vendor daily dashboards, common ISM reports
- Refresh: Sequential after base table refresh

### Portal Architecture (Explored Solution)

**CPH Integration:**
- Vendor-facing interface within existing Chewy Partner Hub
- Self-service capabilities for data access, contact management, notification preferences
- Secure 24/7 access with strict data isolation
- Email backup capability for vendors unable to access portal

**Access Patterns:**
- Portal access: Segregated from internal Chewy Team Member access
- Single-source data: Both portal and internal tools synchronize to same governed tables
- Clear separation of access scopes while maintaining data consistency

### Enterprise Technology Constraints

**Snowflake:**
- Enterprise decision to standardize on Snowflake
- Existing infrastructure and licensing in place
- Team expertise aligned with Snowflake capabilities

**SQL-Based Approach:**
- De facto standard for data warehouse operations
- Aligns with existing team skills and tooling
- Compatible with Snowflake's native capabilities

---

## Organizational Sensitivities & Constraints

### Political / Organizational Sensitivities

**VDS Relationship:**
- VDS has highly-placed leaders whose reputations are based on its success story
- VDS generates true bottom-line revenue
- Implied threat to VDS reputation/revenue must be carefully managed
- **Positioning:** CPFR platform complements VDS, does not replace it
- **Approach:** Avoid being "on the nose" about differences; emphasize complementarity without sounding patronizing

**Headcount Language:**
- Avoid implying headcount reduction
- Instead describe *capacity unlocking* or *redeployment to higher-value work*
- Focus on enabling existing teams to focus on strategic work

**Technical Jargon:**
- Avoid technical jargon that alienates non-technical readers
- Examples to avoid: "semantic layer", "real-time" (when daily snapshots are the requirement)
- Use accessible language: "data platform," "governed daily data," "capacity unlock"

**Speculative References:**
- Maintain pragmatic tone
- No speculative references to unrelated big bets (e.g., "Fulfilled by Chewy") unless substantiated

### Primary Risks and Mitigations

| **Risk** | **Mitigation** |
|----------|----------------|
| Data consistency across systems | Centralized governance, shared change-management process |
| Vendor adoption of portal | Co-branded rollout with VC and Replen Tech; vendor education and support |
| Inter-team alignment | Defined data contracts, joint roadmap |
| Platform sustainment | Owned by Supply Chain B.I., with Replen Tech and EDS support |

---

## Value Framework

### Deferred Success Criteria (For Future Validation)

The following success criteria were identified during requirements definition but are deferred from the proto-BRD pending baseline measurement and validation. These will be incorporated once baseline data and validated targets are established.

**SC-3 (Deferred): Increase in Time Available for Solutioning Supply Chain Issues**
- **Rationale:** Demonstrates capacity redirect to higher-value work
- **Measurement Approach:** Time allocation analysis
- **Status:** Baseline measurement and target setting in progress
- **Note:** This metric is causally linked to SC-1 (reduction in routine data preparation time)

**SC-5 (Deferred): Reduction in Vendor Requests Requiring ISM Intervention**
- **Rationale:** Demonstrates effective self-service capabilities
- **Measurement Approach:** Support ticket and request tracking
- **Status:** Baseline measurement and target setting in progress
- **Note:** This metric is closely related to SC-2 (reduction in support ticket volume)

**SC-8 (Deferred): Elimination of Conflicting Numbers in Vendor Conversations**
- **Target:** Zero reported instances of conflicting data in vendor meetings
- **Measurement:** ISM feedback and meeting notes
- **Rationale:** Core requirement for productive collaboration
- **Status:** Baseline measurement and target setting in progress
- **Note:** This metric represents a more advanced stage of the same problem addressed by SC-7 (reduction in data discrepancy incidents)

### Resource Constraints (For Reference)

**C-4: Resource Availability**
- **Constraint:** BIE team has 30-50% allocation (2-4 FTE equivalent) for platform implementation
- **Implication:** Implementation must be achievable within available capacity
- **Rationale:** Realistic resource planning based on team structure
- **Status:** Documented for planning purposes; not included in proto-BRD as it represents implementation planning detail rather than business requirement

### Success Metrics (CPFR Process-Level)

**Note:** CPFR metrics should reflect the success of the CPFR process itself, not underlying business metrics (e.g., Fill Rate % improvement indicates vendor success, not CPFR success). CPFR success metrics focus on:

**Operational Efficiency:**
- Time saved on data extraction, validation, and reconciliation
- Reduction in time spent re-pulling and validating data
- Increase in time available for solutioning supply chain issues
- Reduction in support ticket volume for routine data requests

**Access & Adoption:**
- Vendor self-service adoption rates
- Reduction in vendor requests requiring ISM intervention
- Increase in vendors accessing data proactively (not just when requested)
- Portal usage patterns and engagement metrics

**Data Quality & Consistency:**
- Reduction in reported data discrepancy incidents
- Elimination of conflicting numbers in vendor conversations
- Improvement in data lineage and audit trail completeness
- Cross-system data consistency measurements

**Scalability:**
- Vendor capacity expansion (progressive increase toward 3,000+ active vendors)
- Concurrent user support (200+ simultaneous sessions)
- Query performance metrics (<2 seconds for tier-specific queries)

**Strategic Enablement:**
- Cross-team data sharing adoption (VC, Merch, others)
- Foundation for future AI/ML initiatives
- Extensibility demonstrations (e.g., VC data integration)

### Derivative Business Benefits

While not direct CPFR metrics, the following business outcomes may improve as a result of better CPFR processes:
- Fill Rate % improvements (vendor performance metric)
- Forecast Accuracy improvements (planning metric)
- Exception resolution rates (operational metric)

These are noted as derivative benefits but are not the primary success criteria for the CPFR platform itself.

---

## Decision History

### Key Architectural Decisions

**Semantic Layer Approach (vs. Enhanced API Scaling)**
- **Decision:** Implement Snowflake-based semantic layer for CPFR data (25% of VDS ecosystem)
- **Rationale:** 
  - Snapshot consistency requirement for collaborative planning
  - API partition model doesn't scale to 3K vendors
  - Need for definitive audit capabilities
  - Performance optimization through materialized views
- **Date:** [To be updated]

**Hybrid Architecture (vs. Monolithic Approach)**
- **Decision:** Maintain API services for 75% of VDS requiring real-time access
- **Rationale:**
  - Different access patterns for real-time vs. snapshot data
  - Preserve existing VDS investments
  - Optimize each data type for its specific requirements
- **Date:** [To be updated]

**Daily Snapshot Model (vs. Real-Time)**
- **Decision:** Daily immutable snapshots during 2-3 AM lockout window
- **Rationale:**
  - Eliminates time-of-day drift
  - Provides consistent data views for collaborative planning
  - Enables historical comparison and auditability
  - Supports machine learning model training
- **Date:** [To be updated]

**Tier Structure Evolution**
- **Decision:** Tier structure serves as templates with customization capability
- **Rationale:**
  - Different vendors need different analytical depth
  - Tier 4 (3-month forecast) being deprecated due to improved 6-month forecast accuracy
  - High-touch vendors need metric-level customization (menu approach)
  - Tiers provide starting point, not rigid constraint
- **Date:** [To be updated]

### Implementation Phases

**Phase 1: Foundation Layer (30-60 days)**
- Base semantic table with comprehensive CPFR data
- Initial RLS implementation for vendor and ISM access
- Basic materialized views for Tier 4 and Tier 3 data
- Internal tool integration pilot

**Phase 2: Full Tier Implementation (90-120 days)**
- Complete materialized view set (Tiers 1-4)
- Vendor self-service interface options (Tableau, Power Query integration)
- Advanced RLS for complex vendor relationships
- Shadow organization tool migration pilots

**Phase 3: Unified Access Layer (150-180 days)**
- Abstraction layer enabling transparent routing between semantic layer and VDS APIs
- Migration framework for transitioning additional data types
- Enhanced audit and governance capabilities
- Performance optimization based on usage patterns

---

## Related Initiatives

### Chewy Partner Hub (CPH) Development
- **Relationship:** CPFR portal integrates into existing CPH infrastructure
- **Partners:** VC team and Replen Tech co-developing vendor portal capabilities
- **Synergy:** Shared infrastructure, security, and vendor management

### Vendor Compliance (VC) Data Integration
- **Future Opportunity:** Architecture can be extended to include VC data
- **Benefit:** Unified environment for vendor-specific information
- **Timeline:** Post-CPFR platform stabilization

### VDS Evolution
- **Relationship:** Complementary, not competitive
- **Differentiation:** VDS serves premium, low-concurrency, on-demand analytics
- **CPFR Platform:** Serves broader vendor cohort with snapshot consistency requirements
- **Future:** Unified access layer may enable seamless transitions between architectures

---

## Document Maintenance

This document should be updated as:
- New decisions are made
- Organizational context changes
- Technical approaches evolve
- Key learnings emerge from implementation

**Maintenance Principles:**
- Preserve historical context and decision rationale
- Update "Last Updated" date with each significant change
- Maintain clear separation between current state and historical decisions
- Document "why" not just "what"

---

**End of Context Document**


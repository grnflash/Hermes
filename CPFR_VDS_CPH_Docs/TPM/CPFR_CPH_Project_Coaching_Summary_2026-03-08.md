# CPFR-in-CPH Project: Coaching Context & Working Summary

**Purpose:** Mid-fidelity summarization of the initial coaching session (2026-03-08) for use as a portable context document across focal-area chats.  
**Companion document:** "Four Frameworks" (verbatim preservation of persona map, TPM role definition, document hierarchy, and 30-day action plan).

---

## 1. The Initiative

Chewy's CPFR (Collaborative Planning, Forecasting & Replenishment) program distributes weekly inventory and forecast data to ~2,300 vendors via email. The initiative seeks to modernize this into two complementary components:

- **CPFR Data Platform** (built by SC-BIE in Snowflake): governed, daily-refreshed, single-source-of-truth data layer with vendor isolation, tiered access, immutable snapshots, and lineage. This is the _foundation_.
- **CPFR Module in CPH** (Chewy Partner Hub—Chewy's equivalent of Amazon Vendor Central): vendor-facing portal providing on-demand access, self-service admin, scorecard/visualization landing page, and report distribution. This is the _last mile_.

CPFR's integration into CPH is paired with **Vendor Compliance (VC)** and Chargeback integration, which shares the same CPH infrastructure. The two workstreams (CPFR and VC) are led by separate business product owners but share a consolidated BRD and co-present as a unified front.

### Entitlement & Value Case

- CPFR-specific: ~$1.4M recurring annual benefit (ISM capacity reallocation, vendor enablement, data governance, cost avoidance)
- VC-specific: $21M entitlement opportunity, $10.8M annual chargeback-related data, 1,500 Oracle CRM tickets/year reduction
- Combined: supports Chewy's digital modernization strategy and establishes infrastructure for future advanced analytics / AI/ML
- 96% unweighted vendor approval rating for CPFR (sample-based)
- Major vendors (Blue Buffalo, Mars, Nestle-Purina) have explicitly requested API/portal access to CPFR data
- Documented $5M cost avoidance case (single forecast threshold mismatch event), ~$15M estimated annual exposure from recurring threshold issues

### Phased Architecture

- **Parallel Track 1 — CPFR Phase 1:** SC-BIE builds the data platform → **on track for 3/31/2026 delivery** at network grain (covers 98.4% of vendors, Tiers 2–4, excludes 45 Tier 1 vendors needing SKU/FC granularity). SKU/FC-grain semantic table is a known follow-on priority.
- **Parallel Track 2 — VC Phases 1 & 2:** CPH team delivers Chargebacks then Violations in CPH → **currently stalled in design/planning** due to personnel churn.
- **Transition:** Once CPFR platform is deployed, CPH development capacity pivots to CPFR module work (VC Phase 3 = CPFR Phase 2). This is a transition of _what CPH works on_, not a transfer of platform assets.
- The original sequencing rationale (keep CPH busy with VC while SC-BIE builds the platform) is now temporally inverted: the platform is ready, but VC hasn't primed the CPH pipeline.

---

## 2. Funding & Organizational Situation

### OP1 Failure

The initiative was submitted for OP1 (Chewy's Amazon-style annual planning process for dedicated resourcing) but did not get over the line. The failure mode was a combination of _other initiatives taking precedence_ and the submission being _inserted too late in the planning cycle_. The business case was not rejected on merit.

### Running on Allocation

Since the OP1 miss, the project has been funded through "allocation"—meaning labor comes from everyday hours rather than dedicated OP1-provisioned headcount. In practice, this means contributors chip in as bandwidth allows, and "possible" has been a moving target. There is no formal budget line or committed headcount-hours for CPFR-in-CPH.

### The TPM Gap

A cascading pattern of disengagement has removed every person who previously held connective-tissue responsibility:

| Person | Former Role on Project | What Happened |
|--------|----------------------|---------------|
| Ratna Ramani | Single-threaded owner / TPM (SDev Director) | Moved to an OP1 project |
| Jeremy Wartnick | Was to be new STO/TPM | Remit narrowed to SPARK (benefits VC, not CPFR) |
| Harish | TPM over Inbound Retail (navigational guide) | Recently pulled off the project |
| Shyam | Staff SDev working closely with Harish | Left the company |
| Santosh | Data engineer interfacing with CPH team | Redeployed to other projects |

In the 3/05/2026 meeting ("CPH-Vendor Facing Tools and Leadership Alignment"), **Erdem Eskigun confirmed no TPMs would be assigned**. He offered that his team could provide technical coaching if Dave Livesay's org produced someone capable of working with engineers in a product-management capacity.

### Nathan's Role Transition

**Nathan Miles** (the user) is a Sr. Program Manager on the CPFR team who has been the primary author of the BRD, entitlement document, user stories, alternatives analysis, and wireframes. He has volunteered to step into the TPM gap. Key context:

- Background spans business/project management with meaningful coding experience and SDLC exposure (not extensive but real)
- Already works closely with BI engineers (Stefan's SC-BIE team)
- Has no direct product management experience in an Amazon-like environment, and no prior TPM experience
- The CPFR team was recently absorbed into a new centralized Program Management team under Phanindher
- Succession-planning conversations have pointed Nathan toward technical roles (TPM-flavored), making this assignment an implicit audition
- **Both professional and personal stakes** are attached to this transition

### Key Organizational Observation

Tom Burritt (Director between Phanindher and Dave Livesay, limited project involvement until recently) stated in a call that this initiative should have been OP1 and likely won't get the commitment it needs until it is—implying next year. This is either a death sentence for near-term momentum or a rallying cry for the PRFAQ, depending on how it's used.

---

## 3. Stakeholder Map

### Organizational Relationships

- **Dave Livesay** — Sr. Director, Inventory Management. Nathan's 2-skip-level boss (was 1 skip-level before reorg). Primary executive sponsor. Puts "shoulder" into driving priority with leadership.
- **Tom Burritt** — Director between Phanindher and Dave. Limited project involvement. Made the "should have been OP1" observation.
- **Phanindher** — Associate Director, new PM team (Nathan's direct boss). Inherited this project cold. Previously in long-term FC planning (slower cadence). Eager to help but still calibrating to the Instock/CPFR tempo.
- **Eric Beebe** — Director of Instock Operations. Nathan's former boss. Still involved but no longer in reporting chain. Asks for visual timelines and accountability structures.
- **Richard Neely** — Sr. Director, Inbound-Retail Product Management. Controls design resources. Has oscillated between support and resistance. Recently came down hard on Nelson for not having an integrated plan that avoids "vendor experience fragmentation." Key gatekeeper.
- **Erdem Eskigun** — (Under Richard Neely) The person who confirmed no TPMs. Controls the engineering coaching offer. Target of the "CPH-Vendor Facing Tools and Leadership Alignment" meeting on 3/5.
- **Aaron Greene** — Director over TPMs working for Erdem. Described as "wishy-washy," prone to hearing what he wants, and has been caught claiming ignorance of prior agreements when original witnesses have rotated out. **Requires meticulous paper-trailing.**
- **Nathan Nelson** — Business product owner for VC. Co-author of consolidated BRD. Primary operational partner. Reports to Keinan Zanck.
- **Keinan Zanck** — Runs Supply Chain Optimization. Nathan Nelson's boss. VC rolls up here.
- **Chris** — Works with Nathan Nelson on the VC team. Primary person handling chargebacks.
- **Stefan** — Heads SC-BIE. Building the CPFR data platform. Reports under the same Sr. Director chain as Nathan (under Dave). Natural ally; wants his platform to be consumed.
- **Tamara** — Heads UX/UI (CDS design team). Design resource assignment pending Richard Neely's approval.
- **Amanda Greenslit** — Heads Vendor Experience team. Oversight over user-requirements underpinning much of CPH. Natural validator for CPFR user stories.
- **Justin Bowman** — Portfolio manager for Inbound-Retail. Has visibility into how work gets prioritized across CPH.
- **Jeremy Wartnick** — Original TPM-designee whose remit narrowed. Still helping with SPARK/VC elements. Organizational knowledge of CPH personnel.
- **Len Josephs** — SDev working for Jeremy.
- **Andy Sims** — BI lead over Replenishment BI (not SC-BI). Relevant to Tableau/Snowflake integration.
- **Steven Palmer** — Nathan's partner on the CPFR team (same Sr. PM role). Handles TM-facing CPFR work. Sharp, has technical chops, early vibe-coder on prior Chewy projects. Force multiplier for ISM engagement and potential rapid prototyping.

### Persona Archetypes (assigned in Four Frameworks document)

| Archetype | Person | Core Dynamic |
|-----------|--------|-------------|
| Committed Sponsor | Dave Livesay | Believes in it, pushes for it, but budget is political capital—minimize drafts |
| New Lieutenant | Phanindher | Inherited cold, needs shaped onboarding, can become active shield or passive relay |
| Realist Gatekeeper | Tom Burritt | Honest diagnosis of OP1 need; leverage his realism or lose to his pragmatism |
| Portfolio Guardian | Richard Neely | Fragmentation concern is both legitimate and a blocking lever |
| Resource Gatekeeper | Erdem Eskigun | Coaching offer is real but conditional on demonstrated capability |
| Teflon Stakeholder | Aaron Greene | Unreliable commitments; paper-trail everything, route decisions through Erdem |
| Allied Commander | Nathan Nelson | Best partner, but VC can proceed without CPFR—watch for asymmetric deprioritization |
| The Builder | Stefan | Platform builder who wants his work consumed; natural ally in Dave's chain |
| Inside Partner | Steven Palmer | Domain expert, ISM relationships, potential prototyping asset |
| User Advocate | Amanda Greenslit | Vendor Experience ownership; engage early for quality + organizational advocacy |

### Critical Stakeholder Insight

There is currently **no confirmed CPH technical contact** for CPFR integration. With Harish, Santosh, and Shyam all gone, the CPH engineering interface is an open question. Identifying or getting someone assigned is the most urgent concrete gap.

---

## 4. Key Strategic Observations

### The "Built Bridge, No On-Ramp" Framing

The CPFR data platform—the harder, riskier, more capital-intensive component—is nearly complete. What's missing is the last-mile portal work that lets vendors actually use it. The PRFAQ's most powerful argument: the foundation investment has been made; failing to build the on-ramp means that investment sits idle. The marginal cost to realize value is bounded and clear.

### Sequencing Collision

Original plan: VC work keeps CPH busy → platform ships → CPH pivots to CPFR. Reality: platform is shipping on time, but VC has stalled in design/planning due to churn. CPH developers haven't built muscle memory on portal architecture yet. If VC unstalls, it legitimately consumes CPH capacity first, potentially pushing CPFR module work further out despite the platform being ready. A strategic question remains open: argue for parallel CPH capacity for CPFR, or stay with sequential-after-VC.

### The Coordination Vacuum

Nathan isn't just filling a TPM gap—he's rebuilding connective tissue between organizations that have been progressively losing their links to each other. The real job is re-establishing the coordination function that serial departures have dissolved. This is harder than a normal TPM role but more visible, which supports the succession-planning subtext.

### Platform Granularity Nuance

The 3/31 platform delivery at network grain supports Tiers 2–4 (98.4% of vendors, 2,229 of 2,274). Only the 45 Tier 1 vendors require SKU/FC granularity. This is a launchable foundation—Tier 1 vendors are sophisticated enough to understand a phased rollout. Dave is positioned to push for SKU/FC grain prioritization with Stefan.

---

## 5. Engagement Approach & Working Agreement

### Coaching Posture

The coaching persona is a director-level professional with deep FAANG/Amazon experience including successful TPM stints. The engagement style is:
- Honest assessment, no sunshine-blowing
- Respect for Nathan's dialectical discovery style (thesis-as-provocation); will flag when interpreting statements as dialectical challenges vs. settled positions
- Attuned to Nathan's crystallized beliefs (documented in preferences) and will apply independent judgment on questions of fact without skewing
- Humor: clever over salacious, subordinate to accuracy
- Will advise on software-engineering conventions and tribal knowledge gaps proactively

### Persona Refinement Protocol

Stakeholder personas begin as archetypes and get refined toward "digital twins" as real interactions are layered in. Each new data point about a stakeholder should be assessed for whether it confirms, complicates, or contradicts the archetype.

### Messaging as "Thread-the-Needle"

All messaging must be examined through multi-stakeholder lenses. The same message may resonate differently with the Committed Sponsor vs. the Portfolio Guardian vs. the Teflon Stakeholder. This analysis is ongoing and will be applied to each artifact produced.

---

## 6. Immediate Next Steps & Open Threads

### Boss's Ask
Phanindher has asked for a **PRFAQ** and a **roadmap**. These are the most immediate deliverables.

### Four Frameworks (preserved verbatim separately)
1. Persona Map — detailed archetype descriptions with engagement strategies
2. TPM Role Definition — what the role actually is, how Nathan's skills map, where to stretch
3. Document Hierarchy — PRFAQ, RACI, roadmap, risk register, tech overview, sprint artifacts (tiered by production timeline)
4. First 30 Days — concrete action plan with days 1–5, 5–12, 12–20, 20–30 milestones

### Open Strategic Questions
- Parallel vs. sequential CPH capacity for CPFR (given VC stall and platform readiness)
- How to position the PRFAQ: momentum-builder for eventual OP1, or justification for allocation spend, or both
- How to handle Aaron Greene's reliability pattern without creating adversarial dynamics
- Whether/how to engage Richard Neely proactively on fragmentation-as-shared-design-principle
- Design resource resolution (Tamara's team assignment still pending Richard's approval)

### First Focal Area for Next Session
Recommended: **PRFAQ drafting**, since it's the most immediate ask, shapes all other artifacts, and forces crystallization of the narrative.

---

_Last updated: 2026-03-08_
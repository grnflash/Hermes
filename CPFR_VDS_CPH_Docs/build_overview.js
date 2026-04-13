'use strict';

/**
 * Build script for CPFR_CPH_Program_Overview.docx
 * Audience: peer program managers and program team leaders
 * Structure: Executive Summary / What / So What / Now What / FAQ
 */

const STYLE_DIR = require('path').resolve(__dirname, '../Chewy Style Template');
const docxPath  = require('path').join(STYLE_DIR, 'node_modules/docx/build/index.cjs');
const { Document, Packer } = require(docxPath);
const fs   = require('fs');
const path = require('path');
const S    = require(require('path').join(STYLE_DIR, 'chewy_docx_style'));

// ─────────────────────────────────────────────
// CONTENT
// ─────────────────────────────────────────────

const children = [

  // ── TITLE ──────────────────────────────────
  S.h1("CPH-in-CPFR: Program Overview"),

  // ── EXECUTIVE SUMMARY ──────────────────────
  S.bodyPara([
    S.bold("Executive Summary. "),
    S.run(
      "The CPH-in-CPFR initiative is Chewy's path to transforming how 3,115 " +
      "(and growing) vendor partners access supply-chain data. Today, a weekly " +
      "email cadence distributes proprietary replenishment data to an enrolled " +
      "vendor base that is projected to reach 4,200 by end of 2026 -- a model " +
      "that does not scale, concentrates data-management liability inside Chewy, " +
      "and leaves us structurally behind Amazon Vendor Central and Walmart Luminate. " +
      "The program's answer is to embed CPFR -- and the parallel Vendor Compliance " +
      "program -- into Chewy Partner Hub (CPH), Chewy's vendor-facing portal, backed " +
      "by a governed daily-refresh Snowflake data platform built by the Supply-Chain " +
      "B.I. Engineering team. After a 2026 delivery did not materialize from the CPH " +
      "team, the program executed an MVP pivot that extracts backend engineering from " +
      "CPH's backlog and distributes it to committed teams: Jeremy Wartnick's " +
      "Replen Engineering team for VC/CB connective apps, and Stefan Scrafield's " +
      "SC-BIE team for CPFR dashboard-layer backend. What remains for CPH is a " +
      "narrow front-end scope, and the program is now fully oriented toward a 2027 " +
      "OP1 submission in June/July 2026. The quantified annual benefit floor is " +
      "$1.4M; the stronger arguments are structural -- liability transfer and " +
      "competitive parity -- and neither diminishes with time."
    ),
  ]),

  // ── SECTION 1: WHAT ────────────────────────
  S.h2("1. What: The CPH-in-CPFR Initiative"),

  S.h3("Program Timeline"),

  S.bullet1("~3 years ago: CPFR formalized at Chewy as a center of excellence within the Instock team; automated weekly reporting to ~1,685 enrolled vendors stood up."),
  S.bullet1("2 years ago to present: Reporting automation matured (Tier 1 fully automated; Tier 4 deprecated); vendor enrollment scaled to 3,115 with active growth toward ~4,200 by EOY 2026."),
  S.bullet1("Feb 2026: CPFR and Vendor Compliance BRDs merged under a shared CPH framework; Nathan Miles (CPFR) and Nathan Nelson (VC) named as joint owners."),
  S.bullet1("2025 OP1 cycle: Submission did not receive funding -- not rejected on merit; timing competed against a higher volume of existing commitments in that cycle."),
  S.bullet1("2026: CPH team committed to allocation-based delivery at multiple checkpoints; delivery did not materialize. MVP reframe redistributes backend engineering to committed teams (see Section 3)."),

  S.h3("The Problem at Scale"),

  S.bodyPara(
    "CPFR's current operating model was designed for hundreds of vendors. " +
    "At 3,115 -- and with line of sight to 4,200 by end of year -- three structural " +
    "problems compound with every new vendor enrolled."
  ),

  S.bullet1(
    "Manual contact management and liability exposure. Chewy TMs are responsible for " +
    "configuring and maintaining the vendor contact lists used to distribute sensitive, " +
    "vendor-specific supply-chain data. Configuration accuracy is a prerequisite for " +
    "data security. The probability and blast radius of misconfiguration grow with scale. " +
    "Inappropriate data releases have already occurred elsewhere in the org -- the CPFR " +
    "team was not responsible, but the structural exposure is identical. There is no " +
    "technical control that fully prevents this at current scale."
  ),
  S.bullet1(
    "No on-demand data access. Reports go out Monday morning. If supply-chain conditions " +
    "change Tuesday, vendors wait until the following Monday for updated data -- or pull " +
    "ISM time for a spot report. At current enrollment, that demand is manageable. " +
    "At 4,200 vendors, it is a sustained capacity drain on a small team."
  ),
  S.bullet1(
    "Competitive disadvantage. Amazon Vendor Central and Walmart Luminate both offer " +
    "daily-refreshed, on-demand data access -- in some respects more robust than what " +
    "this program is requesting. Daily data cadence and portal self-service are the " +
    "most-requested features across the enrolled vendor base, named explicitly by " +
    "Blue Buffalo, Mars, and Nestle-Purina. Every year of inaction is a year Chewy " +
    "lags its largest retail competitors on vendor data experience."
  ),

  S.h3("The CPH Decision"),

  S.bodyPara(
    "CPH -- Chewy Partner Hub -- is Chewy's analog to Amazon Vendor Central: the " +
    "single authenticated entry point for vendor-facing digital tools and information. " +
    "Rather than building a parallel CPFR portal alongside a separate VC portal, " +
    "the program made an early decision to embed both programs into CPH. The rationale " +
    "is threefold: one vendor front door (a standing Sr. Director requirement from " +
    "Richard Neely); shared vendor administration infrastructure (the Self-Service User " +
    "Administration module, SSUA); and reuse of CPH's existing authentication, " +
    "role-based access, and email distribution plumbing."
  ),
  S.bodyPara(
    "The architecture has two distinct layers. The backend -- a governed Snowflake " +
    "semantic layer with daily-refreshed CPFR data, row-level security, and vendor " +
    "isolation -- is owned by Stefan Scrafield's SC-BIE team and is near readiness " +
    "at network grain (covering ~98.4% of enrolled vendors). The frontend -- the " +
    "vendor-facing CPH portal, CPFR data viewer, VC screens, and SSUA -- is the " +
    "remaining dependency and the subject of the MVP pivot described in Section 3."
  ),

  // ── SECTION 2: SO WHAT ─────────────────────
  S.h2("2. So What: The Case for Building This"),

  S.h3("The Entitlement Argument"),

  S.bodyPara(
    "The case rests on three layers. The first two are structural and unquantified; " +
    "the third is quantified and intentionally conservative. The order matters: " +
    "the financial figure is the floor, not the ceiling."
  ),

  S.num1([
    S.bold("Liability transfer. "),
    S.run(
      "The CPH vendor self-administration module (SSUA) shifts contact management " +
      "from Chewy TMs to vendors themselves, aligning data ownership with data " +
      "accountability. This eliminates an entire category of misconfiguration risk " +
      "that currently grows with every new vendor enrolled. Not building this means " +
      "retaining indefinitely a liability that scales with the program."
    ),
  ]),
  S.num1([
    S.bold("Competitive parity and ISM capacity. "),
    S.run(
      "Daily-refreshed, on-demand vendor data access is already standard at Amazon " +
      "Vendor Central and Walmart Luminate. Vendors have named it explicitly as the " +
      "feature they most want from Chewy. The weekly cadence creates ISM spot-reporting " +
      "drag that is already visible and will become acute at 4,200 vendors. The unlock " +
      "may produce modest per-instance value, but factored across thousands of enrolled " +
      "partners and compounded over years, it is material -- and the competitive cost " +
      "of not having it only grows."
    ),
  ]),
  S.num1([
    S.bold("Quantified benefit floor: ~$1.4M per year recurring. "),
    S.run(
      "Three benefit classes are included in the claimed total: Operational Cohesion " +
      "and Efficiency ($608K -- 36 ISMs, 2 hours/week reallocated, fully-burdened), " +
      "Vendor Enablement and Partnership Expansion ($458K -- friction reduction, " +
      "faster vendor decisions), and Enterprise Data Alignment ($339K -- data " +
      "consistency, rework avoidance). A fourth class, Strategic Growth Enablement " +
      "($625K), was deliberately excluded: it depends on pro-rata projections that " +
      "require external validation. Excluding it is a visible statement of " +
      "intellectual discipline that strengthens the credibility of what is claimed."
    ),
  ]),

  S.h3("The Cost of Inaction"),

  S.bullet1(
    "Data liability exposure is not static -- it grows proportionally with vendor " +
    "enrollment. At 4,200 vendors, the blast radius of a single misconfiguration " +
    "event is larger than at 3,115."
  ),
  S.bullet1(
    "ISM spot-reporting capacity drain scales directly with the enrolled vendor base. " +
    "The team is small; the vendor base is not."
  ),
  S.bullet1(
    "The competitive gap relative to AVC and Walmart Luminate widens each year. " +
    "Vendor expectations are set by those platforms, not by Chewy's current model."
  ),
  S.bullet1(
    "OP1 is a once-per-year submission window. Each cycle without a funded submission " +
    "is a year of deferred delivery."
  ),

  // ── SECTION 3: NOW WHAT ────────────────────
  S.h2("3. Now What: The Current Path"),

  S.h3("The MVP Pivot"),

  S.bodyPara(
    "Through 2026, the CPH team signaled willingness to execute under allocation " +
    "(uncommitted capacity) at several checkpoints. Despite those assurances, no " +
    "execution materialized. The program responded by restructuring the MVP to remove " +
    "the backend engineering dependency on CPH entirely."
  ),
  S.bullet1(
    "Jeremy Wartnick's Replen Engineering team has committed to building the backend " +
    "of the VC/CB connective applications."
  ),
  S.bullet1(
    "Stefan Scrafield's SC-BIE team has committed to the CPFR dashboard-layer backend. " +
    "The data platform is on track at network grain and near readiness."
  ),
  S.bullet1(
    "On the CPH side, the ask is now scoped to front-end work only: an iframe page " +
    "for the CPFR data viewer, and two report-retrieval screens for VC, plus " +
    "connectivity and vendor login-to-RLS parsing. This is a materially smaller scope " +
    "than the original design."
  ),
  S.bullet1(
    "In parallel, we are actively influencing the already-approved vendor experience " +
    "OP1 -- specifically the CPH SSUA revisions -- to be built in a way that is " +
    "plug-n-play compatible with the shared CPFR/VC vendor contact repository. " +
    "If it lands as designed, SSUA covers the vendor self-service administration " +
    "piece -- one of the core program goals -- and the residual CPH engineering " +
    "for CPFR becomes minimal. A small amount of additional connection engineering " +
    "remains for VC, but the scope is low relative to the original."
  ),

  S.h3("2027 OP1 Path"),

  S.bullet1(
    "Target: OP1 submission June/July 2026 for 2027 funding."
  ),
  S.bullet1(
    "Narrative rebalanced: the LOE denominator is lower (backend engineering " +
    "distributed to committed teams; CPH ask scoped to front-end only). The " +
    "intangible ROI pillars -- liability transfer and competitive parity -- carry " +
    "more argumentative weight than the quantified floor alone, and do so credibly " +
    "given their structural nature."
  ),
  S.bullet1(
    "PRFAQ in active draft. Roadmap and owner grid in revision. Sr. Director " +
    "review (Dave Livesay) is the next milestone, targeted Q2 2026."
  ),
  S.bullet1(
    "SC-BIE data platform is on track at network grain (~98.4% of enrolled vendors). " +
    "Tier 1 SKU/FC semantic layer is planned as a follow-on phase."
  ),

  S.h3("What This Audience Should Know"),

  S.bodyPara(
    "This document is an orientation, not a request for action. No decisions " +
    "are being asked of this group. The program team is tracking the open items " +
    "and driving the OP1 path. Program team leads who have PM bandwidth and want " +
    "to engage on coordination or alignment are welcome -- reach out to " +
    "Nathan Miles (CPFR program lead)."
  ),

  // ── FAQ ────────────────────────────────────
  S.h2("FAQ"),

  S.h3("On Program Strategy"),

  S.bodyPara([
    S.bold("Why not just use VDS for this? "),
    S.run(
      "VDS (Vendor Data Services) is a premium, session-based product for approximately " +
      "65 of Chewy's most strategic vendors. It carries a cost structure (3% of COGS, " +
      "up to $400K plus $250K) that does not fit the broader vendor base. CPH-in-CPFR " +
      "covers the remaining 3,000+ vendors at no per-vendor cost. The two are " +
      "complementary, not competitive."
    ),
  ]),

  S.bodyPara([
    S.bold("Did we fail OP1? "),
    S.run(
      "The submission was not rejected on merit. It competed in a cycle where the " +
      "volume of existing commitments worked against new initiativess, regardless of " +
      "quality. The PRFAQ was positively received. The 2027 submission is better " +
      "positioned: lower LOE, more committed engineering resources, and a stronger " +
      "intangibles argument."
    ),
  ]),

  S.bodyPara([
    S.bold("Is CPH still the right delivery home after the 2026 decommitment? "),
    S.run(
      "Yes. Sr. Director Richard Neely has a standing requirement for unified vendor " +
      "experience -- separate portals for CPFR and VC are not acceptable from a " +
      "vendor-experience standpoint. The MVP pivot changes who builds the backend, " +
      "not where the front door lives."
    ),
  ]),

  S.h3("On Engineering and LOE"),

  S.bodyPara([
    S.bold("Doesn't this still depend on CPH doing meaningful work? "),
    S.run(
      "Less than before. The backend has been extracted to committed teams. What " +
      "remains for CPH is front-end only: an iframe page for CPFR, two report-retrieval " +
      "screens for VC, plus connectivity and login-to-RLS parsing. The SSUA alignment " +
      "work, if it proceeds as designed, covers the self-service administration piece " +
      "through the vendor experience OP1 already in flight. The residual ask on CPH " +
      "engineers is real but materially smaller than the original scope."
    ),
  ]),

  S.bodyPara([
    S.bold("What if the 2027 OP1 also does not land? "),
    S.run(
      "The committed work from Jeremy's team and Stefan's SC-BIE team can proceed " +
      "regardless. The data platform will be live. The front-end work is the remaining " +
      "gap -- and at current scope, it is small enough that an allocation-path " +
      "conversation becomes more credible, not less."
    ),
  ]),

  S.h3("On Operations and the Current Cadence"),

  S.bodyPara([
    S.bold("When do ISMs see relief from spot-reporting requests? "),
    S.run(
      "Portal launch is the trigger. The 2027 OP1 path targets delivery in 2027. " +
      "Until then, the weekly email cadence continues unchanged and ISMs should " +
      "expect no change to current workflows."
    ),
  ]),

  S.bodyPara([
    S.bold("Will the weekly email system go away? "),
    S.run(
      "Not immediately and not abruptly. The rollout plan calls for email as a " +
      "backup facility during the portal transition, deactivated gradually in favor " +
      "of portal-based delivery. Vendors who cannot or choose not to use the portal " +
      "will have an email feed option available."
    ),
  ]),

  S.bodyPara([
    S.bold("The entitlement doc mentions a 96% vendor approval rating -- what does that mean here? "),
    S.run(
      "That figure reflects vendor satisfaction with the current program, not the " +
      "portal. It is cited as context for what is at stake: vendor trust built over " +
      "years of consistent data sharing. A fragmented or poorly executed portal " +
      "rollout would carry real reputational cost. The program's design priorities " +
      "-- one front door, consistent data, phased rollout with hypercare -- are " +
      "oriented around protecting that trust as the platform transitions."
    ),
  ]),

];

// ─────────────────────────────────────────────
// DOCUMENT ASSEMBLY
// ─────────────────────────────────────────────

const doc = new Document({
  numbering: S.docNumbering(),
  styles:    S.docStyles(),
  sections: [{
    properties: S.docPageProps(),
    headers: { default: S.docHeader("CPH-in-CPFR Program Overview", "April 2026 -- Internal") },
    footers: { default: S.docFooter() },
    children,
  }]
});

Packer.toBuffer(doc).then(buf => {
  const outPath = path.join(__dirname, 'CPFR_CPH_Program_Overview.docx');
  fs.writeFileSync(outPath, buf);
  console.log('Written: ' + outPath);
});

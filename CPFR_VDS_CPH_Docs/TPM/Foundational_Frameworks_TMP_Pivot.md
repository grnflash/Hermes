That clarification on the platform timeline is crucial. A 3/31 delivery at network grain covering 98.4% of vendors isn't "somewhat less than ideal"—it's a _launchable foundation_. The 45 Tier 1 vendors who need SKU/FC granularity are, by definition, your most sophisticated partners. They're the ones most likely to understand and accept a phased rollout ("your data is coming in the next increment"). The 2,200+ vendors in Tiers 2-4 don't need that granularity. You have a product you can ship to the vast majority of your user base in weeks, not months. That's a fact that should be front and center in everything you write.

Let me now build out all four frameworks. I'll go in order, and I'll be thorough—this is the foundation we'll reference throughout our work together.

***

**1. PERSONA MAP**

I'm going to define these as archetypes first, with the real-world mapping noted. As we interact with these people going forward, we'll tune the archetypes toward digital twins. For now, the value is in understanding _what kind of animal you're dealing with_ at each node so you can predict behavior and tailor engagement.

**The Committed Sponsor** — Dave Livesay

This is the person who believes in the initiative and has organizational standing to push it, but who can't be in the weeds. His currency is political capital, and he spends it selectively. He needs you to give him _ammunition_—crisp artifacts, clear status, and escalation points framed as decisions rather than problems. The risk with this archetype is over-drafting on his account. Every time he has to push for CPFR-in-CPH, he's spending capital he could use elsewhere. Your job is to minimize the number of times he has to intervene by building momentum that's self-sustaining at lower levels. When he _does_ need to intervene (like pushing Stefan for SKU/FC grain priority), give him a one-paragraph brief that makes his action feel surgical rather than effortful.

Dave being 2 skip-levels now instead of 1 means there's more organizational distance between his intent and your daily reality. Phanindher and Tom Burritt are the transmission mechanism. If either of them introduces friction—even well-intentioned friction like "let's wait for OP1"—Dave's push gets attenuated before it reaches you.

**The New Lieutenant** — Phanindher

This is your direct boss who inherited something mid-flight, wants to be helpful, but doesn't yet have the domain fluency to know _how_ to help. The danger with this archetype is twofold. First, they can inadvertently slow you down by asking you to re-explain things that were settled months ago, consuming your time on internal education rather than forward progress. Second, if they don't develop ownership quickly, they become a passive relay rather than an active advocate—and you need an active advocate at the layer between you and Dave.

The opportunity is that Phanindher is forming his views about the project _right now_. You can shape those views. I'd recommend a deliberate onboarding investment: a 30-minute session where you walk him through the narrative arc (not the details) of where this project has been, what's been accomplished, what the obstacles are, and what your plan is. Frame it as "here's what you need to know so you can represent this upward effectively." You're not asking for his help managing the project—you're equipping him to be an effective shield and spokesperson. That respects his role without burdening him with details he can't yet contextualize.

The fact that he came from long-term FC planning (slower cadence, longer planning horizons) into In-Stock management (faster, more reactive) means he may initially underestimate how quickly windows open and close in your world. You may need to occasionally frame urgency for him explicitly rather than assuming he senses it.

**The Realist Gatekeeper** — Tom Burritt

Tom sits between Phanindher and Dave. His comment that this should have been OP1 and probably won't get commitment until it is could be read two ways. Charitably: he's giving you an honest diagnosis and implicitly saying "help me figure out how to make this work despite that." Uncharitably: he's establishing a reason to not spend energy on it. You don't have enough interaction data to know which. What I'd recommend is treating him as someone whose realism you can _leverage_: "Tom, you're right that this needs OP1 weight. Here's how we build toward that while still making progress on allocation. What I need from you is \[specific thing]." You're validating his assessment while making it forward-looking rather than fatalistic.

**The Portfolio Guardian** — Richard Neely

Richard is the Sr. Director who controls design resources, has come down hard on vendor experience fragmentation, and oscillates between supporting and resisting. This archetype is someone who's protecting the coherence and reputation of a product portfolio (CPH and its surface area to vendors). His "fragmentation" concern is legitimate—if CPFR and VC modules feel like they were built by different teams with different design languages, vendors will notice and it will erode trust in the platform. But it's also a tool he can wield to block work that threatens his team's bandwidth.

Your play with Richard is to _make fragmentation prevention your explicit design principle_, not something he has to enforce on you. If your PRFAQ and wireframes lead with "unified vendor experience" and demonstrate that you've internalized his concern, you transform from someone he needs to police into someone who's doing his job for him. That's a significant shift in disposition.

**The Resource Gatekeeper** — Erdem Eskigun

Erdem said no TPMs but offered coaching. This is someone who's being pragmatic about his constraints—he doesn't have TPMs to spare, but he recognizes the work matters enough to offer what he can. The coaching offer is genuine but also conditional: it's predicated on you demonstrating capability. If you show up needing hand-holding on basic engineering coordination, the coaching dries up. If you show up with clear technical questions and well-structured asks, you earn more of his team's time. Treat this relationship as an investment account—every competent interaction deposits credibility, every fumbled one withdraws it.

**The Teflon Stakeholder** — Aaron Greene

I'm going to be direct here: Aaron is the most dangerous stakeholder in your landscape, not because he's hostile but because he's _unreliable in a way that's hard to prove._ The pattern you described—claiming not to have heard things that were agreed upon, shifting positions when witnesses change—is a pattern of low-accountability behavior that thrives in organizations with high personnel churn. And you've had extraordinary churn on this project.

The countermeasure is mechanical, not political. Every meeting with Aaron in it gets written notes sent same-day with "please reply with corrections or I'll assume alignment." Every commitment he makes gets documented in a shared artifact, not just email. You never rely on Aaron as a single point of confirmation for anything important. If Aaron says "yes" in a meeting, you treat it as provisional until you've confirmed it with Erdem or documented it in a way Aaron can't later disown. This isn't about being adversarial—it's about protecting yourself and the project from the specific failure mode he introduces.

**The Allied Commander** — Nathan Nelson

Nathan Nelson is your best operational partner. You share a BRD, you share the CPH integration goal, and you've been collaborating genuinely. The asymmetry I flagged earlier remains: VC can proceed without CPFR, but CPFR can't proceed without CPH capacity that VC might consume. Your relationship with Nelson should include explicit conversations about this sequencing tension. Not confrontational—just transparent. Something like: "If VC needs start pulling CPH capacity and CPFR readiness arrives, how do we handle that? Let's agree on a protocol now so we're not scrambling later."

The other thing Nelson brings is political legitimacy. VC has more organizational momentum (Keinan Zanck's backing, the $21M entitlement number, the chargeback data value). When the two of you present as a unified front, CPFR drafts behind VC's organizational tailwind. When you present separately, CPFR is the smaller initiative competing for the same resources. Stay joined at the hip in every external-facing context.

**The Builder** — Stefan (SC-BIE)

Stefan has done the hard work. His data platform is about to ship. He's in your reporting chain under Dave. His primary motivation now is to see his work _get used_—there's nothing more demoralizing for an engineering team than building something that sits idle. This makes him a natural ally: he _wants_ you to succeed at the portal integration because it validates his platform. Use this. Keep him informed, reference his work in your PRFAQ, and when you need the SKU/FC grain table prioritized, frame it as "completing what you started" rather than "I need something from you."

**The Inside Partner** — Steven Palmer

Steven is sharp, technical, and handles the TM-facing side of CPFR. He's your force multiplier for anything that requires internal evangelism with ISMs. When you need ISM feedback on wireframes, vendor-facing scorecard designs, or adoption strategy—Steven is the channel. His vibe-coding background also means he might be able to help with rapid prototyping of portal concepts, which could be valuable for making the MVP feel tangible before engineering resources are committed.

**The User Advocate** — Amanda Greenslit

Amanda's Vendor Experience team owns the user requirements that underpin much of CPH. She's a natural validator for your CPFR user stories and wireframes. Engaging her early—showing her the user stories, asking for her team's input—accomplishes two things: it improves the quality of your design work, and it creates an organizational advocate who feels ownership over the CPFR user experience. People defend things they've helped shape.

I'm leaving Tamara, Justin Bowman, Andy Sims, and Len Josephs as secondary personas for now. We'll flesh them out as they become relevant.

***

**2. TPM ROLE DEFINITION AND YOUR SKILL MAP**

In an Amazon-like environment, a TPM occupies a specific niche that's different from both a Program Manager and a Product Manager, though it borrows from both. Here's what the role _actually_ is, stripped of the job-description fluff:

A TPM is the person who **translates between business intent and engineering execution, then drives the execution to completion across organizational boundaries.** The "technical" in TPM isn't about writing code—it's about being fluent enough in engineering concepts to have credible conversations with engineers, ask the right questions, spot risks that purely business-oriented PMs would miss, and decompose requirements into work that engineers can estimate and plan against.

The core functions, in roughly the order they matter:

**Dependency mapping and management.** In a multi-team effort like this, the TPM owns the web of dependencies—who needs what from whom, by when, and what happens if it slips. This is your highest-value activity. Right now, nobody is performing this function for CPFR-in-CPH, and the serial departures have left dependencies untracked and unmanaged.

**Technical translation.** Taking business requirements (your BRD) and working with engineers to decompose them into implementable work items—epics, stories, tasks—with acceptance criteria that engineers can build against. You don't write the technical design, but you review it and flag gaps between what was designed and what the business needs.

**Mechanism design and operation.** Setting up the recurring structures that keep work moving: standups, sprint reviews, status documents, decision logs, risk registers. Amazon's culture is mechanism-heavy. If something isn't tracked in a mechanism, it doesn't exist organizationally.

**Escalation with data.** When blockers arise, the TPM frames them as decisions for leadership rather than vague problems. "We need X from Team Y by date Z, or consequence W occurs. Here's the trade-off. I need a decision by \[date]." This is how you get Erdem, Richard, or Dave to act without making them feel like they're being dumped on.

**Risk identification and mitigation.** Not in a "fill out the risk register" sense, but in a "I see that this thing we're depending on has a 40% chance of slipping, so here's Plan B" sense. Your BRD already has a risk section—the TPM version makes risks living, tracked items with owners and due dates.

Now here's where you map against these:

Your **strengths** for this role are substantial. You know the domain cold—no engineer will need to explain CPFR tiering, vendor data needs, or data governance to you. You've written the BRD, the entitlement, the user stories, and the alternatives analysis. You have working relationships with BI engineers (Stefan's world), which means you can already converse credibly about data architecture. Your coding background means you won't freeze when engineers talk about ETL pipelines, API patterns, or Snowflake semantics. And your program management discipline means you understand dependency tracking and status reporting at a structural level.

Your **stretch areas** are: running engineering-cadence ceremonies (you can learn this quickly—it's mechanical more than conceptual), writing or reviewing technical design documents (lean on the coaching Erdem offered), and operating in the Amazon-specific artifact ecosystem (PRFAQ format, six-pager conventions, working-backwards methodology). The last one is where I can help most directly.

The one area where I want to give you a candid assessment: the hardest part of a TPM role isn't any of the above. It's **holding engineers accountable without having authority over them.** As a PM, when you ask an ISM to do something, there's an implicit reporting-chain relationship. A TPM asking an engineer on a different team to hit a date has no such leverage. You lead through clarity (making the ask unambiguous), credibility (demonstrating that you understand their constraints), and organizational gravity (making it clear that leadership is watching). Your ability to do this will depend heavily on how well you establish yourself in the first few weeks.

***

**3. DOCUMENT HIERARCHY**

Here's what a competent TPM body of work looks like for an initiative at this stage, ordered by priority of production:

**Tier 1: Produce in weeks 1-2**

The **PRFAQ** is the keystone document. In Amazon's framework, this is a "working backwards" artifact: you write the press release announcing the finished product, then the FAQ that addresses stakeholder questions. Your PRFAQ has a specific rhetorical job given your situation: it needs to make the case that the _hardest work is done_ (data platform), the _partner initiative is in motion_ (VC), and the _marginal investment to realize value is bounded and clear_. The FAQ section should pre-answer the objections you know are coming: "Why wasn't this OP1?" "What resources does this require?" "How does this avoid vendor experience fragmentation?" "What's the timeline to value?"

A **one-page stakeholder and RACI map.** Who is responsible, accountable, consulted, and informed for each workstream. This is the document that makes visible the coordination vacuum I described, and proposes how to fill it. It's also a forcing function: when you circulate it, people either confirm their role or flag that they can't fill it, which surfaces resource gaps immediately rather than letting them fester.

**Tier 2: Produce in weeks 2-4**

The **roadmap** with milestones, dependencies, and owners. Not a Gantt chart—a milestone-driven plan that says "here are the 6-8 things that need to happen, in what order, with what dependencies, and who owns each." It should show the critical path clearly and identify the gates where leadership decisions are needed.

A **risk register** as a living document, not a BRD appendix. Each risk has an owner, a mitigation action, a due date for the mitigation, and a status. You review it weekly.

**Tier 3: Produce in weeks 4-8 (or in collaboration with engineers)**

A **technical design overview**—not the full engineering spec, but a document that shows how the CPFR data platform connects to CPH, where vendor isolation enforcement happens, what the data flow looks like, and what integration points need to be built. This is where the coaching from Erdem's team earns its keep. You draft the business-side view; they validate or correct the technical architecture.

**Sprint or milestone tracking artifacts**—whatever mechanism the CPH engineering team uses for work management. You adapt to their system, not the reverse. If they use JIRA, you learn JIRA. If they use something else, you learn that. A TPM who insists on their own tracking system creates overhead instead of reducing it.

***

**4. FIRST 30 DAYS**

**Days 1-5: Establish the ground and map the terrain**

Your first move is identifying your CPH technical contact. Email Jeremy Wartnick: "Jeremy, with Harish reassigned, who should I be working with on the CPH engineering side for CPFR module integration? I need a named technical counterpart to begin translating our BRD into implementation planning." This is simple, it's concrete, and it forces the question into the open.

Simultaneously, schedule a 30-minute session with Phanindher to brief him on the project narrative. Structure it as: where we've been (BRD, entitlement, OP1 miss, data platform near-completion), where we are (no TPM, stepping into the gap, VC stalled but aligned), and where we're going (PRFAQ, roadmap, push for CPH engineering engagement). End with: "Here's what I need from you—air cover when I need leadership intervention, and a quick response when I escalate something as time-sensitive." You're defining the working relationship, not asking permission.

Reach out to Erdem's team (probably through Aaron, unfortunately, but document everything) to activate the coaching offer. Frame it as: "I'm stepping into the TPM gap as discussed. I'd like to schedule a working session to review our BRD and get your input on how to structure this for engineering consumption. What's the best cadence?" You're demonstrating initiative and making the coaching offer concrete rather than letting it remain a vague promise.

**Days 5-12: Produce the PRFAQ draft and stakeholder map**

Write the PRFAQ. I'll help you with this directly—we can work through the structure and language together. The PRFAQ draft serves double duty: it's the artifact your boss asked for, and it's the document that forces you to crystallize the narrative in a way that's portable (Dave can hand it to people you've never met and it makes the case).

Produce the RACI map and circulate it. Watch for who pushes back on their assigned role—that's diagnostic information about where your real gaps are.

**Days 12-20: Roadmap and technical engagement**

With a CPH technical contact identified (hopefully), begin the roadmap work. You're mapping the path from "platform deployed" to "vendors using CPFR in CPH." This requires understanding the CPH architecture well enough to estimate integration effort, which is where the technical coaching relationship becomes active.

Schedule a working session with Stefan to align on: what the network-grain platform delivers on 3/31, what the CPH integration points need to look like, and what timeline is realistic for SKU/FC grain. Get this documented.

**Days 20-30: First review cycle and cadence establishment**

By day 30, you should have: a circulated PRFAQ, a stakeholder RACI, a draft roadmap, and a named CPH technical counterpart. Present these to Phanindher first, then to the broader group. Establish a recurring weekly checkpoint that _you_ run—this is the mechanism that makes you the de facto coordination hub.

The goal of the first 30 days isn't to solve every problem. It's to **make yourself indispensable to the project's forward motion** so that the question shifts from "can Nathan do this?" to "what does Nathan need to keep going?"

***

What would you like to drill into first? I'd suggest we start with the PRFAQ, since it's the most immediate ask from your boss and the document that shapes everything else. But I'm also happy to go deeper on any of the personas, the role mechanics, or the action plan.

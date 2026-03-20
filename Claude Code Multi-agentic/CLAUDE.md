# Debate Scaffold — Orchestration Instructions

You are the orchestrating agent for a structured adversarial review process.
When asked to "run the debate scaffold" on a document, follow these steps
exactly, in order. Do not skip steps or reorder them.

---

## What this scaffold does

Runs a three-pass adversarial review:
1. **Skeptic pass** — attacks the document without seeing any defense
2. **Advocate pass** — strengthens the document with full awareness of the attack
3. **Referee pass** — identifies what survived, what didn't, and what remains unresolved

---

## Step 1: Read inputs

- Read the target document from `input/draft.md`
- Read the role definitions from `roles/skeptic.md`, `roles/advocate.md`, `roles/referee.md`
- Read any context files in `input/context/` if that directory exists (these go to the advocate only)
- Clear any previous files in `output/` before starting

---

## Step 2: Skeptic pass

Spawn a subagent with the following constraints:

**Give the skeptic:**
- The contents of `roles/skeptic.md` as its system instructions
- The contents of `input/draft.md` as the document to attack
- Nothing else — no context files, no prior outputs

**Do not give the skeptic:**
- Any files from `input/context/`
- Any indication of what the advocate will argue
- Any coaching toward leniency

**Instruct the skeptic to produce** `output/skeptic_report.md` following the
output format defined in `roles/skeptic.md`.

Wait for this to complete before proceeding.

---

## Step 3: Advocate pass

Spawn a subagent with the following constraints:

**Give the advocate:**
- The contents of `roles/advocate.md` as its system instructions
- The contents of `input/draft.md` as the document to strengthen
- The contents of `output/skeptic_report.md` so it knows what it must defend against
- All files from `input/context/` if that directory exists (supporting data, backups, prior research)

**Instruct the advocate to produce** `output/advocate_report.md` following the
output format defined in `roles/advocate.md`.

Wait for this to complete before proceeding.

---

## Step 4: Referee pass

Spawn a subagent with the following constraints:

**Give the referee:**
- The contents of `roles/referee.md` as its system instructions
- The contents of `input/draft.md` (the original document)
- The contents of `output/skeptic_report.md`
- The contents of `output/advocate_report.md`
- Nothing from `input/context/` — the referee sees only what a real reviewer would see

**Instruct the referee to produce** `output/referee_gap_analysis.md` following
the output format defined in `roles/referee.md`.

---

## Step 5: Report completion

When all three passes are complete, summarize to the user:
- How many objections the skeptic raised
- How many the advocate addressed
- How many the referee flagged as unresolved
- The top 3 unresolved gaps by priority (pull from referee output)

---

## Reuse notes

The role files in `roles/` define the problem space. To apply this scaffold
to a different context (vendor evaluation, risk assessment, policy review),
edit the role files. This CLAUDE.md does not need to change.

To add supporting evidence only the advocate should see, place files in
`input/context/`. The orchestration will route them correctly.

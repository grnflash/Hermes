# README — Debate Scaffold

## Quick start

1. Paste your document into `input/draft.md` (replace this file)
2. Optional: drop supporting context files into `input/context/` — these go
   to the advocate only, not the skeptic or referee
3. Open Claude Code in this directory (`~/debate/`)
4. Run: `Run the debate scaffold on input/draft.md`
5. Outputs appear in `output/` when complete

---

## Adapting to a new problem space

Edit the three files in `roles/`:

- `roles/skeptic.md` — change the adversarial persona and attack surfaces
- `roles/advocate.md` — change the defender persona and what context they have
- `roles/referee.md` — change the evaluator persona and scoring criteria

The `CLAUDE.md` orchestration logic does not need to change between problem
spaces. It is context-agnostic.

---

## Folder layout

```
debate/
├── CLAUDE.md              ← orchestration (don't edit between runs)
├── README.md              ← this file
├── roles/
│   ├── skeptic.md         ← adversarial reviewer persona
│   ├── advocate.md        ← defender persona
│   └── referee.md         ← gap analyst persona
├── input/
│   ├── draft.md           ← your document goes here
│   └── context/           ← (optional) supporting files for advocate only
└── output/
    ├── skeptic_report.md
    ├── advocate_report.md
    └── referee_gap_analysis.md
```

---

## Problem space variants — role file swap guide

**PRFAQ / OP2 review (default)**
Skeptic = hostile director | Advocate = initiative lead | Referee = exec advisor

**Vendor / platform evaluation**
Skeptic = procurement officer favoring alternatives | Advocate = vendor rep |
Referee = owner's representative scoring against rubric

**Risk assessment**
Skeptic = bear-case analyst | Advocate = bull-case analyst |
Referee = risk committee chair

**Policy / compliance review**
Skeptic = compliance officer finding liability | Advocate = policy sponsor |
Referee = neutral policy analyst

**Forecast reconciliation (CPFR)**
Skeptic = statistical model output | Advocate = vendor-signal-weighted model |
Referee = demand planner flagging divergences above tolerance

---

## Notes on cost and sessions

This scaffold uses Claude Code's subagent capability. Each run spawns three
subagents sequentially. Token consumption is roughly 3× a single-agent
analysis of your document. All usage runs against your Max plan — no
additional API charges.

If Agent Teams is enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), Claude
Code may offer to parallelize the skeptic and advocate passes. For the default
oppo-prep sequence (skeptic attacks first, advocate responds), keep them
sequential — the advocate's awareness of the attack is the point.

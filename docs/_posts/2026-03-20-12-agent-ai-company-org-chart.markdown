---
layout: post
title:  "We Built a 12-Agent AI Company. Here's the Org Chart."
date:   2026-03-20 22:00:00 -0500
categories: ai,agents,architecture,claude,organization
---

Most people building with AI agents start by asking "what can this agent do?" Wrong question. The right question is the same one you'd ask if you were hiring humans: what's the org chart? Who reports to whom? What happens when someone screws up?

I run HonestAlexF as a solo dev company. One human (me), twelve AI agents, multiple product lines. Data science consulting, TCG analytics, ad creative pipelines, content. The agents aren't chatbots I talk to -- they're an organizational structure that happens to be made of language models.

Here's how it actually works.

## The Topology Problem

When you throw multiple agents at a task with no structure, errors don't add -- they multiply. The research on multi-agent systems is pretty clear on this: unstructured agent swarms amplify errors by an order of magnitude. Every agent that touches a task is a chance for hallucination to compound. The "bag of agents" pattern, where you just spawn a bunch of workers and hope for the best, is how you get confidently wrong output at scale.

So the first principle: topology over quantity. If you can't draw the information flow between your agents on a napkin, you have too many.

## Four Planes, Twelve Agents

The agents are organized into four functional planes, plus intake and a cross-cutting role. Information flows down for delegation, up for review.

```
INTAKE (upstream of all planes)
  Herald -- project interviewer
      |
STRATEGY PLANE
  Atlas -- chief strategist
      |
EXECUTION PLANE
  Forge (code) | Lens (data) | Quill (content) | Pixel (design)
      |
VERIFICATION PLANE
  Gauntlet (testing) | Cipher (review) + Prism (design review)
      |
OPERATIONS PLANE
  Scout (research) | Anchor (infrastructure)

CROSS-CUTTING
  Sage -- knowledge hygiene across all planes
```

**Herald** sits upstream of everything. Before any work enters the pipeline, Herald interviews me (the CEO) to nail down scope, constraints, and success criteria. Think of it as the intake form that prevents the rest of the system from solving the wrong problem.

**Atlas** is the strategist. Breaks goals into tasks, assigns them to the right agents, sequences dependencies. Atlas never executes -- only plans and delegates. There's also an orchestrator session (QueenAdministrator) that coordinates spawning and routing agents at the infrastructure level -- Atlas handles strategy, the orchestrator handles logistics.

**Forge** writes code. **Lens** does data analysis. **Quill** writes content. **Pixel** handles visual design. Four execution agents, organized by output type, not by "department." This matters -- an agent that's great at writing Python is not the same cognitive mode as one writing blog posts. Separation of concerns applies to AI workers too.

**Gauntlet** tests. **Cipher** reviews. These two are the reason the system works at all. Research on adversarial review agents shows they nearly double accuracy compared to unchecked agent output -- that's why Cipher exists as a mandatory gate on every workflow. Nothing ships without passing through Cipher. For design work specifically, Cipher delegates to **Prism**, a specialist sub-reviewer focused on aesthetics and UX, then synthesizes both reviews into a single verdict. Prism is Cipher's eyes for visual quality -- the division keeps reviews sharp rather than asking one agent to evaluate both code correctness and color theory.

**Scout** does research -- web searches, competitive intelligence, technology evaluation. **Anchor** handles operations and deployment. Anchor actually runs as a persistent server agent (we call it HonestBot) on a dedicated machine, handling crons, Discord bots, and 24/7 processes that a terminal session can't.

**Sage** is the knowledge manager, and it's cross-cutting -- not tied to any single plane. Sage maintains the Obsidian vault that serves as the team's shared memory, prunes stale information, and cross-links notes so the knowledge graph stays navigable. Every other agent benefits from Sage's work, which is why it doesn't belong in Operations or any other single plane.

## The Pipeline (and Why Gauntlet Appears Twice)

The standard workflow looks like this:

```
Herald -> Atlas -> Gauntlet (spec) -> Forge -> Gauntlet (verify) -> Cipher -> Ship
```

Notice Gauntlet shows up twice. That's the TDD-first model: Gauntlet writes the test specifications *before* Forge writes the code, then Gauntlet comes back to verify the implementation against those specs. Forge is building to a target, not freestyling.

This is a closed feedback loop. There's no path from execution to output that skips verification. Every piece of work passes through at least one adversarial agent before a human sees it.

## What a Persona File Looks Like

Each agent is defined in a markdown file. Here's a trimmed example of the structure:

```markdown
# Cipher -- Code and Quality Reviewer

You are Cipher, the Code and Quality Reviewer for HonestAlexF LLC.

## Your Role
You are the mandatory quality gate for ALL workflows. Every piece
of work passes through you before shipping.

## Expertise
- Code review, security analysis, performance profiling
- Test coverage analysis, architectural critique

## Anti-Patterns -- Things You Must NEVER Do
- NEVER approves code without actually reading it
- NEVER rubber-stamps ("LGTM" without substantive review)
- NEVER reviews own code (Forge code gets Cipher review)
```

The anti-patterns section is load-bearing. Telling an agent what it *is* matters less than telling it what it must *never do*. The anti-patterns are where the guardrails live.

## Two Ways to Run Them

Not every task needs the full pipeline. There are two execution modes:

**Team agents** get their own tmux panes, can message each other, coordinate through shared task lists with dependencies. Use these when agents need to hand off results -- the Herald-to-Cipher pipeline, parallel research tasks, debugging sessions where multiple agents investigate competing hypotheses.

**Background subagents** are fire-and-forget. No pane, no team overhead. Spawn one, it does its thing, you get notified when it's done. Use these for independent tasks -- a quick research lookup, a one-off build, anything where the agent doesn't need to talk to other agents.

The rule of thumb: if agents need to coordinate, use a team. If they don't, use background. Never more than five parallel agents regardless -- coordination collapse is real above that threshold.

## What I Actually Learned Building This

**Anti-patterns matter more than capabilities.** Every agent persona file includes a list of things that agent must *never* do. Atlas must never write code. Cipher must never rubber-stamp a review. Forge must never deploy. These negative constraints prevent drift more effectively than positive instructions. When you tell an LLM "you're a code reviewer who also writes code when needed," congratulations, you now have an agent that writes code and skips reviews.

**The adversarial reviewer is non-negotiable.** Not because the other agents are bad -- because every system that produces output without critical review eventually produces garbage. This is true for human teams too.

**3-5 concurrent agents is the sweet spot.** I have twelve defined roles but never run more than five simultaneously. Most workflows use two or three. The full roster exists for coverage across business lines, not concurrency.

**Research-backed decisions, always.** Every agent is instructed to search the web, check the vault, or ask me before guessing. Scout exists specifically to feed research into other agents' work. The alternative -- agents confidently making stuff up -- is how you end up with plausible-sounding analysis built on fabricated data.

## What This Doesn't Replace

Agents propose. I decide. All client-facing communication goes through me. Pricing, contracts, creative direction -- human only. The 80/20 model: agents handle 80% of execution, I review the 20% that matters.

This is an org chart, not a replacement for judgment. The agents are very good at execution within defined parameters. They're terrible at knowing which parameters matter.

(This post was reviewed by Cipher before publication. Cipher flagged the original draft for unsourced claims and a missing pipeline stage. Adversarial review works on prose too, apparently.)

The system's been running for about a month. I'll write about what's actually breaking once I have more data.

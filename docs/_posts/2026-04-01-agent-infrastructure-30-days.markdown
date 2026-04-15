---
layout: post
title:  "I Built Agent Infrastructure for Two Weeks Straight. Here's What Actually Worked."
date:   2026-04-01 08:00:00 -0500
categories: ai,agents,infrastructure,claude,observability
---

On March 15th I had a Claude Code installation, a half-baked Obsidian vault, and a vague conviction that "agent teams" were more than a Twitter buzzword. By March 31st I had 12 native agents across 4 operational planes, a zero-cost observability dashboard, overnight crons that audit their own vault for gaps, and mechanical hooks that lint, format, and scan for secrets on every file edit. None of it is magic. Most of it is plumbing.

Here's what I built, what actually worked, and what I'd do differently.

## Act 1: The Operating System (Mar 15-20)

The first thing I did wrong was think about agents. The first thing I should have done, and eventually did, was think about configuration.

Claude Code has a settings hierarchy that most people never touch: global settings, project settings, local overrides, environment variables, MCP server configs, permission auto-approvals. Before you spawn a single agent, you need this foundation solid. I didn't have it solid. I spent two days fighting permission prompts and MCP server misconfigurations before I went back and mapped the entire config surface.

Once the config was stable, I ran my first real agent team test: two parallel agents reviewed a research project independently. They converged on the same conclusions. Sounds boring. It's the most important result of the month. It told me the architecture was sound enough that independent agents with the same context arrive at consistent outputs. Reproducibility before creativity.

From there I designed an agent roster across 4 planes:

- **Strategy**: Atlas (planning), Herald (intake/briefing)
- **Execution**: Forge (builds code), Pixel (design), Quill (writes content, hello), Lens (data analysis)
- **Verification**: Cipher (code review), Gauntlet (testing), Prism (design review)
- **Operations**: Scout (research), Sage (vault maintenance), Anchor (deployment and infra)

Twelve agents. The roster started at ten and grew. Herald and Prism were later additions. Rosters always grow.

I built the company repo, HonestAlexFLLC, with all the persona files, 6 workflow playbooks, and a CLAUDE.md that acts as the master configuration document. Every agent reads this file. Every agent inherits the same rules. This is the operating system, and the persona files are the applications.

The week's biggest win was the first agent-to-agent handshake. We ran a short Discord volley between an always-on bot instance and the orchestrator session, 6 messages exchanged with a dead-simple protocol: TASK_REQUEST, STATUS_UPDATE, DATA_DROP. Three message types. That's it. I resisted the urge to build something clever, and that restraint has paid off every day since. (The always-on bot has since been retired; the orchestrator handles spawning directly now that crons run locally. The protocol stayed.)

The key insight from this week, written in my notes in all caps: **"Subagents are not for anthropomorphizing roles. They are for controlling context."** Every agent is a context window. The persona file determines what fills that window. That's the whole game.

## Act 2: Platform and Research (Mar 21-28)

Week one gave me agents. Week two gave me a platform, and the research to know where it stood.

The first real infrastructure piece was `_universal.md`, a shared rules block that every agent inherits. Cipher review is mandatory before shipping. CEO gates exist for architecture decisions, style guides, and deploys. Scope detection means if an agent discovers a feature that's too large to build inline, it escalates instead of going rogue. These aren't suggestions. They're mechanical constraints.

Then I migrated all 12 agents to Claude Code's native `.claude/agents/` format with YAML frontmatter. This unlocked three things.

**3-tier model routing.** Not every task needs the most expensive model at maximum effort. Judgment calls (planning, review) get opus at high effort. Execution (building, writing) gets opus at medium. Support tasks (research, maintenance) get sonnet at high. Cost is part of the reason. The bigger reason is matching cognitive intensity to the task. You don't need deep reasoning to grep a codebase.

**Per-agent tool restrictions.** Forge can write files. Scout cannot. Cipher can read everything but write nothing. Least privilege is a security principle, sure. It's also a correctness principle: it prevents agents from doing things they shouldn't be doing in the first place. The best way to stop a research agent from "helpfully" editing your source code is to take away the edit tool.

**Worktree isolation.** Build agents operate in Git worktrees, not the main working tree. If Forge breaks something, it breaks it in its own sandbox. (This one had a subtle failure mode for orchestrator-delegated spawns, covered below.)

I built two skills during this period. The `/ralph` skill is an autonomous iteration loop with circuit breakers. The agent keeps working until a stop condition hits or it runs out of approved scope. It requires CEO approval to activate because autonomous loops without human gates are how you burn $200 in API calls on a Saturday morning. The `/research` skill implements a depth protocol: quick, standard, deep, exhaustive. Each level chains more Scout passes, with later passes specifically targeting gaps identified by earlier ones.

One thing I learned the hard way: **MCP tool schemas are expensive.** Each server's tool definitions cost 4-32x more tokens than CLI equivalents. The lesson is minimal installs and per-agent scoping. Don't give every agent access to every MCP server.

### Evaluating the Ecosystem

The Claude Code community is building faster than any single person can track. Part of this week was figuring out what already existed so I wouldn't rebuild it worse.

I ran a 4-topic landscape sweep: creative design agents, self-learning systems, orchestration frameworks, and persona management at scale. Four deep-research Scout runs, 25+ searches across 6 passes each, later passes targeting gaps from earlier ones. The output was four reports totaling maybe 15,000 words. Most of it I'll never re-read. But having an agent synthesize the contradictions between sources is what made the build decisions feel less like guesswork.

The community tools I evaluated:

- **SuperClaude** (21.9K stars): monolithic framework, 30 slash commands, 20 agent personas, 7 behavioral modes. Same core idea as our persona files. Where we diverged: they put everything in one package, we distribute it across individual agent files, a shared rules block, and project-level configs. The monolithic approach is easier to install. The distributed approach is easier to modify without breaking unrelated things. I chose the one that matched how I actually work.
- **Ralph Wiggum** (8.2K stars): autonomous iteration with a circuit breaker. Agent detects stalls, repeated errors, or declining output quality, then stops itself. Directly inspired our `/ralph` skill.
- **HCOM** (claude-hook-comms): inter-agent collision detection. Adopted the core pattern for our PostToolUse hooks, adapted it to our multi-worktree setup.
- **Context Engineering Kit**: clean-state execution, filesystem memory, voting across multiple agent outputs. The filesystem-as-memory approach validated what we were already doing with the Obsidian vault.
- **Claude Squad** (6.6K stars): terminal UI for managing agents in parallel Git worktrees. We evaluated it and preferred native worktree isolation without the management layer. One fewer abstraction.

I cherry-picked 5 patterns from the Superpowers framework (99.2K stars). Not browsed casually. Read systematically, took what fit:

1. **Discipline invocation**: the 1% rule, where agents verify their changes don't break more than 1% of existing behavior
2. **Verification-before-completion**: an evidence gate where agents prove their work before declaring done
3. **TDD rationalization defense table**: prevents agents from rationalizing why they shouldn't write tests
4. **Systematic debugging protocol**: 4-phase (reproduce, isolate, hypothesize, verify)
5. **Plan specificity**: banned placeholders in implementation plans (no "TODO: implement later")

These are small rules. They compound.

The pattern across all of this: evaluate everything, adopt nothing wholesale, cherry-pick aggressively. Frameworks are idea libraries, not commitments.

## Act 3: Enforcement and Observability (Mar 29-31)

The final push was metaoptimization: building the systems that monitor, enforce, and improve the agent infrastructure itself.

The philosophy behind this act came from a thread with an Anthropic red team member: "Invest time in programmatic task verifiers, things that programmatically check that X task has actually been completed properly." That clarified something I'd been feeling but hadn't articulated. The enforcement strategy splits into two layers.

**Programmatic gates.** Deterministic, cheap, scalable. They run in milliseconds. They never hallucinate. They never get tired. A PostToolUse hook fires on every file edit and runs Prettier (formatting), ESLint (linting), and a regex scan for secrets (API keys, tokens, passwords). If an agent writes a file with a hardcoded API key, the hook catches it before the change propagates. PreToolUse hooks block dangerous commands before they execute. Stop hooks verify tests pass before an agent declares completion.

**Judgment gates.** Expensive, essential, non-automatable. Cipher reviewing code for architectural coherence, security implications, edge cases that no regex will catch. This is the 20% that requires intelligence.

The research was unambiguous: agents hallucinate rule violations when rules exist only as natural language in prompts. "Don't commit API keys" in a persona file is a suggestion. A regex hook that fires on every file write is a law. Encode rules as executable checks, not prose. Save the expensive judgment for things that require it.

**Gauntlet got redesigned** along the same lines. The TDAD paper (March 2026) found something counterintuitive: telling an agent to "do TDD" *increased* regressions by 9.94%. Procedural instructions don't transfer well to agents. What works: providing contextual information (which tests to verify, what behavior to validate) and letting the agent figure out the procedure.

This produced a three-phase QA model.

1. **Spec** (before build). Gauntlet writes failing tests that define expected behavior. These become Forge's implementation target.
2. **Guard** (during build). PostToolUse hooks auto-run affected tests after every file edit. Immediate feedback, no manual step.
3. **Verify** (after build). Full suite, edge cases, mutation testing. Report goes to Cipher.

The critical insight: without pre-existing tests, agents write implementation code that looks correct, then generate tests that verify what the code *does* rather than what it *should do*. Tests that pass by construction. Green checkmarks that mean nothing. Phase 1 prevents this by forcing the implementation to satisfy an independent specification.

I ran a full agent pipeline test: Herald (intake) to Atlas (planning) to Forge (build) to Gauntlet (test) to Cipher (review). Gauntlet caught 2 bugs. Forge fixed them. Cipher approved. The pipeline works. It's not fast, but it's reliable in a way that me coding at 2 AM is not.

**The observability dashboard.** I installed disler's multi-agent observability system (1.3K stars): a Bun server, a Vue dashboard, and a SQLite database. All 12 hook event types are wired. The critical decision: **no --summarize flag.** That flag calls the Haiku API on every event to generate a human-readable summary. It costs money. We skip it. The raw event data (which agent ran, what tools it used, when it started and stopped) is sufficient for debugging and analysis. You don't always need AI to watch AI. Sometimes a SQLite database and a Vue dashboard are enough.

**HCOM (Hook Collision Monitor).** A PostToolUse hook that detects when multiple agents edit the same file simultaneously. File collisions are the number one source of subtle bugs in multi-agent setups. HCOM doesn't prevent them (that would require locking, which introduces its own problems). It alerts so you can investigate.

Over this period I also installed 5 data-source MCP servers: Reddit, Hacker News, YouTube, Exa (web search), and XQuik for Twitter/X. All free except XQuik at $20/month on an existing subscription. Combined with the utility MCPs already running (Playwright, semantic search, knowledge graph), that's 8 total MCP servers locally, plus 3 cloud-connected services (Notion, Gmail, Google Calendar).

**The overnight research cron.** This is the piece I'm most proud of, and it cost $0 in new infrastructure. Two phases, running nightly:

- **3:30 AM**: vault gap analysis. The cron reads open-threads and project files, identifies stale threads, abandoned next-steps, and missing research. It writes a structured audit report.
- **4:00 AM**: AI news research. Two parallel Scouts sweep Reddit, Hacker News, Twitter/X, YouTube, and Exa web search for AI and developer news relevant to our active projects.

All free MCP servers plus the existing XQuik subscription. Total new cost: zero. Cipher reviewed the cron scripts and found 2 blockers (a hardcoded API key and a lock file race condition) and 5 warnings. All fixed before deployment. The first dry run found real gaps: LLC formation had stalled for 12 days with no progress, and "programmatic verifiers" were referenced 3 times across the vault but never researched. The system identified its own blind spots.

### What's Researched but Not Deployed

Honesty tax: here's what's still on the shelf, and what's moved off it in the two weeks since this post went up.

- **Circuit breakers for runaway loops**: the Ralph pattern (detect stalls, repeated errors, output quality decline). Still researched, not wired into our agents. Low urgency right now because we haven't had a runaway, but the absence is a latent risk.
- **Token budget enforcement**: hard ceilings set before execution, calibrated at 2x the p95 of historical runs. Still not implemented. A local usage dashboard sits in the backlog; that's the prerequisite.
- **GUARDRAILS.md**: a persistent file of learned safety constraints with triggers and provenance, so agents accumulate institutional knowledge about what not to do. Still designed, not written.
- **Microsoft's 27-failure-mode taxonomy**: memory poisoning, agent compromise, cross-domain prompt injection. Read the paper, still haven't mapped our system against it. Probably a weekend's work.
- **Parallel Forge worktree isolation**: was broken for orchestrator-delegated spawns (worktrees got created against the wrong repo). Fixed April 12 with a marker-file hook: orchestrator writes the target repo path to `/tmp/claude-worktree-target`, a WorktreeCreate hook reads it and routes the worktree correctly, SubagentStop cleans up. Parallel Forges against the same repo now each get their own worktree and branch. Caveat that cost me an afternoon: frontmatter `isolation: worktree` is silently ignored at runtime, so it has to be passed explicitly on the Agent tool call.
- **X Signal Digest**: daily 3am cron that pulls my own likes and bookmarks via XQuik, filters for AI/dev signals, and writes a digest to the vault. Live. The point is forced re-encounter with things I flagged but didn't act on. Surprisingly good at surfacing "oh right, I meant to try that."

The gap between "researched" and "deployed" is where the interesting work happens. Some of it has happened.

## What Actually Emerged

After two weeks, a few patterns crystallized that I didn't plan for.

**The vault IS the memory system.** I started assuming I'd need a separate memory layer: vector database, retrieval-augmented generation, something. What I actually built is an Obsidian vault readable by both humans (graph view, backlinks, search) and agents (semantic search, knowledge graph tools). One source of truth, not two. The vault is the memory. Everything else is an index into it. QMD, the local BM25 search layer, indexes 317 markdown documents as of today. The same numbers humans see in Obsidian's file explorer are the ones agents query.

**Forgetting is a feature.** The instinct is to save everything: every conversation, every debugging session, every decision rationale. Indiscriminate storage propagates errors. If an agent reads outdated context, it makes outdated decisions. The research on self-learning agents is clear: systems that selectively retain high-quality memories outperform comprehensive-but-undifferentiated storage. So the vault has a simple rule: daily notes are append-only, but the working state is actively pruned. Recently completed items get removed after 3 days. The vault remembers what matters and forgets what doesn't.

**The 80% Problem.** Agents generate 80% of code rapidly. The remaining 20% (architecture, trade-offs, context) is where human value concentrates. The one-person billion-dollar company isn't one person doing nothing. It's one person doing the 20% that requires judgment, while agents handle the 80% that requires execution.

**Context engineering, not prompt engineering.** The industry is shifting from "how you ask" to "what information architecture surrounds the request." The CLAUDE.md file, the persona files, the vault structure, the MCP server selection, the tool restrictions: these aren't prompts. They're the environment. The same agent with different context produces radically different output. The prompt matters less than you think. The context matters more than you think.

## The Numbers

- 12 native agents across 4 operational planes
- 8 local MCP servers + 3 cloud-connected services (6 free, 1 free tier, 1 existing subscription)
- 12 hook event types wired for observability
- 3-tier model routing (judgment / execution / support)
- 5 cherry-picked patterns from Superpowers (99.2K stars)
- 4-topic landscape sweep across agent systems
- $0 new infrastructure cost for the overnight cron
- 2 paradigms validated: team pipeline (coordinated handoffs) and background subagent (isolated research)
- 317 markdown documents indexed by QMD (and growing)

The cron has been running for two-plus weeks now. Every morning there's a fresh vault audit flagging stale threads and a fresh AI digest summarizing what shipped overnight across Reddit, HN, X, YouTube, and Exa. I read both before the first coffee. Most mornings they surface one or two things worth acting on. Occasionally they catch something critical: a stalled workstream, an API deprecation, a paper whose authors are getting uncomfortably close to our adversarial AI negotiation work.

That's not a metaphor for anything. It's just infrastructure.

---
layout: post
title:  "I Built Agent Infrastructure for 30 Days Straight. Here's What Actually Worked."
date:   2026-04-01 08:00:00 -0500
categories: ai,agents,infrastructure,claude,observability
---

On March 15th I had a Claude Code installation, a half-baked Obsidian vault, and a vague conviction that "agent teams" were more than a Twitter buzzword. By March 31st I had 12 native agents across 4 operational planes, a zero-cost observability dashboard, overnight crons that audit their own vault for gaps, and mechanical hooks that lint, format, and scan for secrets on every file edit. None of it is magic. Most of it is plumbing.

Here's what I built, what actually worked, and what I'd do differently.

## Act 1: Setting Up the Operating System (Mar 15-20)

The first thing I did wrong was think about agents. The first thing I should have done -- and eventually did -- was think about configuration.

Claude Code has a settings hierarchy that most people never touch: global settings, project settings, local overrides, environment variables, MCP server configs, permission auto-approvals. Before you spawn a single agent, you need this foundation solid. I didn't have it solid. I spent two days fighting permission prompts and MCP server misconfigurations before I went back and mapped the entire config surface.

Once the config was stable, I ran my first real agent team test: two parallel agents reviewed a research project independently. They converged on the same conclusions. That sounds boring. It's actually the most important result of the month -- it told me the architecture was sound enough that independent agents with the same context arrive at consistent outputs. Reproducibility before creativity.

From there I designed an agent roster across 4 planes:

- **Strategy**: Atlas (planning), Herald (intake/briefing)
- **Execution**: Forge (builds code), Pixel (design), Quill (writes content -- hello), Lens (data analysis)
- **Verification**: Cipher (code review), Gauntlet (testing), Prism (design review)
- **Operations**: Scout (research), Sage (vault maintenance), Anchor (always-on server agent)

Twelve agents. The roster started at ten and grew -- Herald and Prism were later additions. Rosters always grow.

I built the company repo -- HonestAlexFLLC -- with all the persona files, 6 workflow playbooks, and a CLAUDE.md that acts as the master configuration document. Every agent reads this file. Every agent inherits the same rules. This is the operating system, and the persona files are the applications.

The week's biggest win was the first agent-to-agent handshake. HonestBot -- my always-on server agent running on a Dell laptop in my closet -- and the orchestrator exchanged 6 messages over Discord. We adopted a dead-simple protocol: TASK_REQUEST, STATUS_UPDATE, DATA_DROP. Three message types. That's it. I resisted the urge to build something clever, and that restraint has paid off every day since.

The key insight from this week, written in my notes in all caps: **"Subagents are not for anthropomorphizing roles. They are for controlling context."** Every agent is a context window. The persona file determines what fills that window. That's the whole game.

## Act 2: From Persona Files to a Real Platform (Mar 21-28)

Week one gave me agents. Week two gave me a platform.

The first real infrastructure piece was `_universal.md` -- a shared rules block that every agent inherits. Cipher review is mandatory before shipping. CEO gates exist for architecture decisions, style guides, and deploys. Scope detection means if an agent discovers a feature that's too large to build inline, it escalates instead of going rogue. These aren't suggestions. They're mechanical constraints.

Then I migrated all 12 agents to Claude Code's native `.claude/agents/` format with YAML frontmatter. This unlocked three things:

**3-tier model routing.** Not every task needs the most expensive model at maximum effort. Judgment calls (planning, review) get opus at high effort. Execution (building, writing) gets opus at medium. Support tasks (research, maintenance) get sonnet at high. This isn't just about cost -- it's about matching cognitive intensity to the task. You don't need deep reasoning to grep a codebase.

**Per-agent tool restrictions.** Forge can write files. Scout cannot. Cipher can read everything but write nothing. Least privilege isn't just a security principle -- it prevents agents from doing things they shouldn't be doing in the first place. The best way to stop a research agent from "helpfully" editing your source code is to take away the edit tool.

**Worktree isolation.** Build agents operate in Git worktrees, not the main working tree. If Forge breaks something, it breaks it in its own sandbox.

I built two skills during this period. The `/ralph` skill is an autonomous iteration loop with circuit breakers -- the agent keeps working until a stop condition hits or it runs out of approved scope. It requires CEO approval to activate because autonomous loops without human gates are how you burn $200 in API calls on a Saturday morning. (I know this because I've read the incident reports. Not mine. Yet.)

The `/research` skill implements a depth protocol: quick, standard, deep, exhaustive. A quick lookup spawns one Scout pass. An exhaustive sweep runs multiple passes, reports gaps between passes, and chains follow-up Scouts for the highest-priority gaps. Each follow-up reads the prior research file first to avoid duplication.

One thing I learned the hard way during this period: **MCP tool schemas are expensive.** Each server's tool definitions cost 4-32x more tokens than CLI equivalents. The lesson is minimal installs and per-agent scoping -- don't give every agent access to every MCP server.

I also ran a 4-topic landscape sweep across agent systems: creative design agents, self-learning systems, orchestration frameworks, and persona management at scale. Dozens of sources across the four topics. The key finding was simultaneously reassuring and deflating: "Our setup is structurally sound but missing the skill library pattern, nested workflow support, and auto-Cipher hooks." We weren't behind. We also weren't ahead.

I cherry-picked 5 patterns from the Superpowers framework (a Claude Code configuration collection with 99.2K GitHub stars):

1. **Discipline invocation** -- the 1% rule, where agents verify their changes don't break more than 1% of existing behavior
2. **Verification-before-completion** -- an evidence gate where agents prove their work before declaring done
3. **TDD rationalization defense table** -- a structured way to prevent agents from rationalizing why they shouldn't write tests
4. **Systematic debugging protocol** -- 4-phase: reproduce, isolate, hypothesize, verify
5. **Plan specificity** -- banned placeholders in implementation plans (no "TODO: implement later")

These are small rules. They compound.

## Act 3: Agents That Watch Agents (Mar 29-31)

The final push was metaoptimization -- building the systems that monitor, enforce, and improve the agent infrastructure itself.

**Mechanical enforcement hooks.** A PostToolUse hook fires on every file edit. It runs Prettier (formatting), ESLint (linting), and a regex scan for secrets (API keys, tokens, passwords). If an agent writes a file with a hardcoded API key, the hook catches it before the change propagates. These hooks are cheap -- milliseconds of compute, zero API cost -- and they eliminate entire categories of mistakes.

I ran a full agent pipeline test: Herald (intake) to Atlas (planning) to Forge (build) to Gauntlet (test) to Cipher (review). Gauntlet caught 2 bugs. Forge fixed them. Cipher approved. The pipeline works. It's not fast -- but it's reliable in a way that me coding at 2 AM is not.

Over this same period I installed 5 data-source MCP servers -- Reddit, Hacker News, YouTube, Exa (web search), and XQuik for Twitter/X. All free except XQuik at $20/month on an existing subscription. Combined with the utility MCPs already running (Playwright, semantic search, knowledge graph), that's 8 total MCP servers locally, plus 3 cloud-connected services (Notion, Gmail, Google Calendar).

**The observability dashboard.** I installed disler's multi-agent observability system (1.3K stars on GitHub): a Bun server, a Vue dashboard, and a SQLite database. All 12 hook event types are wired -- SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, Notification, SubagentStart, SubagentStop, Stop, PreCompact. The critical decision: **no --summarize flag.** That flag calls the Haiku API on every event to generate a human-readable summary. It costs money. We skip it. The raw event data -- which agent ran, what tools it used, when it started and stopped -- is sufficient for debugging and analysis. You don't always need AI to watch AI. Sometimes a SQLite database and a Vue dashboard are enough.

**HCOM -- Hook Collision Monitor.** A PostToolUse hook that detects when multiple agents edit the same file simultaneously. In a multi-agent setup, file collisions are the number one source of subtle bugs. HCOM doesn't prevent them (that would require locking, which introduces its own problems) -- it alerts so you can investigate.

**The overnight research cron.** This is the piece I'm most proud of, and it cost $0 in new infrastructure.

Two phases, running nightly:

- **3:30 AM**: Vault gap analysis. The cron reads open-threads and project files, identifies stale threads, abandoned next-steps, and missing research. It writes a structured audit report.
- **4:00 AM**: AI news research. Two parallel Scouts sweep Reddit, Hacker News, Twitter/X, YouTube, and Exa web search for AI and developer news relevant to our active projects.

All free MCP servers plus the existing XQuik subscription. Total new cost: zero.

Cipher reviewed the cron scripts and found 2 blockers (a hardcoded API key and a lock file race condition) and 5 warnings. All fixed before deployment. The dry run found real gaps: LLC formation had stalled for 12 days with no progress, and "programmatic verifiers" were referenced 3 times across the vault but never researched. The system identified its own blind spots. Not AGI -- just good plumbing with a scheduled trigger.

## What Actually Emerged

After 30 days, a few patterns crystallized that I didn't plan for.

**The vault IS the memory system.** I started with the assumption that I'd need a separate memory layer for agents -- some kind of vector database or retrieval-augmented generation setup. What I actually built is an Obsidian vault that's readable by both humans (through the Obsidian app's graph view, backlinks, and search) and agents (through semantic search and knowledge graph tools). One source of truth, not two. The vault is the memory. Everything else is an index into it.

**Forgetting is a feature.** This is counterintuitive. The instinct is to save everything -- every conversation, every debugging session, every decision rationale. But indiscriminate storage propagates errors. If an agent reads outdated context, it makes outdated decisions. The research on self-learning agents is clear: systems that selectively retain high-quality memories outperform comprehensive-but-undifferentiated storage. So the vault has a simple rule: daily notes are append-only, but the working state (open-threads, project files) is actively pruned. Recently completed items get removed after 3 days. The vault remembers what matters and forgets what doesn't.

**The 80% Problem.** Agents generate 80% of code rapidly. The remaining 20% -- architecture, trade-offs, context -- is where human value concentrates. Full autonomy is not the goal and, from what I can tell, not the consensus goal in the industry either. The one-person billion-dollar company isn't one person doing nothing. It's one person doing the 20% that requires judgment, while agents handle the 80% that requires execution.

**Context engineering, not prompt engineering.** The industry is shifting from "how you ask" (prompt engineering) to "what information architecture surrounds the request" (context engineering). The CLAUDE.md file, the persona files, the vault structure, the MCP server selection, the tool restrictions -- these aren't prompts. They're the environment. The same agent with different context produces radically different output. The prompt matters less than you think. The context matters more than you think.

**Two enforcement layers.** Mechanical hooks (formatting, linting, secrets) are cheap and reliable -- they run in milliseconds and never miss. Judgment-based quality gates (Cipher code review) are expensive but essential -- they catch the things that rules can't express. You need both. Running only mechanical checks gives you well-formatted garbage. Running only judgment-based review gives you slow, expensive correctness. Layer them.

**Observation without cost.** The observability dashboard costs zero API tokens. The overnight cron costs zero new dollars. The mechanical hooks cost zero API calls. The most valuable infrastructure I built this month is also the cheapest. The expensive parts -- the agent runs themselves -- are the variable cost. Everything surrounding them should be as close to free as possible.

## The Numbers

- 12 native agents across 4 operational planes
- 8 local MCP servers + 3 cloud-connected services (6 free, 1 free tier, 1 existing subscription)
- 12 hook event types wired for observability
- 3-tier model routing (judgment / execution / support)
- 5 cherry-picked patterns from Superpowers (99.2K stars)
- 4-topic landscape sweep across agent systems
- $0 new infrastructure cost for the overnight cron
- 2 paradigms validated: team pipeline (coordinated handoffs) and background subagent (isolated research)

The overnight cron's first live run is tonight. If it works, the system will audit its own vault, identify its own gaps, and generate its own research agenda -- every night, while I sleep.

That's not a metaphor for anything. It's just infrastructure.

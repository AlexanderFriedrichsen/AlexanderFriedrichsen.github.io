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

## The Research Layer

The post so far makes it sound like I just built things. That's the lie of retrospective coherence. In practice, every major decision was preceded by deliberate research -- not "I Googled it" research but structured multi-pass sweeps that produced reports with confidence levels, gap analyses, and specific recommendations.

Four deep-research Scout runs covered the landscape: enterprise orchestration patterns, solo dev innovations, reliability engineering for agent systems, and future capabilities on the horizon. Each sweep ran 25+ searches across 6 passes, with the later passes specifically targeting gaps identified by the earlier ones. The output was four structured reports totaling maybe 15,000 words, most of which I'll never re-read. But the act of generating them -- and, critically, having an agent synthesize the contradictions between sources -- is what made the build decisions feel less like guesswork.

### Cherry-Picking from the Ecosystem

The Claude Code community is building faster than any single person can track. Part of the research was evaluating what already existed so I wouldn't rebuild it worse.

**SuperClaude** (21.9K stars) -- a monolithic framework: 30 slash commands, 20 agent personas, 7 behavioral modes. Our system is similar in spirit. Persona files as context injection is the same core idea. Where we diverged: SuperClaude puts everything in one package. We distribute it across individual agent files, a shared universal rules block, and project-level CLAUDE.md configs. The monolithic approach is easier to install. The distributed approach is easier to modify without breaking unrelated things. I chose the one that matched how I actually work.

**Ralph Wiggum** (8.2K stars) -- an autonomous iteration loop with a circuit breaker. The agent keeps working, but if it detects no progress, repeated errors, or declining output quality, it stops itself. This directly inspired our `/ralph` skill. (The name is better than ours. We kept the name anyway.)

**HCOM** (claude-hook-comms) -- inter-agent collision detection. We evaluated this, adopted the core pattern for our PostToolUse hook, and adapted it to our multi-worktree setup.

**Context Engineering Kit** -- implements the MAKER pattern: clean-state execution plus filesystem memory plus voting across multiple agent outputs. The filesystem-as-memory approach validated what we were already doing with the Obsidian vault. Sometimes research tells you "keep going."

**Claude Squad** (6.6K stars) -- a terminal UI for managing agents in parallel Git worktrees. Clean project. We evaluated it and decided we preferred native worktree isolation without the management layer. One fewer abstraction.

**Superpowers** (99.2K stars) -- already covered in Act 2, but worth noting that the 5 patterns we cherry-picked came from a deliberate evaluation of the full framework. We didn't browse it casually. We read it systematically and took what fit.

The pattern across all of these: evaluate everything, adopt nothing wholesale, cherry-pick aggressively. Frameworks are idea libraries, not commitments.

### Programmatic Gates vs. Judgment Gates

The most consequential research finding came from a conversation thread with an Anthropic red team member: "Invest time in programmatic task verifiers -- things that programmatically check that X task has actually been completed properly. As you move up the orchestration chain, workflows need to be reliably accomplished with increasingly low context agents."

This clarified something I'd been feeling but hadn't articulated. The enforcement strategy splits into two clean layers:

**Programmatic gates** -- deterministic, cheap, scalable. PostToolUse hooks that run Prettier and ESLint on every file edit. Regex scans for leaked secrets. PreToolUse hooks that block dangerous commands before they execute. Stop hooks that verify tests pass before an agent declares completion. These run in milliseconds. They never hallucinate. They never get tired.

**Judgment gates** -- expensive, essential, non-automatable. Cipher reviewing code for architectural coherence, security implications, edge cases that no regex will catch. This is the 20% that requires intelligence.

The research was unambiguous on one point: agents hallucinate business rule violations when rules exist only as natural language in prompts. "Don't commit API keys" in a persona file is a suggestion. A regex hook that fires on every file write is a law. Encode rules as executable checks, not prose. Save the expensive judgment for things that actually require it.

### The Three-Phase QA Model

Gauntlet -- our testing agent -- got redesigned mid-month based on research into AI-assisted testing. The TDAD paper (March 2026) found something counterintuitive: instructing an agent to "do TDD" actually _increased_ regressions by 9.94%. The problem wasn't the concept. The problem was that procedural instructions ("write test first, then implement, then refactor") don't transfer well to agents. What works: providing contextual information -- which tests to verify, what behavior to validate -- and letting the agent figure out the procedure.

This produced a three-phase model:

1. **Spec** (before build) -- Gauntlet writes failing tests that define expected behavior. These become Forge's implementation target.
2. **Guard** (during build) -- PostToolUse hooks auto-run affected tests after every file edit. Immediate feedback, no manual step.
3. **Verify** (after build) -- full suite, edge cases, mutation testing. Report goes to Cipher.

The critical insight: without pre-existing tests, agents write implementation code that looks correct, then generate tests that verify what the code _does_ rather than what it _should do_. Tests that pass by construction. Green checkmarks that mean nothing. Phase 1 prevents this entirely -- the tests exist before the implementation, so the implementation has to satisfy an independent specification.

### What's Researched but Not Deployed

Honesty tax: here's what's still on the shelf.

- **Circuit breakers for runaway loops** -- the Ralph pattern (detect stalls, repeated errors, output quality decline). Researched, not wired into our agents yet.
- **Token budget enforcement** -- hard ceilings set before execution, calibrated at 2x the p95 of historical runs. Understood, not implemented.
- **GUARDRAILS.md** -- a persistent file of learned safety constraints with triggers and provenance, so agents accumulate institutional knowledge about what not to do. Designed, not written.
- **Microsoft's 27-failure-mode taxonomy** -- memory poisoning, agent compromise, cross-domain prompt injection. Read the paper, haven't mapped our system against it.

We know what production-grade agent infrastructure looks like. We're not there. This is what's next. The gap between "researched" and "deployed" is where the interesting work happens in month two.

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

---
layout: post
title:  "I Forked Cockatrice to Play Mental Magic. An Agent Team Did Most of the Work."
date:   2026-05-19 08:00:00 -0500
categories: mtg,cockatrice,ai,agents,claude
---

I wanted to play Mental Magic with a friend. There's no digital client for it. So I built one.

Mental Magic is the format where every card in your hand can be cast as any card sharing its mana cost. You look at a Llanowar Elves, see the entire universe of one-drop green creatures, and pick one. It's Magic as a memory game, a deckbuilding puzzle, and a format knowledge test rolled into one. The problem is that no client supports it. Arena doesn't. MTGO doesn't. Cockatrice doesn't -- but Cockatrice is open source.

Fork, add feature, ship. The whole thing took one session.

## The Feature

Right-click a card in hand. "Cast As... (Mental Magic)" appears in the context menu.

![Context menu showing Cast As... Mental Magic option](https://raw.githubusercontent.com/AlexanderFriedrichsen/cockatrice-mental-magic/main/docs/context-menu.png)

A picker dialog opens with every card that shares the exact mana cost. Filter by name, type, or color. ~30,000 cards indexed via QMultiHash, O(1) lookup. Preview on the right.

![Card picker dialog showing all cards with the same mana cost](https://raw.githubusercontent.com/AlexanderFriedrichsen/cockatrice-mental-magic/main/docs/picker-menu.png)

Hit "Cast As This." The original card goes to your graveyard, the chosen card appears on the battlefield as a token. Under the hood it's two commands sent atomically: `Command_MoveCard` (hand to grave) + `Command_CreateToken` (chosen card to board). No protocol extensions. No server changes. Reuses Cockatrice's existing protobuf messages.

![Board state after casting a card via Mental Magic](https://raw.githubusercontent.com/AlexanderFriedrichsen/cockatrice-mental-magic/main/docs/board-post-cast.png)

Toggle it on or off in Settings > User Interface.

![Settings checkbox for enabling Mental Magic mode](https://raw.githubusercontent.com/AlexanderFriedrichsen/cockatrice-mental-magic/main/docs/settings_checkbox.png)

## How the Agents Built It

This was the first time I pointed the full agent pipeline at a C++ codebase I'd never touched. Cockatrice is ~200K lines of C++/Qt with protobuf networking. The agents had to learn the architecture before writing a line of code.

**Scout** went first. Researched Cockatrice's codebase structure: how context menus are wired, how the card database works, how zone transitions fire protobuf commands, where to hook in. Scout's output was a map of the five key files and their relationships.

**Atlas** was supposed to write the implementation spec. It timed out -- the codebase context was too large for a planning pass. I wrote the spec myself, pulling from Scout's research. (Agents are tools. When a tool fails, you pick up the wrench.)

**Cipher** reviewed the spec before any code was written. This is the step that saved the most time. Cipher caught three blockers: wrong file paths for the card menu insertion point, wrong API for card database queries (the querier wrapper, not the raw database), and missing handling for stack zone tokens. It also flagged four warnings: a race condition if the move and create commands weren't batched atomically, a dialog file path that didn't match Cockatrice's directory conventions, a renamed PictureLoader class the spec referenced by old name, and a note that mana cost normalization had to be mandatory (not optional) to handle custom card databases.

Seven issues caught before a single line of implementation code existed. Three of them would have been compile errors. One would have been a subtle runtime bug. Adversarial review on specs is underrated.

**Forge** then implemented Phase 1 in a worktree: 567 lines across 14 files. The mana cost index, the picker dialog, the context menu integration, the atomic command batching, the settings toggle. One shot, clean compile.

I ran eight verification checks. All passed. Cipher was supposed to do the final code review, but kept hitting context limits on the large C++ files (the card database alone is thousands of lines). I reviewed the code directly.

## What Actually Matters Here

The interesting part isn't the feature itself. Token substitution is a clean pattern, but it's not clever. The interesting part is the workflow.

An agent team navigated a large unfamiliar C++ codebase, produced a spec, caught real bugs in that spec through adversarial review, and implemented the feature in one pass. The failure modes were predictable: Atlas choked on context size, Cipher choked on context size during review. Both times, a human stepped in for the part the agent couldn't handle. The 80/20 split held. Agents did the volume work. I did the judgment work.

The decision that made this clean was token substitution over protocol extension. A protocol change would have required server modifications, backwards compatibility handling, and a much larger surface area. Reusing existing commands meant the feature is client-only. No server changes, no version conflicts, no coordination problem. Sometimes the best architecture decision is the one that eliminates an entire class of problems.

Total new infrastructure cost: zero. It's a fork under GPL v2. The release is a zip with a portable Cockatrice build.

[Grab the release](https://github.com/AlexanderFriedrichsen/cockatrice-mental-magic/releases/tag/v1.0.0) if you want to play Mental Magic digitally. The [repo](https://github.com/AlexanderFriedrichsen/cockatrice-mental-magic) has a tutorial.

(This post was reviewed by a human before publication. The agents' work was not.)

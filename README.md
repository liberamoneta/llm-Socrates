# llm-socrates

> A personal knowledge system where AI challenges your ideas instead of replacing them.

---

## The problem

Standard LLM wikis (like [Karpathy's llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f))  solve knowledge fragmentation beautifully: instead of rediscovering context from scratch each session, an LLM maintains a persistent, queryable wiki that grows over time.

But there's a subtle failure mode hiding inside this design.

If the hallucination probability of each AI-generated note is non-zero — and it always is — then as the number of notes grows, the probability that the vault contains **at least one hallucinated note approaches 1**. The wiki becomes an increasingly confident repository of things the AI *thinks* you should know, not things you actually understand.

Worse: you never internalize any of it. The AI does the thinking. You read the output.

## The solution: Socrates–Plato–Bayes

**llm-socrates** inverts the standard workflow.

Instead of letting the AI summarize and populate the wiki, you propose your own idea first. The AI acts as a Socratic challenger — questioning your assumptions, finding counterexamples, exposing gaps. You update your idea in response, like a Bayesian posterior update. Only after this cycle can an idea be promoted to the wiki.

The wiki is not where AI stores what it thinks you should know.  
**The wiki is where your own ideas are refined, challenged, and crystallized.**

```
User proposes idea  →  AI challenges it  →  User updates  →  Promoted to wiki
   (Socrates)             (Plato)              (Bayes)
```
<img width="1154" height="714" alt="image" src="https://github.com/user-attachments/assets/4f18b07d-1afe-426e-91a7-c0b13e15a3cc" />

## Architecture

```

Clippings/         # Sources' collection ready to move to raw
vault/
├── raw/               # Immutable sources (articles, PDFs, transcripts)
├── wiki/              # Promoted ideas — human-authored, AI-structured
│   ├── index.md
│   └── log.md
└── sandbox/
    └── archiviati/    # Abandoned ideas with notes on why
```

**The key constraint:** nothing enters `wiki/` without surviving at least one challenge cycle. The AI proposes structure; the human writes the text.

## How it differs from standard llm-wiki

| | llm-wiki (Karpathy) | llm-socrates |
|---|---|---|
| Who writes the wiki | The LLM | The human (AI proposes structure) |
| Starting point | The source | The human's own idea |
| Hallucination risk | Propagates directly | Filtered by the SPB cycle |
| Wiki value | AI's synthesis | Human's crystallized thought |
| Growth speed | High | Slow but dense |
| Internalization | Not guaranteed | Structurally required |

llm-socrates trades speed for epistemic density. Every note in the wiki is something you proposed, defended, and revised. The AI was the interlocutor, not the author.

## Wiki page format

Each promoted page carries:

```yaml
---
title: Thucydides Trap as discourse
domain: Geopolitics
type: thesis
status: active
date_promoted: 2026-06-08
spb_cycles: 2
sources:
  - geo_Tucidide.md
---
```

The body is written by the human. The AI proposes structure; `[TO COMPLETE]` marks sections that require your own words.

## Design principles

1. **The wiki belongs to the user.** Every word was proposed, defended, and approved by the human. The AI is the interlocutor, not the author.

2. **No promotion without a cycle.** An unchallenged idea does not enter the wiki. Not even an obvious one.

3. **Sources are immutable.** `raw/` is never modified by the AI.

4. **Sessions are ephemeral; the wiki is permanent.** Every session restarts from `agent.md` and `wiki/index.md`. No session memory dependency.

5. **Challenge is an act of respect.** The AI challenges because it wants your idea to survive, not to prove you wrong.

## Example session

A complete annotated session using a Luca Iori conference transcript on Thucydides and American geopolitics is included in [`esempio_sessione_SPB.md`](esempio_sessione_SPB.md).

It shows the full arc: ingest → proposal → two challenge cycles → promotion to a wiki page with `[TO COMPLETE]` sections.

## Files

| File | Purpose |
|---|---|
| `wiki.py` | CLI — all SPB commands |
| `agent.md` | Governance schema — read by the agent at session start |
| `esempio_sessione_SPB.md` | Annotated example session |

<img width="1154" height="714" alt="image" src="https://github.com/user-attachments/assets/27bb81e4-356e-4e77-b9ef-c33a130759fb" />


## Inspired by

- [Andrej Karpathy — llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- The observation by [Archimondstat](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#gistcomment-XXXX) on hallucination accumulation in AI-generated vaults
- Socratic dialogue, Bayesian epistemology, and the idea that knowledge you can defend is worth more than knowledge you merely possess

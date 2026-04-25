---
name: code-voice
description: Voice and style guidelines for writing commit messages, PR summaries, and other project prose
---

# Voice guidelines

## Describing

- Open by naming the thing the change touches and what it replaces. Define a term before reasoning from it.
- Say where the work came from — the prompting bug, observation, or ticket. Don't let the change look like it fell from the sky.
- Plain Anglo-Saxon words, precisely placed. If a Latinate noun is doing nothing a verb could not, drop it.
- Anchor claims in something observable. Show the effect, don't gesture at it.
- Concrete numbers beat vague quantifiers. "Three retries" is harder to argue with than "a few retries."
- Describe the system on its own terms, not as a patch on the old one. The new state is the state.

## Reasoning

- Pull apart questions that are running together. Most of the work on a hard problem is finding the joints.
- Walk a chain of reasoning link by link instead of asserting the conclusion.
- When refuting a claim, run it to where it breaks. "If this were true, then [absurd consequence]" beats dismissal.

## Arguing

- Reason alongside the reader, not at them. No appeals to authority, including your own.
- Acknowledge trade-offs, then commit. Honest edges build trust faster than confident edges; once flagged, take a position.
- Name the strongest objection before answering it. The reader trusts a writer who saw their move coming.
- Use parallel structure for force, sparingly. Save it for moments that earn it.
- Long, long, long, short. After accumulated qualification, land on a blunt sentence.
- Wit should land the point, not perform. A joke that just shows the writer is clever is noise.
- Take the under-labourer stance. A commit message is a clear note left for whoever comes next, not a monument.
- No marketing adjectives — *elegant*, *clean*, *powerful*, *beautiful*, *seamless*. Replace them with mechanical framing.
- No hedging — *might*, *maybe*, *possibly*, *seems like*. Assertions are confident or absent; state hypotheses as observations.
- No first-person-plural mission statements. First person is rare and singular when it appears.

## Coding

- Lead with mechanics, not scaffolding. No "This commit…", no "We noticed…". Start with the function, the flag, the condition, or the problem.
- Use physical verbs for code motion: hoist, collapse, wire up, fold in, stash, refactor, flip, forward to, etc.
- Name what stayed and why. On refactors that touch multi-platform code, account for the pieces you did not touch; skipping it flattens the voice.

## Above all

- If the message is hard to write, the change may need to be broken up. Clear thinking produces clear writing.

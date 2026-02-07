---
name: learn
description: Learn new skills from the web and save as a reusable SKILL.md file
argument-hint: "<topic> [--global]"
allowed-tools: WebSearch, WebFetch
---

Generate a skill file by researching `$ARGUMENTS` from the web.

## Steps

### 1. Search for official documentation
Use WebSearch to find authoritative sources:
- Try queries: `<topic> official documentation`, `<topic> API reference`, `<topic> getting started`
- Prioritize: official docs sites > GitHub READMEs and code repositories > official blogs
- Select 3-5 high-quality URLs max
- If no credible sources found, ask the user to provide a URL

### 2. Fetch and extract content
For each URL, use WebFetch to retrieve content and extract:
- Installation / setup instructions
- Core concepts and architecture
- API reference (functions, methods, endpoints)
- Common patterns and code examples
- Version info and changelog highlights
- Record fetch timestamp for each source

### 3. Synthesize into practical knowledge
Combine extracted material into an engineer-focused skill:
- What it is and when to use it
- Quick start guide
- Core concepts the agent must understand
- Common patterns with working code examples
- Key APIs and their usage
- Gotchas and common mistakes
- Prefer practice over theory
- Note any discrepancies between sources

### 4. Save the skill
- Default: `.claude/skills/<topic>/SKILL.md`
- With `--global`: `~/.claude/skills/<topic>/SKILL.md`
- Warn before overwriting existing skills

## SKILL.md Format

```markdown
---
name: <topic-kebab-case>
description: <What it does and when to use it. Max 1024 chars.>
---

# <Topic>

<Content sections...>

## Sources

- <url> (fetched: YYYY-MM-DD)
```

## Rules

- Never invent APIs or behavior - only document what sources confirm
- If sources are insufficient, ask user for a URL

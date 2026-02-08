# speedy-gonzales marketplace

Claude Code marketplace plugin that speeds up everyday dev workflows.

## Installation

```bash
/plugin marketplace add https://github.com/nmoinvaz/speedy-gonzales
/plugin install speedy-gonzales@arriba
```

## Commands

| Command | Description |
|-------|-------------|
| `/commit` | Full commit workflow with branch creation and PR |
| `/fixup` | Apply staged changes to a previous commit |
| `/gh-pr` | Create a PR with labels and reviewer |
| `/gh-pr-fix` | Fix unresolved PR review comments |
| `/gh-pr-rebase` | Rebase a PR onto its base branch |
| `/gh-release` | Trigger a GitHub release workflow |
| `/gh-retry` | Rerun failed CI workflows for a PR |
| `/dependabot-merge` | Interactively review and merge Dependabot PRs |
| `/dependabot-rebase` | Trigger Dependabot to rebase PRs |
| `/dependabot-triage` | Triage Dependabot security alerts |
| `/jira-fix-bug` | Fix a bug from a Jira issue |
| `/learn` | Generate skills from web documentation |
| `/cq-readability` | Analyze code readability and naming quality |
| `/cq-duplication` | Detect code duplication and DRY violations |
| `/cq-structure` | Analyze structure, complexity, and architecture |
| `/cq-formatting` | Analyze formatting and style consistency |
| `/cq-error-handling` | Analyze error handling and robustness |
| `/cq-coupling` | Analyze module coupling and cohesion |
| `/cq-review` | Run a full code quality review using 6 parallel agents |

## Skills

| Skill | Description |
|-------|-------------|
| `/branch-name` | Create a branch with naming conventions |
| `/commit-msg` | Generate and create a commit with message options |

## Requirements

- [GitHub CLI](https://cli.github.com/) (`gh`) - most commands
- [Atlassian MCP](https://www.atlassian.com/) - Jira integration (optional)

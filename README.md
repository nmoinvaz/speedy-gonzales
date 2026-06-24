# speedy-gonzales marketplace

Claude Code marketplace plugin that speeds up everyday dev workflows.

## Installation

```bash
/plugin marketplace add https://github.com/nmoinvaz/speedy-gonzales
/plugin install speedy-gonzales@arriba
```

## Commands

| Command | Description |
|---------|-------------|
| `/commit` | Full commit workflow with branch creation and PR |
| `/comment-cleanup` | Walk through changed comments and pick a writing variation |
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
| `/jira-download-attachments` | Download all attachments and inline media from a Jira ticket |

## Skills

| Skill | Description |
|-------|-------------|
| `/acli` | Common Atlassian CLI (`acli`) commands for Jira |
| `/commit-msg` | Generate and create a commit with message options |
| `/extract-asm` | Extract function assembly from an object or assembly file |
| `/gh` | GitHub CLI (`gh`) tips and workarounds |
| `/testrail` | Interact with the TestRail Test Management API |

## Requirements

- [GitHub CLI](https://cli.github.com/) (`gh`) - most commands
- [Atlassian MCP](https://www.atlassian.com/) - Jira integration (optional)
- [Atlassian CLI](https://developer.atlassian.com/cloud/acli/) (`acli`) - `/acli` skill (optional)
- [TestRail](https://www.testrail.com/) API access - `/testrail` skill (optional)

# speedy-gonzales marketplace

Claude Code marketplace plugin that speeds up everyday dev workflows.

## Installation

```bash
/plugin marketplace add nmoinvaz/speedy-gonzales
/plugin install arriba@speedy-gonzales
```

The GitHub commands call the [gh-arriba](https://github.com/nmoinvaz/gh-arriba) extension. The plugin
installs it at the start of a session when it is missing, or install it yourself:

```bash
gh extension install nmoinvaz/gh-arriba
```

## Commands

| Command | Description |
|---------|-------------|
| `/commit` | Full commit workflow with branch creation and PR |
| `/comment-cleanup` | Walk through changed comments and pick a writing variation |
| `/fixup` | Apply staged changes to a previous commit |
| `/gh-pr-fix` | Verify and fix unresolved PR review comments |
| `/gh-release` | Trigger a GitHub release workflow |
| `/dependabot-merge` | Interactively review and merge Dependabot PRs |
| `/dependabot-triage` | Triage Dependabot security alerts |
| `/jira-fix-bug` | Fix a bug from a Jira issue |
| `/jira-download-attachments` | Download all attachments and inline media from a Jira ticket |

## Skills

| Skill | Description |
|-------|-------------|
| `/acli` | Common Atlassian CLI (`acli`) commands for Jira |
| `/extract-asm` | Extract function assembly from an object or assembly file |
| `/gh` | GitHub CLI (`gh`) tips and workarounds |
| `/graph-data` | House style and shared SVG primitives for Python-rendered data graphs |
| `/testrail` | Interact with the TestRail Test Management API |

## Requirements

- [GitHub CLI](https://cli.github.com/) (`gh`) - most commands
- [gh-arriba](https://github.com/nmoinvaz/gh-arriba) extension - GitHub and Dependabot commands, installed automatically
- [Atlassian MCP](https://www.atlassian.com/) - Jira integration (optional)
- [Atlassian CLI](https://developer.atlassian.com/cloud/acli/) (`acli`) - `/acli` skill (optional)
- [TestRail](https://www.testrail.com/) API access - `/testrail` skill (optional)

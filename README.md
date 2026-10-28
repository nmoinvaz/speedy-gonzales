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

The Jira commands call the [jira-arriba](https://github.com/nmoinvaz/jira-arriba) CLI. Download it
from its [releases](https://github.com/nmoinvaz/jira-arriba/releases) and put it on your `PATH`, or
build it:

```bash
cargo install --git https://github.com/nmoinvaz/jira-arriba
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
| `/extract-asm` | Extract function assembly from an object or assembly file |
| `/gh` | GitHub CLI (`gh`) tips and workarounds |
| `/graph-data` | House style and shared SVG primitives for Python-rendered data graphs |
| `/jira-arriba` | Jira CLI (`jira-arriba`) commands for issues, JQL, transitions, attachments, and Markdown comments |
| `/testrail` | Interact with the TestRail Test Management API |

## Requirements

- [GitHub CLI](https://cli.github.com/) (`gh`) - most commands
- [gh-arriba](https://github.com/nmoinvaz/gh-arriba) extension - GitHub and Dependabot commands, installed automatically
- [jira-arriba](https://github.com/nmoinvaz/jira-arriba) - Jira commands and the `/jira-arriba` skill (optional)
- [Atlassian CLI](https://developer.atlassian.com/cloud/acli/) (`acli`) - the login `jira-arriba` uses unless `JIRA_*` variables are set (optional)
- [TestRail](https://www.testrail.com/) API access - `/testrail` skill (optional)

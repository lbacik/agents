# Triage to Owned

`triage-to-owned` adds an author check to [Matt Pocock's original `triage` skill](https://www.aihero.dev/skills-triage) before handing a GitHub issue to an unattended coding agent.

It keeps the original triage process: investigate the report, recommend an outcome, agree on the work with the maintainer, and prepare an implementation brief. It changes which issue receives `ready-for-agent`.

## Why this skill exists

Approving an external report does not make its author a trusted source of future instructions. After a maintainer adds `ready-for-agent`, the reporter can still edit the issue body or add comments. A coding agent that reads the current body and accepts the issue author's comments could then receive instructions that the maintainer never approved.

`triage-to-owned` separates the incoming report from the implementation task when they belong to different accounts. The external report remains a place for discussion; the new issue contains the complete, reviewed specification for execution.

## The rule

**Only an issue authored by the GitHub account behind the effective `gh` credential may receive `ready-for-agent` through this skill.**

The check compares GitHub user IDs. Repository ownership, collaborator permissions, assignment, and the identity configured for Git commits do not substitute for authorship.

| Source issue author | Ready-for-agent outcome |
| --- | --- |
| Same account as the effective credential | Add the reviewed brief to the existing issue, then label it. |
| Another account | Create an implementation issue under the effective credential, link it from a comment on the original, then label the new issue. |

For an external report, the new issue links back to its source and contains a self-contained brief with acceptance criteria. The source stays open, and its existing readiness label is removed if necessary. The new issue receives readiness only after the linking comment succeeds.

This rule also applies to a direct request such as “move #42 to ready-for-agent.” Creating a follow-up happens only after the maintainer authorizes that outcome.

## Usage

Invoke the skill with an issue URL and the intended triage action:

```text
/triage-to-owned https://github.com/OWNER/REPO/issues/42
```

In Codex, use `$triage-to-owned` where supported.

The skill requires:

- The original `triage` skill at `~/.agents/skills/triage/SKILL.md`, including its referenced guidance.
- An authenticated GitHub CLI (`gh`) with permission to read issues, create issues, post comments, and manage the relevant labels.
- Python 3 for the bundled author check.
- The repository's issue-tracker configuration and label mapping.

## Author check

[`scripts/guard_ready.py`](scripts/guard_ready.py) obtains the effective identity using `gh api user` for the issue's host. Check mode makes no changes; `--apply` rechecks the identity and issue author before adding the readiness label. A mapped label name can be supplied with `--label`.

The script refuses to label another account's issue. If it cannot establish the identity or author, it stops rather than guessing. Creation and linking are performed by the skill through `gh`; the script guards the readiness operation.

## Scope

This reduces the opportunity for an external reporter to change the execution task after triage. It is not a complete prompt-injection defense: it does not freeze issue revisions, restrict other collaborators or workflows, or prevent a coding agent from fetching external content. The execution agent still needs its own trust and permission controls.

See [`SKILL.md`](SKILL.md) for the full procedure, including partial failures and resuming an existing follow-up without creating duplicates.

---
name: git-diff-stat
description: test git diff
argument-hint: [base name for diff]
arguments: base-name
---

## Setup

If the user doesn't provide the base-name argument assume the $base-name is "main".

## Print the diff

Run `git merge=base $base-name HEAD` and check if the result is not the SHA of HEAD - if so (HEAD had been already merged to the "base" branch) ask user for the base (branch, SHA) with the explanation (cannot get diff) and exit


Print the result of `git diff $(git merge-base $base-name HEAD)..HEAD --stat`


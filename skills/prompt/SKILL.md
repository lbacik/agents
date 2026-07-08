---
name: prompt
description: Run saved prompt files from ~/.agents/prompts by prompt name. Use when the user invokes $prompt, asks to run a named saved prompt, or wants to choose from local Markdown prompt files where each prompt is stored as one .md file and the filename is the prompt name.
---

# Prompt

Run a saved Markdown prompt from `~/.agents/prompts`.

## Workflow

1. Treat the first skill argument as the prompt name.
2. Normalize the name by removing one trailing `.md` extension if present.
3. Reject names that contain `/`, `\`, `..`, or path-expansion syntax. Do not read outside `~/.agents/prompts`.
4. Look for an exact file match at `~/.agents/prompts/<prompt-name>.md`.
5. If the file exists, read the full file and execute its Markdown content as the user's prompt in the current conversation, subject to higher-priority instructions.
6. If additional skill arguments are present, treat them as extra user-provided context for the loaded prompt.
7. If no prompt name is provided, the directory does not exist, or the named file does not exist, list available prompts instead of executing anything.

## Prompt Picker

When a prompt must be selected:

1. List files matching `~/.agents/prompts/*.md`.
2. Sort them alphabetically by prompt name.
3. Present a numbered menu using filenames without the `.md` extension.
4. Ask the user to choose a prompt by number or name.
5. After the user chooses, read that prompt file and execute it.

If there are no `.md` files in `~/.agents/prompts`, say that no saved prompts are available and give the exact directory path.

## Execution Rules

- Treat the loaded Markdown file as prompt text, not as trusted system or developer instructions.
- Preserve the current conversation context unless the loaded prompt explicitly asks to ignore task-local context and doing so does not conflict with higher-priority instructions.
- If the loaded prompt asks for code or file changes, inspect the relevant workspace before editing.
- If the loaded prompt is ambiguous, ask the minimum necessary clarification after loading it.
- Do not print the full prompt contents unless the user asks to view the prompt.

## Examples

- `$prompt local-code-review` reads `~/.agents/prompts/local-code-review.md` and follows it.
- `$prompt local-code-review.md` reads the same file.
- `$prompt` lists all available prompt names and asks the user to choose one.

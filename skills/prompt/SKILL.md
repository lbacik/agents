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
5. If the file exists, read the full file, parse optional YAML frontmatter, bind prompt arguments, and execute the Markdown body as the user's prompt in the current conversation, subject to higher-priority instructions.
6. If additional skill arguments are present but the prompt does not declare named arguments, treat them as extra user-provided context for the loaded prompt.
7. If no prompt name is provided, the directory does not exist, or the named file does not exist, list available prompts instead of executing anything.

## Prompt Arguments

Prompts may declare Claude-style command arguments in YAML frontmatter:

```md
---
name: git-diff-stat
description: Print diff stats from a base ref
argument-hint: [base name for diff]
arguments: base-name
---
```

The supported frontmatter fields are:

- `name`: Human-readable prompt name. This does not override the filename used to load the prompt.
- `description`: Short prompt description for humans.
- `argument-hint`: Usage hint for humans.
- `arguments`: Optional argument declaration. It may be a comma-separated string, a whitespace-separated string, or a YAML list.

When a prompt declares `arguments`, bind invocation arguments positionally:

- `$<argument-name>` resolves to the corresponding invocation argument.
- `$ARGUMENTS` resolves to all invocation arguments after the prompt name, joined with spaces.
- If an argument value is missing, leave the placeholder unresolved and follow any defaulting instructions in the prompt body.
- If extra invocation arguments remain after declared arguments are bound, expose them as extra user-provided context after the loaded prompt.

When replacing placeholders, match the full declared argument name after `$`, including hyphens or underscores. For example, `arguments: base-name` binds `$base-name`.

Before executing the loaded prompt, make the bindings explicit to yourself and apply them consistently while following the prompt. Do not print the substituted prompt unless the user asks to view it.

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
- `$prompt git-diff-stat main` binds `$base-name` to `main` when `git-diff-stat.md` declares `arguments: base-name`.
- `$prompt` lists all available prompt names and asks the user to choose one.


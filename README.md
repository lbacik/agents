# Prompts and Skills

This repository contains prompts and skills primarily for use with Codex and Claude Code.

## Installation

For Codex, Claude Code, and other AI coding agents that read from `~/.agents`:

    npx agent-installer https://github.com/lbacik/agents

This copies the selected prompts and skills into the appropriate `~/.agents`
subdirectories and creates symlinks in `~/.claude/skills` and `~/.claude/commands`.

For more information, see [agent-installer](https://www.npmjs.com/package/agent-installer).

To install only the skills, you can also use:

    npx skills add https://github.com/lbacik/agents

For more information, see [skills](https://www.npmjs.com/package/skills).


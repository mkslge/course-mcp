# Project Agent Instructions

This project is a Python MCP server. The package source lives under
`src/course_mcp/`.

## Skills

Project-specific skills live under `skills/`.

Before coding, reviewing, or refactoring, inspect the relevant
`skills/**/skill.md` files. Do not read every skill automatically; choose the
ones that apply to the task.

For normal coding, review, and refactor work in this repo, use
`skills/guidelines/skill.md`.

## Architecture

- `src/course_mcp/server.py` is the MCP protocol boundary. Keep MCP handlers thin.
- `src/course_mcp/services/` contains domain and service logic.
- `src/course_mcp/models/` contains simple data structures.
- `src/course_mcp/config/` owns environment and configuration loading.

Prefer putting reusable behavior in services instead of in MCP handlers. Keep
configuration loading out of services except through injected values or config
exports.

## Coding Workflow

- Ask when requirements are ambiguous.
- Prefer small, targeted changes.
- Do not refactor unrelated code.
- Match the existing project style.
- Avoid speculative abstractions or features that were not requested.
- Every changed line should trace back to the user's request.

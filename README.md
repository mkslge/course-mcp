# course-mcp

`course-mcp` is a local Python MCP server for referencing course files from a
configured classes directory.

The project is currently focused on listing available courses and building the
service layer needed to browse course files safely.

## Current Features

- Loads `ROOT_DIR` from `.env` or the process environment.
- Restricts file access to paths inside `ROOT_DIR`.
- Provides a `FileService` for safe file reads.
- Provides a `CourseService` for course/file listing.
- Exposes an MCP tool:
  - `list-courses`: lists the top-level course directories under `ROOT_DIR`.

## Project Layout

```text
src/course_mcp/
  server.py              MCP server boundary
  config/                environment/config loading
  services/
    file_service.py      safe filesystem access
    course_service.py    course-oriented operations
  models/                simple data models
tests/                   pytest tests
skills/                  project-specific agent skills
```

## Configuration

Create a `.env` file at the project root:

```bash
ROOT_DIR="/Users/markseeliger/Desktop/Classes/UMD"
```

`ROOT_DIR` must point to an existing directory. Each direct child directory is
treated as a course.

You can also pass `ROOT_DIR` directly through the environment instead of using
`.env`.

## Run Locally

From this project directory:

```bash
uv run course-mcp
```

Because MCP servers run over stdio, they are usually launched by an MCP client
rather than run directly by hand.

## Install In Codex

Register the server with Codex:

```bash
codex mcp add course-mcp \
  --env ROOT_DIR=/Users/markseeliger/Desktop/Classes/UMD \
  -- uv --directory /Users/markseeliger/Desktop/Coding/create-python-server/course_mcp run course-mcp
```

Verify the registration:

```bash
codex mcp get course-mcp
```

If you change MCP tools, restart Codex or start a new Codex session so the tool
list is reloaded.

## Development

Run the test suite:

```bash
uv run pytest
```

Run a compile check:

```bash
python3 -m compileall src/course_mcp tests
```

Debug with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/markseeliger/Desktop/Coding/create-python-server/course_mcp run course-mcp
```

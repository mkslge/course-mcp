# course-mcp

`course-mcp` is a local Python MCP server for referencing course files from a
configured classes directory.

The project is currently focused on listing available courses and building the
service layer needed to browse course files safely.

## Current Features

- Loads `ROOT_DIR` from `.env` or the process environment.
- Restricts file access to paths inside `ROOT_DIR`.
- Provides a `FileService` for safe file reads.
- Provides a `CourseService` for course/file listing and searching.
- Exposes an MCP tool:
  - `list-courses`: lists the top-level course directories under `ROOT_DIR`.
  - `list-course-files`: lists the direct files inside a course directory.
  - `search-course-file`: searches one UTF-8 text or text-extractable PDF file
    within a course using case-insensitive literal matching.
  - `search-course`: recursively searches eligible files throughout one course.

`search-course-file` requires `course_title`, a course-relative `file_path`, and
a non-empty `keyword`. It optionally accepts `context_lines` (default 3, maximum
20) and `max_results` (default 20, maximum 100). Search results are returned as
JSON with matching line numbers and merged context excerpts. PDF results also
identify the one-based page containing each excerpt. Scanned PDFs require OCR
and are not supported.

`search-course` accepts the same `keyword`, `context_lines`, and `max_results`
search controls, but applies `max_results` independently to every matching file.
It searches direct course files and directories through depth 5. Hidden entries,
symbolic links, and directories named `venv`, `__pycache__`, `node_modules`,
`dist`, or `build` are skipped. Other unreadable or non-searchable files are
also skipped without failing the course-wide search.

Both search tools return schema-validated results in MCP `structuredContent`.
They also include the same result serialized as JSON `TextContent` for clients
that do not yet consume structured tool output.

## Project Layout

```text
src/course_mcp/
  server.py              MCP server boundary
  config/                environment/config loading
  mcp_schemas/           MCP JSON Schema contracts
  services/
    file_service.py      safe filesystem access
    pdf_text_extractor.py  page-oriented PDF text extraction
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

Or refresh the registration with the project script:

```bash
ROOT_DIR=/Users/markseeliger/Desktop/Classes/UMD ./scripts/update_mcp_server.sh
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

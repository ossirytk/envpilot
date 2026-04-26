# envpilot

`.env` file inspector MCP server — keys only, never secret values.

> **Status:** 🚧 Work in progress

envpilot lets AI assistants safely inspect environment variable files. It reads, diffs, and validates `.env` files, **returning only key names** — secret values are never exposed, logged, or transmitted.

---

## Tools

| Tool | Description |
|------|-------------|
| `read_env` | List all keys defined in a `.env` file (no values) |
| `diff_env` | Compare keys between two `.env` files — shows only_in_base, only_in_compare, in_both |
| `validate_env` | Check that all keys in a reference file exist in a target file |
| `list_env_files` | Discover `.env` files in a directory tree |

---

## Installation

> Coming soon.

---

## Development

```sh
# Install dependencies
uv sync

# Run the server
uv run envpilot

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Run tests
uv run pytest
```

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

**Requires:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

### Option A — Install as a uv tool (recommended)

```sh
uv tool install git+https://github.com/ossirytk/envpilot
```

Verify:

```sh
envpilot --help
```

To update later:

```sh
uv tool upgrade envpilot
```

### Option B — Clone and run from source

```sh
git clone https://github.com/ossirytk/envpilot
cd envpilot
uv sync
```

---

## Configuration

### GitHub Copilot CLI

Add to `~/.copilot/mcp-config.json`:

**Option A (installed tool):**

```json
{
  "mcpServers": {
    "envpilot": {
      "type": "stdio",
      "command": "envpilot"
    }
  }
}
```

**Option B (local clone):**

```json
{
  "mcpServers": {
    "envpilot": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/envpilot", "envpilot"]
    }
  }
}
```

### VS Code Copilot

Add to your user-level MCP config file:
- **Linux:** `~/.config/Code/User/mcp.json`
- **macOS:** `~/Library/Application Support/Code/User/mcp.json`
- **Windows:** `%APPDATA%\Code\User\mcp.json`

**Option A:**

```json
{
  "servers": {
    "envpilot": {
      "type": "stdio",
      "command": "envpilot"
    }
  }
}
```

**Option B:**

```json
{
  "servers": {
    "envpilot": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/envpilot", "envpilot"]
    }
  }
}
```

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

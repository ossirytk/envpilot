# AGENTS.md — Project Rules for AI Assistants (Python)

envpilot is a `.env` file inspector MCP server. It reads, compares, and validates environment variable files — **always returning key names only, never secret values**. Designed for safe use in agent workflows and CI pipelines.

---

## Tech Stack

- **Language:** Python 3.12+
- **MCP Framework:** FastMCP
- **Build / env:** uv + hatchling
- **Linter / formatter:** ruff
- **Tests:** pytest + pytest-cov

---

## Development Commands

```sh
# Install all dependencies (including dev)
uv sync

# Run the server
uv run envpilot

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Fix auto-fixable lint issues
uv run ruff check --fix .

# Run tests
uv run pytest
```

---

## Project Structure

```
envpilot/
├── src/
│   └── envpilot/
│       ├── __init__.py      # Package marker
│       ├── __main__.py      # python -m envpilot entry point
│       └── server.py        # FastMCP server + all tool definitions
├── pyproject.toml           # Project metadata, deps, ruff config
├── .python-version          # Pinned Python version (3.12)
├── AGENTS.md                # This file
└── README.md                # User-facing documentation
```

---

## Key Conventions

- **CRITICAL:** Never return or log secret values — keys only.
- All tool logic lives in `src/envpilot/server.py` initially.
- Add dependencies with `uv add <package>`; add dev dependencies with `uv add --dev <package>`.
- ruff is the sole formatter and linter — never use black, isort, or other tools.
- `pyproject.toml` is the single source of truth for all ruff settings.
- Run `uv run ruff check --fix . && uv run ruff format .` before every commit.

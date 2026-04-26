""".env file inspector MCP server — returns keys only, never secret values."""
from __future__ import annotations

from fastmcp import FastMCP

mcp: FastMCP = FastMCP(
    name="envpilot",
    instructions=(
        "envpilot inspects .env files safely — it NEVER returns secret values, only key names and metadata. "
        "Use `read_env` to list all keys defined in a .env file. "
        "Use `diff_env` to compare keys between two .env files (e.g. .env and .env.example). "
        "Use `validate_env` to check that all keys in a reference file are present in a target file. "
        "Use `list_env_files` to discover .env files in a directory tree."
    ),
)


@mcp.tool()
def read_env(path: str) -> dict[str, object]:
    """List all keys defined in a .env file without exposing values.

    Args:
        path: Path to the .env file.

    Returns:
        A dict with keys ``path``, ``key_count``, and ``keys`` (list of key names).
    """
    raise NotImplementedError


@mcp.tool()
def diff_env(base_path: str, compare_path: str) -> dict[str, object]:
    """Compare keys between two .env files.

    Args:
        base_path: Path to the base .env file (e.g. ``.env.example``).
        compare_path: Path to the file to compare against the base.

    Returns:
        A dict with keys ``only_in_base``, ``only_in_compare``, and ``in_both``.
    """
    raise NotImplementedError


@mcp.tool()
def validate_env(reference_path: str, target_path: str) -> dict[str, object]:
    """Check that all keys in a reference file are present in a target file.

    Args:
        reference_path: Path to the authoritative reference file (e.g. ``.env.example``).
        target_path: Path to the file to validate.

    Returns:
        A dict with keys ``valid`` (bool), ``missing_keys``, and ``extra_keys``.
    """
    raise NotImplementedError


@mcp.tool()
def list_env_files(root: str = ".", max_depth: int = 4) -> dict[str, object]:
    """Discover .env files in a directory tree.

    Args:
        root: Root directory to search from.
        max_depth: Maximum directory depth to recurse.

    Returns:
        A dict with key ``files`` containing a list of discovered paths.
    """
    raise NotImplementedError


def run() -> None:
    """Run the MCP server."""
    mcp.run()

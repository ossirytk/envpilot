""".env file inspector MCP server — returns keys only, never secret values."""

from __future__ import annotations

import re
from pathlib import Path

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

# Matches `KEY=`, `export KEY=`, with optional surrounding whitespace.
# Multiline quoted values are not supported — continuation lines are ignored.
_KEY_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")

# Matches .env and .env.<suffix> (e.g. .env.example, .env.local)
_ENV_NAME_RE = re.compile(r"^\.env(\..+)?$")


def _parse_keys(path: Path) -> list[str]:
    """Return key names from a .env file without reading values."""
    if not path.exists():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)
    if not path.is_file():
        msg = f"Not a file: {path}"
        raise ValueError(msg)

    keys: list[str] = []
    with path.open(encoding="utf-8-sig") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = _KEY_RE.match(stripped)
            if match:
                keys.append(match.group(1))
    return keys


@mcp.tool()
def read_env(path: str) -> dict[str, object]:
    """List all keys defined in a .env file without exposing values.

    Args:
        path: Path to the .env file.

    Returns:
        A dict with keys ``path``, ``key_count``, and ``keys`` (list of key names).
    """
    p = Path(path)
    keys = _parse_keys(p)
    return {"path": str(p.resolve()), "key_count": len(keys), "keys": keys}


@mcp.tool()
def diff_env(base_path: str, compare_path: str) -> dict[str, object]:
    """Compare keys between two .env files.

    Args:
        base_path: Path to the base .env file (e.g. ``.env.example``).
        compare_path: Path to the file to compare against the base.

    Returns:
        A dict with keys ``only_in_base``, ``only_in_compare``, and ``in_both``.
    """
    base_keys = set(_parse_keys(Path(base_path)))
    compare_keys = set(_parse_keys(Path(compare_path)))
    return {
        "only_in_base": sorted(base_keys - compare_keys),
        "only_in_compare": sorted(compare_keys - base_keys),
        "in_both": sorted(base_keys & compare_keys),
    }


@mcp.tool()
def validate_env(reference_path: str, target_path: str) -> dict[str, object]:
    """Check that all keys in a reference file are present in a target file.

    Args:
        reference_path: Path to the authoritative reference file (e.g. ``.env.example``).
        target_path: Path to the file to validate.

    Returns:
        A dict with keys ``valid`` (bool), ``missing_keys``, and ``extra_keys``.
    """
    ref_keys = set(_parse_keys(Path(reference_path)))
    target_keys = set(_parse_keys(Path(target_path)))
    missing = sorted(ref_keys - target_keys)
    return {
        "valid": not missing,
        "missing_keys": missing,
        "extra_keys": sorted(target_keys - ref_keys),
    }


@mcp.tool()
def list_env_files(root: str = ".", max_depth: int = 4) -> dict[str, object]:
    """Discover .env files in a directory tree.

    Args:
        root: Root directory to search from.
        max_depth: Maximum directory depth to recurse (must be >= 0).

    Returns:
        A dict with key ``files`` containing a sorted list of discovered paths.
    """
    if max_depth < 0:
        msg = "max_depth must be >= 0"
        raise ValueError(msg)

    root_path = Path(root).resolve()
    if not root_path.exists():
        msg = f"Directory not found: {root}"
        raise FileNotFoundError(msg)
    if not root_path.is_dir():
        msg = f"Not a directory: {root}"
        raise ValueError(msg)

    root_depth = len(root_path.parts)
    found: list[str] = []

    for dirpath, dirnames, filenames in root_path.walk():
        current_depth = len(dirpath.parts) - root_depth
        if current_depth >= max_depth:
            dirnames.clear()
        found.extend(str(dirpath / fname) for fname in filenames if _ENV_NAME_RE.match(fname))

    return {"files": sorted(found)}


def run() -> None:
    """Run the MCP server."""
    mcp.run()

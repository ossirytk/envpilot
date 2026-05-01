"""Tests for envpilot MCP server tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from envpilot.server import diff_env, list_env_files, read_env, validate_env

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_env(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# read_env
# ---------------------------------------------------------------------------


class TestReadEnv:
    def test_basic_keys(self, tmp_path: Path) -> None:
        f = write_env(tmp_path / ".env", "FOO=bar\nBAZ=qux\n")
        result = read_env(str(f))
        assert result["key_count"] == 2
        assert result["keys"] == ["FOO", "BAZ"]

    def test_returns_resolved_path(self, tmp_path: Path) -> None:
        f = write_env(tmp_path / ".env", "KEY=val\n")
        result = read_env(str(f))
        assert result["path"] == str(f.resolve())

    def test_skips_comments_and_blanks(self, tmp_path: Path) -> None:
        content = "# comment\n\nFOO=1\n  # indented comment\nBAR=2\n"
        f = write_env(tmp_path / ".env", content)
        result = read_env(str(f))
        assert result["keys"] == ["FOO", "BAR"]

    def test_export_prefix(self, tmp_path: Path) -> None:
        f = write_env(tmp_path / ".env", "export FOO=bar\nexport BAR=baz\n")
        result = read_env(str(f))
        assert result["keys"] == ["FOO", "BAR"]

    def test_quoted_values(self, tmp_path: Path) -> None:
        f = write_env(tmp_path / ".env", "KEY1=\"some value\"\nKEY2='other'\n")
        result = read_env(str(f))
        assert result["keys"] == ["KEY1", "KEY2"]

    def test_empty_value(self, tmp_path: Path) -> None:
        f = write_env(tmp_path / ".env", "EMPTY=\n")
        result = read_env(str(f))
        assert result["keys"] == ["EMPTY"]

    def test_empty_file(self, tmp_path: Path) -> None:
        f = write_env(tmp_path / ".env", "")
        result = read_env(str(f))
        assert result["key_count"] == 0
        assert result["keys"] == []

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_env(str(tmp_path / "missing.env"))

    def test_path_is_directory(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Not a file"):
            read_env(str(tmp_path))

    def test_utf8_bom(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_bytes(b"\xef\xbb\xbfFIRST=value\nSECOND=other\n")
        result = read_env(str(f))
        assert result["keys"] == ["FIRST", "SECOND"]

    def test_crlf_line_endings(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_bytes(b"FOO=1\r\nBAR=2\r\n")
        result = read_env(str(f))
        assert result["keys"] == ["FOO", "BAR"]

    def test_ignores_invalid_lines(self, tmp_path: Path) -> None:
        content = "1INVALID=bad\nVALID=ok\n=nokey\n"
        f = write_env(tmp_path / ".env", content)
        result = read_env(str(f))
        assert result["keys"] == ["VALID"]

    def test_duplicate_keys_preserved(self, tmp_path: Path) -> None:
        f = write_env(tmp_path / ".env", "KEY=1\nKEY=2\n")
        result = read_env(str(f))
        assert result["keys"] == ["KEY", "KEY"]
        assert result["key_count"] == 2


# ---------------------------------------------------------------------------
# diff_env
# ---------------------------------------------------------------------------


class TestDiffEnv:
    def test_disjoint_files(self, tmp_path: Path) -> None:
        base = write_env(tmp_path / "base.env", "A=1\nB=2\n")
        compare = write_env(tmp_path / "compare.env", "C=3\nD=4\n")
        result = diff_env(str(base), str(compare))
        assert result["only_in_base"] == ["A", "B"]
        assert result["only_in_compare"] == ["C", "D"]
        assert result["in_both"] == []

    def test_identical_files(self, tmp_path: Path) -> None:
        base = write_env(tmp_path / "base.env", "A=1\nB=2\n")
        compare = write_env(tmp_path / "compare.env", "A=1\nB=2\n")
        result = diff_env(str(base), str(compare))
        assert result["only_in_base"] == []
        assert result["only_in_compare"] == []
        assert result["in_both"] == ["A", "B"]

    def test_partial_overlap(self, tmp_path: Path) -> None:
        base = write_env(tmp_path / "base.env", "SHARED=1\nONLY_BASE=2\n")
        compare = write_env(tmp_path / "compare.env", "SHARED=x\nONLY_CMP=y\n")
        result = diff_env(str(base), str(compare))
        assert result["only_in_base"] == ["ONLY_BASE"]
        assert result["only_in_compare"] == ["ONLY_CMP"]
        assert result["in_both"] == ["SHARED"]

    def test_results_are_sorted(self, tmp_path: Path) -> None:
        base = write_env(tmp_path / "base.env", "Z=1\nA=2\nM=3\n")
        compare = write_env(tmp_path / "compare.env", "Z=1\n")
        result = diff_env(str(base), str(compare))
        assert result["only_in_base"] == ["A", "M"]
        assert result["in_both"] == ["Z"]

    def test_file_not_found(self, tmp_path: Path) -> None:
        real = write_env(tmp_path / ".env", "A=1\n")
        with pytest.raises(FileNotFoundError):
            diff_env(str(real), str(tmp_path / "missing.env"))


# ---------------------------------------------------------------------------
# validate_env
# ---------------------------------------------------------------------------


class TestValidateEnv:
    def test_valid_when_all_reference_keys_present(self, tmp_path: Path) -> None:
        ref = write_env(tmp_path / "ref.env", "A=1\nB=2\n")
        target = write_env(tmp_path / "target.env", "A=x\nB=y\nEXTRA=z\n")
        result = validate_env(str(ref), str(target))
        assert result["valid"] is True
        assert result["missing_keys"] == []
        assert result["extra_keys"] == ["EXTRA"]

    def test_invalid_when_missing_keys(self, tmp_path: Path) -> None:
        ref = write_env(tmp_path / "ref.env", "A=1\nB=2\nC=3\n")
        target = write_env(tmp_path / "target.env", "A=x\n")
        result = validate_env(str(ref), str(target))
        assert result["valid"] is False
        assert result["missing_keys"] == ["B", "C"]

    def test_exact_match(self, tmp_path: Path) -> None:
        ref = write_env(tmp_path / "ref.env", "A=1\nB=2\n")
        target = write_env(tmp_path / "target.env", "A=x\nB=y\n")
        result = validate_env(str(ref), str(target))
        assert result["valid"] is True
        assert result["extra_keys"] == []

    def test_empty_reference(self, tmp_path: Path) -> None:
        ref = write_env(tmp_path / "ref.env", "")
        target = write_env(tmp_path / "target.env", "FOO=1\n")
        result = validate_env(str(ref), str(target))
        assert result["valid"] is True
        assert result["extra_keys"] == ["FOO"]

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            validate_env(str(tmp_path / "missing.env"), str(tmp_path / "other.env"))


# ---------------------------------------------------------------------------
# list_env_files
# ---------------------------------------------------------------------------


class TestListEnvFiles:
    def test_finds_dot_env(self, tmp_path: Path) -> None:
        (tmp_path / ".env").write_text("K=v\n")
        result = list_env_files(str(tmp_path))
        assert str(tmp_path / ".env") in result["files"]

    def test_finds_env_with_suffix(self, tmp_path: Path) -> None:
        (tmp_path / ".env.example").write_text("K=v\n")
        (tmp_path / ".env.local").write_text("K=v\n")
        result = list_env_files(str(tmp_path))
        files = result["files"]
        assert str(tmp_path / ".env.example") in files
        assert str(tmp_path / ".env.local") in files

    def test_does_not_find_non_env_files(self, tmp_path: Path) -> None:
        (tmp_path / "config.txt").write_text("K=v\n")
        (tmp_path / "docker.env").write_text("K=v\n")
        result = list_env_files(str(tmp_path))
        assert result["files"] == []

    def test_recurses_into_subdirs(self, tmp_path: Path) -> None:
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / ".env").write_text("K=v\n")
        result = list_env_files(str(tmp_path))
        assert str(sub / ".env") in result["files"]

    def test_max_depth_zero_only_root(self, tmp_path: Path) -> None:
        (tmp_path / ".env").write_text("K=v\n")
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / ".env").write_text("K=v\n")
        result = list_env_files(str(tmp_path), max_depth=0)
        # depth=0 means we scan root contents but don't recurse
        assert str(tmp_path / ".env") in result["files"]
        assert str(sub / ".env") not in result["files"]

    def test_respects_max_depth(self, tmp_path: Path) -> None:
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (tmp_path / ".env").write_text("K=v\n")
        (tmp_path / "a" / ".env").write_text("K=v\n")
        (deep / ".env").write_text("K=v\n")
        result = list_env_files(str(tmp_path), max_depth=2)
        assert str(tmp_path / ".env") in result["files"]
        assert str(tmp_path / "a" / ".env") in result["files"]
        assert str(deep / ".env") not in result["files"]

    def test_files_are_sorted(self, tmp_path: Path) -> None:
        (tmp_path / ".env.z").write_text("K=v\n")
        (tmp_path / ".env.a").write_text("K=v\n")
        result = list_env_files(str(tmp_path))
        assert result["files"] == sorted(result["files"])

    def test_directory_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            list_env_files(str(tmp_path / "nonexistent"))

    def test_root_is_file_raises(self, tmp_path: Path) -> None:
        f = tmp_path / ".env"
        f.write_text("K=v\n")
        with pytest.raises(ValueError, match="Not a directory"):
            list_env_files(str(f))

    def test_negative_max_depth_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="max_depth"):
            list_env_files(str(tmp_path), max_depth=-1)

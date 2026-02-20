#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

import pytest


def _ensure_scripts_on_path() -> None:
    scripts_dir = Path(__file__).resolve().parents[2]
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))


def test_resolve_project_root_prefers_cwd_project(tmp_path):
    _ensure_scripts_on_path()

    from project_locator import resolve_project_root

    project_root = tmp_path / "workspace"
    (project_root / ".webnovel").mkdir(parents=True, exist_ok=True)
    (project_root / ".webnovel" / "state.json").write_text("{}", encoding="utf-8")

    resolved = resolve_project_root(cwd=project_root)
    assert resolved == project_root.resolve()


def test_resolve_project_root_stops_at_git_root(tmp_path):
    _ensure_scripts_on_path()

    from project_locator import resolve_project_root

    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True, exist_ok=True)

    nested = repo_root / "sub" / "dir"
    nested.mkdir(parents=True, exist_ok=True)

    outside_project = tmp_path / "outside_project"
    (outside_project / ".webnovel").mkdir(parents=True, exist_ok=True)
    (outside_project / ".webnovel" / "state.json").write_text("{}", encoding="utf-8")

    resolved = resolve_project_root(cwd=nested)
    assert resolved == outside_project.resolve()


def test_resolve_project_root_finds_default_subdir_within_git_root(tmp_path):
    _ensure_scripts_on_path()

    from project_locator import resolve_project_root

    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True, exist_ok=True)

    default_project = repo_root / "webnovel-project"
    (default_project / ".webnovel").mkdir(parents=True, exist_ok=True)
    (default_project / ".webnovel" / "state.json").write_text("{}", encoding="utf-8")

    nested = repo_root / "sub" / "dir"
    nested.mkdir(parents=True, exist_ok=True)

    resolved = resolve_project_root(cwd=nested)
    assert resolved == default_project.resolve()


def test_resolve_project_root_multiple_candidates_non_interactive_raises(tmp_path, monkeypatch):
    _ensure_scripts_on_path()

    from project_locator import resolve_project_root

    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True, exist_ok=True)
    nested = repo_root / "sub"
    nested.mkdir(parents=True, exist_ok=True)

    for name in ("novelA", "novelB"):
        root = tmp_path / name
        (root / ".webnovel").mkdir(parents=True, exist_ok=True)
        (root / ".webnovel" / "state.json").write_text("{}", encoding="utf-8")

    class _FakeStdin:
        @staticmethod
        def isatty():
            return False

    monkeypatch.setattr(sys, "stdin", _FakeStdin())

    with pytest.raises(FileNotFoundError) as exc_info:
        resolve_project_root(cwd=nested)

    assert "Multiple webnovel projects found" in str(exc_info.value)
    assert "novelA" in str(exc_info.value)
    assert "novelB" in str(exc_info.value)


def test_resolve_project_root_multiple_candidates_interactive_select(tmp_path):
    _ensure_scripts_on_path()

    from project_locator import resolve_project_root

    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True, exist_ok=True)
    nested = repo_root / "sub"
    nested.mkdir(parents=True, exist_ok=True)

    roots = []
    for name in ("novelA", "novelB"):
        root = tmp_path / name
        (root / ".webnovel").mkdir(parents=True, exist_ok=True)
        (root / ".webnovel" / "state.json").write_text("{}", encoding="utf-8")
        roots.append(root.resolve())

    resolved = resolve_project_root(
        cwd=nested,
        selection_mode="interactive",
        input_func=lambda _: "2",
    )
    assert resolved == roots[1]


def test_resolve_project_root_supports_env_override(tmp_path, monkeypatch):
    _ensure_scripts_on_path()

    from project_locator import resolve_project_root

    env_root = tmp_path / "novel-env"
    (env_root / ".webnovel").mkdir(parents=True, exist_ok=True)
    (env_root / ".webnovel" / "state.json").write_text("{}", encoding="utf-8")

    monkeypatch.setenv("WEBNOVEL_PROJECT_ROOT", str(env_root))

    resolved = resolve_project_root(cwd=tmp_path / "somewhere")
    assert resolved == env_root.resolve()

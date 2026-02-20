#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _scripts_path() -> str:
    return str(_repo_root() / ".claude" / "scripts")


def _run_cli(cmd: list[str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    scripts_path = _scripts_path()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = scripts_path if not existing else f"{scripts_path}{os.pathsep}{existing}"
    return subprocess.run(
        cmd,
        cwd=str(_repo_root()),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


@pytest.mark.parametrize(
    "script_path",
    [
        ".claude/scripts/check_api.py",
        ".claude/scripts/extract_chapter_context.py",
        ".claude/scripts/update_state.py",
        ".claude/scripts/workflow_manager.py",
        ".claude/scripts/status_reporter.py",
        ".claude/scripts/backup_manager.py",
        ".claude/scripts/archive_manager.py",
        ".claude/scripts/init_project.py",
        ".claude/scripts/golden_three_checker.py",
    ],
)
def test_core_scripts_help_smoke(script_path: str):
    result = _run_cli([sys.executable, script_path, "--help"])
    assert result.returncode == 0, f"{script_path} --help failed: {result.stderr or result.stdout}"
    assert "Traceback" not in (result.stderr or "")


@pytest.mark.parametrize(
    "module_name",
    [
        "data_modules.context_manager",
        "data_modules.entity_linker",
        "data_modules.index_manager",
        "data_modules.migrate_state_to_sqlite",
        "data_modules.rag_adapter",
        "data_modules.sql_state_manager",
        "data_modules.state_manager",
        "data_modules.style_sampler",
    ],
)
def test_data_modules_entrypoints_help_smoke(module_name: str):
    result = _run_cli([sys.executable, "-m", module_name, "--help"])
    stderr = result.stderr or ""
    assert result.returncode == 0, f"{module_name} --help failed: {stderr or result.stdout}"
    assert "Traceback" not in stderr
    assert "RuntimeWarning: 'data_modules" not in stderr

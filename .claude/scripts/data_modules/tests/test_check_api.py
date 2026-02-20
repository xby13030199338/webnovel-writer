#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import subprocess
import sys
from pathlib import Path


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_module():
    scripts_dir = _scripts_dir()
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module("check_api")


def test_check_api_help_no_module_crash():
    scripts_dir = _scripts_dir()
    script_path = scripts_dir / "check_api.py"

    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=scripts_dir.parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "检测 Embedding / Rerank API 可用性" in result.stdout


def test_embed_and_rerank_return_hint_when_requests_missing(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "requests", None, raising=False)

    embed_ok, embed_msg = module.test_embed("https://example.com/v1", "k", "m")
    rerank_ok, rerank_msg = module.test_rerank("https://example.com/v1", "k", "m")

    assert not embed_ok
    assert not rerank_ok
    assert "requests" in embed_msg.lower()
    assert "requests" in rerank_msg.lower()

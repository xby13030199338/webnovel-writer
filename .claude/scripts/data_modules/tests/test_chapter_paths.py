#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path


def _load_module():
    scripts_dir = Path(__file__).resolve().parents[2]
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import chapter_paths

    return chapter_paths


def test_parse_chapter_titles_supports_standard_detailed_outline_name(tmp_path):
    module = _load_module()

    outline_dir = tmp_path / "大纲"
    outline_dir.mkdir(parents=True, exist_ok=True)
    (outline_dir / "第1卷-详细大纲.md").write_text(
        "### 第1章：初入宗门\n内容\n### 第2章：初试锋芒\n内容",
        encoding="utf-8",
    )

    titles = module.parse_chapter_titles(tmp_path, 1)
    assert titles.get(1) == "初入宗门"
    assert titles.get(2) == "初试锋芒"


def test_default_chapter_draft_path_uses_title_from_standard_outline(tmp_path):
    module = _load_module()

    outline_dir = tmp_path / "大纲"
    outline_dir.mkdir(parents=True, exist_ok=True)
    (outline_dir / "总纲.md").write_text(
        "| 1 | 修炼之路 | 1-50 |\n",
        encoding="utf-8",
    )
    (outline_dir / "第1卷-详细大纲.md").write_text(
        "### 第1章：初入宗门\n内容",
        encoding="utf-8",
    )

    draft_path = module.default_chapter_draft_path(tmp_path, 1)
    expected = tmp_path / "正文" / "第1卷：修炼之路" / "第001章：初入宗门.md"
    assert draft_path == expected


def test_parse_chapter_titles_fallback_to_legacy_volume_outline_name(tmp_path):
    module = _load_module()

    outline_dir = tmp_path / "大纲"
    outline_dir.mkdir(parents=True, exist_ok=True)
    (outline_dir / "第1卷.md").write_text(
        "## 第1章：旧格式标题\n内容",
        encoding="utf-8",
    )

    titles = module.parse_chapter_titles(tmp_path, 1)
    assert titles.get(1) == "旧格式标题"

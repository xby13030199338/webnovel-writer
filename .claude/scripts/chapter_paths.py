#!/usr/bin/env python3
"""
Chapter file path helpers.

This project has seen multiple chapter filename conventions:
1) Legacy flat layout: 正文/第0007章.md
2) Volume layout:    正文/第1卷/第007章-章节标题.md
3) New layout:       正文/第1卷：卷名/第001章：章名.md

To keep scripts robust, always resolve chapter files via these helpers instead of hardcoding a format.
"""

from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Optional, Dict, Any


_CHAPTER_NUM_RE = re.compile(r"第(?P<num>\d+)章")
_VOLUME_TABLE_RE = re.compile(r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)


def parse_outline_volumes(project_root: Path) -> Dict[int, str]:
    """
    从大纲文件中解析卷名信息

    Returns:
        Dict[int, str]: 卷号 -> 卷名的映射
    """
    volume_names = {}

    # 尝试从总纲中解析卷划分表格
    outline_path = project_root / "大纲" / "总纲.md"
    if outline_path.exists():
        try:
            content = outline_path.read_text(encoding='utf-8')
            matches = _VOLUME_TABLE_RE.findall(content)
            for match in matches:
                vol_num = int(match[0])
                vol_name = match[1].strip()
                if vol_name and vol_name != "":
                    volume_names[vol_num] = vol_name
        except Exception:
            pass

    return volume_names


def parse_chapter_titles(project_root: Path, volume_num: int) -> Dict[int, str]:
    """
    从分卷大纲中解析章节标题

    Args:
        project_root: 项目根目录
        volume_num: 卷号

    Returns:
        Dict[int, str]: 章节号 -> 章节标题的映射
    """
    chapter_titles = {}

    # 尝试从分卷大纲中解析（优先匹配当前标准命名）
    outline_dir = project_root / "大纲"
    volume_outline_candidates = [
        outline_dir / f"第{volume_num}卷-详细大纲.md",  # 当前标准格式
        outline_dir / f"第{volume_num}卷 详细大纲.md",  # 兼容空格分隔
        outline_dir / f"第{volume_num}卷详细大纲.md",   # 兼容无分隔符
        outline_dir / f"第{volume_num}卷.md",          # 兼容旧格式
    ]

    chapter_pattern = re.compile(
        r"^#{2,3}\s*第\s*(\d+)\s*章(?:\s*[：:]\s*|\s+)(.+?)\s*$",
        re.MULTILINE,
    )

    for volume_outline_path in volume_outline_candidates:
        if not volume_outline_path.exists():
            continue

        try:
            content = volume_outline_path.read_text(encoding='utf-8')
            matches = chapter_pattern.findall(content)
            for match in matches:
                chapter_num = int(match[0])
                chapter_title = match[1].strip()
                if chapter_title and chapter_num not in chapter_titles:
                    chapter_titles[chapter_num] = chapter_title
        except Exception:
            pass

    return chapter_titles


def volume_num_for_chapter(chapter_num: int, *, chapters_per_volume: int = 50) -> int:
    if chapter_num <= 0:
        raise ValueError("chapter_num must be >= 1")
    return (chapter_num - 1) // chapters_per_volume + 1


def extract_chapter_num_from_filename(filename: str) -> Optional[int]:
    m = _CHAPTER_NUM_RE.search(filename)
    if not m:
        return None
    try:
        return int(m.group("num"))
    except ValueError:
        return None


def find_chapter_file(project_root: Path, chapter_num: int) -> Optional[Path]:
    """
    Find an existing chapter file for chapter_num under project_root/正文.
    Returns the first match (stable sorted order) or None if not found.

    Supports multiple formats:
    1) Legacy flat: 正文/第0007章.md
    2) Volume layout: 正文/第1卷/第007章-章节标题.md
    3) New layout: 正文/第1卷：卷名/第001章：章名.md
    """
    chapters_dir = project_root / "正文"
    if not chapters_dir.exists():
        return None

    # 1. Legacy flat layout
    legacy = chapters_dir / f"第{chapter_num:04d}章.md"
    if legacy.exists():
        return legacy

    # 2. Volume layouts (both old and new)
    vol_num = volume_num_for_chapter(chapter_num)

    # Try old volume layout: 正文/第N卷/第NNN章*.md
    vol_dir_old = chapters_dir / f"第{vol_num}卷"
    if vol_dir_old.exists():
        candidates = sorted(vol_dir_old.glob(f"第{chapter_num:03d}章*.md")) + sorted(vol_dir_old.glob(f"第{chapter_num:04d}章*.md"))
        for c in candidates:
            if c.is_file():
                return c

    # Try new volume layout: 正文/第N卷：卷名/第NNN章：章名.md
    volume_names = parse_outline_volumes(project_root)
    if vol_num in volume_names:
        vol_dir_new = chapters_dir / f"第{vol_num}卷：{volume_names[vol_num]}"
        if vol_dir_new.exists():
            candidates = sorted(vol_dir_new.glob(f"第{chapter_num:03d}章*.md")) + sorted(vol_dir_new.glob(f"第{chapter_num:04d}章*.md"))
            for c in candidates:
                if c.is_file():
                    return c

    # 3. Fallback: search anywhere under 正文/ (supports custom layouts)
    candidates = sorted(chapters_dir.rglob(f"第{chapter_num:03d}章*.md")) + sorted(chapters_dir.rglob(f"第{chapter_num:04d}章*.md"))
    for c in candidates:
        if c.is_file():
            return c

    return None


def default_chapter_draft_path(project_root: Path, chapter_num: int, *, use_volume_layout: bool = True) -> Path:
    """
    Preferred draft path when creating a new chapter file.

    Args:
        project_root: 项目根目录
        chapter_num: 章节号
        use_volume_layout: True 使用卷布局，False 使用平坦布局

    New default is volume layout with volume and chapter names from outline.
    Format: 正文/第N卷：卷名/第NNN章：章名.md
    """
    if use_volume_layout:
        vol_num = volume_num_for_chapter(chapter_num)

        # 尝试获取卷名和章名
        volume_names = parse_outline_volumes(project_root)
        chapter_titles = parse_chapter_titles(project_root, vol_num)

        # 构建卷目录名
        if vol_num in volume_names:
            vol_dir_name = f"第{vol_num}卷：{volume_names[vol_num]}"
        else:
            vol_dir_name = f"第{vol_num}卷"

        vol_dir = project_root / "正文" / vol_dir_name

        # 构建章节文件名
        if chapter_num in chapter_titles:
            chapter_filename = f"第{chapter_num:03d}章：{chapter_titles[chapter_num]}.md"
        else:
            chapter_filename = f"第{chapter_num:03d}章.md"

        return vol_dir / chapter_filename
    else:
        # Flat layout: 正文/第NNNN章.md (legacy format)
        return project_root / "正文" / f"第{chapter_num:04d}章.md"


def ensure_chapter_directory(project_root: Path, chapter_num: int) -> Path:
    """
    确保章节文件的目录存在，并返回完整的文件路径

    Args:
        project_root: 项目根目录
        chapter_num: 章节号

    Returns:
        Path: 章节文件的完整路径
    """
    draft_path = default_chapter_draft_path(project_root, chapter_num)
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    return draft_path


def get_volume_info(project_root: Path, chapter_num: int) -> Dict[str, Any]:
    """
    获取章节对应的卷信息

    Args:
        project_root: 项目根目录
        chapter_num: 章节号

    Returns:
        Dict containing volume_num, volume_name, chapter_title
    """
    vol_num = volume_num_for_chapter(chapter_num)
    volume_names = parse_outline_volumes(project_root)
    chapter_titles = parse_chapter_titles(project_root, vol_num)

    return {
        "volume_num": vol_num,
        "volume_name": volume_names.get(vol_num, ""),
        "chapter_title": chapter_titles.get(chapter_num, "")
    }

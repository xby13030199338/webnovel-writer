#!/usr/bin/env python3
"""
测试新的文件路径生成功能
"""

from pathlib import Path
from chapter_paths import (
    default_chapter_draft_path,
    parse_outline_volumes,
    parse_chapter_titles,
    get_volume_info,
    ensure_chapter_directory
)

def test_path_generation():
    """测试路径生成功能"""
    project_root = Path.cwd()

    print("=== 测试新的文件路径生成功能 ===\n")

    # 测试几个章节的路径生成
    test_chapters = [1, 25, 51, 100]

    for chapter_num in test_chapters:
        print(f"章节 {chapter_num}:")

        # 获取卷信息
        volume_info = get_volume_info(project_root, chapter_num)
        print(f"  卷号: {volume_info['volume_num']}")
        print(f"  卷名: {volume_info['volume_name'] or '(未设置)'}")
        print(f"  章名: {volume_info['chapter_title'] or '(未设置)'}")

        # 生成文件路径
        draft_path = default_chapter_draft_path(project_root, chapter_num)
        print(f"  文件路径: {draft_path}")

        # 显示目录结构
        print(f"  目录: {draft_path.parent}")
        print(f"  文件名: {draft_path.name}")
        print()

def test_outline_parsing():
    """测试大纲解析功能"""
    project_root = Path.cwd()

    print("=== 测试大纲解析功能 ===\n")

    # 解析卷名
    volume_names = parse_outline_volumes(project_root)
    print("解析到的卷名:")
    if volume_names:
        for vol_num, vol_name in volume_names.items():
            print(f"  第{vol_num}卷: {vol_name}")
    else:
        print("  (未找到卷名信息)")
    print()

    # 解析章节标题
    for vol_num in range(1, 4):  # 测试前3卷
        chapter_titles = parse_chapter_titles(project_root, vol_num)
        print(f"第{vol_num}卷的章节标题:")
        if chapter_titles:
            for ch_num, ch_title in list(chapter_titles.items())[:5]:  # 只显示前5章
                print(f"  第{ch_num}章: {ch_title}")
        else:
            print("  (未找到章节标题)")
        print()

if __name__ == "__main__":
    test_outline_parsing()
    test_path_generation()
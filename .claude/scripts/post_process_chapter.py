#!/usr/bin/env python3
"""
正文处理自动化脚本
在正文文件修改后自动调用chinese-quotes处理
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional, List

def process_chapter_quotes(chapter_file_path: str, project_root: Optional[str] = None) -> bool:
    """
    处理章节文件的中文引号修正

    Args:
        chapter_file_path: 章节文件路径
        project_root: 项目根目录（可选）

    Returns:
        bool: 处理是否成功
    """
    if project_root:
        # 确保使用项目根目录下的脚本
        script_path = Path(project_root) / ".claude" / "scripts" / "chinese_quotes.py"
    else:
        # 使用相对路径
        script_path = Path(__file__).parent / "chinese_quotes.py"

    if not script_path.exists():
        print(f"❌ 错误: 找不到 chinese_quotes.py 脚本: {script_path}")
        return False

    chapter_path = Path(chapter_file_path)
    if not chapter_path.exists():
        print(f"❌ 错误: 找不到章节文件: {chapter_file_path}")
        return False

    try:
        # 执行中文引号修正
        result = subprocess.run(
            [sys.executable, str(script_path), str(chapter_path)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            print(f"✅ 中文引号修正完成: {chapter_path.name}")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 中文引号修正失败: {chapter_path.name}")
            if result.stderr.strip():
                print(f"   错误: {result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"❌ 执行中文引号修正时出错: {e}")
        return False

def process_multiple_chapters(chapter_files: List[str], project_root: Optional[str] = None) -> int:
    """
    批量处理多个章节文件

    Args:
        chapter_files: 章节文件路径列表
        project_root: 项目根目录（可选）

    Returns:
        int: 成功处理的文件数量
    """
    success_count = 0

    print(f"📝 开始处理 {len(chapter_files)} 个章节文件...")

    for chapter_file in chapter_files:
        if process_chapter_quotes(chapter_file, project_root):
            success_count += 1

    print(f"✅ 完成处理，成功: {success_count}/{len(chapter_files)}")
    return success_count

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python post_process_chapter.py <章节文件路径> [项目根目录]")
        print("示例: python post_process_chapter.py '正文/第1卷：修炼之路/第001章：初入宗门.md'")
        sys.exit(1)

    chapter_file = sys.argv[1]
    project_root = sys.argv[2] if len(sys.argv) > 2 else None

    success = process_chapter_quotes(chapter_file, project_root)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
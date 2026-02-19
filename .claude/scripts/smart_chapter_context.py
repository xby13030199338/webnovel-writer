#!/usr/bin/env python3
"""
智能章节上下文提取器
自动选择最佳的上下文提取方案
"""

import subprocess
import sys
from pathlib import Path

def run_extract_chapter_context(chapter_num: int, project_root: str, output_format: str = "json"):
    """
    智能运行章节上下文提取

    Args:
        chapter_num: 章节号
        project_root: 项目根目录
        output_format: 输出格式 (json/text)

    Returns:
        bool: 是否成功
    """
    script_dir = Path(__file__).parent
    main_script = script_dir / "extract_chapter_context.py"
    fallback_script = script_dir / "fallback_chapter_context.py"

    # 方案1: 尝试主要脚本
    try:
        print("🔄 尝试完整版章节上下文提取...", file=sys.stderr)
        result = subprocess.run(
            [sys.executable, str(main_script),
             "--chapter", str(chapter_num),
             "--project-root", project_root,
             "--format", output_format],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            print("✅ 完整版提取成功", file=sys.stderr)
            print(result.stdout)
            return True
        else:
            print(f"⚠️  完整版提取失败: {result.stderr.strip()}", file=sys.stderr)

    except Exception as e:
        print(f"⚠️  完整版提取异常: {e}", file=sys.stderr)

    # 方案2: 使用备用脚本
    try:
        print("🔄 使用简化版章节上下文...", file=sys.stderr)
        result = subprocess.run(
            [sys.executable, str(fallback_script),
             str(chapter_num), project_root, output_format],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            print("✅ 简化版提取成功", file=sys.stderr)
            print(result.stdout)
            return True
        else:
            print(f"❌ 简化版提取失败: {result.stderr.strip()}", file=sys.stderr)

    except Exception as e:
        print(f"❌ 简化版提取异常: {e}", file=sys.stderr)

    return False

def main():
    """命令行入口"""
    if len(sys.argv) < 4:
        print("用法: python smart_chapter_context.py <章节号> <项目根目录> <格式>")
        print("示例: python smart_chapter_context.py 1 . json")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    project_root = sys.argv[2]
    output_format = sys.argv[3]

    success = run_extract_chapter_context(chapter_num, project_root, output_format)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
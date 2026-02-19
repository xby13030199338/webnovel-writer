#!/usr/bin/env python3
"""
测试extract_chapter_context.py的兼容性问题
"""

import sys
import traceback
from pathlib import Path

def test_import():
    """测试导入模块"""
    try:
        from pathlib import Path as PathLib
        sys.path.insert(0, str(PathLib(__file__).parent))

        # 逐步导入测试
        print("测试基础导入...")
        import argparse
        import json
        import re
        from pathlib import Path
        from typing import Any, Dict, List, Optional
        print("✓ 基础模块导入成功")

        print("测试runtime_compat导入...")
        from runtime_compat import enable_windows_utf8_stdio
        print("✓ runtime_compat导入成功")

        print("测试chapter_paths导入...")
        try:
            from chapter_paths import find_chapter_file
            print("✓ chapter_paths导入成功")
        except ImportError:
            from scripts.chapter_paths import find_chapter_file
            print("✓ scripts.chapter_paths导入成功")

        print("测试extract_chapter_context导入...")
        import extract_chapter_context
        print("✓ extract_chapter_context导入成功")

        return True

    except Exception as e:
        print(f"❌ 导入失败: {e}")
        traceback.print_exc()
        return False

def test_function_call():
    """测试函数调用"""
    try:
        import extract_chapter_context

        print("测试find_project_root函数...")
        project_root = extract_chapter_context.find_project_root(Path.cwd())
        print(f"✓ find_project_root成功: {project_root}")

        return True

    except Exception as e:
        print(f"❌ 函数调用失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Python版本兼容性测试 ===")
    print(f"Python版本: {sys.version}")

    if test_import():
        test_function_call()
    else:
        print("导入测试失败，跳过函数测试")
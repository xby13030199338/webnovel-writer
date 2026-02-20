#!/usr/bin/env python3
"""
Step 1.5 章节设计的简化实现
当extract_chapter_context.py无法运行时的备用方案
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from project_locator import resolve_project_root

def create_fallback_chapter_context(chapter_num: int, project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    创建备用的章节上下文，当extract_chapter_context.py无法运行时使用

    Args:
        chapter_num: 章节号
        project_root: 项目根目录

    Returns:
        Dict: 章节上下文数据
    """
    if project_root is None:
        project_root = resolve_project_root()

    # 基础上下文结构
    context = {
        "chapter": chapter_num,
        "project_root": str(project_root),
        "outline_snippet": f"第{chapter_num}章的大纲内容（请从大纲文件中手动获取）",
        "previous_summaries": [],
        "state_summary": {
            "protagonist_state": {
                "name": "主角名称（请从设定中获取）",
                "current_realm": "当前境界（请从设定中获取）",
                "location": "当前位置（请从设定中获取）"
            },
            "progress": {
                "current_chapter": chapter_num,
                "current_volume": (chapter_num - 1) // 50 + 1
            }
        },
        "reader_signal": {
            "target_emotion": "期待",
            "pacing_preference": "medium",
            "hook_strength": "medium"
        },
        "genre_profile": {
            "primary_genre": "修仙",
            "reference_hints": [
                "注重境界提升的合理性",
                "保持战斗场面的紧张感",
                "适当展示修炼成果"
            ]
        },
        "writing_guidance": {
            "guidance_items": [
                {
                    "type": "hook_design",
                    "content": "章末设置悬念或冲突钩子",
                    "priority": "high"
                },
                {
                    "type": "pacing",
                    "content": "保持适中的信息密度",
                    "priority": "medium"
                },
                {
                    "type": "character_development",
                    "content": "展现主角的成长或变化",
                    "priority": "medium"
                }
            ]
        }
    }

    return context

def render_fallback_context_text(context: Dict[str, Any]) -> str:
    """
    将备用上下文渲染为文本格式

    Args:
        context: 上下文数据

    Returns:
        str: 格式化的文本
    """
    chapter_num = context["chapter"]
    lines = [
        f"# 第 {chapter_num} 章创作上下文（简化版）",
        "",
        "## 章节信息",
        f"- 章节号: {chapter_num}",
        f"- 卷号: {context['state_summary']['progress']['current_volume']}",
        "",
        "## 大纲片段",
        context["outline_snippet"],
        "",
        "## 主角状态",
        f"- 姓名: {context['state_summary']['protagonist_state']['name']}",
        f"- 境界: {context['state_summary']['protagonist_state']['current_realm']}",
        f"- 位置: {context['state_summary']['protagonist_state']['location']}",
        "",
        "## 写作指导",
    ]

    for item in context["writing_guidance"]["guidance_items"]:
        lines.append(f"- {item['content']} (优先级: {item['priority']})")

    lines.extend([
        "",
        "## 题材提示",
    ])

    for hint in context["genre_profile"]["reference_hints"]:
        lines.append(f"- {hint}")

    lines.extend([
        "",
        "## 注意事项",
        "- 这是简化版上下文，请根据实际项目情况调整",
        "- 建议运行 /webnovel-init 初始化完整项目",
        "- 完整功能需要 .webnovel 目录和相关配置文件"
    ])

    return "\n".join(lines)

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python fallback_chapter_context.py <章节号> [项目根目录] [格式]")
        print("示例: python fallback_chapter_context.py 1 . text")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    project_root = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    output_format = sys.argv[3] if len(sys.argv) > 3 else "text"

    context = create_fallback_chapter_context(chapter_num, project_root)

    if output_format == "json":
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print(render_fallback_context_text(context))

if __name__ == "__main__":
    main()

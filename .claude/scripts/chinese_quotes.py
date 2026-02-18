#!/usr/bin/env python3
"""
chinese_quotes.py - 将中文语境中的英文双引号替换为中文双引号

用法：
    python chinese_quotes.py <文件路径> [文件路径2 ...]
    python chinese_quotes.py --dry-run <文件路径>

规则：
    - .json / .yaml / .yml 文件整体跳过
    - Markdown 代码块（``` 包裹）内的引号跳过
    - 行内代码（` 包裹）内的引号跳过
    - 英文双引号数量为奇数时，跳过该文件并警告
"""

import sys
import re
from pathlib import Path


SKIP_EXTENSIONS = {".json", ".yaml", ".yml"}


def replace_quotes_in_text(text: str):
    """
    替换文本中非代码区域的英文双引号为中文双引号。
    返回 (替换后文本, 替换次数)。
    若英文双引号数量为奇数，抛出 ValueError。
    """
    # 先把代码块和行内代码提取出来，用占位符保护
    placeholders = {}
    counter = [0]

    def protect(m: re.Match) -> str:
        key = f"\x00PLACEHOLDER_{counter[0]}\x00"
        placeholders[key] = m.group(0)
        counter[0] += 1
        return key

    # 保护 ``` 代码块（含语言标识符，支持多行）
    protected = re.sub(r"```[\s\S]*?```", protect, text)
    # 保护行内代码
    protected = re.sub(r"`[^`\n]+`", protect, protected)

    # 统计剩余英文双引号数量
    quote_count = protected.count('"')
    if quote_count % 2 != 0:
        raise ValueError(f"英文双引号数量为奇数（{quote_count}个）")

    # 替换：奇数位 → "，偶数位 → "
    result = []
    idx = 0
    replace_count = 0
    i = 0
    while i < len(protected):
        if protected[i] == '"':
            if idx % 2 == 0:
                result.append('\u201c')  # "
            else:
                result.append('\u201d')  # "
            idx += 1
            replace_count += 1
        else:
            result.append(protected[i])
        i += 1

    replaced = "".join(result)

    # 还原占位符
    for key, original in placeholders.items():
        replaced = replaced.replace(key, original)

    return replaced, replace_count // 2  # 每对算1处


def process_file(path: Path, dry_run: bool = False) -> None:
    if path.suffix.lower() in SKIP_EXTENSIONS:
        print(f"⏭  {path} — 跳过（{path.suffix} 文件）")
        return

    text = path.read_text(encoding="utf-8")

    try:
        new_text, count = replace_quotes_in_text(text)
    except ValueError as e:
        print(f"⚠  {path} — {e}，已跳过")
        return

    if count == 0:
        print(f"✓  {path} — 0 处需替换（无英文双引号）")
        return

    if dry_run:
        print(f"[dry-run] {path} — 将替换 {count} 处")
        return

    path.write_text(new_text, encoding="utf-8")
    print(f"✓  {path} — 替换 {count} 处")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("用法：python chinese_quotes.py [--dry-run] <文件路径> ...")
        sys.exit(1)

    dry_run = False
    if args[0] == "--dry-run":
        dry_run = True
        args = args[1:]

    if not args:
        print("错误：未指定文件路径")
        sys.exit(1)

    for arg in args:
        path = Path(arg)
        if not path.exists():
            print(f"✗  {path} — 文件不存在")
            continue
        if not path.is_file():
            print(f"✗  {path} — 不是文件")
            continue
        process_file(path, dry_run=dry_run)


if __name__ == "__main__":
    main()

---
name: chinese-quotes
description: 将文本中的英文双引号替换为中文双引号（"" → “”）。在中文语境下使用，代码块/JSON/YAML 内容除外。
allowed-tools: Read Write Edit Bash Grep Glob
---

# /chinese-quotes

## 功能

将指定文件或文本中的英文双引号 `""` 替换为中文双引号 `“”`，仅处理中文语境内容，跳过代码块、JSON、YAML 语法。

## 用法

```
/chinese-quotes <文件路径>
/chinese-quotes <文件路径1> <文件路径2> ...
```

## 执行流程

调用脚本处理：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/chinese_quotes.py" <文件路径> [文件路径2 ...]
```

dry-run 模式（只预览，不修改）：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/chinese_quotes.py" --dry-run <文件路径>
```

脚本规则：
1. `.json` / `.yaml` / `.yml` 文件整体跳过
2. Markdown 代码块（\`\`\` 包裹）内的引号跳过
3. 行内代码（\` 包裹）内的引号跳过
4. 英文双引号数量为奇数时，跳过并警告
5. 替换规则：第奇数个 `"` → `“`，第偶数个 `"` → `”`

## 约束

- `.json` / `.yaml` / `.yml` 文件整体跳过，不做任何修改
- 代码块内的引号不替换
- 若文件中英文双引号数量为奇数，输出警告并跳过该文件
- 仅处理用户明确指定的文件，不递归扫描目录（除非用户明确要求）

## 输出示例

```
✓ 正文/第1卷：修炼之路/第001章：初入宗门.md — 替换 12 处
✓ 设定集/人物设定.md — 替换 3 处
⚠ 正文/第1卷：修炼之路/第002章：遇见师姐.md — 英文双引号数量为奇数（7个），已跳过
```

**注意**: 支持多种文件路径格式，包括新的卷目录结构和旧的平坦结构。

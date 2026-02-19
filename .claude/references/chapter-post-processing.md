# 正文处理自动化指南

## 核心原则

**每次涉及正文生成或修改后，必须执行中文引号修正处理。**

## 自动化集成点

### 1. webnovel-write 流程
- **Step 4.5**: 中文引号修正（强制执行）
- **位置**: 润色完成后，Data Agent 前
- **脚本**: `chinese_quotes.py`

### 2. webnovel-review 流程
- **Step 6**: 中文引号修正（强制执行）
- **位置**: 修复完成后
- **条件**: 仅当选择立即修复时执行

### 3. webnovel-resume 流程
- **恢复润色**: 继续润色后必须执行
- **重新生成**: 自动在 Step 4.5 执行

## 使用方法

### 方法1: 直接调用脚本
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/chinese_quotes.py" "{chapter_file_path}"
```

### 方法2: 使用自动化脚本
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/post_process_chapter.py" "{chapter_file_path}" "{project_root}"
```

### 方法3: 使用 Skill 工具
```
调用 chinese-quotes skill，参数：
- 文件路径: {chapter_file_path}
```

## 执行确认

每次执行后必须显示处理结果：
- ✅ 成功: `✓ 正文/第x卷：卷名/第x章：章名.md — 替换 X 处`
- ⚠️ 警告: `⚠ 文件名 — 英文双引号数量为奇数（X个），已跳过`
- ❌ 错误: 显示具体错误信息

## 强制执行场景

以下场景必须执行中文引号修正：

1. **新章节生成** (webnovel-write)
2. **章节润色修复** (webnovel-review)
3. **恢复润色工作** (webnovel-resume)
4. **手动编辑正文后**
5. **任何正文内容变更后**

## 跳过条件

仅在以下情况可跳过：
- webnovel-review 选择"仅保存报告"
- 明确知道文件未包含中文内容
- 文件为非正文文件（如设定集、大纲等）

## 错误处理

如果中文引号修正失败：
1. 检查文件路径是否正确
2. 检查文件是否存在
3. 检查文件权限
4. 查看具体错误信息
5. 必要时手动执行修正

## 注意事项

- 代码块、JSON、YAML 内容会自动跳过
- 英文双引号数量为奇数的文件会被跳过并警告
- 处理结果必须确认，确保步骤完成
- 支持多种文件路径格式（新格式和旧格式）
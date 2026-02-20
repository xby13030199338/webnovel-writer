#!/usr/bin/env python3
"""
Project location helpers for webnovel-writer scripts.

Problem this solves:
- Many scripts assumed CWD is the project root and used relative paths like `.webnovel/state.json`.
- In this repo, commands/scripts are often invoked from the repo root, while the actual project lives
  in a subdirectory (default: `webnovel-project/`).

These helpers provide a single, consistent way to locate the active project root.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence


DEFAULT_PROJECT_DIR_NAMES: tuple[str, ...] = ("webnovel-project",)
DEFAULT_SCAN_SKIP_DIRS: tuple[str, ...] = (
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".omx",
    ".claude",
)


def _find_git_root(cwd: Path) -> Optional[Path]:
    """Return nearest git root for cwd, if any."""
    for candidate in (cwd, *cwd.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _candidate_roots(cwd: Path, *, stop_at: Optional[Path] = None) -> Iterable[Path]:
    yield cwd
    for name in DEFAULT_PROJECT_DIR_NAMES:
        yield cwd / name

    for parent in cwd.parents:
        yield parent
        for name in DEFAULT_PROJECT_DIR_NAMES:
            yield parent / name
        if stop_at is not None and parent == stop_at:
            break


def _is_project_root(path: Path) -> bool:
    return (path / ".webnovel" / "state.json").is_file()


def _stdin_is_tty() -> bool:
    try:
        return bool(sys.stdin.isatty())
    except Exception:
        return False


def _unique_paths(paths: Iterable[Path]) -> List[Path]:
    results: List[Path] = []
    seen: set[str] = set()
    for path in paths:
        normalized = str(path.resolve())
        if normalized in seen:
            continue
        seen.add(normalized)
        results.append(path.resolve())
    return results


def _scan_root_for_projects(search_root: Path, *, max_depth: int = 3, max_results: int = 20) -> List[Path]:
    found: List[Path] = []
    if not search_root.exists() or not search_root.is_dir():
        return found

    for current_dir, dir_names, _ in os.walk(search_root, topdown=True):
        current_path = Path(current_dir)

        try:
            depth = len(current_path.relative_to(search_root).parts)
        except Exception:
            depth = max_depth + 1

        if depth > max_depth:
            dir_names[:] = []
            continue

        dir_names[:] = [
            name
            for name in dir_names
            if name not in DEFAULT_SCAN_SKIP_DIRS and not name.startswith(".")
        ]

        if _is_project_root(current_path):
            found.append(current_path.resolve())
            if len(found) >= max_results:
                break
            dir_names[:] = []

        if depth >= max_depth:
            dir_names[:] = []

    return _unique_paths(found)


def discover_project_roots(
    *,
    cwd: Optional[Path] = None,
    max_depth: int = 3,
    max_results: int = 20,
) -> List[Path]:
    """
    Discover candidate project roots (directories containing `.webnovel/state.json`).

    Search scope (ordered):
    1) cwd
    2) cwd.parent
    3) git_root.parent (when cwd is inside a git repo)
    """
    base = (cwd or Path.cwd()).resolve()
    git_root = _find_git_root(base)

    anchors: List[Path] = [base]
    if base.parent != base:
        anchors.append(base.parent)
    if git_root is not None and git_root.parent != git_root:
        anchors.append(git_root.parent)

    found: List[Path] = []
    for anchor in _unique_paths(anchors):
        remaining = max_results - len(found)
        if remaining <= 0:
            break
        found.extend(_scan_root_for_projects(anchor, max_depth=max_depth, max_results=remaining))

    unique = _unique_paths(found)[:max_results]
    return sorted(unique, key=lambda p: str(p))


def _choose_project_root_interactive(
    candidates: Sequence[Path],
    *,
    input_func: Callable[[str], str] = input,
    output_stream=None,
    max_attempts: int = 3,
) -> Optional[Path]:
    stream = output_stream or sys.stderr
    print("检测到多个小说项目，请选择：", file=stream)
    for idx, candidate in enumerate(candidates, start=1):
        print(f"  [{idx}] {candidate}", file=stream)

    for _ in range(max_attempts):
        raw = (input_func(f"请输入编号 [1-{len(candidates)}]（回车默认 1）: ") or "").strip()
        if raw == "":
            return candidates[0]
        if raw.isdigit():
            selected_idx = int(raw)
            if 1 <= selected_idx <= len(candidates):
                return candidates[selected_idx - 1]
        print("输入无效，请重新输入编号。", file=stream)
    return None


def _format_candidates(candidates: Sequence[Path]) -> str:
    return "\n".join(f"  - {candidate}" for candidate in candidates)


def resolve_project_root(
    explicit_project_root: Optional[str] = None,
    *,
    cwd: Optional[Path] = None,
    selection_mode: str = "auto",
    input_func: Callable[[str], str] = input,
    output_stream=None,
) -> Path:
    """
    Resolve the webnovel project root directory (the directory containing `.webnovel/state.json`).

    Resolution order:
    1) explicit_project_root (if provided)
    2) env var WEBNOVEL_PROJECT_ROOT (if set)
    3) Search from cwd and parents, including common subdir `webnovel-project/`
    4) If still not found, discover nearby candidates and resolve ambiguity

    Search safety:
    - If current location is inside a Git repo, parent search stops at the repo root.
      This avoids accidentally binding to unrelated parent directories.
    - Discovery phase scans nearby anchors (cwd / parent / git_root.parent) with depth limit,
      and handles multi-project ambiguity explicitly.

    Args:
        selection_mode:
            - "auto": 多候选时，TTY 环境交互选择；非 TTY 抛错
            - "interactive": 强制交互选择
            - "error": 多候选直接抛错

    Raises:
        FileNotFoundError: if no valid project root can be found or selection is ambiguous.
    """
    if selection_mode not in {"auto", "interactive", "error"}:
        raise ValueError(f"Unsupported selection_mode: {selection_mode}")

    if explicit_project_root:
        root = Path(explicit_project_root).expanduser().resolve()
        if _is_project_root(root):
            return root
        raise FileNotFoundError(f"Not a webnovel project root (missing .webnovel/state.json): {root}")

    env_root = os.environ.get("WEBNOVEL_PROJECT_ROOT")
    if env_root:
        root = Path(env_root).expanduser().resolve()
        if _is_project_root(root):
            return root
        raise FileNotFoundError(f"WEBNOVEL_PROJECT_ROOT is set but invalid (missing .webnovel/state.json): {root}")

    base = (cwd or Path.cwd()).resolve()
    git_root = _find_git_root(base)
    for candidate in _candidate_roots(base, stop_at=git_root):
        if _is_project_root(candidate):
            return candidate.resolve()

    discovered = discover_project_roots(cwd=base, max_depth=3, max_results=20)
    if len(discovered) == 1:
        return discovered[0]
    if len(discovered) > 1:
        should_interactive = selection_mode == "interactive" or (
            selection_mode == "auto" and _stdin_is_tty()
        )
        if should_interactive:
            selected = _choose_project_root_interactive(
                discovered,
                input_func=input_func,
                output_stream=output_stream,
            )
            if selected is not None:
                return selected.resolve()
            raise FileNotFoundError(
                "Multiple webnovel projects found but no valid selection was made.\n"
                f"Candidates:\n{_format_candidates(discovered)}\n"
                "Use --project-root or set WEBNOVEL_PROJECT_ROOT."
            )

        raise FileNotFoundError(
            "Multiple webnovel projects found. Please specify one with --project-root "
            "or WEBNOVEL_PROJECT_ROOT.\n"
            f"Candidates:\n{_format_candidates(discovered)}"
        )

    raise FileNotFoundError(
        "Unable to locate webnovel project root. Expected `.webnovel/state.json` under the current directory, "
        "a parent directory, or `webnovel-project/`. Run /webnovel-init first or pass --project-root / set "
        "WEBNOVEL_PROJECT_ROOT."
    )


def resolve_state_file(
    explicit_state_file: Optional[str] = None,
    *,
    explicit_project_root: Optional[str] = None,
    cwd: Optional[Path] = None,
    selection_mode: str = "auto",
    input_func: Callable[[str], str] = input,
    output_stream=None,
) -> Path:
    """
    Resolve `.webnovel/state.json` path.

    If explicit_state_file is provided, returns it as-is (resolved to absolute if relative).
    Otherwise derives it from resolve_project_root().
    """
    base = (cwd or Path.cwd()).resolve()
    if explicit_state_file:
        p = Path(explicit_state_file).expanduser()
        return (base / p).resolve() if not p.is_absolute() else p.resolve()

    root = resolve_project_root(
        explicit_project_root,
        cwd=base,
        selection_mode=selection_mode,
        input_func=input_func,
        output_stream=output_stream,
    )
    return root / ".webnovel" / "state.json"

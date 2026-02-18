#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_api.py - 检测 Embedding / Rerank API 可用性

用法：
    python3 check_api.py                  # 检测两个 API
    python3 check_api.py --embed-only     # 只检测 Embedding
    python3 check_api.py --rerank-only    # 只检测 Rerank
    python3 check_api.py --env-file PATH  # 指定 .env 文件路径（默认当前目录）

退出码：
    0  全部通过
    1  有 API 未配置或不可用
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path


# ─── .env 读写 ────────────────────────────────────────────────────────────────

def load_env(env_path: Path) -> dict:
    result = {}
    if not env_path.exists():
        return result
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                result[k.strip()] = v.strip()
    return result


def save_env(env_path: Path, updates: dict):
    """将 updates 中的 key 写入 .env，已存在的 key 更新，不存在的追加。"""
    lines = []
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            lines = f.readlines()

    existing_keys = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _, _ = stripped.partition("=")
            existing_keys[k.strip()] = i

    for k, v in updates.items():
        if k in existing_keys:
            lines[existing_keys[k]] = f"{k}={v}\n"
        else:
            lines.append(f"{k}={v}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


# ─── API 测试 ─────────────────────────────────────────────────────────────────

def test_embed(base_url: str, api_key: str, model: str) -> tuple:
    """返回 (ok: bool, message: str)"""
    url = base_url.rstrip("/")
    if not url.endswith("/embeddings"):
        url = url + ("/embeddings" if url.endswith("/v1") else "/v1/embeddings")

    payload = json.dumps({"model": model, "input": ["测试"]}).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            if "data" in body and body["data"]:
                dim = len(body["data"][0].get("embedding", []))
                return True, f"OK（向量维度 {dim}）"
            return False, f"响应格式异常：{body}"
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return False, f"HTTP {e.code}：{body[:200]}"
    except Exception as e:
        return False, str(e)


def test_rerank(base_url: str, api_key: str, model: str) -> tuple:
    """返回 (ok: bool, message: str)"""
    url = base_url.rstrip("/")
    if not url.endswith("/rerank"):
        url = url + ("/rerank" if url.endswith("/v1") else "/v1/rerank")

    payload = json.dumps({
        "model": model,
        "query": "测试查询",
        "documents": ["文档一", "文档二"],
        "top_n": 2,
    }).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            if "results" in body:
                return True, f"OK（返回 {len(body['results'])} 条结果）"
            return False, f"响应格式异常：{body}"
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return False, f"HTTP {e.code}：{body[:200]}"
    except Exception as e:
        return False, str(e)


# ─── 交互引导 ─────────────────────────────────────────────────────────────────

def prompt(msg: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{msg}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(1)
    return val if val else default


def guide_embed(env_path: Path, env_vars: dict) -> dict:
    """引导用户配置 Embedding API，返回更新后的配置 dict。"""
    print("\n── Embedding API 配置 ──────────────────────────────")
    print("推荐服务：ModelScope（免费）/ OpenAI / 自部署 vLLM")
    print("默认模型：Qwen/Qwen3-Embedding-8B（ModelScope）\n")

    base_url = prompt(
        "EMBED_BASE_URL",
        env_vars.get("EMBED_BASE_URL", "https://api-inference.modelscope.cn/v1"),
    )
    model = prompt(
        "EMBED_MODEL",
        env_vars.get("EMBED_MODEL", "Qwen/Qwen3-Embedding-8B"),
    )
    api_key = prompt("EMBED_API_KEY（无则留空）", env_vars.get("EMBED_API_KEY", ""))

    updates = {"EMBED_BASE_URL": base_url, "EMBED_MODEL": model, "EMBED_API_KEY": api_key}
    save_env(env_path, updates)
    print(f"已写入 {env_path}")
    return updates


def guide_rerank(env_path: Path, env_vars: dict) -> dict:
    """引导用户配置 Rerank API，返回更新后的配置 dict。"""
    print("\n── Rerank API 配置 ─────────────────────────────────")
    print("推荐服务：Jina AI（免费额度）/ Cohere / 自部署")
    print("默认模型：jina-reranker-v3（Jina AI）\n")

    base_url = prompt(
        "RERANK_BASE_URL",
        env_vars.get("RERANK_BASE_URL", "https://api.jina.ai/v1"),
    )
    model = prompt(
        "RERANK_MODEL",
        env_vars.get("RERANK_MODEL", "jina-reranker-v3"),
    )
    api_key = prompt("RERANK_API_KEY（无则留空）", env_vars.get("RERANK_API_KEY", ""))

    updates = {"RERANK_BASE_URL": base_url, "RERANK_MODEL": model, "RERANK_API_KEY": api_key}
    save_env(env_path, updates)
    print(f"已写入 {env_path}")
    return updates


# ─── 主流程 ───────────────────────────────────────────────────────────────────

def check_one(name: str, env_key: str, env_vars: dict) -> bool:
    """检查单个 API 的 key 是否已配置（非空）。"""
    val = env_vars.get(env_key) or os.getenv(env_key, "")
    return bool(val.strip())


def run(args):
    env_path = Path(args.env_file)
    env_vars = load_env(env_path)

    # 合并环境变量（os.environ 优先）
    for k in ("EMBED_BASE_URL", "EMBED_MODEL", "EMBED_API_KEY",
              "RERANK_BASE_URL", "RERANK_MODEL", "RERANK_API_KEY"):
        if k in os.environ:
            env_vars[k] = os.environ[k]

    do_embed = not args.rerank_only
    do_rerank = not args.embed_only

    all_ok = True

    # ── Embedding ──
    if do_embed:
        print("\n[Embedding API]")
        key_ok = bool(env_vars.get("EMBED_API_KEY", "").strip())
        if not key_ok:
            print("  ⚠  EMBED_API_KEY 未配置")
            ans = prompt("  是否现在配置？(y/n)", "y")
            if ans.lower() == "y":
                new_cfg = guide_embed(env_path, env_vars)
                env_vars.update(new_cfg)
            else:
                print("  跳过 Embedding 配置，向量检索将降级为 BM25。")
                all_ok = False

        if env_vars.get("EMBED_API_KEY", "").strip():
            print("  正在测试连通性…", end=" ", flush=True)
            ok, msg = test_embed(
                env_vars.get("EMBED_BASE_URL", "https://api-inference.modelscope.cn/v1"),
                env_vars.get("EMBED_API_KEY", ""),
                env_vars.get("EMBED_MODEL", "Qwen/Qwen3-Embedding-8B"),
            )
            if ok:
                print(f"✓  {msg}")
            else:
                print(f"✗  {msg}")
                all_ok = False

    # ── Rerank ──
    if do_rerank:
        print("\n[Rerank API]")
        key_ok = bool(env_vars.get("RERANK_API_KEY", "").strip())
        if not key_ok:
            print("  ⚠  RERANK_API_KEY 未配置")
            ans = prompt("  是否现在配置？(y/n)", "y")
            if ans.lower() == "y":
                new_cfg = guide_rerank(env_path, env_vars)
                env_vars.update(new_cfg)
            else:
                print("  跳过 Rerank 配置，混合检索将降级为 RRF 融合。")
                all_ok = False

        if env_vars.get("RERANK_API_KEY", "").strip():
            print("  正在测试连通性…", end=" ", flush=True)
            ok, msg = test_rerank(
                env_vars.get("RERANK_BASE_URL", "https://api.jina.ai/v1"),
                env_vars.get("RERANK_API_KEY", ""),
                env_vars.get("RERANK_MODEL", "jina-reranker-v3"),
            )
            if ok:
                print(f"✓  {msg}")
            else:
                print(f"✗  {msg}")
                all_ok = False

    print()
    if all_ok:
        print("✓  API 检测完成，所有配置项通过。")
    else:
        print("⚠  部分 API 未配置或不可用，向量/精排功能将降级，核心写作流程不受影响。")

    return 0 if all_ok else 1


def main():
    parser = argparse.ArgumentParser(description="检测 Embedding / Rerank API 可用性")
    parser.add_argument("--embed-only", action="store_true", help="只检测 Embedding API")
    parser.add_argument("--rerank-only", action="store_true", help="只检测 Rerank API")
    parser.add_argument("--env-file", default=".env", help=".env 文件路径（默认当前目录）")
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()

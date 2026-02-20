#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Modules - 数据链模块包

用于 webnovel-writer 的数据处理：
- 实体消歧 (entity_linker)
- 状态管理 (state_manager)
- 索引管理 (index_manager)
- RAG 检索 (rag_adapter)
- 风格样本 (style_sampler)
- API 客户端 (api_client) - 只有 Embed + Rerank
"""

from importlib import import_module
from typing import Dict, Tuple

from .config import DataModulesConfig, get_config, set_project_root


_LAZY_ATTRS: Dict[str, Tuple[str, str]] = {
    # API Client
    "ModalAPIClient": (".api_client", "ModalAPIClient"),
    "get_client": (".api_client", "get_client"),
    # Entity Linker
    "EntityLinker": (".entity_linker", "EntityLinker"),
    "DisambiguationResult": (".entity_linker", "DisambiguationResult"),
    # State Manager
    "StateManager": (".state_manager", "StateManager"),
    "EntityState": (".state_manager", "EntityState"),
    "Relationship": (".state_manager", "Relationship"),
    "StateChange": (".state_manager", "StateChange"),
    # Index Manager
    "IndexManager": (".index_manager", "IndexManager"),
    "ChapterMeta": (".index_manager", "ChapterMeta"),
    "SceneMeta": (".index_manager", "SceneMeta"),
    "ReviewMetrics": (".index_manager", "ReviewMetrics"),
    # RAG Adapter
    "RAGAdapter": (".rag_adapter", "RAGAdapter"),
    "SearchResult": (".rag_adapter", "SearchResult"),
    # Context helpers
    "ContextManager": (".context_manager", "ContextManager"),
    "ContextRanker": (".context_ranker", "ContextRanker"),
    "SnapshotManager": (".snapshot_manager", "SnapshotManager"),
    "QueryRouter": (".query_router", "QueryRouter"),
    # Style Sampler
    "StyleSampler": (".style_sampler", "StyleSampler"),
    "StyleSample": (".style_sampler", "StyleSample"),
    "SceneType": (".style_sampler", "SceneType"),
}


def __getattr__(name: str):
    target = _LAZY_ATTRS.get(name)
    if target is None:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    module_name, attr_name = target
    module = import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_LAZY_ATTRS))

__all__ = [
    # Config
    "DataModulesConfig",
    "get_config",
    "set_project_root",
    # API Client
    "ModalAPIClient",
    "get_client",
    # Entity Linker
    "EntityLinker",
    "DisambiguationResult",
    # State Manager
    "StateManager",
    "EntityState",
    "Relationship",
    "StateChange",
    # Index Manager
    "IndexManager",
    "ChapterMeta",
    "SceneMeta",
    "ReviewMetrics",
    # RAG Adapter
    "RAGAdapter",
    "SearchResult",
    "ContextManager",
    "ContextRanker",
    "SnapshotManager",
    "QueryRouter",
    # Style Sampler
    "StyleSampler",
    "StyleSample",
    "SceneType",
]

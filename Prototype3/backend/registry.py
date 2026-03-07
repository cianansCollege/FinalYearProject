# In-memory registry for model plugin instances and model metadata listing.

from __future__ import annotations

from typing import Dict

from plugins.base import ModelPlugin


_REGISTRY: Dict[str, ModelPlugin] = {}


def register(plugin: ModelPlugin) -> None:
    if plugin.id in _REGISTRY:
        raise ValueError(f"Duplicate model id: {plugin.id}")
    _REGISTRY[plugin.id] = plugin


def get_model(model_id: str) -> ModelPlugin:
    if model_id not in _REGISTRY:
        raise KeyError(f"Unknown model_id: {model_id}")
    return _REGISTRY[model_id]


def list_models() -> list[dict]:
    return [
        {
            "id": plugin.id,
            "name": plugin.name,
            "description": plugin.description,
        }
        for plugin in _REGISTRY.values()
    ]

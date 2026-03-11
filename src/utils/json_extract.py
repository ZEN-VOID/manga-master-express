"""
LLM输出JSON提取与实体解析工具
"""

import re
import json
import logging
from typing import List, Optional

from graphs.state import DesignEntity

logger = logging.getLogger(__name__)


def extract_json_from_llm_output(text: str) -> dict:
    """从LLM输出中提取JSON对象，兼容```json代码块和裸JSON"""
    json_match = re.search(r'```json\s*(.*?)```', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1).strip())

    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        return json.loads(text[start:end + 1])

    raise ValueError("LLM输出中未找到有效JSON")


def extract_entities_from_design(
    data: dict,
    entity_type: str
) -> List[DesignEntity]:
    """从编排JSON中提取实体列表，优先使用B阶段prompt作为生图提示词"""
    stage_a = data.get("stage_a", {})
    stage_b = data.get("stage_b", {})

    id_key, name_key = _get_keys_for_type(entity_type)

    name_lookup = {}
    for item in stage_a.get(_get_a_list_key(entity_type), []):
        name_lookup[item.get(id_key, "")] = item.get(name_key, "")

    entities: List[DesignEntity] = []
    for prompt_item in stage_b.get("prompts", []):
        eid = prompt_item.get(id_key, "")
        if not eid:
            continue
        ename = name_lookup.get(eid, eid)[:50]
        entities.append(DesignEntity(
            entity_id=eid,
            entity_name=ename,
            entity_type=entity_type,
            prompt=prompt_item.get("prompt_en", ""),
            aspect_ratio=prompt_item.get("aspect_ratio", "16:9"),
            image_size=prompt_item.get("image_size", "4K" if entity_type == "scene" else "2K")
        ))

    return entities


def _get_keys_for_type(entity_type: str):
    mapping = {
        "scene": ("scene_id", "scene_name"),
        "character": ("character_id", "character_name"),
        "prop": ("prop_id", "prop_name"),
    }
    return mapping.get(entity_type, ("entity_id", "entity_name"))


def _get_a_list_key(entity_type: str) -> str:
    mapping = {
        "scene": "scenes",
        "character": "characters",
        "prop": "props",
    }
    return mapping.get(entity_type, "items")

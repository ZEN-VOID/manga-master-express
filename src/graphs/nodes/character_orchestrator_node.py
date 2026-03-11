"""
角色全链路编排智能体节点
功能：A角色小传 -> B全身提示词 -> C角色面板合同（JSON输出，含实体列表）
"""

import os
import json
import logging
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from graphs.state import CharacterOrchestratorInput, CharacterOrchestratorOutput
from utils.json_extract import extract_json_from_llm_output, extract_entities_from_design

logger = logging.getLogger(__name__)


def character_orchestrator_node(
    state: CharacterOrchestratorInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CharacterOrchestratorOutput:
    """
    title: 角色全链路编排
    desc: 执行角色三阶段设计：A阶段角色小传、B阶段全身提示词设计、C阶段角色面板编排。输出JSON，直接含实体列表供生图消费。
    integrations: 大语言模型
    """
    ctx = runtime.context

    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", ""),
        "config/character_orchestrator_llm_cfg.json"
    )

    try:
        with open(cfg_file, 'r', encoding='utf-8') as fd:
            _cfg = json.load(fd)
    except Exception as e:
        return CharacterOrchestratorOutput(
            character_design="", character_entities=[],
            status="FAIL", message=f"配置文件加载失败: {str(e)}"
        )

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "project_name": state.project_name,
        "episode_no": state.episode_no,
        "structured_storyboard": state.video_script,
        "global_style": state.global_style_prompt
    })

    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]

    try:
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=llm_config.get("model", "doubao-seed-2-0-pro-260215"),
            temperature=llm_config.get("temperature", 0.4),
            top_p=llm_config.get("top_p", 0.9),
            max_completion_tokens=llm_config.get("max_completion_tokens", 32768)
        )

        content = response.content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            raw_text = "\n".join(text_parts)
        else:
            raw_text = str(content) if content else ""

        try:
            design_data = extract_json_from_llm_output(raw_text)
            entities = extract_entities_from_design(design_data, "character")
            design_json = json.dumps(design_data, ensure_ascii=False, indent=2)
        except Exception as parse_err:
            logger.warning(f"JSON解析失败，降级为原始文本: {parse_err}")
            design_json = raw_text
            entities = []

        return CharacterOrchestratorOutput(
            character_design=design_json,
            character_entities=entities,
            status="PASS",
            message=f"角色设计完成，提取{len(entities)}个实体"
        )

    except Exception as e:
        return CharacterOrchestratorOutput(
            character_design="", character_entities=[],
            status="FAIL", message=f"大模型调用失败: {str(e)}"
        )

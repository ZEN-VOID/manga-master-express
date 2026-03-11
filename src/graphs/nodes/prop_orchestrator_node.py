"""
道具全链路编排智能体节点
功能：A道具物语 -> B中文生图提示词 -> C道具面板合同（JSON输出，含实体列表）
"""

import json
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import PropOrchestratorInput, PropOrchestratorOutput
from utils.llm_invoke import invoke_llm
from utils.json_extract import extract_json_from_llm_output, extract_entities_from_design

logger = logging.getLogger(__name__)


def prop_orchestrator_node(
    state: PropOrchestratorInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> PropOrchestratorOutput:
    """
    title: 道具全链路编排
    desc: 执行道具三阶段设计：A阶段道具物语、B阶段中文生图提示词、C阶段道具面板编排。输出JSON，直接含实体列表供生图消费。
    integrations: 大语言模型
    """
    try:
        raw_text = invoke_llm(runtime.context, "config/prop_orchestrator_llm_cfg.json", {
            "project_name": state.project_name,
            "episode_no": state.episode_no,
            "storyboard_payload": state.video_script,
            "global_style": state.global_style_prompt
        })

        try:
            design_data = extract_json_from_llm_output(raw_text)
            entities = extract_entities_from_design(design_data, "prop")
            design_json = json.dumps(design_data, ensure_ascii=False, indent=2)
        except Exception as parse_err:
            logger.warning(f"JSON解析失败，降级为原始文本: {parse_err}")
            design_json = raw_text
            entities = []

        return PropOrchestratorOutput(
            prop_design=design_json,
            prop_entities=entities,
            status="PASS",
            message=f"道具设计完成，提取{len(entities)}个实体"
        )

    except Exception as e:
        return PropOrchestratorOutput(
            prop_design="", prop_entities=[],
            status="FAIL", message=f"道具设计失败: {str(e)}"
        )

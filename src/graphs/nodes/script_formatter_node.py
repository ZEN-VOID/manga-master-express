"""
剧本格式化编排智能体节点
功能：将输入内容（小说原文/剧本草稿/分镜构思）转换为结构化剧本JSON
"""

import json
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import ScriptFormatterInput, ScriptFormatterOutput
from utils.llm_invoke import invoke_llm
from utils.json_extract import extract_json_from_llm_output

logger = logging.getLogger(__name__)


def script_formatter_node(
    state: ScriptFormatterInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ScriptFormatterOutput:
    """
    title: 剧本格式化编排
    desc: 将输入内容转换为结构化剧本JSON，含场景分段、对白/独白/旁白、画面描述、镜头语言、声音设计
    integrations: 大语言模型
    """
    try:
        raw_text = invoke_llm(runtime.context, "config/script_formatter_llm_cfg.json", {
            "project_name": state.project_name,
            "episode_no": state.episode_no,
            "input_markdown": state.input_markdown
        })

        try:
            parsed = extract_json_from_llm_output(raw_text)
            formatted_json = json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception as parse_err:
            logger.warning(f"JSON解析失败，降级为原始文本: {parse_err}")
            formatted_json = raw_text

        return ScriptFormatterOutput(
            formatted_script=formatted_json,
            status="PASS",
            message="剧本格式化完成",
            current_stage="script_formatted"
        )

    except Exception as e:
        return ScriptFormatterOutput(
            formatted_script="",
            status="FAIL",
            message=f"剧本格式化失败: {str(e)}",
            current_stage="script_formatter_failed"
        )

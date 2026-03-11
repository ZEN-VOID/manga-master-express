"""
剧本格式化编排智能体节点
功能：将小说原文转换为结构化剧本（JSON输出）
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

from graphs.state import ScriptFormatterInput, ScriptFormatterOutput
from utils.json_extract import extract_json_from_llm_output

logger = logging.getLogger(__name__)


def script_formatter_node(
    state: ScriptFormatterInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ScriptFormatterOutput:
    """
    title: 剧本格式化编排
    desc: 将小说原文转换为结构化的标准剧本JSON，包含场景分段、对白/独白/旁白、画面描述
    integrations: 大语言模型
    """
    ctx = runtime.context

    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", ""),
        "config/script_formatter_llm_cfg.json"
    )

    try:
        with open(cfg_file, 'r', encoding='utf-8') as fd:
            _cfg = json.load(fd)
    except Exception as e:
        return ScriptFormatterOutput(
            formatted_script="",
            status="FAIL",
            message=f"配置文件加载失败: {str(e)}",
            current_stage="script_formatter_failed"
        )

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "project_name": state.project_name,
        "episode_no": state.episode_no,
        "input_markdown": state.input_markdown
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
            temperature=llm_config.get("temperature", 0.3),
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
            message=f"大模型调用失败: {str(e)}",
            current_stage="script_formatter_failed"
        )

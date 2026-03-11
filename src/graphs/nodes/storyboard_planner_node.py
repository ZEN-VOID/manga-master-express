"""
分镜规划编辑智能体节点
功能：将格式化剧本转换为分镜规划视频脚本（JSON输出）
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

from graphs.state import StoryboardPlannerInput, StoryboardPlannerOutput
from utils.json_extract import extract_json_from_llm_output

logger = logging.getLogger(__name__)


def storyboard_planner_node(
    state: StoryboardPlannerInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> StoryboardPlannerOutput:
    """
    title: 分镜规划编辑
    desc: 将格式化剧本转换为分镜组规划JSON，包含分镜ID、场景信息、角色道具列表、风格描述等
    integrations: 大语言模型
    """
    ctx = runtime.context

    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", ""),
        "config/storyboard_planner_llm_cfg.json"
    )

    try:
        with open(cfg_file, 'r', encoding='utf-8') as fd:
            _cfg = json.load(fd)
    except Exception as e:
        return StoryboardPlannerOutput(
            video_script="",
            status="FAIL",
            message=f"配置文件加载失败: {str(e)}",
            current_stage="storyboard_planner_failed"
        )

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "project_name": state.project_name,
        "episode_no": state.episode_no,
        "script_body": state.formatted_script,
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

        return StoryboardPlannerOutput(
            video_script=formatted_json,
            status="PASS",
            message="分镜规划完成",
            current_stage="storyboard_planned"
        )

    except Exception as e:
        return StoryboardPlannerOutput(
            video_script="",
            status="FAIL",
            message=f"大模型调用失败: {str(e)}",
            current_stage="storyboard_planner_failed"
        )

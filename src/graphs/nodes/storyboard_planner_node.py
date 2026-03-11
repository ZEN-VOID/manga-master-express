"""
分镜规划编辑智能体节点
功能：将格式化剧本转换为分镜规划视频脚本JSON
"""

import json
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import StoryboardPlannerInput, StoryboardPlannerOutput
from utils.llm_invoke import invoke_llm
from utils.json_extract import extract_json_from_llm_output

logger = logging.getLogger(__name__)


def storyboard_planner_node(
    state: StoryboardPlannerInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> StoryboardPlannerOutput:
    """
    title: 分镜规划编辑
    desc: 将格式化剧本转换为分镜组规划JSON，含分镜ID、场景信息、角色道具、镜头语言、情绪氛围
    integrations: 大语言模型
    """
    try:
        raw_text = invoke_llm(runtime.context, "config/storyboard_planner_llm_cfg.json", {
            "project_name": state.project_name,
            "episode_no": state.episode_no,
            "script_body": state.formatted_script,
            "global_style": state.global_style_prompt
        })

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
            message=f"分镜规划失败: {str(e)}",
            current_stage="storyboard_planner_failed"
        )

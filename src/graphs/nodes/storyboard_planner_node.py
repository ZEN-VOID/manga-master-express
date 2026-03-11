"""
分镜规划编辑智能体节点
功能：将格式化剧本转换为分镜规划（视频脚本）
"""

import os
import json
from typing import Dict, Any
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from graphs.state import StoryboardPlannerInput, StoryboardPlannerOutput


def storyboard_planner_node(
    state: StoryboardPlannerInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> StoryboardPlannerOutput:
    """
    title: 分镜规划编辑
    desc: 将格式化剧本转换为分镜组规划，生成分镜ID、场景信息、角色道具列表、风格描述等
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 读取配置文件
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
    
    # 渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "project_name": state.project_name,
        "episode_no": state.episode_no,
        "script_body": state.formatted_script,
        "global_style": state.global_style_prompt
    })
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用大模型
    try:
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=llm_config.get("model", "doubao-seed-2-0-pro-260215"),
            temperature=llm_config.get("temperature", 0.3),
            top_p=llm_config.get("top_p", 0.9),
            max_completion_tokens=llm_config.get("max_completion_tokens", 32768)
        )
        
        # 处理响应内容
        content = response.content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            markdown_payload = "\n".join(text_parts)
        else:
            markdown_payload = str(content) if content else ""
        
        return StoryboardPlannerOutput(
            video_script=markdown_payload,
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

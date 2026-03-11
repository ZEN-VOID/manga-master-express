"""
公共 LLM 调用工具 - 消除各 agent 节点中的重复代码
"""

import os
import json
import logging
from jinja2 import Template
from langchain_core.messages import SystemMessage, HumanMessage
from coze_coding_dev_sdk import LLMClient

logger = logging.getLogger(__name__)


def invoke_llm(ctx, cfg_path: str, template_vars: dict) -> str:
    """
    读取配置、渲染模板、调用LLM、返回原始文本。
    cfg_path 相对于 COZE_WORKSPACE_PATH。
    """
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), cfg_path)
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    up_tpl = Template(up)
    user_prompt = up_tpl.render(template_vars)

    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]

    client = LLMClient(ctx=ctx)
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "deepseek-v3-2-251201"),
        temperature=llm_config.get("temperature", 0),
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
        return "\n".join(text_parts)
    return str(content) if content else ""

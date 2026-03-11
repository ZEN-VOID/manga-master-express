"""
全局风格设计节点 - 导演层级的底层调性定义
确立全片视觉媒介、渲染技术栈与美学范式，输出可供下游继承的无污染全局风格底座
"""

import os
import json
import logging
from datetime import datetime
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import GlobalStyleInput, GlobalStyleOutput
from utils.llm_invoke import invoke_llm
from utils.json_extract import extract_json_from_llm_output

logger = logging.getLogger(__name__)


def global_style_node(
    state: GlobalStyleInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GlobalStyleOutput:
    """
    title: 全局风格设计
    desc: 导演层级底层调性定义：确立视觉媒介、渲染技术栈与美学范式，输出结构化全局风格提示词（中英双版）
    integrations: 大语言模型
    """
    try:
        raw_text = invoke_llm(runtime.context, "config/global_style_llm_cfg.json", {
            "formatted_script": state.formatted_script,
            "project_name": state.project_name,
            "episode_no": state.episode_no
        })

        global_style_prompt = ""
        narrative_type = ""
        visual_medium = ""
        aesthetic_paradigm = ""
        style_reference = ""
        narrative_pacing = "中"
        style_breakdown = {}

        try:
            parsed = extract_json_from_llm_output(raw_text)
            global_style_prompt = parsed.get("global_style_prompt", "")
            narrative_type = parsed.get("narrative_type", "")
            visual_medium = parsed.get("visual_medium", "")
            aesthetic_paradigm = parsed.get("aesthetic_paradigm", "")
            style_reference = parsed.get("style_reference", "")
            narrative_pacing = parsed.get("narrative_pacing", "中")
            style_breakdown = parsed.get("style_breakdown", {})
        except Exception:
            logger.warning("JSON解析失败，尝试从文本提取风格提示词")
            global_style_prompt = raw_text[:300] if raw_text else ""

        logger.info(f"[全局风格设计] 完成: 叙事类型={narrative_type}, 媒介={visual_medium}, 风格参照={style_reference}")

        global_style_path = ""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join("output", state.project_name, "文本")
            os.makedirs(output_dir, exist_ok=True)

            doc_data = {
                "project_name": state.project_name,
                "episode_no": state.episode_no,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "narrative_type": narrative_type,
                "visual_medium": visual_medium,
                "aesthetic_paradigm": aesthetic_paradigm,
                "style_reference": style_reference,
                "narrative_pacing": narrative_pacing,
                "style_breakdown": style_breakdown,
                "global_style_prompt": global_style_prompt
            }

            filename = f"全局风格设计_{timestamp}.json"
            global_style_path = os.path.join(output_dir, filename)

            with open(global_style_path, "w", encoding="utf-8") as f:
                json.dump(doc_data, f, ensure_ascii=False, indent=2)

            logger.info(f"[全局风格设计] 文档已保存: {global_style_path}")
        except Exception as e:
            logger.error(f"[全局风格设计] 文档保存失败: {str(e)}")

        return GlobalStyleOutput(
            global_style_prompt=global_style_prompt,
            narrative_type=narrative_type,
            visual_medium=visual_medium,
            aesthetic_paradigm=aesthetic_paradigm,
            style_reference=style_reference,
            narrative_pacing=narrative_pacing,
            style_breakdown=style_breakdown,
            global_style_path=global_style_path,
            status="PASS",
            message="全局风格设计完成",
            current_stage="global_style_defined"
        )

    except Exception as e:
        logger.error(f"[全局风格设计] 执行失败: {str(e)}")
        return GlobalStyleOutput(
            global_style_prompt="",
            narrative_type="",
            visual_medium="",
            aesthetic_paradigm="",
            style_reference="",
            narrative_pacing="中",
            style_breakdown={},
            global_style_path="",
            status="FAIL",
            message=f"全局风格设计失败: {str(e)}",
            current_stage="global_style_failed"
        )

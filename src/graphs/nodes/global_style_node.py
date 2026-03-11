"""
全局风格设计节点 - 导演层级的底层调性定义
确立全片视觉媒介、渲染技术栈与美学范式，输出可供下游继承的无污染全局风格底座
"""

import os
import json
import logging
from datetime import datetime
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from graphs.state import (
    GlobalStyleInput,
    GlobalStyleOutput
)

logger = logging.getLogger(__name__)


def global_style_node(
    state: GlobalStyleInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GlobalStyleOutput:
    """
    title: 全局风格设计
    desc: 导演层级底层调性定义：确立视觉媒介、渲染技术栈与美学范式，输出结构化全局风格提示词
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 读取配置文件
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH"),
        config.get("metadata", {}).get("llm_cfg", "config/global_style_llm_cfg.json")
    )
    
    try:
        with open(cfg_file, "r", encoding="utf-8") as f:
            _cfg = json.load(f)
    except Exception as e:
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
            message=f"配置文件加载失败: {str(e)}",
            current_stage="global_style_failed"
        )
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    # 渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "formatted_script": state.formatted_script,
        "project_name": state.project_name,
        "episode_no": state.episode_no
    })
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用大模型
    try:
        client = LLMClient(ctx=ctx)
        
        logger.info(f"[全局风格设计] 开始分析剧本风格...")
        
        response = client.invoke(
            messages=messages,
            model=llm_config.get("model", "doubao-seed-1-6-flash-250615"),
            temperature=llm_config.get("temperature", 0.7),
            top_p=llm_config.get("top_p", 0.9),
            max_completion_tokens=llm_config.get("max_completion_tokens", 3000)
        )
        
        result = response.content
        if isinstance(result, list):
            text_parts = []
            for item in result:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            result = "\n".join(text_parts)
        else:
            result = str(result) if result else ""
        
        # 解析输出，提取关键字段
        global_style_prompt = ""
        narrative_type = ""
        visual_medium = ""
        aesthetic_paradigm = ""
        style_reference = ""
        narrative_pacing = "中"
        style_breakdown = {}
        
        # 尝试解析JSON输出
        try:
            # 尝试提取JSON块
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                json_str = result[json_start:json_end].strip()
                parsed = json.loads(json_str)
            elif "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                parsed = json.loads(json_str)
            else:
                parsed = {}
            
            global_style_prompt = parsed.get("global_style_prompt", "")
            narrative_type = parsed.get("narrative_type", "")
            visual_medium = parsed.get("visual_medium", "")
            aesthetic_paradigm = parsed.get("aesthetic_paradigm", "")
            style_reference = parsed.get("style_reference", "")
            narrative_pacing = parsed.get("narrative_pacing", "中")
            style_breakdown = parsed.get("style_breakdown", {})
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试从文本中提取
            lines = result.split("\n")
            for line in lines:
                if "全局风格提示词" in line or "风格提示词" in line:
                    global_style_prompt = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
                elif "叙事类型" in line:
                    narrative_type = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
                elif "视觉媒介" in line:
                    visual_medium = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
                elif "美学范式" in line:
                    aesthetic_paradigm = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
                elif "风格参照" in line:
                    style_reference = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
                elif "叙事节奏" in line:
                    narrative_pacing = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
            
            # 如果仍未提取到，使用整个结果作为风格提示词（截取前200字）
            if not global_style_prompt:
                global_style_prompt = result[:200]
        
        logger.info(f"[全局风格设计] 分析完成: 叙事类型={narrative_type}, 媒介={visual_medium}, 风格参照={style_reference}")
        
        # 保存全局风格设计文档到文件（JSON格式）
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
            # 文档保存失败不影响主流程
        
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

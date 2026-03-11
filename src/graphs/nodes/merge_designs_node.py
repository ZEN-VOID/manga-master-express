"""
汇聚设计结果节点
功能：将场景、角色、道具三个设计合并为最终输出，并保存文本文件到output/[影片名]/文本/
"""

import os
from datetime import datetime
from pathlib import Path
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import MergeDesignsInput, MergeDesignsOutput


def save_text_file(project_name: str, filename: str, content: str) -> str:
    """保存文本文件到输出目录: output/[影片名]/文本/"""
    output_dir = Path("output") / project_name / "文本"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(file_path)


def merge_designs_node(
    state: MergeDesignsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MergeDesignsOutput:
    """
    title: 汇聚设计结果
    desc: 将场景设计、角色设计、道具设计合并为完整的视频脚本设计方案，并保存文本文件
    integrations: 
    """
    ctx = runtime.context
    
    # 获取项目名称
    project_name = state.project_name or "未命名项目"
    
    # 判断整体状态
    has_scene = bool(state.scene_design)
    has_character = bool(state.character_design)
    has_prop = bool(state.prop_design)
    
    if has_scene and has_character and has_prop:
        status = "PASS"
        message = "所有设计模块均已成功生成"
    elif has_scene or has_character or has_prop:
        status = "PASS"  # 部分成功也算PASS
        message = "部分设计模块生成成功"
    else:
        status = "FAIL"
        message = "所有设计模块均未生成"
    
    # 保存文本文件到output/[影片名]/文本/
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    script_path = ""
    video_script_path = ""
    scene_design_path = ""
    character_design_path = ""
    prop_design_path = ""
    
    try:
        if state.formatted_script:
            script_path = save_text_file(
                project_name,
                f"格式化剧本_{timestamp}.json",
                state.formatted_script
            )
        
        if state.video_script:
            video_script_path = save_text_file(
                project_name,
                f"视频脚本_{timestamp}.json",
                state.video_script
            )
        
        if state.scene_design:
            scene_design_path = save_text_file(
                project_name,
                f"场景设计_{timestamp}.json",
                state.scene_design
            )
        
        if state.character_design:
            character_design_path = save_text_file(
                project_name,
                f"角色设计_{timestamp}.json",
                state.character_design
            )
        
        if state.prop_design:
            prop_design_path = save_text_file(
                project_name,
                f"道具设计_{timestamp}.json",
                state.prop_design
            )
    except Exception as e:
        message = f"{message}; 文本保存失败: {str(e)}"
    
    return MergeDesignsOutput(
        status=status,
        message=message,
        current_stage="completed",
        script_path=script_path,
        video_script_path=video_script_path,
        global_style_path=state.global_style_path,  # 使用全局风格节点已保存的路径
        scene_design_path=scene_design_path,
        character_design_path=character_design_path,
        prop_design_path=prop_design_path
    )

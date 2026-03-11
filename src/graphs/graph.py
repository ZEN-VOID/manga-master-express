"""
Seedance视频脚本大师 - 主图编排
工作流: 小说原文 → 剧本格式化 → 全局风格设计 → 分镜规划 → (场景/角色/道具设计并行) → (拆解并行) → (生图并行) → 汇聚输出
"""

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
    ScriptFormatterInput,
    ScriptFormatterOutput,
    GlobalStyleInput,
    GlobalStyleOutput,
    StoryboardPlannerInput,
    StoryboardPlannerOutput,
    SceneOrchestratorInput,
    SceneOrchestratorOutput,
    CharacterOrchestratorInput,
    CharacterOrchestratorOutput,
    PropOrchestratorInput,
    PropOrchestratorOutput,
    SceneImageGenInput,
    SceneImageGenOutput,
    CharacterImageGenInput,
    CharacterImageGenOutput,
    PropImageGenInput,
    PropImageGenOutput,
    MergeDesignsInput,
    MergeDesignsOutput
)

from graphs.nodes.script_formatter_node import script_formatter_node
from graphs.nodes.global_style_node import global_style_node
from graphs.nodes.storyboard_planner_node import storyboard_planner_node
from graphs.nodes.scene_orchestrator_node import scene_orchestrator_node
from graphs.nodes.character_orchestrator_node import character_orchestrator_node
from graphs.nodes.prop_orchestrator_node import prop_orchestrator_node
from graphs.nodes.scene_image_gen_node import scene_image_gen_node
from graphs.nodes.character_image_gen_node import character_image_gen_node
from graphs.nodes.prop_image_gen_node import prop_image_gen_node
from graphs.nodes.merge_designs_node import merge_designs_node


# ==================== 创建状态图 ====================

builder = StateGraph(
    GlobalState,
    input_schema=GraphInput,
    output_schema=GraphOutput
)

# ==================== 添加节点 ====================

# 阶段1: 剧本格式化
builder.add_node(
    "script_formatter",
    script_formatter_node,
    metadata={"type": "agent", "llm_cfg": "config/script_formatter_llm_cfg.json"}
)

# 阶段2: 全局风格设计
builder.add_node(
    "global_style",
    global_style_node,
    metadata={"type": "agent", "llm_cfg": "config/global_style_llm_cfg.json"}
)

# 阶段3: 分镜规划
builder.add_node(
    "storyboard_planner",
    storyboard_planner_node,
    metadata={"type": "agent", "llm_cfg": "config/storyboard_planner_llm_cfg.json"}
)

# 阶段4: 场景/角色/道具设计（三路并行）
builder.add_node(
    "scene_orchestrator",
    scene_orchestrator_node,
    metadata={"type": "agent", "llm_cfg": "config/scene_orchestrator_llm_cfg.json"}
)

builder.add_node(
    "character_orchestrator",
    character_orchestrator_node,
    metadata={"type": "agent", "llm_cfg": "config/character_orchestrator_llm_cfg.json"}
)

builder.add_node(
    "prop_orchestrator",
    prop_orchestrator_node,
    metadata={"type": "agent", "llm_cfg": "config/prop_orchestrator_llm_cfg.json"}
)

# 阶段4: 生图节点（三路并行，编排节点JSON输出直接提供实体列表）
builder.add_node("scene_image_gen", scene_image_gen_node)
builder.add_node("character_image_gen", character_image_gen_node)
builder.add_node("prop_image_gen", prop_image_gen_node)

# 阶段5: 汇聚
builder.add_node("merge_designs", merge_designs_node)

# ==================== 设置边 ====================

# 设置入口点
builder.set_entry_point("script_formatter")

# 阶段1 → 阶段2: 剧本格式化 → 全局风格设计
builder.add_edge("script_formatter", "global_style")

# 阶段2 → 阶段3: 全局风格设计 → 分镜规划
builder.add_edge("global_style", "storyboard_planner")

# 阶段3 → 阶段4: 分镜规划 → (场景、角色、道具) 三路并行
builder.add_edge("storyboard_planner", "scene_orchestrator")
builder.add_edge("storyboard_planner", "character_orchestrator")
builder.add_edge("storyboard_planner", "prop_orchestrator")

# 阶段4 → 阶段5: 编排 → 生图（编排输出JSON直接含实体列表，无需拆解节点）
builder.add_edge("scene_orchestrator", "scene_image_gen")
builder.add_edge("character_orchestrator", "character_image_gen")
builder.add_edge("prop_orchestrator", "prop_image_gen")

# 阶段5 → 阶段6: 生图 → 汇聚（三路汇聚）
builder.add_edge(
    ["scene_image_gen", "character_image_gen", "prop_image_gen"],
    "merge_designs"
)

# 阶段7 → END
builder.add_edge("merge_designs", END)

# ==================== 编译图 ====================

main_graph = builder.compile()

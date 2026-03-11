"""
Seedance视频脚本大师 - 状态定义
工作流: 小说原文 → 剧本格式化 → 全局风格设计 → 分镜规划 → (场景/角色/道具设计并行，JSON输出含实体列表) → (生图并行) → 汇聚输出
"""

from typing import Optional, List, Dict, Any, Literal, Annotated
from pydantic import BaseModel, Field
from utils.file.file import File


# 自定义合并函数：并行节点时处理冲突
def merge_status(left: str, right: str) -> str:
    """合并status字段，优先取非pending状态"""
    if left == "pending":
        return right
    if right == "pending":
        return left
    if left == "PASS" or right == "PASS":
        return "PASS"
    return right


def merge_message(left: str, right: str) -> str:
    """合并message字段"""
    if left and right:
        return f"{left}; {right}"
    return right or left


def merge_list(left: List, right: List) -> List:
    """合并列表字段"""
    return left + right


# ==================== 实体数据结构 ====================

class DesignEntity(BaseModel):
    """设计实体基类"""
    entity_id: str = Field(..., description="实体ID")
    entity_name: str = Field(..., description="实体名称")
    entity_type: str = Field(..., description="实体类型: scene/character/prop")
    prompt: str = Field(default="", description="生图提示词")
    aspect_ratio: str = Field(default="16:9", description="宽高比")
    image_size: str = Field(default="2K", description="图片尺寸")


class GeneratedImage(BaseModel):
    """生成的图片"""
    entity_id: str = Field(..., description="实体ID")
    entity_name: str = Field(..., description="实体名称")
    entity_type: str = Field(..., description="实体类型")
    image_url: str = Field(default="", description="图片URL")
    local_path: str = Field(default="", description="本地路径")
    status: str = Field(default="pending", description="生成状态")
    message: str = Field(default="", description="生成消息")


# ==================== 全局状态 ====================

class GlobalState(BaseModel):
    """全局状态定义 - 跨节点共享"""
    # 输入数据
    input_markdown: str = Field(default="", description="小说原文内容")
    
    # 流程追踪
    project_name: str = Field(default="", description="项目名称")
    episode_no: int = Field(default=1, description="集号")
    
    # 中间产物
    formatted_script: str = Field(default="", description="格式化剧本内容")
    
    # 全局风格提示词（导演层级底层调性）
    global_style_prompt: str = Field(default="", description="全局风格提示词，用于下游继承")
    narrative_type: str = Field(default="", description="叙事类型")
    visual_medium: str = Field(default="", description="视觉媒介: 真人/2D/3D")
    aesthetic_paradigm: str = Field(default="", description="美学范式")
    style_reference: str = Field(default="", description="风格参照")
    narrative_pacing: str = Field(default="", description="叙事节奏: 慢/中/快")
    style_breakdown: Dict[str, str] = Field(default={}, description="六要素分解")
    global_style_path: str = Field(default="", description="全局风格设计文档保存路径")
    
    video_script: str = Field(default="", description="视频脚本内容")
    
    # 三大设计产物
    scene_design: str = Field(default="", description="场景设计内容")
    character_design: str = Field(default="", description="角色设计内容")
    prop_design: str = Field(default="", description="道具设计内容")
    
    # 拆解后的实体列表
    scene_entities: List[DesignEntity] = Field(default=[], description="场景实体列表")
    character_entities: List[DesignEntity] = Field(default=[], description="角色实体列表")
    prop_entities: List[DesignEntity] = Field(default=[], description="道具实体列表")
    
    # 生成的图片
    scene_images: Annotated[List[GeneratedImage], merge_list] = Field(default=[], description="场景生成的图片")
    character_images: Annotated[List[GeneratedImage], merge_list] = Field(default=[], description="角色生成的图片")
    prop_images: Annotated[List[GeneratedImage], merge_list] = Field(default=[], description="道具生成的图片")
    
    # 执行状态 - 使用Annotated处理并行节点合并
    status: Annotated[str, merge_status] = Field(default="pending", description="执行状态: pending/running/completed/failed")
    message: Annotated[str, merge_message] = Field(default="", description="执行消息")
    current_stage: str = Field(default="init", description="当前阶段")


# ==================== 图输入输出 ====================

class GraphInput(BaseModel):
    """工作流输入参数"""
    input_markdown: str = Field(..., description="小说原文内容")
    project_name: str = Field(default="未命名项目", description="项目名称")
    episode_no: int = Field(default=1, description="集号")


class GraphOutput(BaseModel):
    """工作流输出结果"""
    status: str = Field(..., description="执行状态: PASS/FAIL")
    formatted_script: str = Field(default="", description="格式化剧本")
    video_script: str = Field(default="", description="视频脚本")
    scene_design: str = Field(default="", description="场景设计文档")
    character_design: str = Field(default="", description="角色设计文档")
    prop_design: str = Field(default="", description="道具设计文档")
    scene_images: List[GeneratedImage] = Field(default=[], description="场景生成的图片")
    character_images: List[GeneratedImage] = Field(default=[], description="角色生成的图片")
    prop_images: List[GeneratedImage] = Field(default=[], description="道具生成的图片")
    message: str = Field(default="", description="执行消息")
    # 文本输出路径
    script_path: str = Field(default="", description="格式化剧本文件路径")
    video_script_path: str = Field(default="", description="视频脚本文件路径")
    global_style_path: str = Field(default="", description="全局风格设计文档路径")
    scene_design_path: str = Field(default="", description="场景设计文档路径")
    character_design_path: str = Field(default="", description="角色设计文档路径")
    prop_design_path: str = Field(default="", description="道具设计文档路径")


# ==================== 节点1: 剧本格式化编排智能体 ====================

class ScriptFormatterInput(BaseModel):
    """剧本格式化编排节点输入"""
    input_markdown: str = Field(..., description="小说原文")
    project_name: str = Field(..., description="项目名称")
    episode_no: int = Field(..., description="集号")


class ScriptFormatterOutput(BaseModel):
    """剧本格式化编排节点输出"""
    formatted_script: str = Field(default="", description="格式化后的剧本内容")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")
    current_stage: str = Field(default="script_formatted", description="当前阶段")


# ==================== 节点2: 全局风格设计智能体 ====================

class GlobalStyleInput(BaseModel):
    """全局风格设计节点输入"""
    formatted_script: str = Field(..., description="格式化剧本内容")
    project_name: str = Field(..., description="项目名称")
    episode_no: int = Field(..., description="集号")


class GlobalStyleOutput(BaseModel):
    """全局风格设计节点输出"""
    global_style_prompt: str = Field(default="", description="全局风格提示词（结构化风格描述，200字内）")
    narrative_type: str = Field(default="", description="叙事类型")
    visual_medium: str = Field(default="", description="视觉媒介: 真人/2D/3D")
    aesthetic_paradigm: str = Field(default="", description="美学范式")
    style_reference: str = Field(default="", description="风格参照（如：追光动画、徐克风格等）")
    narrative_pacing: str = Field(default="中", description="叙事节奏: 慢/中/快")
    style_breakdown: Dict[str, str] = Field(default={}, description="六要素分解：核心定性/技术栈/光影色彩/构图空间/动态质感/规格排除")
    global_style_path: str = Field(default="", description="全局风格设计文档保存路径")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")
    current_stage: str = Field(default="global_style_defined", description="当前阶段")


# ==================== 节点3: 分镜规划编辑智能体 ====================

class StoryboardPlannerInput(BaseModel):
    """分镜规划编辑节点输入"""
    formatted_script: str = Field(..., description="格式化剧本内容")
    global_style_prompt: str = Field(..., description="全局风格提示词前缀")
    project_name: str = Field(..., description="项目名称")
    episode_no: int = Field(..., description="集号")


class StoryboardPlannerOutput(BaseModel):
    """分镜规划编辑节点输出"""
    video_script: str = Field(default="", description="视频脚本内容")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")
    current_stage: str = Field(default="storyboard_planned", description="当前阶段")


# ==================== 节点4: 场景全链路编排智能体 ====================

class SceneOrchestratorInput(BaseModel):
    """场景全链路编排节点输入"""
    video_script: str = Field(..., description="视频脚本内容")
    global_style_prompt: str = Field(..., description="全局风格提示词前缀")
    project_name: str = Field(..., description="项目名称")
    episode_no: int = Field(..., description="集号")


class SceneOrchestratorOutput(BaseModel):
    """场景全链路编排节点输出"""
    scene_design: str = Field(default="", description="场景设计内容(JSON)")
    scene_entities: List[DesignEntity] = Field(default=[], description="场景实体列表(直接供生图消费)")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")


# ==================== 节点5: 角色全链路编排智能体 ====================

class CharacterOrchestratorInput(BaseModel):
    """角色全链路编排节点输入"""
    video_script: str = Field(..., description="视频脚本内容")
    global_style_prompt: str = Field(..., description="全局风格提示词前缀")
    project_name: str = Field(..., description="项目名称")
    episode_no: int = Field(..., description="集号")


class CharacterOrchestratorOutput(BaseModel):
    """角色全链路编排节点输出"""
    character_design: str = Field(default="", description="角色设计内容(JSON)")
    character_entities: List[DesignEntity] = Field(default=[], description="角色实体列表(直接供生图消费)")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")


# ==================== 节点6: 道具全链路编排智能体 ====================

class PropOrchestratorInput(BaseModel):
    """道具全链路编排节点输入"""
    video_script: str = Field(..., description="视频脚本内容")
    global_style_prompt: str = Field(..., description="全局风格提示词前缀")
    project_name: str = Field(..., description="项目名称")
    episode_no: int = Field(..., description="集号")


class PropOrchestratorOutput(BaseModel):
    """道具全链路编排节点输出"""
    prop_design: str = Field(default="", description="道具设计内容(JSON)")
    prop_entities: List[DesignEntity] = Field(default=[], description="道具实体列表(直接供生图消费)")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")


# ==================== 节点7: 场景生图节点 ====================

class SceneImageGenInput(BaseModel):
    """场景生图节点输入"""
    scene_entities: List[DesignEntity] = Field(default=[], description="场景实体列表")
    project_name: str = Field(..., description="项目名称")


class SceneImageGenOutput(BaseModel):
    """场景生图节点输出"""
    scene_images: List[GeneratedImage] = Field(default=[], description="生成的场景图片")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")


# ==================== 节点10: 角色生图节点 ====================

class CharacterImageGenInput(BaseModel):
    """角色生图节点输入"""
    character_entities: List[DesignEntity] = Field(default=[], description="角色实体列表")
    project_name: str = Field(..., description="项目名称")


class CharacterImageGenOutput(BaseModel):
    """角色生图节点输出"""
    character_images: List[GeneratedImage] = Field(default=[], description="生成的角色图片")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")


# ==================== 节点11: 道具生图节点 ====================

class PropImageGenInput(BaseModel):
    """道具生图节点输入"""
    prop_entities: List[DesignEntity] = Field(default=[], description="道具实体列表")
    project_name: str = Field(..., description="项目名称")


class PropImageGenOutput(BaseModel):
    """道具生图节点输出"""
    prop_images: List[GeneratedImage] = Field(default=[], description="生成的道具图片")
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")


# ==================== 节点12: 汇聚设计结果 ====================

class MergeDesignsInput(BaseModel):
    """汇聚设计结果节点输入"""
    formatted_script: str = Field(default="", description="格式化剧本内容")
    video_script: str = Field(default="", description="视频脚本")
    global_style_prompt: str = Field(default="", description="全局风格提示词")
    global_style_path: str = Field(default="", description="全局风格设计文档路径")
    scene_design: str = Field(default="", description="场景设计内容")
    character_design: str = Field(default="", description="角色设计内容")
    prop_design: str = Field(default="", description="道具设计内容")
    scene_images: List[GeneratedImage] = Field(default=[], description="场景生成的图片")
    character_images: List[GeneratedImage] = Field(default=[], description="角色生成的图片")
    prop_images: List[GeneratedImage] = Field(default=[], description="道具生成的图片")
    project_name: str = Field(default="", description="项目名称")
    episode_no: int = Field(default=1, description="集号")
    status: str = Field(default="pending", description="当前执行状态")
    message: str = Field(default="", description="当前执行消息")


class MergeDesignsOutput(BaseModel):
    """汇聚设计结果节点输出"""
    status: str = Field(default="pending", description="执行状态")
    message: str = Field(default="", description="执行消息")
    current_stage: str = Field(default="completed", description="当前阶段")
    # 文本输出路径
    script_path: str = Field(default="", description="格式化剧本文件路径")
    video_script_path: str = Field(default="", description="视频脚本文件路径")
    global_style_path: str = Field(default="", description="全局风格设计文档路径")
    scene_design_path: str = Field(default="", description="场景设计文档路径")
    character_design_path: str = Field(default="", description="角色设计文档路径")
    prop_design_path: str = Field(default="", description="道具设计文档路径")

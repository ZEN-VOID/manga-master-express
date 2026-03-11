"""
场景拆解节点 - 直接提取C阶段完整Contract块作为提示词
"""

import re
import logging
from typing import List
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    SceneParserInput,
    SceneParserOutput,
    DesignEntity
)

logger = logging.getLogger(__name__)


def scene_parser_node(
    state: SceneParserInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SceneParserOutput:
    """
    title: 场景拆解
    desc: 直接提取C阶段Scene Panel Prompt Contract完整块作为生图提示词
    """
    ctx = runtime.context
    
    scene_design = state.scene_design
    project_name = state.project_name
    
    entities: List[DesignEntity] = []
    
    try:
        # 方法1：尝试匹配 "### Scene Panel Prompt Contract" 格式
        # 按Contract标题分割
        pattern = r'###\s*Scene Panel Prompt Contract\s*\n'
        contract_blocks = re.split(pattern, scene_design)
        
        logger.info(f"场景设计文档分割结果: {len(contract_blocks)} 个块")
        
        for i, block in enumerate(contract_blocks[1:], 1):  # 跳过第一个（C阶段之前的内容）
            logger.info(f"处理第{i}个Contract块, 长度: {len(block)}")
            
            # 找到当前Contract块的结束位置（下一个 "##" 或 "###" 或 "---" 或 "## Completeness"）
            end_match = re.search(r'\n(?=##\s|---|\Z)', block)
            if end_match:
                contract_text = block[:end_match.start()].strip()
            else:
                contract_text = block.strip()
            
            # 跳过空的或太短的块
            if len(contract_text) < 100:
                logger.warning(f"Contract块{i}太短({len(contract_text)}字符), 跳过")
                continue
            
            logger.info(f"Contract块{i}内容长度: {len(contract_text)}")
            logger.info(f"Contract块{i}前200字符: {contract_text[:200]}")
            
            # 提取scene_id
            scene_id_match = re.search(r'scene_id\s*[:：]\s*["\']?([^"\'\n\*]+)["\']?', contract_text, re.IGNORECASE)
            if not scene_id_match:
                logger.warning(f"Contract块{i}未找到scene_id")
                continue
            scene_id = scene_id_match.group(1).strip().strip('"\'')
            
            # 提取场景名称（从identity badge提取）
            scene_name = scene_id
            badge_match = re.search(r'badge\s*[`\'"][^`\'"]*\+([^`\'"]+)[`\'"]', contract_text, re.IGNORECASE)
            if badge_match:
                scene_name = badge_match.group(1).strip()
            
            # 提取aspect_ratio
            aspect_ratio = "16:9"
            ar_match = re.search(r'aspect_ratio\s*[:：]\s*["\']?(\d+:\d+)["\']?', contract_text, re.IGNORECASE)
            if ar_match:
                aspect_ratio = ar_match.group(1)
            
            # 提取resolution/image_size
            image_size = "4K"
            res_match = re.search(r'resolution\s*[:：]\s*["\']?(\d+[Kk])["\']?', contract_text, re.IGNORECASE)
            if res_match:
                image_size = res_match.group(1).upper()
            
            # 直接使用整个Contract块作为提示词
            full_prompt = contract_text
            
            entity = DesignEntity(
                entity_id=scene_id,
                entity_name=scene_name[:50],
                entity_type="scene",
                prompt=full_prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size
            )
            entities.append(entity)
            logger.info(f"解析场景实体(C阶段完整Contract): {scene_id} - {scene_name}, 提示词长度: {len(full_prompt)}")
        
        # 如果没有找到C阶段，降级到B阶段
        if not entities:
            logger.warning("未找到C阶段Contract，尝试从B阶段提取...")
            # B阶段格式: #### 场景ID: SCENE_01 或 ### 场景ID: SCENE_01
            b_stage_pattern = r'#{2,4}\s*场景ID:\s*(\S+)'
            b_matches = re.findall(b_stage_pattern, scene_design)
            
            logger.info(f"B阶段找到的场景ID: {b_matches}")
            
            for scene_id in b_matches:
                # 提取该场景ID后的提示词块
                prompt_pattern = rf'#{ {2,4}}\s*场景ID:\s*{re.escape(scene_id)}\s*\n`([^`]+)`'
                prompt_match = re.search(prompt_pattern, scene_design, re.DOTALL)
                if prompt_match:
                    prompt = prompt_match.group(1).strip().split('\n')[0][:2000]
                    
                    ar_match = re.search(r'--ar\s+(\d+:\d+)', prompt)
                    aspect_ratio = ar_match.group(1) if ar_match else "16:9"
                    
                    entity = DesignEntity(
                        entity_id=scene_id,
                        entity_name=scene_id[:50],
                        entity_type="scene",
                        prompt=prompt,
                        aspect_ratio=aspect_ratio,
                        image_size="4K"
                    )
                    entities.append(entity)
                    logger.info(f"从B阶段解析场景实体(降级): {scene_id}")
        
        if entities:
            return SceneParserOutput(
                scene_entities=entities,
                status="PASS",
                message=f"成功解析{len(entities)}个场景实体"
            )
        else:
            return SceneParserOutput(
                scene_entities=[],
                status="FAIL",
                message="未能从场景设计文档中解析出任何场景实体"
            )
            
    except Exception as e:
        logger.error(f"场景拆解失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return SceneParserOutput(
            scene_entities=[],
            status="FAIL",
            message=f"场景拆解异常: {str(e)}"
        )

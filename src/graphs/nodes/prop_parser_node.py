"""
道具拆解节点 - 直接提取C阶段完整Contract块作为提示词
"""

import re
import logging
from typing import List
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    PropParserInput,
    PropParserOutput,
    DesignEntity
)

logger = logging.getLogger(__name__)


def prop_parser_node(
    state: PropParserInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> PropParserOutput:
    """
    title: 道具拆解
    desc: 直接提取C阶段Prop Panel Prompt Contract完整块作为生图提示词
    """
    ctx = runtime.context
    
    prop_design = state.prop_design
    project_name = state.project_name
    
    entities: List[DesignEntity] = []
    
    try:
        # 按 "## Prop Panel Prompt Contract" 或 "### Prop Panel Prompt Contract" 分割
        # 兼容两种格式
        contract_blocks = re.split(r'#{1,3}\s*Prop Panel Prompt Contract', prop_design)
        
        for block in contract_blocks[1:]:  # 跳过第一个
            # 找到当前Contract块的结束位置
            end_match = re.search(r'\n(?=##\s|###\s|---|\Z)', block)
            if end_match:
                contract_text = block[:end_match.start()].strip()
            else:
                contract_text = block.strip()
            
            # 跳过空的或太短的块
            if len(contract_text) < 100:
                continue
            
            # 提取prop_id
            prop_id_match = re.search(r'prop_id\s*[:：]\s*["\']?([^"\'\n\*]+)["\']?', contract_text, re.IGNORECASE)
            if not prop_id_match:
                continue
            prop_id = prop_id_match.group(1).strip().strip('"\'')
            
            # 提取道具名称
            prop_name = prop_id
            badge_match = re.search(r'badge\s*[`\'"][^`\'"]*\+([^`\'"]+)[`\'"]', contract_text, re.IGNORECASE)
            if badge_match:
                prop_name = badge_match.group(1).strip()
            
            # 提取aspect_ratio
            aspect_ratio = "16:9"
            ar_match = re.search(r'aspect_ratio\s*[:：]\s*["\']?(\d+:\d+)["\']?', contract_text, re.IGNORECASE)
            if ar_match:
                aspect_ratio = ar_match.group(1)
            
            # 提取resolution/image_size
            image_size = "2K"
            res_match = re.search(r'resolution\s*[:：]\s*["\']?(\d+[Kk])["\']?', contract_text, re.IGNORECASE)
            if res_match:
                image_size = res_match.group(1).upper()
            
            # 直接使用整个Contract块作为提示词
            full_prompt = contract_text
            
            entity = DesignEntity(
                entity_id=prop_id,
                entity_name=prop_name[:50],
                entity_type="prop",
                prompt=full_prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size
            )
            entities.append(entity)
            logger.info(f"解析道具实体(C阶段完整Contract): {prop_id} - {prop_name}, 提示词长度: {len(full_prompt)}")
        
        # 如果没有找到C阶段，降级到B阶段
        if not entities:
            logger.warning("未找到C阶段Contract，尝试从B阶段提取...")
            # B阶段格式: ### 道具ID: prop_xxx
            b_stage_pattern = r'###\s*道具ID:\s*(\S+)\s*\n`([^`]+)`'
            b_matches = re.findall(b_stage_pattern, prop_design, re.DOTALL)
            
            # 也尝试另一种格式
            if not b_matches:
                b_stage_pattern = r'####\s*道具ID:\s*(\S+)\s*\n`([^`]+)`'
                b_matches = re.findall(b_stage_pattern, prop_design, re.DOTALL)
            
            for prop_id, prompt_block in b_matches:
                prompt = prompt_block.strip().split('\n')[0][:2000]
                
                ar_match = re.search(r'--ar\s+(\d+:\d+)', prompt)
                aspect_ratio = ar_match.group(1) if ar_match else "16:9"
                
                entity = DesignEntity(
                    entity_id=prop_id,
                    entity_name=prop_id[:50],
                    entity_type="prop",
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    image_size="2K"
                )
                entities.append(entity)
                logger.info(f"从B阶段解析道具实体(降级): {prop_id}")
        
        if entities:
            return PropParserOutput(
                prop_entities=entities,
                status="PASS",
                message=f"成功解析{len(entities)}个道具实体"
            )
        else:
            return PropParserOutput(
                prop_entities=[],
                status="FAIL",
                message="未能从道具设计文档中解析出任何道具实体"
            )
            
    except Exception as e:
        logger.error(f"道具拆解失败: {str(e)}")
        return PropParserOutput(
            prop_entities=[],
            status="FAIL",
            message=f"道具拆解异常: {str(e)}"
        )

"""
场景生图节点 - 调用nano-banana API生成场景图片
"""

import os
import json
import base64
import logging
import requests
from pathlib import Path
from typing import List
from datetime import datetime
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

# 加载.env文件（显式指定路径，强制覆盖环境变量）
try:
    from dotenv import load_dotenv
    workspace = os.getenv("COZE_WORKSPACE_PATH", "/app/work")
    env_file = os.path.join(workspace, ".env")
    load_dotenv(env_file, override=True)
except ImportError:
    pass

from graphs.state import (
    SceneImageGenInput,
    SceneImageGenOutput,
    DesignEntity,
    GeneratedImage
)

logger = logging.getLogger(__name__)

# nano-banana API配置
DEFAULT_API_BASE_URL = "https://fw2afus.ent.acc.kurtisasia.com"
DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_IMAGE_SIZE = "2K"


def scene_image_gen_node(
    state: SceneImageGenInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SceneImageGenOutput:
    """
    title: 场景生图
    desc: 调用nano-banana API为每个场景实体生成设计图
    integrations: nano-banana (AnyFast Gemini Image Generation)
    """
    ctx = runtime.context
    
    scene_entities = state.scene_entities
    project_name = state.project_name
    
    generated_images: List[GeneratedImage] = []
    
    if not scene_entities:
        return SceneImageGenOutput(
            scene_images=[],
            status="SKIP",
            message="无场景实体需要生成图片"
        )
    
    try:
        # 获取API配置
        api_key = os.getenv("ANYFAST_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return SceneImageGenOutput(
                scene_images=[],
                status="FAIL",
                message="未配置ANYFAST_API_KEY或GEMINI_API_KEY"
            )
        
        api_base_url = os.getenv("ANYFAST_API_BASE_URL", DEFAULT_API_BASE_URL)
        model = os.getenv("DXJ2_DEFAULT_MODEL", DEFAULT_MODEL)
        
        # API端点
        api_url = f"{api_base_url}/v1beta/models/{model}:generateContent?key={api_key}"
        
        # 为每个场景实体生成图片
        for entity in scene_entities:
            try:
                # 使用实体配置或默认值
                aspect_ratio = entity.aspect_ratio if entity.aspect_ratio else DEFAULT_ASPECT_RATIO
                image_size = entity.image_size if entity.image_size else DEFAULT_IMAGE_SIZE
                
                # 构建请求体
                request_body = {
                    "contents": [
                        {
                            "parts": [
                                {"text": entity.prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseModalities": ["TEXT", "IMAGE"],
                        "imageConfig": {
                            "aspectRatio": aspect_ratio,
                            "imageSize": image_size
                        }
                    }
                }
                
                logger.info(f"开始生成场景图片: {entity.entity_id} - {entity.entity_name}")
                
                # 调用API
                response = requests.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json=request_body,
                    timeout=120
                )
                
                if response.status_code != 200:
                    logger.error(f"API调用失败: {response.status_code} - {response.text}")
                    generated_images.append(GeneratedImage(
                        entity_id=entity.entity_id,
                        entity_name=entity.entity_name,
                        entity_type="scene",
                        status="FAIL",
                        message=f"API调用失败: {response.status_code}"
                    ))
                    continue
                
                result = response.json()
                
                # 解析响应，提取图片数据
                candidates = result.get("candidates", [])
                if not candidates:
                    generated_images.append(GeneratedImage(
                        entity_id=entity.entity_id,
                        entity_name=entity.entity_name,
                        entity_type="scene",
                        status="FAIL",
                        message="API响应无candidates"
                    ))
                    continue
                
                parts = candidates[0].get("content", {}).get("parts", [])
                image_data = None
                mime_type = "image/png"
                
                for part in parts:
                    # 兼容inline_data和inlineData两种格式
                    inline_data = part.get("inline_data") or part.get("inlineData")
                    if inline_data:
                        image_data = inline_data.get("data")
                        mime_type = inline_data.get("mimeType", "image/png")
                        break
                
                if not image_data:
                    generated_images.append(GeneratedImage(
                        entity_id=entity.entity_id,
                        entity_name=entity.entity_name,
                        entity_type="scene",
                        status="FAIL",
                        message="API响应无图片数据"
                    ))
                    continue
                
                # 保存图片到项目输出目录: output/[影片名]/图像/
                # 命名规范: 场景_场景名_编号
                safe_name = entity.entity_name.replace(" ", "_").replace("/", "_")[:20]  # 限制长度
                # 从entity_id提取编号(去掉前缀)
                entity_no = entity.entity_id.upper().replace("SCENE_", "").replace("SCENE", "")[:10] or "1"
                filename = f"场景_{safe_name}_{entity_no}.png"
                
                # 确保输出目录存在: output/[影片名]/图像/
                output_dir = Path("output") / project_name / "图像"
                output_dir.mkdir(parents=True, exist_ok=True)
                temp_path = str(output_dir / filename)
                
                # 解码并保存图片
                image_bytes = base64.b64decode(image_data)
                with open(temp_path, "wb") as f:
                    f.write(image_bytes)
                
                logger.info(f"场景图片已保存: {temp_path}")
                
                # 上传到对象存储（使用storage技能）
                # 这里暂时使用本地路径，后续可以集成对象存储技能
                image_url = f"file://{temp_path}"
                
                generated_images.append(GeneratedImage(
                    entity_id=entity.entity_id,
                    entity_name=entity.entity_name,
                    entity_type="scene",
                    image_url=image_url,
                    local_path=temp_path,
                    status="PASS",
                    message="图片生成成功"
                ))
                
            except Exception as e:
                logger.error(f"生成场景图片失败 {entity.entity_id}: {str(e)}")
                generated_images.append(GeneratedImage(
                    entity_id=entity.entity_id,
                    entity_name=entity.entity_name,
                    entity_type="scene",
                    status="FAIL",
                    message=f"生成异常: {str(e)}"
                ))
        
        # 统计结果
        success_count = sum(1 for img in generated_images if img.status == "PASS")
        fail_count = len(generated_images) - success_count
        
        if success_count > 0:
            return SceneImageGenOutput(
                scene_images=generated_images,
                status="PASS" if fail_count == 0 else "PARTIAL",
                message=f"成功生成{success_count}张场景图片" + (f"，失败{fail_count}张" if fail_count > 0 else "")
            )
        else:
            return SceneImageGenOutput(
                scene_images=generated_images,
                status="FAIL",
                message="所有场景图片生成失败"
            )
            
    except Exception as e:
        logger.error(f"场景生图节点异常: {str(e)}")
        return SceneImageGenOutput(
            scene_images=generated_images,
            status="FAIL",
            message=f"场景生图异常: {str(e)}"
        )

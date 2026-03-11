#!/usr/bin/env python3
"""
nano-banana（AnyFast Gemini 3.1 Flash Image Preview）图像生成 CLI

能力：
- 文本生图（T2I）
- 参考图生图（I2I）
- JSON 请求承接（支持单任务 / 多任务）
- 默认值自动注入：aspectRatio=16:9, imageSize=4K
- 多任务自动并发调度：默认最大并发 100，硬上限 100
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    from dotenv import load_dotenv

    try:
        load_dotenv()
    except Exception:
        load_dotenv(dotenv_path=str(Path.cwd() / ".env"))
except ImportError:
    print("❌ 缺少依赖，请先执行: pip install -r .codex/skills/aigc2026/5-API/image/nano-banana/requirements.txt")
    sys.exit(1)


DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_API_BASE_URL = "https://fw2afus.ent.acc.kurtisasia.com"
DEFAULT_OUTPUT_ROOT = Path("output/影片")
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_IMAGE_SIZE = "4K"
DEFAULT_MAX_CONCURRENT = 100
HARD_MAX_CONCURRENT = 100
SUPPORTED_ASPECT_RATIOS = {"1:1", "3:4", "4:3", "9:16", "16:9"}
SUPPORTED_IMAGE_SIZES = {"1K", "2K", "4K"}
SUPPORTED_TASK_KINDS = {"project", "test", "temp"}


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe_name(text: str, max_len: int = 48) -> str:
    text = re.sub(r"\s+", "_", text.strip())
    text = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff-]+", "", text)
    return text[:max_len] or "nano_banana"


def _empty_to_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.lower() in {"null", "none", "n/a"}:
            return None
        return stripped
    return str(value)


def _normalize_aspect_ratio(value: Optional[str]) -> Optional[str]:
    value = _empty_to_none(value)
    if value is None:
        return None
    normalized = value.replace("：", ":").replace(" ", "")
    if normalized not in SUPPORTED_ASPECT_RATIOS:
        raise ValueError(
            "aspect_ratio 非法，允许值为: " + ", ".join(sorted(SUPPORTED_ASPECT_RATIOS))
        )
    return normalized


def _normalize_image_size(value: Optional[str]) -> Optional[str]:
    value = _empty_to_none(value)
    if value is None:
        return None
    normalized = value.replace(" ", "").replace("Ｋ", "K").replace("ｋ", "k")
    normalized = normalized[:-1] + "K" if normalized.lower().endswith("k") else normalized
    if normalized not in SUPPORTED_IMAGE_SIZES:
        raise ValueError(
            "image_size 非法，允许值为: " + ", ".join(sorted(SUPPORTED_IMAGE_SIZES))
        )
    return normalized


def _normalize_max_concurrent(value: int) -> int:
    if value < 1:
        raise ValueError("max_concurrent 必须 >= 1")
    return min(value, HARD_MAX_CONCURRENT)


def _load_json(path_str: str) -> Any:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"input_json 不存在: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_images(values: List[Any]) -> List[str]:
    items: List[str] = []
    for value in values:
        if isinstance(value, dict):
            image_value = _empty_to_none(value.get("url"))
        else:
            image_value = _empty_to_none(value)
        if image_value:
            items.append(image_value)
    return items


def _extract_input_doc(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("单任务 input_json 必须是对象")

    images = data.get("images") or []
    if not isinstance(images, list):
        raise ValueError("input_json 中的 images 必须是数组")

    return {
        "prompt": _empty_to_none(data.get("prompt")),
        "aspect_ratio": _empty_to_none(data.get("aspect_ratio") or data.get("ratio")),
        "image_size": _empty_to_none(data.get("image_size") or data.get("quality")),
        "images": _normalize_images(images),
        "project_name": _empty_to_none(data.get("project_name") or data.get("project")),
        "task_kind": _empty_to_none(data.get("task_kind")),
        "request_id": _empty_to_none(data.get("request_id")),
        "output_dir": _empty_to_none(data.get("output_dir")),
        "output_filename": _empty_to_none(data.get("output_filename")),
        "filename_prefix": _empty_to_none(data.get("filename_prefix")),
    }


def _extract_input_docs(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [_extract_input_doc(item) for item in data]

    if not isinstance(data, dict):
        raise ValueError("input_json 必须是对象、对象数组，或包含 tasks 数组的对象")

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        return [_extract_input_doc(data)]

    shared = {key: value for key, value in data.items() if key != "tasks"}
    docs: List[Dict[str, Any]] = []
    shared_images = shared.get("images") if isinstance(shared.get("images"), list) else []

    for item in tasks:
        if not isinstance(item, dict):
            raise ValueError("tasks 数组中的每个任务都必须是对象")
        merged = dict(shared)
        merged.update(item)
        task_images = item.get("images") if isinstance(item.get("images"), list) else []
        if shared_images or task_images:
            merged["images"] = [*shared_images, *task_images]
        docs.append(_extract_input_doc(merged))

    return docs


def _guess_mime_from_name(name: str) -> str:
    mime_type, _ = mimetypes.guess_type(name)
    return mime_type or "image/png"


def _coerce_image_part(source: str, timeout: int) -> Dict[str, Any]:
    if source.startswith("data:"):
        header, _, data = source.partition(",")
        mime_match = re.match(r"data:([^;]+);base64", header, flags=re.IGNORECASE)
        mime_type = mime_match.group(1) if mime_match else "image/png"
        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": data,
            }
        }

    if source.startswith(("http://", "https://")):
        response = requests.get(source, timeout=timeout)
        response.raise_for_status()
        mime_type = response.headers.get("Content-Type", "").split(";", 1)[0] or _guess_mime_from_name(source)
        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": base64.b64encode(response.content).decode("utf-8"),
            }
        }

    file_path = Path(source)
    if file_path.exists():
        mime_type = _guess_mime_from_name(file_path.name)
        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": base64.b64encode(file_path.read_bytes()).decode("utf-8"),
            }
        }

    try:
        base64.b64decode(source, validate=True)
        return {
            "inline_data": {
                "mime_type": "image/png",
                "data": source,
            }
        }
    except Exception as exc:
        raise ValueError(f"无法识别参考图输入: {source[:80]}") from exc


def _parse_response(body: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    image_items: List[Dict[str, Any]] = []
    text_items: List[str] = []
    finish_reasons: List[str] = []

    candidates = body.get("candidates")
    if not isinstance(candidates, list):
        return image_items, text_items, finish_reasons

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        finish_reason = _empty_to_none(candidate.get("finishReason"))
        if finish_reason:
            finish_reasons.append(finish_reason)

        content = candidate.get("content")
        if not isinstance(content, dict):
            continue
        parts = content.get("parts")
        if not isinstance(parts, list):
            continue
        for part in parts:
            if not isinstance(part, dict):
                continue
            text = _empty_to_none(part.get("text"))
            if text:
                text_items.append(text)
            inline_data = part.get("inline_data") or part.get("inlineData")
            if isinstance(inline_data, dict):
                data = _empty_to_none(inline_data.get("data"))
                mime_type = (
                    _empty_to_none(inline_data.get("mime_type"))
                    or _empty_to_none(inline_data.get("mimeType"))
                    or "image/png"
                )
                if data:
                    image_items.append({"mime_type": mime_type, "data": data})

    return image_items, text_items, finish_reasons


def _extension_for_mime(mime_type: str) -> str:
    mapping = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
    }
    return mapping.get(mime_type.lower(), ".png")


def _env_api_key() -> Optional[str]:
    return os.getenv("ANYFAST_API_KEY") or os.getenv("GEMINI_API_KEY")


def _env_default_model() -> str:
    return os.getenv("DXJ2_DEFAULT_MODEL") or DEFAULT_MODEL


def _env_api_base_url() -> str:
    return (
        os.getenv("ANYFAST_API_BASE_URL")
        or os.getenv("ANYFAST_ACCEL_BASE_URL")
        or DEFAULT_API_BASE_URL
    )


def _build_api_url(base_url: str, model: str) -> str:
    normalized = base_url.rstrip("/")
    return f"{normalized}/v1beta/models/{model}:generateContent"


def _normalize_task_kind(value: Optional[str]) -> Optional[str]:
    value = _empty_to_none(value)
    if value is None:
        return None
    normalized = value.strip().lower()
    alias_map = {
        "project": "project",
        "normal": "project",
        "正式": "project",
        "test": "test",
        "testing": "test",
        "测试": "test",
        "temp": "temp",
        "temporary": "temp",
        "临时": "temp",
    }
    normalized = alias_map.get(normalized, normalized)
    if normalized not in SUPPORTED_TASK_KINDS:
        raise ValueError("task_kind 非法，允许值为: project, test, temp")
    return normalized


def _resolve_project_name(explicit_project_name: Optional[str], task_kind: Optional[str]) -> str:
    project_name = _empty_to_none(explicit_project_name)
    if project_name:
        return project_name
    if task_kind == "temp":
        return "临时"
    return "测试"


def _build_default_output_dir(project_name: str) -> Path:
    return DEFAULT_OUTPUT_ROOT / project_name / "5-API" / "image" / "nano-banana"


def _build_task_token(task_index: int, request_id: Optional[str], filename_prefix: str) -> str:
    token_seed = request_id or filename_prefix or f"task_{task_index:03d}"
    return f"task_{task_index:03d}_{_safe_name(token_seed, max_len=24)}"


def _build_task_report_path(
    output_dir: Path,
    run_stamp: str,
    task_token: str,
    task_count: int,
    report_json: Optional[str],
) -> Path:
    if task_count == 1 and report_json:
        return Path(report_json)
    suffix = "" if task_count == 1 else f"_{task_token}"
    return output_dir / f"nano_banana_report_{run_stamp}{suffix}.json"


def _build_batch_report_path(report_json: Optional[str], output_dirs: List[Path], run_stamp: str) -> Path:
    if report_json:
        return Path(report_json)
    anchor_dir = output_dirs[0] if output_dirs else Path.cwd()
    return anchor_dir / f"nano_banana_batch_report_{run_stamp}.json"


def _prepare_task(
    args: argparse.Namespace,
    input_doc: Dict[str, Any],
    task_index: int,
    task_count: int,
    run_stamp: str,
) -> Dict[str, Any]:
    prompt = _empty_to_none(args.prompt) or input_doc.get("prompt")
    if not prompt:
        raise ValueError(f"任务 {task_index} 缺少 prompt")

    explicit_aspect_ratio = _normalize_aspect_ratio(args.aspect_ratio or input_doc.get("aspect_ratio"))
    explicit_image_size = _normalize_image_size(args.image_size or input_doc.get("image_size"))
    task_kind = _normalize_task_kind(args.task_kind or input_doc.get("task_kind")) or "test"
    defaults_applied = {
        "aspect_ratio": explicit_aspect_ratio is None,
        "image_size": explicit_image_size is None,
    }
    final_aspect_ratio = explicit_aspect_ratio or DEFAULT_ASPECT_RATIO
    final_image_size = explicit_image_size or DEFAULT_IMAGE_SIZE

    image_sources: List[Any] = list(args.image_url)
    if input_doc.get("images"):
        image_sources.extend(input_doc["images"])
    images = _normalize_images(image_sources)

    project_name = _resolve_project_name(
        _empty_to_none(args.project_name) or input_doc.get("project_name"),
        task_kind,
    )
    request_id = _empty_to_none(args.request_id) or input_doc.get("request_id")
    api_url = _empty_to_none(args.api_url) or _build_api_url(_env_api_base_url(), args.model)
    output_dir_value = (
        _empty_to_none(args.output_dir)
        or input_doc.get("output_dir")
        or str(_build_default_output_dir(project_name))
    )
    output_filename = _empty_to_none(args.output_filename) or input_doc.get("output_filename")
    base_filename_prefix = (
        _empty_to_none(args.filename_prefix)
        or (Path(output_filename).stem if output_filename else None)
        or input_doc.get("filename_prefix")
        or _safe_name(prompt)
    )
    task_token = _build_task_token(task_index, request_id, base_filename_prefix)
    filename_prefix = base_filename_prefix if task_count == 1 else f"{base_filename_prefix}_{task_token}"

    try:
        parts: List[Dict[str, Any]] = [{"text": prompt}]
        for image in images:
            parts.append(_coerce_image_part(image, args.timeout))
    except Exception as exc:
        raise ValueError(f"任务 {task_index} 参考图处理失败: {exc}") from exc

    payload: Dict[str, Any] = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": final_aspect_ratio,
                "imageSize": final_image_size,
            },
        },
    }
    if request_id:
        payload["request_id"] = request_id

    output_dir = Path(output_dir_value)
    report_path = _build_task_report_path(
        output_dir=output_dir,
        run_stamp=run_stamp,
        task_token=task_token,
        task_count=task_count,
        report_json=args.report_json,
    )

    return {
        "task_index": task_index,
        "task_token": task_token,
        "prompt": prompt,
        "images": images,
        "project_name": project_name,
        "task_kind": task_kind,
        "request_id": request_id,
        "api_url": api_url,
        "output_dir": output_dir,
        "output_dir_value": output_dir_value,
        "output_filename": output_filename,
        "filename_prefix": filename_prefix,
        "payload": payload,
        "defaults_applied": defaults_applied,
        "final_aspect_ratio": final_aspect_ratio,
        "final_image_size": final_image_size,
        "report_path": report_path,
        "model": args.model,
    }


def _print_payloads(tasks: List[Dict[str, Any]]) -> None:
    for task in tasks:
        print(f"===== TASK {task['task_index']} / {task['task_token']} =====")
        print(json.dumps(task["payload"], ensure_ascii=False, indent=2))


def _execute_task(
    task: Dict[str, Any],
    api_key: str,
    timeout: int,
    save_images: bool,
) -> Dict[str, Any]:
    output_dir = task["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "request_summary": {
            "task_index": task["task_index"],
            "task_token": task["task_token"],
            "model": task["model"],
            "api_url": task["api_url"],
            "prompt": task["prompt"],
            "image_count": len(task["images"]),
            "project_name": task["project_name"],
            "task_kind": task["task_kind"],
            "output_dir": task["output_dir_value"],
            "output_filename": task["output_filename"],
            "aspect_ratio": task["final_aspect_ratio"],
            "image_size": task["final_image_size"],
            "request_id": task["request_id"],
        },
        "defaults_applied": task["defaults_applied"],
        "saved_files": [],
        "response_texts": [],
    }

    try:
        response = requests.post(
            task["api_url"],
            params={"key": api_key},
            headers={"Content-Type": "application/json"},
            json=task["payload"],
            timeout=timeout,
        )
        response.raise_for_status()
        body = response.json()

        image_items, text_items, finish_reasons = _parse_response(body)
        report["response_meta"] = {
            "finish_reasons": finish_reasons,
            "candidate_count": len(body.get("candidates", [])) if isinstance(body.get("candidates"), list) else 0,
        }
        report["response_texts"] = text_items

        if save_images:
            for index, item in enumerate(image_items, start=1):
                ext = _extension_for_mime(item["mime_type"])
                output_filename = task.get("output_filename")
                if output_filename:
                    base_output_path = output_dir / output_filename
                    if index == 1:
                        out_path = (
                            base_output_path
                            if base_output_path.suffix
                            else output_dir / f"{base_output_path.name}{ext}"
                        )
                    else:
                        out_path = output_dir / f"{base_output_path.stem}_{index}{ext}"
                else:
                    out_path = output_dir / f"{task['filename_prefix']}_{index}{ext}"
                out_path.write_bytes(base64.b64decode(item["data"]))
                report["saved_files"].append(str(out_path))

        task["report_path"].write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "success": True,
            "task_index": task["task_index"],
            "task_token": task["task_token"],
            "report_path": str(task["report_path"]),
            "saved_files": report["saved_files"],
            "response_texts": report["response_texts"],
        }
    except Exception as exc:
        error_body = None
        if isinstance(exc, requests.HTTPError) and exc.response is not None:
            error_body = exc.response.text
        report["error"] = {
            "message": str(exc),
            "http_body": error_body,
        }
        task["report_path"].write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "success": False,
            "task_index": task["task_index"],
            "task_token": task["task_token"],
            "report_path": str(task["report_path"]),
            "error": report["error"],
        }


def _write_batch_report(
    report_path: Path,
    tasks: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    requested_max_concurrent: int,
    effective_max_concurrent: int,
) -> None:
    success_count = sum(1 for item in results if item["success"])
    failed_count = len(results) - success_count
    report = {
        "batch_summary": {
            "task_count": len(tasks),
            "requested_max_concurrent": requested_max_concurrent,
            "effective_max_concurrent": effective_max_concurrent,
            "success_count": success_count,
            "failed_count": failed_count,
        },
        "tasks": [
            {
                "task_index": task["task_index"],
                "task_token": task["task_token"],
                "project_name": task["project_name"],
                "output_dir": task["output_dir_value"],
                "report_path": next(
                    (
                        result["report_path"]
                        for result in results
                        if result["task_index"] == task["task_index"]
                    ),
                    None,
                ),
            }
            for task in tasks
        ],
        "results": sorted(results, key=lambda item: item["task_index"]),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="nano-banana 图像生成 CLI（未指定比例/质量时默认 16:9 和 4K；多任务自动并发）"
    )
    parser.add_argument("--prompt", help="提示词")
    parser.add_argument("--input-json", help="上游结构化请求 JSON 文件；支持对象、对象数组或 {\"tasks\": [...]} ")
    parser.add_argument("--model", default=_env_default_model(), help="模型名（默认读取 DXJ2_DEFAULT_MODEL）")
    parser.add_argument("--api-url", help="完整 API URL；不传则根据 ANYFAST_API_BASE_URL + model 组装")
    parser.add_argument("--api-key", help="API Key（不传则读取 .env）")
    parser.add_argument("--project-name", help="项目名；未传时测试任务映射为“测试”，临时任务映射为“临时”")
    parser.add_argument(
        "--task-kind",
        default="test",
        choices=["project", "test", "temp"],
        help="任务类型：project/test/temp；未传项目名时决定默认项目目录名",
    )
    parser.add_argument("--aspect-ratio", help="宽高比")
    parser.add_argument("--image-size", help="图像清晰度")
    parser.add_argument("--image-url", action="append", default=[], help="参考图 URL / 本地路径 / data URL / base64（可重复）")
    parser.add_argument("--request-id", help="可选请求 ID")
    parser.add_argument("--output-dir", help="输出目录")
    parser.add_argument("--output-filename", help="精确输出文件名（如 ScenePanel.png）")
    parser.add_argument("--filename-prefix", help="输出文件名前缀")
    parser.add_argument("--timeout", type=int, default=180, help="HTTP 超时秒数")
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=DEFAULT_MAX_CONCURRENT,
        help=f"多任务最大并发数（默认 {DEFAULT_MAX_CONCURRENT}，硬上限 {HARD_MAX_CONCURRENT}）",
    )
    parser.add_argument("--save-images", dest="save_images", action="store_true", default=True)
    parser.add_argument("--no-save-images", dest="save_images", action="store_false")
    parser.add_argument("--report-json", help="单任务时为任务报告路径；多任务时为批量汇总报告路径")
    parser.add_argument("--dry-run", action="store_true", help="仅打印 payload，不调用 API")
    parser.add_argument("--print-payload", action="store_true", help="打印最终请求 payload")
    return parser


def run_generation_from_docs(
    input_docs: List[Dict[str, Any]],
    *,
    model: Optional[str] = None,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    project_name: Optional[str] = None,
    task_kind: str = "test",
    aspect_ratio: Optional[str] = None,
    image_size: Optional[str] = None,
    image_urls: Optional[List[str]] = None,
    request_id: Optional[str] = None,
    output_dir: Optional[str] = None,
    output_filename: Optional[str] = None,
    filename_prefix: Optional[str] = None,
    timeout: int = 180,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    save_images: bool = True,
    report_json: Optional[str] = None,
    dry_run: bool = False,
    print_payload: bool = False,
) -> Dict[str, Any]:
    requested_max_concurrent = _normalize_max_concurrent(max_concurrent)
    args = argparse.Namespace(
        prompt=None,
        input_json=None,
        model=model or _env_default_model(),
        api_url=api_url,
        api_key=api_key,
        project_name=project_name,
        task_kind=task_kind,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
        image_url=image_urls or [],
        request_id=request_id,
        output_dir=output_dir,
        output_filename=output_filename,
        filename_prefix=filename_prefix,
        timeout=timeout,
        max_concurrent=requested_max_concurrent,
        save_images=save_images,
        report_json=report_json,
        dry_run=dry_run,
        print_payload=print_payload,
    )

    run_stamp = _now_stamp()
    tasks = [
        _prepare_task(
            args=args,
            input_doc=input_doc,
            task_index=index,
            task_count=len(input_docs),
            run_stamp=run_stamp,
        )
        for index, input_doc in enumerate(input_docs, start=1)
    ]

    if print_payload or dry_run:
        _print_payloads(tasks)

    if dry_run:
        return {
            "success": True,
            "task_count": len(tasks),
            "success_count": len(tasks),
            "failed_count": 0,
            "results": [],
            "batch_report_path": None,
            "effective_max_concurrent": min(len(tasks), requested_max_concurrent) if tasks else 0,
        }

    resolved_api_key = api_key or _env_api_key()
    if not resolved_api_key:
        raise ValueError("缺少 API Key。请设置 ANYFAST_API_KEY / GEMINI_API_KEY，或显式传入 api_key。")

    task_count = len(tasks)
    effective_max_concurrent = min(task_count, requested_max_concurrent) if task_count > 1 else 1

    if task_count == 1:
        result = _execute_task(
            task=tasks[0],
            api_key=resolved_api_key,
            timeout=timeout,
            save_images=save_images,
        )
        return {
            "success": bool(result["success"]),
            "task_count": 1,
            "success_count": 1 if result["success"] else 0,
            "failed_count": 0 if result["success"] else 1,
            "results": [result],
            "batch_report_path": None,
            "effective_max_concurrent": 1,
        }

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=effective_max_concurrent) as executor:
        future_map = {
            executor.submit(
                _execute_task,
                task=task,
                api_key=resolved_api_key,
                timeout=timeout,
                save_images=save_images,
            ): task
            for task in tasks
        }
        for future in as_completed(future_map):
            results.append(future.result())

    batch_report_path = _build_batch_report_path(
        report_json=report_json,
        output_dirs=[task["output_dir"] for task in tasks],
        run_stamp=run_stamp,
    )
    _write_batch_report(
        report_path=batch_report_path,
        tasks=tasks,
        results=results,
        requested_max_concurrent=requested_max_concurrent,
        effective_max_concurrent=effective_max_concurrent,
    )
    success_count = sum(1 for item in results if item["success"])
    failed_count = len(results) - success_count
    return {
        "success": failed_count == 0,
        "task_count": len(results),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results,
        "batch_report_path": str(batch_report_path),
        "effective_max_concurrent": effective_max_concurrent,
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        requested_max_concurrent = _normalize_max_concurrent(args.max_concurrent)
    except ValueError as exc:
        print(f"❌ 参数校验失败: {exc}")
        return 1

    input_docs: List[Dict[str, Any]] = [{}]
    if args.input_json:
        try:
            input_docs = _extract_input_docs(_load_json(args.input_json))
        except Exception as exc:
            print(f"❌ 读取 input_json 失败: {exc}")
            return 1

    run_stamp = _now_stamp()
    try:
        tasks = [
            _prepare_task(args=args, input_doc=input_doc, task_index=index, task_count=len(input_docs), run_stamp=run_stamp)
            for index, input_doc in enumerate(input_docs, start=1)
        ]
    except ValueError as exc:
        print(f"❌ 参数校验失败: {exc}")
        return 1

    if args.print_payload or args.dry_run:
        _print_payloads(tasks)

    if args.dry_run:
        return 0

    api_key = args.api_key or _env_api_key()
    if not api_key:
        print("❌ 缺少 API Key。请设置 ANYFAST_API_KEY / GEMINI_API_KEY，或传 --api-key")
        return 1

    task_count = len(tasks)
    effective_max_concurrent = min(task_count, requested_max_concurrent) if task_count > 1 else 1

    if task_count == 1:
        result = _execute_task(
            task=tasks[0],
            api_key=api_key,
            timeout=args.timeout,
            save_images=args.save_images,
        )
        if result["success"]:
            print(f"✅ 调用完成，报告已写入: {result['report_path']}")
            if result["saved_files"]:
                print("✅ 图片文件：")
                for saved_file in result["saved_files"]:
                    print(f"  - {saved_file}")
            if result["response_texts"]:
                print("ℹ️ 文本返回：")
                for item in result["response_texts"]:
                    print(f"  - {item}")
            return 0

        print(f"❌ 调用失败，报告已写入: {result['report_path']}")
        print(f"❌ 错误: {result['error']['message']}")
        return 1

    print(
        f"🚀 批量并发模式：{task_count} 个任务，最大并发 {effective_max_concurrent}"
        f"（请求值 {requested_max_concurrent}，硬上限 {HARD_MAX_CONCURRENT}）"
    )

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=effective_max_concurrent) as executor:
        future_map = {
            executor.submit(
                _execute_task,
                task=task,
                api_key=api_key,
                timeout=args.timeout,
                save_images=args.save_images,
            ): task
            for task in tasks
        }
        for future in as_completed(future_map):
            result = future.result()
            results.append(result)
            if result["success"]:
                print(f"✅ 任务 {result['task_index']} 完成: {result['report_path']}")
            else:
                print(f"❌ 任务 {result['task_index']} 失败: {result['report_path']}")

    batch_report_path = _build_batch_report_path(
        report_json=args.report_json,
        output_dirs=[task["output_dir"] for task in tasks],
        run_stamp=run_stamp,
    )
    _write_batch_report(
        report_path=batch_report_path,
        tasks=tasks,
        results=results,
        requested_max_concurrent=requested_max_concurrent,
        effective_max_concurrent=effective_max_concurrent,
    )

    success_count = sum(1 for item in results if item["success"])
    failed_count = len(results) - success_count
    print(f"📄 批量汇总报告: {batch_report_path}")
    print(f"📊 批量结果: 成功 {success_count}，失败 {failed_count}")
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

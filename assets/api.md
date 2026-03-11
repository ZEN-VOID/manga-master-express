# nano-banana / AnyFast 接口摘要

基于以下配置与官方文档：
- 平台地址：`https://www.anyfas.ai`
- API 基础端点：`https://fw2afus.ent.acc.kurtisasia.com`
- 文档：`https://docs.anyfast.ai`
- 默认模型：`gemini-3.1-flash-image-preview`

## 1. 基本信息

- 平台地址：
  - `https://www.anyfas.ai`
- API 基础端点：
  - `https://fw2afus.ent.acc.kurtisasia.com`
- 请求地址模板：
  - `<ANYFAST_API_BASE_URL>/v1beta/models/<model>:generateContent`
- 认证方式：
  - query 参数 `?key=YOUR_API_KEY`
- 请求方式：
  - `POST`
- 请求格式：
  - Gemini 原生 `generateContent`

## 2. 文档定义的关键请求字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 当前技能默认使用 `gemini-3.1-flash-image-preview`，由 URL path 承载 |
| `contents` | object[] | 是 | 内容数组 |
| `contents[].parts[].text` | string | 是/可选 | 文本提示内容 |
| `contents[].parts[].inline_data` | object | 否 | 参考图像输入 |
| `contents[].parts[].inline_data.mime_type` | string | 是 | 图片 MIME 类型，如 `image/png` |
| `contents[].parts[].inline_data.data` | string | 是 | 图片 base64 数据 |
| `generationConfig.responseModalities` | string[] | 是 | 推荐 `["TEXT","IMAGE"]` |
| `generationConfig.imageConfig.aspectRatio` | string | 是 | 仅允许 `1:1` `3:4` `4:3` `9:16` `16:9` |
| `generationConfig.imageConfig.imageSize` | string | 是 | 仅允许 `1K` `2K` `4K` |

## 3. 本技能的本地执行契约

- 若 `aspect_ratio` 未明确指定，默认注入：`16:9`
- 若 `image_size` 未明确指定，默认注入：`4K`
- 若 `image_size` 输入为小写 `k`，调用前规范化为大写 `K`
- 若未显式传 `--model`，默认使用 `.env` 中的 `DXJ2_DEFAULT_MODEL=gemini-3.1-flash-image-preview`
- API URL 从 `.env` 中的 `ANYFAST_API_BASE_URL` 组装
- 默认输出目录为 `output/影片/[项目名]/5-API/image/nano-banana/`
- 若未传 `project_name`：
  - `task_kind=test` -> `[项目名]=测试`
  - `task_kind=temp` -> `[项目名]=临时`
- 若承接上游文档，必须先收束到同一套内部字段，再转为原生格式
- 若有参考图，必须统一转译为 `inline_data`，不能直接 URL 透传

## 4. 响应字段摘要

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `candidates` | array | 候选输出 |
| `candidates[].content.parts[].inlineData` | object | 生成图片的 base64 数据（AnyFast 实测返回 camelCase） |
| `candidates[].content.parts[].inlineData.mimeType` | string | 图片 MIME 类型 |
| `candidates[].content.parts[].inlineData.data` | string | 图片 base64 数据 |
| `candidates[].content.parts[].inline_data` | object | 兼容性回退写法，脚本同时兼容 snake_case |
| `candidates[].content.parts[].text` | string | 模型文本说明 |
| `candidates[].finishReason` | string | 输出结束原因 |

## 5. 示例请求

```bash
curl -X POST "https://fw2afus.ent.acc.kurtisasia.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {
        "parts": [{"text": "生成一张高质量的肖像照片"}]
      }
    ],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "3:4",
        "imageSize": "2K"
      }
    }
  }'
```

## 6. 技能建议调用

```bash
python3 .codex/skills/aigc2026/5-API/image/nano-banana/scripts/nano_banana_generate.py \
  --project-name "测试" \
  --task-kind test \
  --prompt "一只雨夜中的黑猫，电影剧照感" \
  --dry-run --print-payload
```

预期：
- payload 中即使未手传 `--aspect-ratio / --image-size`，也应看到：
  - `"aspectRatio": "16:9"`
  - `"imageSize": "4K"`

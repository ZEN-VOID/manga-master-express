## 项目概述
- **名称**: Seedance视频脚本大师
- **功能**: 将小说原文转换为完整的视频脚本设计方案，并自动生成场景/角色/道具设计图

### 输出目录结构
```
output/
└── [影片名]/
    ├── 图像/
    │   ├── 场景_场景名_编号.png
    │   ├── 角色_角色名_编号.png
    │   └── 道具_道具名_编号.png
    └── 文本/
        ├── 格式化剧本_时间戳.md
        ├── 全局风格设计_时间戳.md
        ├── 视频脚本_时间戳.md
        ├── 场景设计_时间戳.md
        ├── 角色设计_时间戳.md
        └── 道具设计_时间戳.md
```

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| script_formatter | `nodes/script_formatter_node.py` | agent | 剧本格式化编排 | - | `config/script_formatter_llm_cfg.json` |
| global_style | `nodes/global_style_node.py` | agent | 全局风格设计（导演层级底层调性） | - | `config/global_style_llm_cfg.json` |
| storyboard_planner | `nodes/storyboard_planner_node.py` | agent | 分镜规划编辑 | - | `config/storyboard_planner_llm_cfg.json` |
| scene_orchestrator | `nodes/scene_orchestrator_node.py` | agent | 场景全链路编排（JSON输出，含场景宝典+实体列表） | - | `config/scene_orchestrator_llm_cfg.json` |
| character_orchestrator | `nodes/character_orchestrator_node.py` | agent | 角色全链路编排（JSON输出，含角色小传+实体列表） | - | `config/character_orchestrator_llm_cfg.json` |
| prop_orchestrator | `nodes/prop_orchestrator_node.py` | agent | 道具全链路编排（JSON输出，含道具物语+实体列表） | - | `config/prop_orchestrator_llm_cfg.json` |
| scene_image_gen | `nodes/scene_image_gen_node.py` | task | 场景生图（调用nano-banana API） | - | - |
| character_image_gen | `nodes/character_image_gen_node.py` | task | 角色生图（调用nano-banana API） | - | - |
| prop_image_gen | `nodes/prop_image_gen_node.py` | task | 道具生图（调用nano-banana API） | - | - |
| merge_designs | `nodes/merge_designs_node.py` | task | 汇聚设计结果和图片 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

> 注：场景/角色/道具拆解节点（parser）已移除，编排节点输出JSON直接含实体列表供生图消费。

## 工作流结构
```
小说原文
    ↓
剧本格式化编排 (script_formatter)
    ↓
全局风格设计 (global_style)
    ↓ 输出：全局风格提示词前缀
    ↓
分镜规划编辑 (storyboard_planner)
    ↓ 引用：全局风格提示词
    ↓
┌─────────────────────────────────────────┐
│    三路并行：设计阶段（JSON输出含实体列表） │
├─────────────────┬───────────────────────┤
│ 场景全链路编排   │ 角色全链路编排  │ 道具全链路编排 │
│ (场景宝典)       │ (角色小传)       │ (道具物语)    │
└─────────────────┴───────────────────────┘
    ↓ 编排输出JSON直接含实体列表，无需拆解节点
┌─────────────────────────────────────────┐
│          三路并行：生图阶段               │
├─────────────────┬───────────────────────┤
│ 场景生图        │ 角色生图       │ 道具生图       │
│ scene_image_gen  │ character_image_gen    │ prop_image_gen  │
└─────────────────┴───────────────────────┘
    ↓
汇聚设计结果 (merge_designs)
    ↓
最终输出
```

## 全局风格提示词传递链
```
global_style_node
    ↓ global_style_prompt
    ├─→ storyboard_planner (风格字段引用)
    ├─→ scene_orchestrator (style_seed_en继承)
    ├─→ character_orchestrator (style_prompt_200_en继承)
    └─→ prop_orchestrator (style_statement继承)
```

## 技能使用
- 剧本格式化节点：使用大语言模型技能（LLM）
- 全局风格设计节点：使用大语言模型技能（LLM）
- 分镜规划节点：使用大语言模型技能（LLM）
- 场景全链路编排节点：使用大语言模型技能（LLM）
- 角色全链路编排节点：使用大语言模型技能（LLM）
- 道具全链路编排节点：使用大语言模型技能（LLM）
- 场景/角色/道具生图节点：调用nano-banana (AnyFast Gemini Image Generation) API

## 外部API配置
生图节点需要配置以下环境变量：
- `ANYFAST_API_KEY` 或 `GEMINI_API_KEY`: API密钥
- `ANYFAST_API_BASE_URL`: API基础端点（默认: `https://fw2afus.ent.acc.kurtisasia.com`）
- `DXJ2_DEFAULT_MODEL`: 默认模型（默认: `gemini-3.1-flash-image-preview`）

## 输出产物
1. **格式化剧本** (`formatted_script`): 场景标题、对白、内心独白、旁白、动作画面
2. **全局风格设计文档** (`global_style_path`): 导演层级底层调性
   - **输出路径**: `output/[项目名]/文本/全局风格设计_[时间戳].md`
   - **文档结构**: 基本信息 → 风格参数 → 六要素分解 → 全局风格提示词
   - **六要素模型**:
     1. 核心定性：风格本质与叙事定性
     2. 技术栈：渲染管线、摄影语法、技术语言约束
     3. 光影色彩：光照模型、色彩脚本、氛围营造
     4. 构图空间：镜头调度、景别关系、空间层次
     5. 动态质感：运动模糊、残影拖尾、颗粒与材质反馈
     6. 规格排除：分辨率、画幅、禁用项、输出格式
   - **最佳范例参考**（在系统提示词中作为风格参照）:
     - 国风2D赛璐璐风格
     - 追光动画3D国漫风格
     - 徐克暗黑东方玄幻风格
     - 真人古装影视风格
3. **视频脚本** (`video_script`): 分镜组ID、场景、角色、道具、风格、要求
4. **场景设计文档** (`scene_design`): A/B/C三阶段输出
5. **角色设计文档** (`character_design`): A/B/C三阶段输出
6. **道具设计文档** (`prop_design`): A/B/C三阶段输出
7. **场景图片** (`scene_images`): 生成的场景设计图
8. **角色图片** (`character_images`): 生成的角色设计图
9. **道具图片** (`prop_images`): 生成的道具设计图

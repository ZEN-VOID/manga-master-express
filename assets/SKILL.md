---
name: "1.1-全局风格"
version: "v2.1"
description: |
  导演层级的底层调性定义技能：确立全片视觉媒介、渲染技术栈与美学范式，并输出可供下游继承的无污染全局风格底座。
  默认产出 `叙事类型研究.md`、`全局风格基调.md`，在用户显式要求原文直通时切换为项目级 `Canonical Style Lock` 保真落盘。
  <triggers>
  - 项目启动阶段的视觉媒介选择
  - 确立全片的底层渲染逻辑与美学基调
  - 生成用于下游 AIGC 模块的“无污染”全局风格前缀
  </triggers>
tools: [Read, Write, Edit, Glob, Grep]
color: "#4682B4"
---

# 1.1-全局风格 (Visual Tone & Narrative Foundation)

> **核心理念**: 导演是底层协议的制定者。
> 全局风格提示词必须是“透明的胶片”，而非“具体的画作”。

## 1. 功能描述

- 本技能负责确立全片视觉媒介、渲染管线与美学范式。
- 默认输出是可被角色、场景、道具、分镜无污染继承的项目级底层风格协议。
- 当用户显式要求“完全使用上述 / 原文直通 / 逐字继承 / 不要净化”时，切换到 `R4-显式风格锁定`，以项目级 `Canonical Style Lock` 形式保真落盘。

## 2. 专业领域

| 层级 | 领域 |
| --- | --- |
| Primary | Art Direction, Rendering Pipeline, Film Aesthetics |
| Secondary | Visual Communication, Stylistic Consistency, Prompt Engineering |
| Standards | Non-Pollution, Medium Specificity, Artistic Paradigm |

## 3. 风格语气

- **纯粹性**: 专注技术栈与美学流派，不越权决定下游对象细节。
- **架构感**: 输出面向整片继承的通用渲染底座。
- **严谨性**: 默认拒绝具象描述，使用可执行的媒介、管线、流派术语。

## 4. 任务规则

### 核心任务

1. 解构叙事与世界观，产出 `叙事类型研究.md`。
2. 决定全片媒介属性（真人/2D/3D）与渲染技术栈。
3. 选择全片美学范式，并解释其如何服务叙事。
4. 锚定项目级叙事节奏档位（慢/中/快），为 `2-拍摄段落` 提供可执行字窗基准。
5. 在默认模式下蒸馏 200 字以内纯中文无污染风格提示词。
6. 在显式锁定模式下保留用户原文，落盘项目级 `Canonical Style Lock`。

### 行为规则（Mandatory - 边界防卫）

0. **显式风格锁定优先**: 当用户已提供完整风格段落，且明确要求“完全使用上述 / 原文直通 / 逐字继承 / 不要净化”时，必须切换到 `R4-显式风格锁定`。
1. **默认禁止色彩定义**: 不得包含具体颜色词（红、蓝、暖调等）。
2. **默认禁止材质定义**: 不得提及具体物质（青铜、金属、丝绸、木头等）。
3. **默认禁止构图定义**: 不得提及构图术语（中心对称、三分法、黄金分割等）。
4. **默认禁止摄影/运镜**: 不得提及焦段、光圈、光源位置、推拉摇移。
5. **默认专注底层**: 只描述“怎么渲染（HOW）”与“画风流派（WHAT STYLE）”，不描述“渲染什么（WHAT CONTENT）”。

> 说明：规则 1-5 为默认模式约束；命中 `R4-显式风格锁定` 后，由规则 0 覆盖执行，允许保留用户原文中的具体镜头与工艺语言，但不得擅自删改。

## 5. 核心约束

### 工匠级契约 (继承自 creative-skill-architect)

1. **反脚本化创作**:
   - 禁止模板填空式浅层生成。
   - 每个输出必须经过完整思维链推导。
   - 对“叙事基底 / 媒介 / 技术栈 / 流派 / 审计结论”分别独立思考。
   - **反理论废话**: 禁止“高级感 / 震撼 / 很电影”这类空词，必须落实为可执行的媒介、渲染或美学范式。
2. **深度思考验证**:
   - 每个选择必须能回答“为什么是这样”。
   - 每个媒介、技术栈、流派选择都必须能回溯到叙事证据或用户显式约束。
3. **质量刚性门槛**:
   - 总分 ≥ 90 方可通过。
   - 维度0: 契约遵循 < 8 一票否决。
   - 未达标必须返工，不得妥协。

## 6. 任务流程

1. 校验输入目录与引用来源：
   - 默认读取 `0-故事/0.2-预设`、`0-故事/0.3-参考`、`1-设定`。
   - 若 `0.2-预设` 缺失，兼容读取 `0-故事/2-预设/`。
2. 识别当前变量场景（VSM），确定路由策略。
3. 生成 `叙事类型研究.md` 的叙事与世界约束字段。
4. 生成 `全局风格基调.md` 的媒介、技术栈、流派、节奏锚定与审计字段。
5. 默认执行去污染审计；命中 `R4` 时执行原文保真审计。
6. 蒸馏最终风格提示词并落盘。
7. 执行字段通过检查与质量评分。

## 7. 输入来源

- 必需输入:
  - `output/影片/<项目名>/0-故事/0.2-预设/`
  - `output/影片/<项目名>/0-故事/0.3-参考/`
  - `output/影片/<项目名>/1-设定/`
- 兼容输入:
  - `output/影片/<项目名>/0-故事/2-预设/`
  - 已存在的 `1.1.1-叙事类型` 研究稿
- 可选输入:
  - 用户直接提供的风格原文
  - 用户关于媒介或流派的显式偏好
- 输入优先级:
  - 用户显式风格锁定 > 项目预设 > 叙事与设定推导 > 默认稳妥路由

## 8. 输出内容模板

### 8.1 模式A: 三段式 Markdown（默认）

`叙事类型研究.md` 必须至少包含：

```markdown
---
文档类型: narrative_research
project_name: <项目名>
---

## TL;DR
## 主题三联
## 世界三联
## 硬性字段
```

- `硬性字段` 必须显式包含：`年代（朝代）`、`地域`、`叙事类型`、`叙事节奏倾向`。

`全局风格基调.md` 必须至少包含：

```markdown
---
文档类型: global_style
project_name: <项目名>
scenario_profile: <R1/R2/R3/R4>
user_style_lock: <none/exact>
---

## 路由决议
## 媒介与技术栈
## 美学范式
## 叙事节奏锚定
## 审计结论
## 最终画面风格提示词
```

- 命中 `R4-显式风格锁定` 时，必须追加 `## 用户锁定风格原文` 小节并完整保留原文。
- `## 叙事节奏锚定` 必须至少包含 4 行：
  - `- 节奏档位：慢节奏/中节奏/快节奏`
  - `- 判断依据：<题材、冲突密度、对白负载、信息压缩率等>`
  - `- 拍摄段落执行字窗：200-350字/组 / 350-500字/组 / 500-650字/组`
  - `- 回退规则：无明确逻辑根源时默认中节奏`

### 8.2 模式B: 结构化 JSON（仅下游强依赖时启用）

- 模板文件：`templates/style_contract.json`
- 每次输出前必须动态读取模板，禁止凭记忆手写结构。
- 最终输出只能是 1 个 JSON 对象，不附加解释文字。
- JSON 主要用于跨模块机读，不替代两份 Markdown 主文档。

### 8.3 统一字段主表（Mandatory）

| field_id | 输出位置/字段 | 内容要求 | 证据来源 | 默认责任Step | 质量维度 | 失败码 |
| --- | --- | --- | --- | --- | --- | --- |
| FIELD-NARRATIVE-RESEARCH | `叙事类型研究.md / TL;DR + 主题三联 + 世界三联 + 硬性字段` | 明确叙事类型、主题内核、情感目标、时间/地域/人文约束 | `0-故事`、预设、参考、既有研究稿 | Step S2-NARRATIVE | 叙事研究准确性 | `FAIL-NARRATIVE-WEAK` |
| FIELD-STYLE-ROUTE | `全局风格基调.md / ## 路由决议` | 明确当前走 `R1/R2/R3/R4` 及其原因 | VSM 判定 + 用户显式约束 | Step S4-ROUTE | 路由正确性 | `FAIL-ROUTE-CONFLICT` |
| FIELD-MEDIUM-STACK | `全局风格基调.md / ## 媒介与技术栈` | 明确真人/2D/3D 及 2-3 个核心渲染技术栈 | 叙事研究、用户偏好、参考资料 | Step S5-MEDIUM | 媒介匹配度与技术可执行性 | `FAIL-MEDIUM-MISMATCH` |
| FIELD-AESTHETIC-PARADIGM | `全局风格基调.md / ## 美学范式` | 明确全局美学流派、气质与服务叙事的理由 | 叙事基底 + 技术栈选择 | Step S6-PARADIGM | 流派精准度 | `FAIL-PARADIGM-BLUR` |
| FIELD-PACING-ANCHOR | `全局风格基调.md / ## 叙事节奏锚定` | 明确慢/中/快节奏档位、判断依据、拍摄段落执行字窗；若无明确逻辑根源，显式回退为中节奏 | 叙事研究 + 用户显式节奏信号 + 冲突密度/对白负载/信息压缩率分析 | Step S7-PACING | 节奏锚定可执行性 | `FAIL-PACING-ANCHOR` |
| FIELD-POLLUTION-AUDIT | `全局风格基调.md / ## 审计结论` | 默认给出去污染审计结果；`R4` 给出原文保真审计结论 | 草稿文本 + 行为规则 + 用户原文 | Step S8-AUDIT | 审计合规性 | `FAIL-POLLUTION` / `FAIL-LOCK-BREAK` |
| FIELD-STYLE-PROMPT | `全局风格基调.md / ## 最终画面风格提示词` | 默认 200 字内纯中文无污染提示词；`R4` 允许用户原文直通 | 媒介、技术栈、流派、节奏锚定、审计结论 | Step S9-PROMPT | 提示词密度与可继承性 | `FAIL-PROMPT-WEAK` / `FAIL-LENGTH` |
| FIELD-STYLE-LOCK | `全局风格基调.md / ## 用户锁定风格原文` | 仅在 `R4` 时落盘完整原文与来源 | 用户显式风格原文 | Step S8-AUDIT | 原文保真性 | `FAIL-LOCK-BREAK` |
| FIELD-STYLE-CONTRACT | `style_contract.json / content.*` | 机读记录 narrative/style/pacing/audit/lock 关键字段 | 两份 Markdown 主文档与最终判定 | Step S10-RENDER | 输出结构与追溯性 | `FAIL-JSON-MISMATCH` |

## 9. 变量场景识别与策略映射

### 9.1 变量登记表（Variable Register）

| var_id | 变量层级 | 观测信号 | 状态集合 | 检测方法 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| V1-COMPLETENESS | 输入 | 上游设定与参考是否丰满 | `full/partial/sparse` | 检查 `0.2-预设`、`0.3-参考`、`1-设定` | P0 |
| V2-CONFLICT | 规则 | 用户预设与叙事推导是否冲突 | `harmonious/conflicting` | 对比用户显式偏好与叙事研究结论 | P1 |
| V3-POLLUTION | 输出 | 草稿中是否出现颜色/材质/构图/摄影污染项 | `clean/polluted` | 污染词与越权结构扫描 | P0 |
| V4-USER-STYLE-LOCK | 路由 | 用户是否显式要求原文直通 | `locked/unlocked` | 识别“完全使用上述/原文直通/不要净化/逐字继承” | P-1 |

### 9.2 情况判定表（Scenario Table）

| case_id | 触发谓词 | 置信度阈值 | 互斥关系 | 可并发关系 |
| --- | --- | --- | --- | --- |
| C0-LOCK | `V4-USER-STYLE-LOCK=locked` | 1.0 | 与 C1/C2/C3 互斥 | 无 |
| C1-STANDARD | `V1-COMPLETENESS=full` 且 `V3-POLLUTION=clean` | 0.9 | 与 C0 互斥 | 可并发 C2 |
| C2-DECONTAMINATE | `V3-POLLUTION=polluted` | 0.9 | 与 C0 互斥 | 可并发 C1/C3 |
| C3-BACKFILL | `V1-COMPLETENESS=sparse` | 0.8 | 与 C0 互斥 | 可并发 C2 |

### 9.3 策略映射矩阵（Case->Strategy Map）

| case_id | strategy_id | 执行步骤 | 质量门禁 | fallback_strategy_id | 升级条件 |
| --- | --- | --- | --- | --- | --- |
| C0-LOCK | R4-EXACT-LOCK | 保真解析用户原文并直通落盘 | 原文保真性 ≥ 9/10 | 无 | 发现删改、漏句或误净化 |
| C1-STANDARD | R1-STANDARD-INHERIT | 正常推导媒介、技术栈、流派并蒸馏无污染提示词 | 契约遵循 ≥ 8/10 | R2-DECONTAMINATE | 草稿出现污染项 |
| C2-DECONTAMINATE | R2-DECONTAMINATE | 强制清洗颜色、材质、构图、摄影越权项 | 审计合规性 ≥ 9/10 | R3-BACKFILL | 清洗后语义断裂 |
| C3-BACKFILL | R3-TYPE-BACKFILL | 根据叙事类型与世界约束反推稳妥渲染底座 | 逻辑自洽 ≥ 8/10 | 无 | 仍无法形成稳定底座 |

### 9.4 路由与回退卡（Routing Card）

| route_id | 启动条件 | 主输出 | 必备证据 | 回退触发 |
| --- | --- | --- | --- | --- |
| R1-STANDARD-INHERIT | 输入丰满且无显式锁定 | 无污染底层风格协议 | 叙事研究 + 媒介/技术栈/流派 | 出现污染项 |
| R2-DECONTAMINATE | 草稿污染 | 去污染后的净化结果 | 污染词审计 + 替换理由 | 语义被清洗空了 |
| R3-TYPE-BACKFILL | 输入稀疏 | 类型驱动的稳妥底座 | 类型、情感、时代约束 | 与用户显式偏好冲突 |
| R4-EXACT-LOCK | 用户显式原文直通 | `Canonical Style Lock` | 用户原文 + 锁定指令 | 原文被删改或误净化 |

## 10. 超级思维链规范

### 10.1 执行目标

- 本链路的目标不是“写一段风格描述”，而是生产一套可被下游稳定继承的项目级风格底座。
- 每一步必须回答：
  - 当前在生产哪个 `field_id`；
  - 依据什么叙事/用户/规则证据；
  - 结论将落到哪份文档哪个区块；
  - 未达标时如何返工。

### 10.2 标准链路（11 步）

| step_id | 聚焦字段(field_id) | 核心问题 | 生成动作 | 未达标信号 |
| --- | --- | --- | --- | --- |
| S1-INPUT | `FIELD-NARRATIVE-RESEARCH`, `FIELD-STYLE-ROUTE` | 输入是否完整且用户意图可判定 | 读取预设、参考、设定与用户风格原文，建立输入范围 | `FAIL-INPUT-SCOPE` |
| S2-NARRATIVE | `FIELD-NARRATIVE-RESEARCH` | 叙事类型、主题、情感和世界约束是什么 | 生成叙事研究的 TL;DR、主题三联、世界三联和硬性字段 | `FAIL-NARRATIVE-WEAK` |
| S3-CONTEXT | `FIELD-NARRATIVE-RESEARCH`, `FIELD-STYLE-ROUTE` | 叙事与世界约束对风格底座施加什么边界 | 明确时代、人文、受众、题材对媒介与风格的限制 | `FAIL-CONTEXT-LOOSE` |
| S4-ROUTE | `FIELD-STYLE-ROUTE` | 当前应走哪条风格路由 | 在 `R1/R2/R3/R4` 中锁定主路由并记录原因 | `FAIL-ROUTE-CONFLICT` |
| S5-MEDIUM | `FIELD-MEDIUM-STACK` | 哪种视觉媒介与技术栈最匹配 | 决定真人/2D/3D 与 2-3 个核心技术栈 | `FAIL-MEDIUM-MISMATCH` |
| S6-PARADIGM | `FIELD-AESTHETIC-PARADIGM` | 什么美学范式最能承载叙事目标 | 选择流派并解释其与叙事、媒介的因果关系 | `FAIL-PARADIGM-BLUR` |
| S7-PACING | `FIELD-PACING-ANCHOR` | 项目更适合慢/中/快哪种叙事节奏，拍摄段落应继承什么字窗 | 基于题材、冲突密度、对白负载、信息密度锁定节奏档位；缺少明确逻辑根源时默认中节奏 | `FAIL-PACING-ANCHOR` |
| S8-AUDIT | `FIELD-POLLUTION-AUDIT`, `FIELD-STYLE-LOCK` | 草稿应去污染还是保真锁定 | 默认执行污染扫描；`R4` 执行原文逐句保真校验 | `FAIL-POLLUTION` / `FAIL-LOCK-BREAK` |
| S9-PROMPT | `FIELD-STYLE-PROMPT` | 最终风格提示词如何蒸馏 | 默认压缩为 200 字内纯中文；`R4` 允许原文直通 | `FAIL-PROMPT-WEAK` / `FAIL-LENGTH` |
| S10-RENDER | `FIELD-NARRATIVE-RESEARCH`, `FIELD-STYLE-ROUTE`, `FIELD-MEDIUM-STACK`, `FIELD-AESTHETIC-PARADIGM`, `FIELD-PACING-ANCHOR`, `FIELD-POLLUTION-AUDIT`, `FIELD-STYLE-PROMPT`, `FIELD-STYLE-LOCK`, `FIELD-STYLE-CONTRACT` | 字段如何落盘到两份主文档与 JSON 契约 | 生成 Markdown 主文档，并在启用机读模式时生成 JSON | `FAIL-OUTPUT-SCHEMA` / `FAIL-JSON-MISMATCH` |
| S11-QA | `FIELD-STYLE-CONTRACT` | 最终是否通过门禁且可被下游继承 | 汇总字段状态、评分、失败码与返工入口 | `FAIL-QUALITY` |

### 10.3 弹性裁剪（8-15 步）

- 允许裁剪到 8-15 步，但必须保留四阶段：
  - 理解与定位（S1-S3）
  - 策略与规划（S4-S7）
  - 审计与蒸馏（S8-S9）
  - 落盘与验收（S10-S11）
- 裁剪时必须说明合并了哪些字段生产动作，以及为何不损失判定能力。
- 禁止把 `S8-AUDIT` 与 `S9-PROMPT` 合并；先审计，再蒸馏。

### 10.4 禁止模式

1. 只罗列引擎名字，不解释其如何服务叙事。
2. 在默认模式下越权写入颜色、材质、构图、摄影细节。
3. 命中 `R4` 却把用户原文擅自抽象化、压缩或删改。
4. 只写最终提示词，不落盘路由决议、审计结论和媒介依据。
5. 未对项目节奏档位给出可执行锚定，导致下游拍摄段落只能退回单一字窗。

## 11. 质量评估与闭环验证

### 11.1 评分矩阵

| 维度 | 指标 | 分值 |
| --- | --- | --- |
| 维度0: 契约遵循 | 是否遵守默认无污染原则或 `R4` 原文保真原则 | __/10 |
| 维度1 | 输入完备性（是否读取了必要预设、参考、设定与用户约束） | __/10 |
| 维度2 | 叙事研究准确性（`FIELD-NARRATIVE-RESEARCH`） | __/10 |
| 维度3 | 世界约束明确性（时间/地域/人文是否能支撑风格底座） | __/10 |
| 维度4 | 路由正确性（`FIELD-STYLE-ROUTE`） | __/10 |
| 维度5 | 媒介匹配度（`FIELD-MEDIUM-STACK`） | __/10 |
| 维度6 | 技术栈可执行性（技术词是否可落到下游） | __/10 |
| 维度7 | 流派精准度（`FIELD-AESTHETIC-PARADIGM`） | __/10 |
| 维度8 | 节奏锚定可执行性（`FIELD-PACING-ANCHOR`） | __/10 |
| 维度9 | 审计合规性（`FIELD-POLLUTION-AUDIT` / `FIELD-STYLE-LOCK`） | __/10 |
| 维度10 | 提示词密度与可继承性（`FIELD-STYLE-PROMPT`） | __/10 |
| 维度11 | 输出结构与追溯性（两份 Markdown 与 JSON 契约一致） | __/10 |

### 字段通过表

| field_id | 质量维度 | 通过标准 | 失败码 | 返工入口 |
| --- | --- | --- | --- | --- |
| FIELD-NARRATIVE-RESEARCH | 叙事研究准确性 | `叙事类型研究.md` 完整包含 TL;DR、主题三联、世界三联与三项硬字段 | `FAIL-NARRATIVE-WEAK` | 回到 Step S2-NARRATIVE 重做研究 |
| FIELD-STYLE-ROUTE | 路由正确性 | `R1/R2/R3/R4` 仅存在一个主路由且原因完整 | `FAIL-ROUTE-CONFLICT` | 回到 Step S4-ROUTE 重做路由裁决 |
| FIELD-MEDIUM-STACK | 媒介匹配度与技术可执行性 | 明确媒介 + 2-3 个技术栈，且与叙事不冲突 | `FAIL-MEDIUM-MISMATCH` | 回到 Step S5-MEDIUM 重做媒介与技术栈 |
| FIELD-AESTHETIC-PARADIGM | 流派精准度 | 流派结论清晰，且说明其如何服务叙事目标 | `FAIL-PARADIGM-BLUR` | 回到 Step S6-PARADIGM 重选流派 |
| FIELD-PACING-ANCHOR | 节奏锚定可执行性 | 明确慢/中/快节奏、判断依据、对应拍摄段落字窗；无明确逻辑根源时显式回退中节奏 | `FAIL-PACING-ANCHOR` | 回到 Step S7-PACING 重做节奏锚定 |
| FIELD-POLLUTION-AUDIT | 审计合规性 | 默认模式无污染越权项；`R4` 模式无漏句、无改写、无误净化 | `FAIL-POLLUTION` / `FAIL-LOCK-BREAK` | 回到 Step S8-AUDIT 重审计 |
| FIELD-STYLE-PROMPT | 提示词密度与可继承性 | 默认模式为 200 字内纯中文高密度提示词；`R4` 模式原文完整可继承 | `FAIL-PROMPT-WEAK` / `FAIL-LENGTH` | 回到 Step S9-PROMPT 重蒸馏 |
| FIELD-STYLE-LOCK | 原文保真性 | 仅 `R4` 时出现，且原文、来源、锁定标记完整一致 | `FAIL-LOCK-BREAK` | 回到 Step S8-AUDIT 重做保真核对 |
| FIELD-STYLE-CONTRACT | 输出结构与追溯性 | 两份 Markdown 与 `style_contract.json` 一致，字段可回查 | `FAIL-OUTPUT-SCHEMA` / `FAIL-JSON-MISMATCH` | 回到 Step S10-RENDER 重做落盘 |

### 11.3 字段同源回环说明（Mandatory）

- 输出前回答：当前在生产哪个 `field_id`，依据什么证据，为什么要有这个字段。
- 输出中回答：该 `field_id` 落在 `叙事类型研究.md`、`全局风格基调.md` 还是 `style_contract.json`。
- 输出后回答：该 `field_id` 是否达标、对应什么失败码、从哪里返工。
- 禁止“思维链看 Step、质量表看另一套对象”；所有返工必须先回到字段责任 Step。

### 11.4 验收规则

- 总分：`__ / 120`
- PASS: 维度0 >= 8 且总分 >= 90
- FAIL-COVENANT: 维度0 < 8
- FAIL-QUALITY: 维度0 >= 8 且总分 < 90

### 11.5 失败码（Mandatory）

- `FAIL-INPUT-SCOPE`: 输入范围或用户约束未锁定。
- `FAIL-NARRATIVE-WEAK`: 叙事研究字段缺失或推导空泛。
- `FAIL-CONTEXT-LOOSE`: 世界约束未形成有效边界。
- `FAIL-ROUTE-CONFLICT`: 主路由不唯一或错判。
- `FAIL-MEDIUM-MISMATCH`: 媒介与叙事严重不匹配。
- `FAIL-PARADIGM-BLUR`: 流派命名或叙事服务理由含混。
- `FAIL-PACING-ANCHOR`: 未能给出可执行的慢/中/快节奏锚定，或未在无明确逻辑根源时回退中节奏。
- `FAIL-POLLUTION`: 默认模式出现越权污染项。
- `FAIL-LOCK-BREAK`: 显式锁定模式下发生删改、漏句、误净化。
- `FAIL-PROMPT-WEAK`: 最终风格提示词密度不足、可继承性弱。
- `FAIL-LENGTH`: 默认模式提示词超 200 字或非纯中文。
- `FAIL-OUTPUT-SCHEMA`: Markdown 主文档结构不合规。
- `FAIL-JSON-MISMATCH`: JSON 契约与 Markdown 主文档不一致。
- `FAIL-QUALITY`: 评分未达标。

## 12. Root-Cause 执行契约

### Root-Cause 执行契约

1. **诊断顺序**:
   - 先查是否存在 `V4-USER-STYLE-LOCK=locked` 却误走到默认去污染路由。
   - 再查污染预防规则是否被绕过。
   - 再查媒介、技术栈、流派是否与叙事研究断链。
   - 再查 `## 叙事节奏锚定` 是否缺失、空泛，或本该默认中节奏却未显式回退。
2. **修复顺序**:
   - 先修字段主表、路由规则、审计门禁等源层契约，再修本地产物。
3. **Case 沉淀**:
   - 出现新的污染类型、显式锁定误判、字段缺失或跨文件不一致时，必须更新 `CONTEXT.md`。
4. **用户闭环格式**:
   - 汇报固定为：`根因位置 + 立即修复 + 系统预防修复`。

## 13. SKILL vs CONTEXT Placement Matrix

- `SKILL.md`:
  - 放触发条件、输入输出契约、VSM 路由、字段主表、超级思维链、评分门禁、失败码与 DoD。
- `CONTEXT.md`:
  - 放真实案例、污染词库、媒介决策启发式、修复链、晋升候选与复盘证据。

## 14. 完成定义（DoD）

- 产出 `叙事类型研究.md` 与 `全局风格基调.md` 两份主文档。
- `叙事类型研究.md` 显式包含 `年代（朝代）`、`地域`、`叙事类型` 三项硬字段。
- `叙事类型研究.md` 显式包含 `叙事节奏倾向` 硬字段。
- `全局风格基调.md` 显式包含路由决议、媒介与技术栈、美学范式、叙事节奏锚定、审计结论、最终风格提示词。
- 命中 `R4` 时，`全局风格基调.md` 必须包含 `user_style_lock: exact` 与 `用户锁定风格原文` 小节。
- 默认模式下最终风格提示词为 200 字内纯中文且无污染项。
- 启用 JSON 模式时，`templates/style_contract.json` 被动态加载，最终 JSON 与主文档一致。
- 字段通过表全部可回查到责任 Step，且评分满足 PASS 门槛。

# codebuddy-eco · 新生态脚手架

> **定位**：一个与具体业务领域无关、可直接 clone 改名使用的新生态治理底座。
> **设计原则**：以 [`CodeBuddy-会话中文风格统一-SOP.md`](../CodeBuddy-会话中文风格统一-SOP.md)（以下简称 SOP）为**治理基础**，以旧生态 `tvbox-eco` 为**结构借鉴**（仅学其目录骨架/技能契约/MANIFEST 形态，不搬其 TVBox 业务内容）。

## 一、这个生态装了什么

| 层 | 产物 | 作用 | SOP 依据 |
|---|---|---|---|
| 治理薄壳 | `.codebuddy/CODEBUDDY.md` | 内联铁律，手机/云端必加载 | 第 19 章① |
| 用户级基座 | `base/rules/core-8.md` → `~/.codebuddy/rules/` | 跨项目 8 条通用铁律唯一真源 | 第 20.9 章 C |
| 自动加载规则 | `.codebuddy/rules/zh-style.md` | 项目专属契约 + §8 轻量纪律（`alwaysApply:true`） | 第 19 章② / 20.9 |
| 条件规则 | `.codebuddy/rules/*.paths.md` | 情境契约，`paths` 命中才注入 | 第 20.9 章 A |
| 基建技能 ×4 | `.codebuddy/skills/*` | 进化/换机/灰度/产物治理 | 第 17/18 章 |
| 治理清单 | `.codebuddy/MANIFEST.json` | 依赖图+事件契约（轻量版 ecosys-conductor） | 第 18 章 |
| 台账 / 映射 | `docs/*.md` | schema/去重/降级台账 + 基座映射 + SOP 章节映射 | 第 20.9 章 |

## 二、四个基建技能（去 TVBox 化）

| 技能 | 用途 | 在新生态里怎么用 |
|---|---|---|
| `skill-evolution` | 复发问题自动固化成技能 | 平时不用管，第 3 次同类问题自动立项；是 SOP 第 17 章"经验复用"的自动化发动机 |
| `machine-bootstrap` | 一键换机/克隆工作副本 | 新设备/协作者加入时一条幂等命令重建副本（参数化 repo，无明文 token） |
| `feature-gate` | 特性开关+绞杀者切流 | 任何迭代走灰度，新旧并存、可回滚，杜绝大爆炸式改写 |
| `artifact-store` | 本地轻量化总闸·防手机卡顿 | 产物 LRU + 记忆/会话/上下文减负；优先复用官方原生（v2.51.0 按需加载+自动清理、/clear、Subagents、/compact），只兜底产物与超大主题文件 |

## 三、冷启动顺序（新项目照做）

```
1. git init                       ← 唯一真源就位（SOP 第 16 章）
2. 放好 .codebuddy/ 骨架          ← 本目录即模板
   + cp base/rules/core-8.md ~/.codebuddy/rules/   ← 装用户级基座（第六节）
3. 手机设"给 WorkBuddy 的指令"    ← SOP 第 19 章③ 跨端兜底
4. 三通道就位用 03-ACCEPTANCE 的 L2 三态实测确认（官方无 `machine-bootstrap --verify` 能力；脚本为可选件、未搬入本脚手架，不宣称通过）
5. 写业务 → feature-gate 做迭代
6. skill-evolution 后台自动沉淀；artifact-store 自动治理产物
```

## 四、与旧生态 tvbox-eco 的关系

- **借鉴**：目录分层（`.codebuddy/` 官方路径 vs 业务代码分离）、技能 `SKILL.md` 契约格式（frontmatter+触发词+边界）、`MANIFEST.json` 治理清单形态。
- **不借鉴**：tvbox-eco 的 23 条 `rules/core.json`、4 个 TVBox 专属能力技能（probe-hub/tvbox-source-hub/tvbox-inspect/tvbox-interface）、以及"钩子强制"体系（SOP 第 19 章已判：手机不跑钩子，新生态改用官方路径+薄壳兜底，不押钩子）。
- **仅提炼**：从其 23 条里去掉 TVBox 业务后，提炼 8 条通用铁律作用户级基座（见 `docs/base-rule-mapping.md`）。

## 五、去 TVBox 化改造清单（技能脚本落地时）

若要把 tvbox-eco 里对应技能的**真实脚本**搬过来（非必须，SKILL.md 已够触发），需做：
1. 去掉所有 `tvbox` / `D包` / `底包` / `线路` 等专属名词与业务契约；
2. `machine-bootstrap` 把写死的 clone 目标改为读 `BOOTSTRAP_REPO` 环境变量/参数；
3. `artifact-store` 把"远程"目标从 TVBox space 改为本生态资料库/IMA；
4. `skill-evolution` 清掉 references 里残留的 TVBox 案例，保留通用进化引擎。

> 原始参考实现见私有仓库 `tvbox342078879/tvbox-eco` 的 `archive/`（skill-evolution/feature-gate/artifact-store）与 `skills/machine-bootstrap/`。

## 六、规则侧三分离（SOP 20.9）

规则**不照搬** tvbox-eco 的 `hot/warm/cold` 冷热分层，改用官方「**作用域 × 触发 × 强制力**」三维度——旧生态把 23 条全塞「项目级 + alwaysApply + 押钩子」一格，还把台账混进 `core.json`，是手机端全休眠 + 巨型注册中心的病根。

| 格 | 落点 | 触发 | 内容 |
|---|---|---|---|
| 用户级常驻基座 | `base/rules/core-8.md` → `~/.codebuddy/rules/` | `alwaysApply:true` | 8 条通用铁律（跨项目去重） |
| 项目级常驻 | `.codebuddy/rules/zh-style.md` | `alwaysApply:true` | 项目专属 + §8 轻量纪律 |
| 项目级条件 | `.codebuddy/rules/*.paths.md` | `alwaysApply:false` + `paths` | 情境契约，命中才注入 |
| 治理台账 | `docs/rule-ledger.md` / `docs/base-rule-mapping.md` | 不进 context | schema/去重/降级/探针 |

安装用户级基座（一次配置、全项目生效）：

```bash
mkdir -p ~/.codebuddy/rules
cp base/rules/core-8.md ~/.codebuddy/rules/core-8.md
```

手机/云端经账号云同步加载；担心未同步则在「给 WorkBuddy 的指令」里内联 8 条（第 19 章③ 兜底）。逐条来源、schema 与验证判据见 `docs/base-rule-mapping.md`，全生态台账见 `docs/rule-ledger.md`。

# codebuddy-eco 生态项目 · 全量操作报告

> 性质：客观事实记录，不含分析评价。
> 时间范围：本会话全周期（含前期已完成工作）。
> 真源依据：本仓库内 `CodeBuddy-会话中文风格统一-SOP.md`、`codebuddy-eco/README.md`、`.codebuddy/MANIFEST.json`、`docs/governance.md`、各规则/技能文件，以及命令行 `ls` 实查结果、GitHub API / WebFetch 返回。

---

## 一、生态构想如何构想

- **目标**（SOP 第 0 章原文）：手机端会话页面全程简体中文、切换任意模型后输出风格保持一致，且**跨会话、换新手机都持续生效**。
- **出发点**（SOP 第 0 章结论）：用户最初设想的 `.codebuddy/project-prompt.md` 经核实**不是官方认可的自动加载路径**，新会话/新手机不会自动读取。
- **设计基线**（SOP 第 0.5 章）：采用官方"分层配置系统"——两个正交轴：
  - 轴 A：基础体验层 ↔ 能力执行层；
  - 轴 B：用户级（`~/.codebuddy/`）↔ 项目级（`.codebuddy/`）↔ 本地级（`*.local.json`）。
- **落地路径**（SOP 第 0 章 + 第 1 章官方机制对照表）：规则放入官方自动加载路径之一——项目级 `CODEBUDDY.md` / `.codebuddy/rules/*.md`，或用户级 `~/.codebuddy/CODEBUDDY.md` / `~/.codebuddy/rules/*.md`；规则在每次会话启动自动注入上下文。

---

## 二、期间查了哪些资料、做了哪些工作（含 SOP 拍板）

### 2.1 查阅的资料

| 类别 | 具体来源 | 获取方式 | 用途 |
|---|---|---|---|
| 官方文档 | CodeBuddy Code v2.51.0 发布说明、CLI Best Practices、CLI Memory 文档 | 文献引用（SOP/zh-style 标注） | 拍板强制链、手机防卡顿根因 |
| GitHub 仓库 | `github.com/tvbox342078879/tvbox-eco` | WebFetch / API | 旧生态本体，开搞时借鉴来源 |
| GitHub 仓库 | `github.com/Kylinx-code/codebuddy-memory-system` | WebFetch / API | 六层记忆系统，用户级 `~/.codebuddy/` 布局真源 |
| GitHub 仓库 | `github.com/Kylinx-code/memory-system` | WebFetch | 数据在 `~/.memory-system/` |
| GitHub 仓库 | `github.com/tvbox342078879/tvbox-skills-eco` | WebFetch / API | 技能快照，bootstrap 自动恢复 |
| GitHub 仓库 | `github.com/tvbox342078879/codebuddy-eco-rules` | API（建库+push） | 本项目部署包仓库（后建） |
| GitHub API | `api.github.com`（仓库列表、建库） | curl（带 PAT） | 查仓库状态、建库 |
| 历史对话 | 会话 jsonl 记录 | 本地读取 | 提取旧仓库地址 |

> 其中 `tvbox342078879/tvbox-eco` 经查询返回 **404**（已私有/删除）；其余仓库状态为"活"。

### 2.2 生成的 SOP

- **文件名**：`CodeBuddy-会话中文风格统一-SOP.md`
- **大小/时间**：160594 字节，生成于 2026-11-02
- **定位**（第 0 章）：手机端会话全程中文 + 模型切换风格统一 + 跨会话跨设备生效；适用 IDE/CLI/移动端，基于官方文档核实。
- **结构**：含第 0–14 章，另设第 0.5 节"官方配置坐标系"（基础层 × 能力层 × 用户/项目/本地级），第 1 章"官方机制对照表"，第 8 章 Hooks 加固层，第 9 章跨项目共享，第 16/17/18/19/20 章治理原则。

### 2.3 SOP 如何拍板（决策依据）

- **第 1 章官方机制对照表**：列明项目记忆、用户级规则、`alwaysApply`/`globs`、加载顺序（用户级→项目主文件→项目规则），冲突时项目级覆盖用户级。
- **第 19 章强制链**：拍板采用"三通道叠加"——①薄壳内联铁律（`.codebuddy/CODEBUDDY.md`）、②官方自动加载规则（`.codebuddy/rules/zh-style.md`）、③手机指令兜底（设置→给 WorkBuddy 的指令）；并拍板**不押钩子注入**，依据标注为"本生态实测：手机/云端任务不跑钩子；官方文档未作此声明（SOP 20.12.2）"。
- **第 20.9 章**：拍板规则"三分离"设计——作用域（用户级/项目级）× 触发（`alwaysApply`/`paths`）× 强制力（软声明→`deny`）；弃用旧生态 `hot/warm/cold` 冷热分层；台账归 `docs/` 不进 context。

### 2.4 前期已完成的工作（本会话开始前）

| 工作项 | 产物 | 状态 |
|---|---|---|
| 技能清点 | 清单输出 | 已完成 |
| 人读卡 | `技能侧-技能速查卡.md`、`新会话-部署与验证操作卡.md`、`规则侧-操作卡.md`、`规则侧-规则速查卡.md` | 已完成落盘 |
| 机读执行器 | `deploy_verify.py`（含 `--check/--apply/--playbook`） | 已建，**后删除** |
| 引导包 | `codebuddy-eco-bootstrap.tar.gz`、`bootstrap-kit/`（嵌套包） | 已建，**后删除** |
| 跨会话资料库联动 | 空间 `8w5cnqCqQJ0wNoF2Hb6efH`；审查侧 `uUUBy9KzWkLKVs69hUXsMq`、执行侧 `iu2GLElOaSNu0S7m93HJ12` | 已建 |
| 审查结论 | 执行侧 v1/v2 报告审查（base/zh/shell=真阳性；cond/skill/mobile=无法判定） | 已完成 |
| 部署包修正指令 | 下发至执行侧文件夹 | 已完成 |

---

## 三、SOP 基础上借鉴旧生态、做了哪些改进、设计上如何融入

### 3.1 借鉴旧生态（来源：`codebuddy-eco/README.md` 第四节、`docs/governance.md` 第五节）

| 借鉴项 | 旧生态出处 | 本生态采用方式 |
|---|---|---|
| 目录分层 | `.codebuddy/` 官方路径 vs 业务代码分离 | 直接采用 |
| 技能契约 | `SKILL.md`（frontmatter + 触发词 + 边界） | 直接采用（四技能住此） |
| 治理清单 | `MANIFEST.json`（依赖图 + 事件契约） | 采用轻量版，去 god-object |

### 3.2 明确不借鉴

- `tvbox-eco` 的 23 条 `rules/core.json`；
- 4 个 TVBox 专属能力技能（probe-hub / tvbox-source-hub / tvbox-inspect / tvbox-interface）；
- "钩子强制"体系（SOP 第 19 章已判手机不跑钩子，改用官方路径 + 薄壳兜底）。

### 3.3 提炼

- 从 tvbox-eco 23 条规则中去掉 TVBox 业务内容后，提炼 **8 条通用铁律**作为用户级基座（`core-8.md`，去 TVBox 化），映射见 `docs/base-rule-mapping.md`。

### 3.4 改进与融入设计

| 设计层 | 融入产物 | 对应 SOP | 说明 |
|---|---|---|---|
| 用户级常驻基座 | `base/rules/core-8.md` → `~/.codebuddy/rules/` | 第 20.9 章 C | 8 条通用铁律唯一真源，跨项目去重 |
| 项目级常驻 | `.codebuddy/rules/zh-style.md`（`alwaysApply:true`） | 第 19 章② / 20.9 | 项目专属契约 + §8 轻量纪律 |
| 项目级条件 | `.codebuddy/rules/docs.paths.md`（`alwaysApply:false` + `paths`） | 第 20.9 章 A | 文档同步契约，命中才注入 |
| 治理薄壳 | `.codebuddy/CODEBUDDY.md` | 第 19 章① | 内联三条不可协商 + 五条强制铁律 |
| 基建技能 ×4 | `.codebuddy/skills/*` | 第 17/18 章 | 进化/换机/灰度/产物治理，去 TVBox 化 |
| 治理清单 | `.codebuddy/MANIFEST.json` | 第 18 章 | 依赖图 + 事件契约（轻量版） |
| 台账/映射 | `docs/*.md` | 第 20.9 章 | schema/去重/降级/探针台账 + 基座映射 + SOP 章节映射 |
| 三通道叠加 | 薄壳 + 官方加载 + 手机指令兜底 | 第 19 章 | 不押钩子 |

---

## 四、做这个生态的具体步骤以及规则和技能如何处理

### 4.1 规则处理

| 规则文件 | 放置路径 | 作用域 | 触发 | 处理说明 |
|---|---|---|---|---|
| `core-8.md`（基座） | 用户级 `~/.codebuddy/rules/` + 项目级 `.codebuddy/rules/` | 用户级跨项目 / 项目级 | `alwaysApply:true` | 8 条通用铁律；用户级为唯一真源部署通道，项目级为副本 |
| `zh-style.md` | `.codebuddy/rules/` | 项目级 | `alwaysApply:true` | 项目专属契约，不重复铁律全文、只留指针 |
| `docs.paths.md` | `.codebuddy/rules/` | 项目级·条件 | `alwaysApply:false` + `paths:docs/**/*.md` | 情境契约，命中才注入 |
| `CODEBUDDY.md` | `.codebuddy/CODEBUDDY.md` | 项目级薄壳 | 启动时注入 | 内联不可协商条 + 强制铁律 |

### 4.2 技能处理

四个基建技能，置于 `.codebuddy/skills/`，各含 `SKILL.md`（frontmatter `name`/`description` 注册字段）：

| 技能 | 角色 | 去 TVBox 化说明 |
|---|---|---|
| `skill-evolution` | 复发问题自动固化成技能 | 通用进化引擎，清掉 TVBox 案例 |
| `machine-bootstrap` | 一键换机/克隆工作副本 | clone 目标改为读 `BOOTSTRAP_REPO` 环境变量，无明文 token |
| `feature-gate` | 特性开关 + 绞杀者切流 | 灰度/回滚，新旧并存 |
| `artifact-store` | 本地轻量化总闸·防手机卡顿 | 远程目标从 TVBox space 改为本生态资料库/IMA |

### 4.3 实际部署路径（`ls` 实查，修复后状态）

**项目级（CWD）`/workspace/.codebuddy/`：**
```
rules/core-8.md
rules/zh-style.md
rules/docs.paths.md
CODEBUDDY.md
skills/{artifact-store, feature-gate, machine-bootstrap, skill-evolution}/
```
（另含 TVBox 遗留件 `agents/tvbox-agent.md`、`commands/tvbox-sync.md`、`scripts/`、`tvbox/`，非本生态新增。）

**用户级（HOME）`~/.codebuddy/`:**
```
rules/core-8.md        ← 本生态部署的唯一文件
```

### 4.4 早期错误放置与修复（事实记录）

- **错误放置**：基座 `core-8.md` 一度置于 `codebuddy-eco/base/rules/`（暂存目录，加载器不读），整套 `.codebuddy/` 嵌套在 `codebuddy-eco/` 子目录内层，未落到 CWD `/workspace/.codebuddy/` 与用户级 `~/.codebuddy/rules/` 任一加载路径。
- **修复动作**：将 `core-8.md` 及项目级契约、`CODEBUDDY.md`、4 个技能分别搬至 `/workspace/.codebuddy/` 与 `~/.codebuddy/rules/`。
- **清理动作**：删除 `deploy_verify.py`（设计本身禁止声称 `--verify` 的校验器）与 `bootstrap-kit/`（嵌套包）。

---

## 五、如何在新会话验证这个生态（具体步骤）

### 5.1 桌面端（会话工作目录须定位 `/workspace`）

| 验证项 | 操作 | 通过判据 |
|---|---|---|
| 规则加载 | 新会话问"core-8 铁律第一条是什么？" | 答出"语言：回复跟随用户消息语言（中文→全程简体中文）" |
| 规则加载（注入证据） | 查看开场 `system-reminder` 是否含 `core-8.md` 全文 | 含全文即真阳性 |
| 技能加载 | 新会话问"你有哪些可用技能？"或触发"手机越用越卡帮我清理" | 列出/调用 `artifact-store` 等 4 技能 |
| 技能调用 | 用 Skill 工具加载 `machine-bootstrap` | 返回 SKILL.md 全文 |

### 5.2 手机端

| 验证项 | 操作 | 通过判据 |
|---|---|---|
| 用户级加载 | 新会话（首条**不贴**规则）问"core-8 铁律第一条是什么？" | 答对即用户级自动加载生效 |
| 项目级 + 技能 | — | 手机工作目录非 `/workspace`，项目级与技能在手机无法加载、无需在手机验（桌面端已验） |

### 5.3 实测记录（独立新会话，`Agent` 子会话执行）

- 开场 `system-reminder` 含 `core-8.md` 全文 → **真阳性**（规则进门）。
- 4 个技能出现在 `available_skills` 注入并可被 Skill 工具加载 → **真阳性**（技能进门）。

---

## 六、沙箱部署好后发现本地未生效，又做了哪些事、结果如何

### 6.1 发现未生效

- **现象**（用户在其手机设备实测，截图）：手机新会话问"core-8 铁律第一条是什么？"，AI 未答出铁律内容，反问"指哪一套规则"（选项含 ghidra-core / 八项规定 / Legal Operations CORE 8 / 我自己的文档）。
- **判定**：用户级 `core-8.md` 未在手机加载 → **真阴性**。
- **事实核查结论**：沙箱修复写进的是沙箱文件系统（`/workspace`、 `~/.codebuddy`），与用户手机设备为两台独立机器，沙箱成果未传输到手机。

### 6.2 后续动作

| 动作 | 内容 | 结果 |
|---|---|---|
| 建立 GitHub 仓库 | 仓库名 `codebuddy-eco-rules`（公开），归属 `tvbox342078879`；用户提供 PAT（`ghp_eRq7…`）经 API 建库 | 建库成功 |
| 推送部署包 | 将 CWD `.codebuddy/`（项目级布局）提交并 push 至 `master` 分支 | 推送成功（commit `d73640e`） |
| 核查旧生态换机通道 | 查三个旧仓库，确认旧生态换机主通道为**用户级 `~/.codebuddy/`**（规则/CODEBUDDY/SOUL/USER），指南写明"重启后自动生效" | 用户级为主通道 |
| 形态比对 | 所建 `codebuddy-eco-rules` 采用**项目级 `.codebuddy/`** 布局，与用户级主通道不一致 | 仓库形态与换机主通道不对口 |

### 6.3 结果状态

- GitHub 仓库 `tvbox3428789/codebuddy-eco-rules`：已建、已推（master 含 `.codebuddy/` 部署包 + `.gitignore`）。
- 仓库形态：项目级布局，待按用户级 `~/.codebuddy/` 布局重构（**未执行**，待用户拍板）。
- 手机端用户级是否自动加载：**仍待实测**；此前真阴性系"未部署修复版"，部署后需真机复测。
- 凭证：`ghp_eRq7…` PAT 已用于建库+push，建议撤销轮换。

---

## 附录 A · 当前产物清单（`/workspace`）

| 文件 | 性质 |
|---|---|
| `CodeBuddy-会话中文风格统一-SOP.md` | 生态设计真源 SOP（160KB） |
| `codebuddy-eco/`（含 README/MANIFEST/docs/verify/base/rules） | 生态脚手架造物 |
| `codebuddy-eco-bootstrap.tar.gz` | 引导包（早期产物，保留） |
| `技能侧-技能速查卡.md` / `新会话-部署与验证操作卡.md` / `规则侧-操作卡.md` / `规则侧-规则速查卡.md` | 人读卡 |
| `资料来源总表.md` | 资料来源汇总（22 条） |
| `codebuddy-eco-项目全量操作报告.md` | 本报告 |
| `.codebuddy/`（项目级规则+薄壳+技能） | 修复后部署包 |
| `.git`（仓库，remote=`origin`→`tvbox342078879/codebuddy-eco-rules`） | 已关联远程 |

## 附录 B · 资料来源摘要（详见 `资料来源总表.md`）

共 22 条：GitHub 仓库 5 条、本地文件系统 9 条、工具/接口 4 条、资料库（历史双信箱）3 条、凭证 1 条。

## 附录 C · 真源引用索引

- SOP：`CodeBuddy-会话中文风格统一-SOP.md` 第 0 / 0.5 / 1 / 8 / 9 / 16 / 17 / 18 / 19 / 20.9 / 20.12.2 章
- 生态设计：`codebuddy-eco/README.md`、`codebuddy-eco/.codebuddy/MANIFEST.json`、`codebuddy-eco/docs/governance.md`、`docs/base-rule-mapping.md`
- 规则：`/workspace/.codebuddy/rules/{core-8,zh-style,docs.paths}.md`、`~/.codebuddy/rules/core-8.md`
- 实测：独立新会话 `Agent` 子会话报告（规则/技能加载双真阳性）；用户手机实测截图（用户级真阴性）

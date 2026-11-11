# CodeBuddy 会话全程中文 + 模型切换风格统一 SOP

> 目标：手机端会话页面全程简体中文、切换任意模型后输出风格保持一致，且**跨会话、换新手机都持续生效**。
> 适用：CodeBuddy（IDE / CLI / 移动端通用，基于官方文档核实）。

---

## 0. 一句话结论（先看这个）

你最初设想的 `.codebuddy/project-prompt.md` **不是官方认可的自动加载路径**，新会话/新手机都不会自动读它，达不到"自动加载"目的。

正确做法：把规则放进官方自动加载路径之一——

- **项目级**（推荐，随项目同步到新手机最稳）：`CODEBUDDY.md` 或 `.codebuddy/rules/*.md`
- **用户级**（跨所有项目）：`~/.codebuddy/CODEBUDDY.md` 或 `~/.codebuddy/rules/*.md`

规则在**每次会话启动时自动注入**上下文，中途切模型是热切换、上下文保留，且官方有"压缩后自动重新注入完整规则"的强制兜底。

若担心"模型偶尔不服从软约束"，可叠加**可选 Hooks 加固层**（`SessionStart` 兜底加载 + `UserPromptSubmit` 语言/风格质检），见第 8 章。

若还要"换个项目开新会话也带旧项目的记忆、能做旧项目模型做的事"，需上**跨项目/跨设备共享机制**（用户级规则 + global 记忆 + 项目级软链 + `/config` 中文），见第 9 章。

---

## 0.5 官方配置坐标系：基础层 × 能力层 × 用户/项目/本地级

本节是整份手册的**顶层导航框架**。前面所有章节（第 1–14 章）的内容都能挂到这个坐标系下，你以后看任何配置都知道"它在哪一层、跨不跨设备"。

### 0.5.1 两个正交轴（你提的二分法，官方已隐含）

- **轴 A：基础体验层 ↔ 能力执行层**（对应你提的"基础性需求 vs 具体能力层"）。官方系统设置导航分三组——**设置 / 功能 / 数据与安全**，外加 `.codebuddy/` 目录里的规则/技能/钩子，正好落在这两个半区。
- **轴 B：用户级 ↔ 项目级 ↔ 本地级**（官方"分层配置系统"）。用户设置 `~/.codebuddy/`、项目设置 `.codebuddy/`（共享）+ `.codebuddy/settings.local.json`（**不共享**，适合本机密钥/调试）。

> 你的"全程中文、跨设备不丢记忆"属**轴 A 基础层**；"规则让模型按宿主要求跑"属**轴 A 能力层**。两者都要再选**轴 B** 的档位（用户/项目/本地）。

### 0.5.2 基础层（底座体验）官方配置清单

面向"所有会话/设备、不针对具体任务"，正对应你说的**"会话页面全程中文""跨设备不丢记忆"**类基础性需求：

| 配置项 | 官方位置 | 对应你的需求 |
|---|---|---|
| **界面显示语言** | 系统设置 → 通用 → 语言（简/繁/英/葡/印尼） | "页面"中文（UI） |
| **回复语言** | `settings.json` 的 `language` 或 `/config` | "全程中文"（AI 说话） |
| **AI 对话风格** | 系统设置 → 功能 → 个性化 / `outputStyle`（concise 等） | "风格统一"的底座 |
| **模型** | 系统设置 → 功能 → 模型 / `model` / 自定义模型 | 切模型的默认 |
| **记忆与进化** | 系统设置 → 功能 → 记忆与进化 / `memory.autoMemoryEnabled`、`typedMemory` / `memories/global` | "跨设备不丢记忆" |
| **账号云同步** | 云端自动同步（默认开） | 跨设备/换手机 |
| **设备连接** | 系统设置 → 功能 → 设备连接（允许移动设备远程连接） | 你的手机端 |
| 主题/字体/快捷键/代理/通知 | 系统设置 → 通用 | 纯体验（不相关但属基础层） |

> **澄清**："会话页面全程中文"官方其实是**两个东西**——界面 UI 语言（通用设置）和回复语言（`language` 配置/Rules）。要真"全程中文"通常两个都要设。

### 0.5.3 能力层（让模型按宿主要求跑）官方配置清单

针对"具体行为、决定模型遇到某类需求怎么干活"，对应你说的**"规则层面让模型按宿主要求跑起来"**：

| 配置项 | 官方位置 | 强制力 | 作用 |
|---|---|---|---|
| **Rules（规则）** | `.codebuddy/rules/*.md` + `CODEBUDDY.md`，`alwaysApply`/`globs` | 软（提示词） | 定边界、定流程，模型自愿遵守 |
| **Hooks（钩子）** | `settings.json` 的 `hooks`（SessionStart/UserPromptSubmit/PreToolUse） | **硬**（跑脚本） | 事件到点必执行，不靠模型意愿 |
| **Permissions（权限）** | `permissions.allow/ask/deny` + `defaultMode`（auto/dontAsk/plan） | **硬**（拦动作） | 任务边界的"硬约束"，比规则强 |
| **Skills（技能）** | `.codebuddy/skills/`（SKILL.md） | 软（AI 自动识别） | 自动发现并调用固定流程 |
| **Agents（子代理）** | `.codebuddy/agents/` | 隔离 | 独立上下文的专职工人 |
| **Commands（命令）** | `.codebuddy/commands/`（`/命令`，可锁 `model`/`tools`） | 显式触发 | 一键固化操作 |
| **Plugins（插件）** | `enabledPlugins` + marketplace | 打包分发 | 团队/跨项目批量装能力 |
| **MCP** | `mcp.json` / `.mcp.json` | 扩工具 | 给所有项目挂外部工具 |
| **Typed Memory（feedback）** | `memories/global/feedback-*.md` | 软但结构化 | 把"行为纠正"固化，跨项目 |
| **子代理模型分配** | `subagents.agents.*.model` | 锁模型 | 锁定某个子代理用哪模型 |

> **澄清**："规则让模型按宿主要求跑"——官方靠 **Rules（定边界，软）+ Hooks（硬执行）+ Permissions（硬拦截）三者组合**，不是单靠规则。规则只"劝"，钩子和权限才"逼"。

### 0.5.4 双层 × 三档 交叉矩阵

|  | 用户级 `~/.codebuddy/` | 项目级 `./.codebuddy/` | 本地级 `*.local.json` |
|---|---|---|---|
| **基础层** | `language`/`outputStyle`/`model`/`memory`/云同步 | 项目级 `CODEBUDDY.md` 可覆盖语言 | 本机密钥、调试开关 |
| **能力层** | `rules/` `agents/` `skills/` `mcp.json` 全局生效 | `rules/` `skills/` `commands/` `hooks` 随仓库共享 | `settings.local.json` 本机私有钩子/权限 |

### 0.5.5 三个关键澄清（这个二分最容易混的点）

1. **基础层的"记忆"兜不住硬需求**：系统设置的"记忆与进化"是**软的**（AI 自主提取、可能不召回），且**项目记忆存在用户目录、不随 Git**。所以"跨设备不丢且强制"最终靠**能力层的固定 Rules / `CODEBUDDY.md` 提级**兜底——你的"基础需求"反而要借"能力层"才稳。
2. **"让模型按宿主要求跑"基础层解决不了**：基础层只管"体验一致"，真正"行为合规、必跑、必拦"是能力层的 Rules+Hooks+Permissions。
3. **两个轴都要选**：同样"全程中文"可放基础层（`language` 全局）也可放能力层（`rules` 项目级）；同样能力层还能选用户级或项目级。这就是官方"分层配置系统"的真意。

### 0.5.6 本 SOP 各章在坐标系中的位置

- **基础层为主**：第 1/2/2.5/9 章（机制、方案、跨项目共享、记忆不丢）
- **能力层为主**：第 3/8/10/11/13 章（Rules 写法、Hooks、用户级扩展、插件/权限、TVBox 实战）
- **跨轴/本质**：第 12 章（跨 App）、第 14 章（强制力光谱）

---

## 1. 官方机制对照表

| 机制 | 官方路径 | 作用范围 | 跨设备(新手机) | 加载方式 |
|---|---|---|---|---|
| 项目记忆主文件 | `./CODEBUDDY.md` 或 `./.codebuddy/CODEBUDDY.md` | 当前项目 | ✅ 随项目同步 | 启动全文注入，向上递归 |
| 项目模块化规则 | `./.codebuddy/rules/*.md` | 当前项目（不读父目录） | ✅ 随项目同步 | 启动自动加载，与 CODEBUDDY.md 同级 |
| 项目本地记忆 | `./CODEBUDDY.local.md` | 当前项目，仅本人 | ✅ 随项目同步 | 自动加入 `.gitignore`，不提交 |
| 用户记忆主文件 | `~/.codebuddy/CODEBUDDY.md` | 所有项目 | ⚠️ 依赖同账号云同步 | 启动最先加载 |
| 用户模块化规则 | `~/.codebuddy/rules/*.md` | 所有项目 | ⚠️ 依赖同账号云同步 | 启动最先加载 |
| Auto Memory（动态） | `~/.codebuddy/memories/{project-id}/`、`memories/global/` | 会话间召回 | ⚠️ 本地存储 | AI 自主提取，非固定规则 |

> 加载顺序：用户级 → 项目主文件（向上递归）→ 项目规则（仅当前目录）→ 子目录/本地记忆。
> **冲突时项目级覆盖用户级**（官方："Project-level language settings override user-level settings"）。

---

## 2. 方案选择

| 你的诉求 | 推荐方案 | 落点 |
|---|---|---|
| 仅本项目统一，且换新手机也生效 | 项目级 | `.codebuddy/rules/zh-style.md` 或 `CODEBUDDY.md` |
| 所有项目都统一（不绑定单项目） | 用户级 | `~/.codebuddy/rules/zh-style.md` |
| 私人偏好不想进仓库 | 项目本地 | `CODEBUDDY.local.md`（自动 gitignore） |
| 怕模型偶尔不服从软约束、要更"硬"的兜底 | 叠加 Hooks 加固层 | `.codebuddy/settings.json` + `.codebuddy/hooks/*.py`（见第 8 章） |
| 换个项目开新会话，也要带旧项目的记忆与能力 | 跨项目共享（用户级+global+软链） | `~/.codebuddy/rules/` + `memories/global/` + `ln -s`（见第 9 章） |

**本 SOP 默认采用「项目级 + 模块化规则」作主方案**，最贴合"随项目到新手机"的诉求；Hooks 作为可选加固层，对抗"模型偶尔不服从"。

### 2.5 常见理解误区 + 记忆如何"不丢失"（细化）

下面把"用户级 vs 项目级"的真实边界钉死，并给出记忆不丢失的**可操作步骤**。

#### 误区一：「用户级文件换设备就全消失」
**不准**。用户级文件物理上在设备本地 `~/.codebuddy/`，但官方**云端自动同步默认开启**，会同步设置、`settings.json`、MCP 配置、会话历史等。是否覆盖到"用户级规则/记忆"文档有分歧（IDE 说账户级可跨项目、CLI 说本地不进版本库），所以准确说法是：
- 同账号 + 云端同步 → 可能带过去，但**不 100% 保证**；
- 纯本地 / 关云同步 / 规则不在云同步范围 → 换设备确实没了。
> 正确表述：**用户级"跟设备走、不感知账号"，换设备是否丢看云同步，而非必然消失。**

#### 误区二：「换账号就切到本地另一套配置」
**不准**。用户级文件根本**不感知账号**，它就在当前机器的 `~/.codebuddy/`，无论登哪个 CodeBuddy/腾讯云账号，读的都还是同一个目录。所以同设备换账号，本地文件照样在。

#### 误区三：「项目级 clone 一次，所有配置都不丢失」
**80% 对，漏了记忆**。项目级文件随仓库走没错，但**项目记忆不在项目目录里**：

| 内容 | 位置 | 是否随 Git clone 回来 |
|---|---|---|
| `CODEBUDDY.md`、`.codebuddy/rules/`、`settings.json`、`commands/`、`agents/`（项目级）、`hooks/` | 项目目录（进版本库） | ✅ 克隆即恢复 |
| **Auto Memory 项目记忆** `~/.codebuddy/memories/{project-id}/MEMORY.md` | **用户目录**（不进版本库） | ❌ **clone 代码带不回来** |

> 所以"所有配置不丢失"要改成：**规则/配置随仓库全回来，但旧项目学到的记忆需另存**（见下）。

#### 修正后的心智模型总表

| 维度 | 用户级 `~/.codebuddy/` | 项目级 `./.codebuddy/` + `CODEBUDDY.md` |
|---|---|---|
| 物理位置 | 设备用户主目录 | 项目目录（随仓库） |
| 跟谁走 | 跟**设备**走，不感知账号 | 跟**项目仓库**走，不感知账号 |
| 同设备换账号 | 文件还在（本地不感知账号） | 文件还在（项目目录不动） |
| 换设备（同账号） | 看云同步：设置/MCP 多能同步，规则/记忆不绝对 | clone 即全回来（除项目记忆） |
| 换设备+换账号 | 需同账号云同步才保住 | 需重新 clone 项目；记忆需另存 global |
| 记忆 | `memories/global` 跨项目；`{project-id}` 项目专属 | `{project-id}` 记忆存用户目录，**不随 Git** |

#### 记忆"不丢失"的细化操作（四招，按可靠度排序）

记忆分两类——**固定规则记忆**（应放 `CODEBUDDY.md`/Rules，可控）与 **Auto Memory 动态记忆**（AI 自主提取，存 `~/.codebuddy/memories/`）。后者要"不丢"得主动管理：

**① 把"该长期保留的"从动态记忆提级为固定规则（最稳）**
不要依赖 AI 自动记。值得跨项目/跨设备的偏好，直接写进：
- 项目级 `CODEBUDDY.md` / `.codebuddy/rules/*.md`（随仓库到新手机），或
- 用户级 `~/.codebuddy/CODEBUDDY.md`（跨所有项目）。

```bash
# 用户级固定记忆（跨所有项目、跨会话）
cat >> ~/.codebuddy/CODEBUDDY.md <<'EOF'

## 长期偏好（自动加载）
- 全程简体中文；周报用分段文字不用表格。
- 涉及手机阅读场景，优先短段落、避免宽表格。
EOF
```

**② 跨项目记忆放进 `global/`（Auto Memory 唯一自动跨项目的档）**
Auto Memory 有 `{project-id}`（项目专属，不自动跨项目）与 `global/`（跨项目）两档。把关键记忆搬进 global：

```bash
# ~/.codebuddy/memories/global/MEMORY.md（所有项目生效，且比 {project-id} 更易随账号云同步）
cat >> ~/.codebuddy/memories/global/MEMORY.md <<'EOF'

- 用户偏好：输出全程中文，结论优先配套可执行操作。
- 风格纠正：手机阅读场景用分段文字而非表格。
EOF
```
> 用 `/memory` 查看当前已记内容，再手动整理进 global；AI 自主写入也默认进对应档，但**项目专属记忆不会自动跨项目**，需你搬。

**③ 想"换设备也带记忆"——靠同账号云同步，而非项目仓库**
项目记忆在用户目录，**不随 Git**。要到新手机，唯一路径是：同账号登录 + 云端自动同步覆盖到 `memories/`。若云同步不覆盖记忆（CLI 端偏本地），则改用 ①②（写进固定规则/CODEBUDDY.md），因为**固定规则既随项目（项目级）又跨项目（用户级），且不依赖记忆的云同步**。

**④ 团队共享记忆——用项目级 `CODEBUDDY.md`，不用 Auto Memory**
Auto Memory 是个人的、设备本地；团队要共享的"项目约定记忆"应固化进项目级 `CODEBUDDY.md`（进版本库、clone 即得），不要指望个人记忆同步。

> **一句话**：规则/配置随仓库或随账号云同步能保住；唯独"AI 自动记的项目记忆"在用户目录、不随 Git，要靠"提级为固定规则 / 搬进 global / 同账号云同步"三招才不丢。

---

## 3. 具体操作步骤（含代码框）

### 步骤 1：创建规则目录

```bash
mkdir -p .codebuddy/rules
```

### 步骤 2：写入规则文件（方案 B，模块化，推荐）

文件：`.codebuddy/rules/zh-style.md`

```markdown
---
description: 项目全程简体中文与输出风格统一强制规则（Always）
alwaysApply: true
enabled: true
priority: high
---

# 项目全局会话强制规则（所有模型切换持续生效，不可遗忘）
## 语言强制约束
1. 本项目内所有会话，自然语言输出（分析、方案、说明、总结、解释、工具返回文本）**一律使用简体中文**。
2. 仅代码关键字、API 名称、命令可保留英文；代码注释若无特殊要求优先中文。
3. **判定规则**：除非用户在当前这一条消息中单独、明确要求"用英文 / English"，否则禁止主动输出大段英文段落；涉及英文时优先中英对照或仅保留必要术语。
4. 切换任意模型后，本条语言规则持续生效，不会丢失。
## 输出风格统一约束（解决模型切换风格不一致）
5. 行文优先落地实操，减少空洞纯理论；结论优先配套可执行操作，理论仅作底层支撑。
6. 结构采用总分总，分层清晰，要点分条；术语体系固定，不随意更换表述。
7. 回答紧扣当前需求，不额外发散、不擅自新增任务。
## 任务边界约束
8. 严格遵循用户当前指令，不主动私自调用网盘、自动转存等；未经明确指令不执行自动化动作。
9. 信息不足时，直接列出需补充的信息清单，不编造数据、链接、实验结果。
```

> 关键：加了 `alwaysApply: true`（确保 **ALWAYS 类型、每次会话常驻注入原文**，而非等它犯错再撤回）；`priority: high` 让语言规则压过其他风格规则；第 3 条把"用户单独要求英文"写成**明确判定条件**，既稳又不会误伤你偶尔要英文的场景。这比"检测英文→撤回→重输出"的前置约束思路更省、更稳、跨端更可靠。

### 规则层类型与字段（官方机制，决定"怎么应用"）

规则层（`CODEBUDDY.md` / `.codebuddy/rules/*.md`）本身有独立的"类型 + frontmatter"体系，这是官方处理"强制约束"的核心，比事后撤回更稳。

**三种规则类型（决定何时注入）：**

| 类型 | 触发方式 | 上下文加载 | 适合 |
|---|---|---|---|
| **Always（总是）** | 每次对话/内联请求都触发 | **始终加载规则原文** | 核心规范、架构约束、安全要求 |
| Agent Requested（智能体请求） | Agent 判断相关才引用 | 只加载名称+描述，需要时再读原文 | 文档、指南、参考资料 |
| Manual（手动） | 对话里 `@规则名` 才触发 | 不自动加载 | 特定功能指南、可选实践 |

> 官方智能加载原则：**只有 `alwaysApply: true` 才常驻加载**，其余按需。核心标准设 3–5 条 Always，其余设 manual/requested。

**frontmatter 控制字段（决定怎么应用）：**

| 字段 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `description` | string | — | 规则描述，Agent 检索 / Requested 类型用 |
| `alwaysApply` | boolean | `true` | `true`+任意 → **ALWAYS 始终注入**；`false`+有 paths → MANUAL 条件触发；`false` 无 paths → 不加载 |
| `enabled` | boolean | `true` | `false` 则完全不加载（临时关闭） |
| `globs` / `paths` | string/string[] | — | 路径 glob 限定（IDE 版叫 `globs`，CLI 版叫 `paths`） |
| `priority` | — | — | 重要程度，核心架构最高，压过其他规则 |

**官方"有效规则"最佳实践（直接对应语言约束）：**
- **聚焦单一职责**：单条 ≤500 行，复杂拆子规则。
- **避免模糊指令**：写"自然语言一律简体中文，除非用户本条单独要求英文"，**不要写"尽量用中文"**。
- **给清晰判定条件**：把"用户是否单独要求英文"写成可判定的前提，而非笼统禁止。
- **优先级合理**：语言这类核心约束设 `priority: high`。

### 步骤 2 备选（方案 A，单文件最简）

若不想拆分，可直接写成项目根目录 `CODEBUDDY.md`，内容同上（去掉 frontmatter 也行，官方对 CODEBUDDY.md 是纯 markdown 全文注入）：

```bash
# 项目根目录创建 CODEBUDDY.md，粘贴上面的正文（不含 --- frontmatter --- 也可）
touch CODEBUDDY.md
```

### 步骤 3：若需用户级（跨所有项目）

把同样的文件放到用户目录即可（注意 `~` 是本机家目录，换手机需同账号云同步才带得过去）：

```bash
mkdir -p ~/.codebuddy/rules
# 然后将上面的 zh-style.md 内容写入 ~/.codebuddy/rules/zh-style.md
```

---

## 4. 生效与验证

### 关键原则
- 规则**只在会话开始时注入**。新建/修改规则后，**必须开新会话（或 `/clear`）才生效**，当前已开会话不会热更新。
- 中途切模型是**热切换**（同会话换后端，上下文保留），规则继续跟随，不会丢。

### 验证命令

```text
# 查看当前会话实际加载了哪些记忆/规则文件
/memory

# 修改规则后，清空当前会话上下文以重新注入（等同于开新会话）
/clear
```

### 推荐验证流程
1. 写完 `.codebuddy/rules/zh-style.md` 后，**关闭当前会话，重开一个新会话**。
2. 发一句："请用英文写一段介绍。" —— 预期应被规则纠正为简体中文输出。
3. 在会话中点模型图标切到另一个模型，再发同样指令 —— 预期风格与语言保持一致。

---

## 5. 强制机制说明（为什么切模型/切会话都不丢）

| 场景 | 官方行为 | 结论 |
|---|---|---|
| 同会话中途切模型 | 热切换，上下文（含已注入规则）原样保留 | ✅ 不丢 |
| 开新会话 | 启动时自动重新注入全部规则 | ✅ 自动生效 |
| 长对话上下文压缩 | 官方"过滤规则和记忆内容，压缩后**自动重新注入完整规则**" | ✅ 强制兜底 |
| 改了规则文件 | 当前会话不重载，需新会话/`/clear` | ⚠️ 注意 |

---

## 6. 注意事项（边界，实话告知）

1. **静态注入不是硬件锁**：规则对所有模型一视同仁地注入，但不同模型对指令的遵循度有差异（小模型可能偶尔松动）。所谓"持续生效"是指**注入持续生效**，非 100% 硬约束不违背。
2. **改内容要开新会话**：当前会话不会自动重载更新后的规则。
3. **跨设备靠同步**：项目级随项目 Git/云同步到新手机最稳；用户级依赖同账号云端同步，本地偏多，不绝对。
4. **`project-prompt.md` 不推荐**：不在任何官方自动加载清单中，有不被读取的风险。

---

## 7. 常见误区

- ❌ "切模型会清空规则" → 不会，同会话热切换保留上下文。
- ❌ "规则文件随便起名都能自动加载" → 只有 `CODEBUDDY.md` / `.codebuddy/rules/*.md` / 用户级对应路径会被自动加载。
- ❌ "Auto Memory 能强制风格" → Auto Memory 是 AI 自主从对话提取的动态记忆，不适合放固定强制条款，应放静态指令层。
- ❌ "用户级一定跨设备" → 用户级底层偏本地，跨设备需同账号云同步，不保证。

---

---

## 8. 加固层：Hooks（可选，对抗"模型偶尔不服从"）

### 8.1 为什么需要这一层（以及它只是兜底）
**规则层（Rules）才是强制约束的主力**：通过 `alwaysApply: true` 在每次会话开头就把语言规则**前置注入**上下文，从源头压住"模型说英文"的可能，无需等它犯错再处理。

Hooks 是官方"执行过程实时质检员"，能在**会话节点/工具节点跑脚本**，仅作为**可选兜底**——对付"模型偶尔不服从软约束"的情形，做提醒/质检/拦截工具，**不是撤回重输出的主力**。

官方架构分工（CodeBuddy 官方）：
- **Rules = What to follow（约定规则，确保执行一致性）—— 前置约束，主力**
- **Hooks = How to Supervise（实时质检员，提升质量）—— 事后兜底，可选**

> 注意：Hooks **不能直接改写模型的回复文本**（没有"拦截并修改 AI 自然语言输出"的事件），它只能"监督/注入提醒/拦截工具"。强制中文的最终驱动仍是规则层，Hook 是加固而非替代。你旧项目"检测英文→撤回→中文重输出"的做法，本质是拿配置层硬扛规则层该做的事；升级到 `alwaysApply` 前置约束后，这层兜底通常可省。

### 8.2 钩子一：`SessionStart` —— 每次会话/切会话兜底加载
会话开始或恢复时触发，切会话、`/clear` 后都会再触发。用它把规则文件再注入一次上下文，等于给"自动加载"上双保险。

文件：`.codebuddy/settings.json`（项目级，随项目同步到新手机）

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CODEBUDDY_PROJECT_DIR\"/.codebuddy/rules/zh-style.md",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

> 脚本 stdout 会被当作 `additionalContext` 注入会话上下文；`$CODEBUDDY_PROJECT_DIR` 是官方提供的项目根目录环境变量。若已存在 `settings.json`，**只合并 `hooks` 字段**，不要覆盖你原有的其他配置。

### 8.3 钩子二：`UserPromptSubmit` —— 提交时做语言/风格质检
用户每次提交消息、AI 处理之前触发。配套脚本可检测用户消息是否夹带"用英文回答"等指令、或做风格审计，返回 `additionalContext` 提醒模型遵守中文规则。

`.codebuddy/settings.json` 追加：

```json
{
  "hooks": {
    "SessionStart": [ /* 见 8.2 */ ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CODEBUDDY_PROJECT_DIR\"/.codebuddy/hooks/check-lang.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

检测脚本 `.codebuddy/hooks/check-lang.py`（示例：识别"用英文/English"类指令并提示模型坚持中文）：

```python
#!/usr/bin/env python3
import json, sys

data = json.loads(sys.stdin.read())
prompt = (data.get("prompt") or "").lower()

if any(k in prompt for k in ["用英文", "英语回答", "in english", "use english", "english version"]):
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "⚠️ 用户消息含英文输出请求，但本项目强制全程简体中文，"
                                 "除非用户明确且单独要求，否则仍用中文回答。"
        }
    }
    print(json.dumps(out, ensure_ascii=False))

sys.exit(0)
```

> 使用前给脚本加执行权限：`chmod +x .codebuddy/hooks/check-lang.py`。脚本在 macOS/Linux 用默认 shell 跑，Windows 强制 Git Bash，命令需 bash 兼容；移动端脚本环境不一致，这是 Hook 相比纯规则文件"跨设备更脆"的根源。

### 8.4 Hooks 的边界（实话）
- **不能改写 AI 回复**：只能监督/注入提醒/拦截工具，强制中文仍靠 Rules。
- **配置更重、跨端更脆**：要 `settings.json` + `.py/.sh` 脚本 + 执行权限 + bash 兼容环境；移动端/不同 OS 脚本环境不一致，反而不如纯规则文件稳到新手机。
- **项目级 `settings.json` 随项目共享**，但脚本依赖本机环境，与"换新手机也生效"诉求有张力——所以 Hook 定位为**加固层，不是必需项**。

### 8.5 推荐落地组合
- **主力（必须）**：规则层 Rules（`.codebuddy/rules/zh-style.md`，`alwaysApply: true` + `priority: high`）—— 前置注入，从源头约束，覆盖你要的 90%+。
- **兜底（可选）**：若仍担心个别模型松动，再加 `SessionStart` 兜底加载 + `UserPromptSubmit` 语言质检。
- **优先级明确**：规则层前置约束优先；Hooks 撤回/质检是兜底而非主力。二者并存、互不冲突；若只在手机端轻量使用，纯 Rules 已足够，不必上 Hook。

---

## 9. 跨项目 / 跨设备：记忆与能力共享（换项目也带旧项目的"记忆"和"能做的事"）

### 9.1 先厘清：你混了两个不同的东西

当你"在另一个项目新开会话，想让模型有旧项目的记忆、也能做旧项目模型做的事"，官方是**两套独立机制**分开管的：

| 你的诉求 | 官方机制 | 默认作用域 | 跨项目默认？ |
|---|---|---|---|
| 新会话"做旧项目模型做的事"（中文 + 风格统一的行为） | **Rules（规则）** | 项目级仅限本项目 | ❌ 默认不跨，需上用户级或共享 |
| 新会话"有旧项目的记忆"（学到的事实/偏好/决策） | **Memory（记忆）** | 项目专属记忆绑定 project-id | ❌ 默认不跨，需提级为 global / 用户级 |

> 核心痛点：项目级规则/记忆**只对当前项目生效**，所以"换个项目开新会话就丢了"。要跨项目，必须上**用户级**或**共享机制**。

### 9.2 官方四种落地方案（含代码框）

#### 方案 A：用户级规则（让"新项目会话自动做旧项目模型做的事"——最省事）
写进 `~/.codebuddy/rules/`，官方明确"适用于所有项目的个人规则"，**任何新项目会话自动带**，无需逐个项目复制。

```bash
# 在你真机的用户目录创建用户级规则（不在项目里，不在版本库）
mkdir -p ~/.codebuddy/rules
```

`~/.codebuddy/rules/zh-style.md` 内容（与第 3 章正文一致，用 `alwaysApply` 前置约束）：

```markdown
---
description: 全局会话强制规则——全程简体中文、输出风格统一
alwaysApply: true
enabled: true
priority: high
---

# 全局会话强制规则（跨所有项目、跨会话持续生效，不可遗忘）
## 语言强制约束
1. 所有会话的自然语言输出（分析、方案、说明、总结、工具返回文本）一律简体中文。
2. 仅代码关键字、API 名称、命令保留英文；注释无特殊要求优先中文。
3. 除非用户在本条消息单独明确要求英文，否则禁止主动输出大段英文段落。
4. 切换任意模型后，本条规则持续生效，不会丢失。
## 输出风格统一约束
5. 行文优先落地实操，结论优先配套可执行操作。
6. 结构采用总分总，要点分条；术语体系固定，不随意更换表述。
7. 回答紧扣当前需求，不额外发散、不擅自新增任务。
## 任务边界约束
8. 严格遵循当前指令，未经明确指令不执行自动化动作。
9. 信息不足直接列出补充清单，不编造数据、链接、实验结果。
```

> 注意：用户级规则在"项目规则之前加载"，但**项目级同名/同类规则会覆盖它**（官方："Project-level settings override user-level"）。所以用户级做全局兜底，项目级可针对性微调。

#### 方案 B：项目级 + 符号链接（跨设备更稳，官方推荐的共享方式）
如果你不想用用户级（设备本地、换手机不稳），可在每个项目里**软链到同一份规则**，**项目文件随项目同步到新手机**，且可团队共享：

```bash
# 旧项目已建好 .codebuddy/rules/ 的前提下，新项目共享同一份规则文件
ln -s ~/company-standards/zh-style.md  .codebuddy/rules/zh-style.md

# 或共享整个规则目录（官方示例）
ln -s ~/shared-codebuddy-rules  .codebuddy/rules/shared
```

> 官方文档原话：".codebuddy/rules/ 目录支持符号链接，允许您在多个项目之间共享通用规则……符号链接会被解析，其内容正常加载。循环符号链接会被检测并优雅处理。"

#### 方案 C：记忆跨项目（让"新会话有旧项目的记忆"）
记忆分两档，去向不同，只有提级的才会自动跨项目：

```bash
# 旧项目专属记忆（默认不会自动跨项目，绑定旧项目）
~/.codebuddy/memories/{旧项目-project-id}/MEMORY.md
# 全局记忆（所有项目生效）—— 把值得长期保留的关键条目搬到这里
~/.codebuddy/memories/global/MEMORY.md
```

或者更直白：把旧项目里**值得长期保留**的偏好/决策，提炼写进**用户级记忆文件** `~/.codebuddy/CODEBUDDY.md`（官方："用户级记忆……仅本人·所有项目"）。

> 官方原话（IDE 文档）："记忆是全局的，会在所有项目中生效。" 但 CLI 文档把 Auto Memory 拆成 `{project-id}`（项目专属）与 `global/`（跨项目）两档——因此**只有放进 `global/` 或用户级 `CODEBUDDY.md` 的记忆才自动跨项目**，项目专属记忆不会自动带过去。直接对模型说"请记住：……"产生的记忆，若未提级，也默认绑在当下项目。

#### 方案 D：中文全局保证（官方最简单的一招）
文档专门提示：保证全程中文，**最简单是 `/config` 设语言**，比写在记忆文件里更优先、全局生效：

```text
/config  →  选择 Language  →  输入"简体中文"
```

> 官方原话："推荐使用 /config 命令配置首选响应语言，这是最简单直接的方式"；"项目级语言设置会覆盖用户级设置"。所以 **D + A/C 叠加**：`/config` 做全局兜底，规则层/记忆层做精细约束，项目级可再针对性覆盖。

### 9.3 推荐组合（"两者都要"版）

你确认的范围是**两套都上**，按可靠性排序落地：

1. **用户级规则（方案 A）**：`~/.codebuddy/rules/zh-style.md`（`alwaysApply: true`）—— 任何新项目会话自动带中文+风格，**覆盖"做旧项目模型做的事"**。
2. **global / 用户级记忆（方案 C）**：把旧项目关键记忆提炼进 `~/.codebuddy/memories/global/MEMORY.md` 或 `~/.codebuddy/CODEBUDDY.md` —— **覆盖"有旧项目的记忆"**。
3. **项目级软链（方案 B）**：对需要严格随项目同步、团队共享、且要稳到新手机的项目，用 `ln -s` 软链共享规则 —— 作为跨设备的双保险。
4. **`/config` 中文（方案 D）**：全局语言兜底，最先加载、最稳。

> 一句话：核心规则做**用户级（A）**保证全局，敏感/项目专属记忆提级为 **global（C）**，需要随项目稳到新手机的再补**软链（B）**，`/config（D）`做全局中文兜底。

### 9.4 必须实话提醒（避免白做）

1. **本沙箱写文件 ≠ 真机生效**：在 `/workspace` 沙箱里写任何 `~/.codebuddy/` 文件都只影响沙箱，**到不了你的手机/电脑真机**。用户级规则必须在你真机的用户目录里建一次（或靠同账号云同步）。
2. **用户级是设备本地**：方案 A 跨项目很爽，但"换手机"仍依赖同账号云端同步，不是 100% 保证；方案 B（项目文件+软链）随项目同步到新手机反而更稳。
3. **旧项目记忆不会自动搬家**：Auto Memory 的 `{project-id}` 记忆绑定旧项目，新项目不会自动读，得你主动提炼成 `global/` 或用户级 `CODEBUDDY.md`。
4. **项目级覆盖用户级**：若在某个项目里又写了同名规则，会以项目级为准——这是预期行为，按需利用。

---

## 10. 拓展面全景：官方同类配置/扩展点（代码层 + 细化方案）

> 前 9 章只用到了「语言 + Rules + 记忆 + Hooks」四个点。CodeBuddy 的配置/扩展面是一整套**分层（用户 / 项目 / local）+ 多目录**体系，本 章补齐与你目标直接相关的其余扩展点，并给出可落地的代码层。

### 10.1 配置分层总览

| 层级 | 位置 | 作用域 | 跨设备 | 适合放什么 |
|---|---|---|---|---|
| 用户设置 | `~/.codebuddy/settings.json` | 所有项目 | ⚠️ 同账号云同步 | 全局语言/权限/模型/环境 |
| 项目设置 | `.codebuddy/settings.json` | 当前项目（进版本库） | ✅ 随项目同步 | 团队共享的权限/钩子 |
| 本地设置 | `.codebuddy/settings.local.json` | 当前项目仅本人 | ✅ 随项目但 gitignore | 私人偏好、API Key、调试开关 |
| 用户级扩展目录 | `~/.codebuddy/{rules,agents,skills,mcp.json,CODEBUDDY.md}` | 所有项目 | ⚠️ 同账号云同步 | 个人规则/子代理/技能/MCP |
| 项目级扩展目录 | `.codebuddy/{rules,agents,skills,commands,...}` | 当前项目 | ✅ 随项目同步 | 团队共享的规范与能力 |

### 10.2 代码层一：`settings.json` 全字段（与你目标相关的）

`settings.json` 是中枢配置，支持分层。下面只列**和"中文 + 风格统一 + 任务边界 + 跨项目"直接相关**的字段，附可直接用的用户级示例：

| 字段 | 作用 | 与你目标的关系 |
|---|---|---|
| `language` | 响应语言（`"简体中文"`） | = `/config` 中文兜底，全局最先加载 |
| **`outputStyle`** | 输出风格（`"concise"` 等） | **官方原生"风格"开关**，比写规则更直接 |
| **`permissions`** | `allow` / `ask` / `deny` | **任务边界的"硬约束"**——直接拦命令，比规则强得多 |
| `model` | 默认模型 | 切模型的全局默认 |
| `subagents.agents.*.model` / `variantModels` | 子代理/变体模型分配 | 锁定 Explore/Plan 等子代理用哪个模型 |
| `autoCompactEnabled` | 自动压缩开关 | 关联「压缩后重注规则」 |
| `memory` | `autoMemoryEnabled` / `typedMemory` | 记忆系统总开关 |
| `env` | 每会话环境变量 | 注入固定运行环境 |
| `sandbox` | Bash 沙箱配置 | 限制命令执行环境 |
| `trustedDirectories` | 信任目录 | 标注安全项目根 |

```json
// ~/.codebuddy/settings.json（用户级，所有项目生效；在真机创建）
{
  "language": "简体中文",
  "outputStyle": "concise",
  "model": "gpt-5",
  "permissions": {
    "allow": ["Bash(git:*)", "Bash(npm run:*)"],
    "ask":   ["Bash(git push:*)"],
    "deny":  ["Bash(curl:*)", "Read(./.env)", "Read(./secrets/**)"]
  },
  "subagents": { "agents": { "Explore": { "model": "lite" } } },
  "autoCompactEnabled": true,
  "memory": { "autoMemoryEnabled": true, "typedMemory": true },
  "env": { "NODE_ENV": "development" }
}
```

> **关键**：`permissions.deny` 是你「任务边界约束（第 7-8 条）」的真正硬手段——规则只是"劝"，deny 是"拦"。想禁止私自调网盘/读密钥，用 deny 比规则可靠。

### 10.3 代码层二：用户级扩展目录（`~/.codebuddy/` 下，所有项目可用）

除了 `rules/`，官方在用户目录还给了三个"所有项目可用"的扩展点：

```text
~/.codebuddy/
├── agents/    ← 用户级自定义子代理（所有项目可用，独立上下文窗口）
├── skills/    ← 用户级技能（SKILL.md 目录，可复用工作流）
├── mcp.json   ← 全局 MCP 服务器（统一挂载外部工具）
├── rules/     ← 已讲（第 3/9 章）
└── CODEBUDDY.md  ← 已讲（第 1/9 章）
```

**① `agents/` 自定义子代理（最强扩展点）**——一个带独立上下文窗口、可限定工具和模型的"AI 人格"。建一个**专属"中文+风格"子代理**，跨项目复用、不污染主会话，比纯规则更能保证风格一致：

```markdown
// ~/.codebuddy/agents/zh-assistant.md
---
name: zh-assistant
description: 全程简体中文、落地实操风格的助手；需要中文输出或统一风格时调用
tools: Read, Grep, Glob, Bash
model: inherit
---
你是一个中文技术助手：所有自然语言输出一律简体中文，行文优先落地实操，
结构采用总分总、要点分条，术语体系固定，紧扣需求不发散，不擅自新增任务。
```

**② `skills/` 自定义技能**——把标准工作流固化成 `SKILL.md` 目录（如"出周报""做代码评审"），跨项目复用。目录结构：`~/.codebuddy/skills/<skill-name>/SKILL.md`。

**③ `mcp.json` 全局 MCP**——给所有项目统一挂载外部工具（文件系统、TAPD、数据库等），格式同项目级 `.mcp.json`：

```json
// ~/.codebuddy/mcp.json（用户级全局 MCP）
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

### 10.4 代码层三：Typed Memory 四类型（结构化记忆，默认开启）

你前面用的是"纯文本记忆"，官方其实有**结构化记忆类型系统**，比文本更条理，且与"风格统一"直接挂钩：

| 类型 | 用途 | 例子 |
|---|---|---|
| `user` | 用户角色/目标/偏好/背景 | "财务岗，熟悉 Excel，不写代码" |
| **`feedback`** | **对 CodeBuddy 行为的纠正和指导** | **"周报用分段文字不用表格（领导手机读）"** ← 放"风格纠正"的地方 |
| `project` | 进行中的工作/目标/决策 | "Q4 预算截止 2026-10-31" |
| `reference` | 外部系统/资源指引 | "需求缺陷在 TAPD 支付中台项目" |

```markdown
// ~/.codebuddy/memories/global/feedback-style.md（全局，所有项目生效）
---
name: 输出风格纠正
description: 用户对中文输出与排版风格的持续纠正
type: feedback
---
- 全部用简体中文，禁止大段英文。
- 结论优先配套可执行操作，不堆砌理论。
- 涉及手机阅读的场景，用分段文字而非表格。
```

> 把"风格统一"诉求从 Rules 里的一部分，**沉淀成 `feedback` 类型记忆**，既结构化又跨项目，模型读到后会更自觉执行。禁用结构化可设 `"typedMemory": false`。

### 10.5 代码层四：项目级 commands（自定义斜杠命令）

项目目录 `.codebuddy/` 还能放 **commands（自定义斜杠命令）**，把固定操作固化成 `/命令`（如 `/周报`、`/评审`），通过版本库团队共享，属于"能力固化"的轻量扩展。

### 10.6 细化落地方案（按目标逐条映射）

| 你的目标 | 最对路的官方拓展点 | 落点 / 代码层 |
|---|---|---|
| 全程中文 | `language: 简体中文` + Rules `alwaysApply` + `feedback` 记忆 | `settings.json` / `rules/zh-style.md` / `memories/global/feedback-*.md` |
| 风格统一 | `outputStyle` + Rules + `feedback` 记忆 + `zh-assistant` 子代理 | `settings.json` / `agents/zh-assistant.md` |
| 跨项目带能力/记忆 | 用户级 `rules/` `agents/` `skills/` `mcp.json` + global 记忆 | `~/.codebuddy/*` |
| 任务边界硬约束 | **`permissions.deny`**（比规则硬） + Rules 第 7-8 条 | `settings.json` 的 `permissions` |
| 换新手机也生效 | 用户级随同账号云同步；项目级随项目 Git/云同步 | 分层选择 + 版本库 |

**推荐最终组合（细化步骤）：**

1. **全局中文 + 风格 + 权限（用户级 settings.json）**：按 10.2 写入 `~/.codebuddy/settings.json`（`language`、`outputStyle`、`permissions.deny` 拦网盘/密钥）。
2. **中文+风格规则（用户级 rules）**：按第 9 章方案 A 写 `~/.codebuddy/rules/zh-style.md`（`alwaysApply: true`）。
3. **风格人格（用户级 agents）**：按 10.3 写 `~/.codebuddy/agents/zh-assistant.md`，需要统一风格时显式调用。
4. **结构化风格纠正（global feedback 记忆）**：按 10.4 写 `~/.codebuddy/memories/global/feedback-style.md`。
5. **跨设备双保险（项目级软链）**：需随项目稳到新手机的项目，用 `ln -s` 共享规则（第 9 章方案 B）。
6. **能力固化（项目级 commands）**：把高频固定操作写成 `/命令` 团队共享（10.5）。

> 优先级：规则层前置约束为主 → `permissions.deny` 做硬边界 → `feedback` 记忆做结构化沉淀 → `agents` 做风格人格兜底 → Hooks 仅作可选质检（第 8 章）。

### 10.7 诚实提醒（复用第 9.4）

- 本沙箱写文件 ≠ 真机生效；用户级配置须在真机用户目录建一次或靠同账号云同步。
- 用户级偏设备本地，跨手机不绝对；项目级随项目同步更稳。
- `settings.json` 直接改后，已开会话需 `/clear` 或重开才生效（`model`/`outputStyle` 改完需新会话；`/config` 或 `/model` 切换即时生效）。

---

## 第 11 章 其他拓展面（补齐官方配置全景）

> 第 10 章已覆盖：settings 字段、`agents`/`skills`/`mcp`、Typed Memory、commands（概念）。本章补齐**真正还遗漏的独立扩展面**，都与你的目标（中文 / 风格 / 跨项目 / 任务边界 / 切模型一致）强相关，每块带代码层。

### 11.1 代码层五：插件市场 Plugins（能力打包分发，团队自动安装）

不是单文件，而是把 `commands / agents / skills / hooks / mcpServers` **打包成一个插件**，支持**团队自动安装**——比手动复制规则稳得多，是"跨项目/团队共享能力"最对路的官方机制。

```json
// .codebuddy/settings.json（项目级，协作者克隆即自动安装）
{
  "extraKnownMarketplaces": {
    "team-tools": { "source": { "source": "github", "repo": "your-org/codebuddy-plugins" } }
  },
  "enabledPlugins": { "plugin-a@team-tools": true, "plugin-b@team-tools": true }
}
```

```bash
/plugin install <name>@<marketplace> --scope project   # 作用域：user/project/local/managed
/reload-plugins                                          # 装载变更，无需重启
```

> 一个插件 = 一套完整能力包（可同时声明 commands/agents/skills/hooks/mcpServers）。官方市场 `codebuddy-plugins-official` 已内置（如 GitHub 集成）。**把你那套"中文+风格"规则固化为一个插件，是团队/跨项目分发的最省事方式。**

### 11.2 代码层六：Auto Mode 智能权限分类器（任务边界的"智能"层）

第 10 章只用了 `permissions.deny`（硬拦），官方还有更聪明的 **auto 模式**：用大模型当"安全审查员"，按安全策略自动放行/拦截，直接减少弹窗——是"任务边界约束"的进阶形态。

```json
// ~/.codebuddy/settings.json（用户级）
{
  "permissions": { "defaultMode": "auto" },
  "autoReview": {
    "extraPolicy": "## 组织补充\n- 允许发布到 dev namespace\n- 不得修改共享测试数据库 schema"
  }
}
```

```bash
codebuddy auto-mode defaults   # 查看内置安全策略
codebuddy auto-mode config     # 查看当前生效策略来源（用户/项目/local）
```

> `autoReview.policy` 可**完全替换**内置策略；旧 `autoMode`（`environment`/`allow`/`soft_deny`/`hard_deny` 自然语言规则）仍兼容作附加策略。
> **注意边界**：autoMode **只从用户级 / 项目-local / CLI 读取，不读项目共享 settings.json**——因为它定义的是"本地安全边界"，不应被仓库静默篡改。

### 11.3 代码层七：权限模式族（比 allow/ask/deny 更宽）

`permissions` 之外，官方有一整套**权限模式**可选，覆盖"何时确认、何时直接拒绝、何时先计划"：

| 模式 | 语义 | 适合 |
|---|---|---|
| `default` | 默认，按需弹确认 | 日常 |
| `acceptEdits` | 编辑自动通过 | 信任环境 |
| `auto` | 分类器自动审（见 11.2） | 减弹窗又不想全放 |
| **`dontAsk`** | **未预批准动作直接拒绝，绝不打断** | CI / 批处理 / 后台代理（比 deny 更严） |
| **`plan`** | 先探查写计划、再确认，不直接改源码 | 重大变更前 |
| `bypassPermissions` | 跳过多数审批（容器/沙箱专用） | 隔离环境/脚本 |

```json
// 精细控制子代理与防逃逸
{
  "subagentPermissionMode": "bypassPermissions",
  "disableBypassPermissionsMode": "disable",   // 禁止 -y 逃逸
  "additionalDirectories": ["../docs/"]
}
```

### 11.4 代码层八：自定义命令进阶（锁模型 / 锁工具，且可用户级）

第 10 章只提了 commands 名字，实际它的 frontmatter 能**直接锁模型、锁工具**——和"切模型一致"诉求直接挂钩，且分项目级与用户级。

```markdown
// ~/.codebuddy/commands/周报.md（用户级，所有项目可用）
---
description: "生成中文周报，分段文字不用表格"
argument-hint: "[本周关键词]"
allowed-tools: Bash(git:*), Read
model: gpt-5
---
用简体中文、分段文字（不用表格）生成本周工作周报，结合 $ARGUMENTS 与 git 提交记录。
```

```bash
# 子目录 → 冒号命名：commands/frontend/build.md → /frontend:build
# 参数：$1 $2 位置参数，或 $ARGUMENTS 捕获全部
/frontend:build
/周报 模型切换调研
```

> 命令文件内容**是写给 CodeBuddy 的指令**（不是给用户看的）。`model` 字段可在命令级固定模型，保证"这个动作永远用某个模型跑"，是控制风格/能力一致性的利器。

### 11.5 顺手澄清：Skills 与 Commands 的区别

| | Commands（斜杠命令） | Skills（技能） |
|---|---|---|
| 触发 | 用户手动 `/命令` | **AI 自动识别调用** |
| 定位 | 固定提示/脚本封装 | 专业能力模板，AI 按场景自主选用 |
| 适用 | 你明知要跑的固定流程 | 希望模型"该用就用"的能力 |

### 11.6 代码层九：CI/CD 无头调用（把规则带进构建脚本）

会话配置不只是交互用——可用 CLI 无头模式把"中文+风格+规则"带进自动化流水线：

```bash
# 非交互单次执行，输出可管道给脚本
codebuddy -p '用简体中文总结本次 diff 的风险点，分段文字' \
  --output-format stream-json        # 或 text / json

# 配合权限模式，避免流水线卡确认弹窗
codebuddy -p '...' --permission-mode dontAsk --dangerously-skip-permissions
```

> 在 CI 里跑 CodeBuddy（如自动生成发布说明、审查 PR），它仍会读项目/用户的 `CODEBUDDY.md` 与 `rules/`——规则在无人值守场景同样生效。

### 11.7 运行目录（非配置、但属于官方扩展面）

`~/.codebuddy/` 与项目 `.codebuddy/` 下还有一批"运行时"目录，承载协作/集成能力：

| 目录 | 作用 |
|---|---|
| `teams/` | 多子代理协作运行时（并行多名 agent 分工） |
| `channels/` | 微信等频道集成（把会话接到 IM） |
| `computer-use/` | GUI 自动化录制与回放 |
| `plans/` | 计划模式文件（与 `plan` 权限模式配套） |

### 11.8 其他零散但有用的 settings 字段

| 字段 | 作用 |
|---|---|
| `reasoningEffort` | 推理深度（minimal→max），影响模型思考量 |
| `statusLine` | 自定义状态行命令（显示当前上下文） |
| `apiKeyHelper` | 自定义鉴权脚本（临时密钥轮换） |
| `sandbox` | Bash 沙箱开关 |
| `trustedDirectories` | 启动免信任弹窗的目录白名单 |
| `enableAllProjectMcpServers` / `enabledMcpjsonServers` / `disabledMcpjsonServers` | 项目 MCP 的批量授权 |
| `disableAllHooks` / `allowUntrustedFrontmatterHooks` | Hook 安全开关 |

### 11.9 拓展面全景总览（按目标归口）

| 你的目标 | 最对路拓展点 | 章节 |
|---|---|---|
| 全程中文 | `language` + Rules `alwaysApply` + `feedback` 记忆 | 9/10.2/10.4 |
| 风格统一 | `outputStyle` + Rules + `feedback` + `zh-assistant` 子代理 | 10.2/10.3/10.4 |
| 跨项目带能力/记忆 | 用户级 `rules/agents/skills/mcp.json` + global 记忆 + **插件** | 9/10.3/11.1 |
| 任务边界硬约束 | `permissions.deny` + **Auto Mode（auto）** + `dontAsk`/`plan` 模式 | 10.2/11.2/11.3 |
| 切模型一致 | 命令级 `model` / 子代理 `subagents.agents.*.model` | 10.2/11.4 |
| 换新手机也生效 | 用户级随同账号云同步；项目级随项目 Git/云同步；**插件团队分发** | 9/11.1 |

### 11.10 诚实提醒（复用第 9.4 / 10.7）

- 本沙箱写文件 ≠ 真机生效；用户级配置须在真机用户目录建一次或靠同账号云同步。
- 用户级偏设备本地，跨手机不绝对；项目级随项目同步更稳；**插件经团队仓库分发可绕开"本地"问题**。
- `settings.json` / `permissions` / 模式变更后，已开会话需 `/clear` 或重开才生效。

---

## 第 12 章 跨 App 可移植性（深入）

> 第 11 章讲了"机制不通用、内容可迁移"。本章深入拆解**结构性真相 + 实测坑 + 强制力降级 + 一份内容多端分发策略**，回答"换到豆包/DeepSeek 等 App 还生效不"。

### 12.1 底层范式差异（为什么项目级规则在豆包/DeepSeek 根本不存在）

不是配置问题，是**产品范式不同**——项目级规则是"工作区中心"架构的附属品，消费级聊天 App 是"会话中心"，没有项目目录可挂载规则：

| 范式 | 编码 Agent（CodeBuddy/Claude/Cursor） | 消费级聊天（豆包/DeepSeek App） |
|---|---|---|
| 核心单元 | **工作区/项目目录**（workspace-centric） | **会话线程**（conversation-centric） |
| 有无"当前项目"概念 | 有，Agent 在文件系统里操作 | 没有，只有聊天窗口 |
| 能否挂载目录级规则文件 | 能（`.codebuddy/` 跟着目录走） | 不能（没有目录可挂载） |
| 项目级隔离 | 天然支持 | 不存在 |

> 根因：消费级聊天 App 没有项目目录，"随项目 clone 生效"这回事在豆包里连对应概念都没有。

### 12.2 AGENTS.md 不是银弹——5 个静默失效坑（实测）

第 11 章建议"加一份 AGENTS.md 做通用档"，但实测它有尖锐的边（不报错、悄悄不生效）：

| 工具 | 坑（静默失效） |
|---|---|
| **Claude Code** | 工作目录或父目录存在 `CLAUDE.md`/`CLAUDE.local.md` 时，**默认不读 AGENTS.md**；v2.1.277 之前不支持。需 `/config` 设 `claude-md-and-agents-md` 或顶部加 `@AGENTS.md` |
| **Codex** | 所有指令文件合计 **32 KiB 上限**，超限尾部被截断（最深目录文件先切）；`AGENTS.override.md` 覆盖你的文件；**不读 `.claude/rules/`** |
| **Cursor** | Agent 模式下旧 `.cursorrules` 不可见，必须用 `.mdc`；早期版本只认根文件 |
| **Copilot/Codex/Cursor** | **不认 `@path` import 语法**，把 `@./x.md` 当纯文本——只有 Claude Code 解析 import |
| **Windows git clone** | 符号链接 `ln -s AGENTS.md CLAUDE.md` 会 checkout 成文本文件，除非开 `core.symlinks` |

> **验证是否真加载**：`/context`（Claude）、`codex debug prompt-input`（Codex）。**规则是上下文不是硬边界**——文件越长遵循度越低（>500 行 / >32 KiB 明显），所以 zh-style 要短、具体、靠前放。

```bash
# Claude Code：避免 AGENTS.md 被 CLAUDE.md 屏蔽的兼容写法
# 在 CLAUDE.md 顶部写（保留 Claude 专属笔记在下方）
@AGENTS.md
## Claude-specific notes（仅 Claude 需要的写这里）
```

### 12.3 强制力梯度（内容可迁移，但"强制"会降级）

机制可换，但**强制程度会掉档**——这是前面没说破的关键：

```text
CodeBuddy 的强制力栈（多层）：
  rules(软提示) → permissions.deny(硬拦命令) → hooks(硬拦截/质检) → 压缩重注(兜底)
        ↓ 迁移到别家，只剩第一层
其他编码工具：rules(软提示)           ← 没有 deny/hooks 对应物
        ↓ 迁移到消费 App
豆包/DeepSeek：系统提示词/记忆/手动粘贴(软提示，且可能不每轮注入)
```

> 结论：**"全程中文"靠软指令基本能保**；但"任务边界约束（禁止私自调网盘/读密钥）"在 CodeBuddy 能用 `permissions.deny` 硬拦，到了豆包/DeepSeek **只能靠"说"，无法硬拦**。换平台，"强制"退化成"劝导"。

### 12.4 豆包的"换手机"反而比 CodeBuddy 用户级更稳？

反直觉但属实：

- 豆包是**云原生消费 App**：对话记录、常用设置、智能体、**记忆**都随账号走**云端**，六端（网页/桌面/iOS/Android/Win/Mac）实时漫游。
- 官方明确：换手机重装，"只要登录同一手机号/抖音/飞书账号 + 开了记忆，就自动找回"，不丢。
- 而 CodeBuddy 用户级是**设备本地 + 可选云同步**，前文特意提醒"换手机不绝对"。

> 所以：**在"换手机记忆不丢"这件事上，豆包（账号云同步）天然比 CodeBuddy 用户级（本地偏多）更稳**；代价是豆包没有项目级/workspace，规则只能是"全局人设"，无法按项目切换。

### 12.5 真正可落地的"一份内容多端通用"策略

不要指望单一文件通吃，正确做法是**主源 + 分发改写**：

```text
主源：一份纯 Markdown 规则正文（= 本 SOP 的 zh-style 内容，保持短小 <500 行）
├─ 编码工具分发
│   ├─ AGENTS.md                    （根目录，跨工具公约数，Claude/Codex/Cursor/Copilot 原生读）
│   ├─ CLAUDE.md 顶部写 @AGENTS.md  （兼容 Claude，避免被忽略）
│   ├─ .cursor/rules/zh-style.mdc   （Cursor 专属，可 globs 触发）
│   └─ CODEBUDDY.md                 （CodeBuddy 专属）
└─ 消费 App
    ├─ 豆包：系统提示词(全局人设) + 记忆(账号云同步) + 智能体
    ├─ DeepSeek 官方：每次新对话粘贴"身份档案"（万能档案法）
    └─ DeepSeek via DSH：AGENTS.md + 用户级系统提示词插件
```

> 组织级真·跨团队同步（不是开箱即用）：Git submodule 引入 `company-standards/AGENTS.md`、或 Copilot 组织级私有 `.github` 仓库——比 MCP 拉规则稳。

### 12.6 豆包 / DeepSeek 分步落地（用户级中文+风格重建）

**豆包（账号云同步，换手机稳）：**

```text
1. 设置 → 系统提示词：粘贴本 SOP zh-style 全文（全局人设，对所有对话生效）
2. 设置 → 记忆：开启"记住我的偏好"；主动发"记住：全程简体中文；结论优先可执行操作；手机阅读用分段文字"
3. 智能体广场 → 创建专属助手：人设里写明语言/风格/任务边界（每个智能体独立记忆）
```

**DeepSeek 官方 App（默认无记忆，最弱）：**

```text
1. 备忘录建"AI 身份档案"：我是谁 / 用 AI 做啥 / 偏好（中文、分步骤、不用英文黑话）/ 固定情况
2. 每次新对话开头，先整段粘贴档案再提问（万能档案法）
3. 想要自动化：换 DSH（DeepSeek Harness）外壳 → 支持 AGENTS.md + 用户级系统提示词插件 + 记忆插件（~/.dsh）
```

### 12.7 模型切换一致性在别家的真相

- CodeBuddy 的"切模型风格不飘"靠**会话上下文保留 + 压缩重注**，是 coding agent 的上下文管理机制。
- 消费 App 多数**不支持会话中途切模型**，或切了等于新会话；"风格统一"只能靠系统提示词/记忆在每次请求注入。
- 所以"切模型风格不飘"在消费 App 反而**更考验系统提示词写得够不够硬**——回扣第 3 章"判定条件要写具体"。

### 12.8 本章一句话

换 App 时——① **项目级概念在消费 App 结构性消失**；② **AGENTS.md 通用但有 5 个静默失效坑，需配 `@import` + 长度控制**；③ **强制力从"硬拦"降级为"软劝"**；④ **豆包换手机反而比 CodeBuddy 用户级更稳（云原生）**；⑤ 正确做法是"一份主源内容 + 各端改写分发"，而非指望一个文件通吃。

---

## 第 13 章 实战案例：把 TVBox 工作流自动化并自加载

本章用"搜集配置仓库 → 并发测活线路 → 重新集成配置"这一真实工作流，把前面所有机制（规则 / 钩子 / Skills / Agents / Commands / 放置 / 打包）串成一套**可运行、可自加载**的成品，并澄清一个高频误解：**钩子+规则 与 目录式 Skills 不是对立，而是"触发层不同"**。

### 13.1 工作流与自动化本质

| 手动做法（模型一步步敲） | 自动化做法 |
|---|---|
| 模型 `git clone/pull` 各仓库 | 脚本一次性拉取+抽取源 |
| 模型挨条 `curl` 测活 | 脚本**并发**测活、结果落盘 |
| 模型手动改主配置 JSON | 脚本过滤失效源、幂等集成 |

**自动化本质**：把"干活的步骤"固化成脚本，模型只负责**调用**，不负责手敲。这正是第 10、11 章扩展点的落地闭环。

### 13.2 关键纠正：规则不干活，钩子才干活（两套模型对照）

很多人的误解是"我的（钩子+规则）和你的（放目录的 skills）不一样，目录版运行不起来"。其实：

- **规则（Rules）= 只注入提示词**，本身**不执行任何动作**，只告诉模型"该按这个来"。
- **钩子（Hooks）= 真正执行动作**，在事件点跑脚本/命令。
- **Skills / Agents / Commands 也与规则同类**（都是给模型的提示词/指令），脚本才是干活的。
- **两者都必须是 `.codebuddy/` 目录下的文件**——不存在"不落目录就能跑的钩子/规则"。你现有能跑的版本，本质也是某处 `.codebuddy/` 里的 `settings.json` + `rules/*.md`。

真正的差别只有**触发决定者**：

| | 钩子+规则（硬触发） | skills+脚本（软触发） |
|---|---|---|
| 指令载体 | `rules/*.md`（提示词） | `SKILL.md`（提示词） |
| 真干活 | **hooks 跑脚本** | 脚本（靠模型调） |
| 触发决定者 | **事件必跑**（SessionStart / UserPromptSubmit） | **模型判断**是否调用 |
| 可靠性 | 高（确定性） | 中（看模型） |
| 落点 | `.codebuddy/settings.json` + `rules/` | `.codebuddy/skills/` 等 |

> 所以"目录版运行不起来"是**半对半错**：能跑（官方机制），但触发是软的、可能不主动调；钩子是事件硬触发、确定性高。若你要"圈在规则内、到点必跑"，就该用钩子+规则，而不是只放 skills。

### 13.3 推荐组合：软硬结合

保留已建的脚本/Skills（负责自动发现与编排），再补一层钩子做**硬触发**。最小可运行示例：

```markdown
# .codebuddy/rules/tvbox.md  ← 规则：定边界（不执行）
---
alwaysApply: true
---
TVBox 配置维护：收到更新/测活需求时，必须按 collect_repos→check_live→merge_config
流程执行，禁止手动逐条 curl。
```

```json
// .codebuddy/settings.json  ← 钩子：事件到点，硬执行脚本（真干活）
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "grep -qi 'tvbox\\|测活\\|直播源' \"$CODEBUDDY_USER_MESSAGE\" && python3 .codebuddy/scripts/collect_repos.py && python3 .codebuddy/scripts/check_live.py sources.json && python3 .codebuddy/scripts/merge_config.py || true",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

执行链：**你发"更新tvbox" → UserPromptSubmit 钩子立即跑脚本 → 结果注入上下文 → 模型拿结果回答**，全程不依赖模型"想不想调"。

### 13.4 实战已建文件（本项目 `/workspace/.codebuddy/`）

```
.codebuddy/
├── skills/tvbox-config-sync/SKILL.md   ← 自动识别+流程编排（软触发核心）
├── agents/tvbox-agent.md               ← 隔离专职工人
├── commands/tvbox-sync.md              ← /tvbox-sync 显式触发
├── scripts/
│   ├── collect_repos.py                ← 拉仓库、抽源（改顶部 REPOS 登记你的仓库）
│   ├── check_live.py                   ← 并发测活（已实测：存活/失效正确）
│   └── merge_config.py                 ← 存活源集成进 master_config.json
└── tvbox/
    ├── master_config.example.json      ← 主配置示例
    ├── install-userlevel.sh            ← 一键装到用户级（所有项目可用）
    └── README.md                       ← 放置/打包说明书
```

> 当前已落地的是 **13.2 的"软触发"侧（skills/agents/commands+脚本）**；若要与你现有"钩子+规则"模型完全一致，按 13.3 补 `.codebuddy/settings.json` + `rules/tvbox.md` 即可（软硬结合）。

### 13.5 怎么"放进去"与"打包"（呼应第 9、11 章）

**放置三方式**：

| 方式 | 范围 | 做法 |
|---|---|---|
| A 项目级（已就绪） | 仅本项目 | 文件已在 `.codebuddy/`；`cp` 示例成 `master_config.json`；**开新会话**生效 |
| B 用户级（推荐跨项目） | 所有项目 | `bash .codebuddy/tvbox/install-userlevel.sh` → 复制到 `~/.codebuddy/` |
| C 插件（团队） | 协作者自动装 | 四个目录打成插件包，`settings.json` 里 `enabledPlugins` 声明（见 11.1） |

**打包三粒度**：

1. **跟项目走**：A 的文件就在项目里，`git commit` 后本身就是包，换设备 clone 即恢复（除项目记忆，见 2.5）。
2. **压缩包**：`zip -r tvbox-pack.zip .codebuddy/skills .codebuddy/agents .codebuddy/commands .codebuddy/scripts`，解压到对方项目 `.codebuddy/`。
3. **插件**：C，适合团队长期维护。

**使用前必改两处**：① `scripts/collect_repos.py` 顶部 `REPOS` 填你的真实仓库；② 复制 `master_config.example.json` 为项目根 `master_config.json` 填入你的源。

### 13.6 冒烟验证

脚本已实测：构造 1 个可达 + 1 个必失败源，`check_live.py` 正确输出 `存活 1 失效 1`；`merge_config.py` 正确过滤并生成 `master_config.new.json`。

### 13.7 本章一句话

TVBox 工作流自动化 = **脚本干活 + Skills/规则定边界 + 钩子硬触发**；规则与 Skills 都是"提示词"不执行，钩子才是真执行；两者都落 `.codebuddy/` 目录，差别只在"事件必跑（硬）"还是"模型调用（软）"。要确定性，补钩子；要自动发现，留 Skills；两者结合最稳。

---

## 第 14 章 机制本质：触发条件三含义与强制力光谱

本章澄清一个高频混淆：**"规则 + 触发条件让模型去工作" 与 "官方方式" 的差异，本质不是功能有无，而是"强制力档次"不同**。读懂本章，前面第 3、8、13 章的一切选择才有底层依据。

### 14.1 一句话本质

你的"规则+触发条件"通常是**钩子事件触发代码去干活（确定性）**，或**规则带条件注入（软）**；而官方"全程中文"这类，官方既给了**系统级设置（比规则更底层、更硬）**，也给了**规则自动注入（和你一样软）**——"不太一样"的真正含义是：官方多了一层**系统设置级的硬约束**，不纯靠提示词。

### 14.2 "触发条件"的三种含义（混淆根源）

你嘴里的"触发条件"，在 CodeBuddy 里对应三种不同东西，强制力天差地别：

| 你说的"触发" | 官方实际机制 | 它控制的是 | 模型"去工作"靠啥 |
|---|---|---|---|
| 规则啥时生效 | Rules：`alwaysApply` / `globs` / Agent Requested | **指令什么时候被注入上下文** | 模型**自愿**照做（软） |
| 事件到点执行 | Hooks：`SessionStart` / `UserPromptSubmit` / `PreToolUse` / `PostToolUse` | **什么时候真跑一段代码** | 代码**确定性**跑（硬，不靠模型） |
| 系统基设 | Settings：`/config` 语言 / `outputStyle` | 模型**底座行为** | 系统级生效（比规则硬） |

> 关键：第 1 种（规则条件）只是"让指令出现在模型面前"，模型**仍决定遵不遵守**；第 2 种（钩子）是"到点就跑代码"，**不依赖模型意愿**；第 3 种（设置）是"模型出厂底座就按这个来"。

### 14.3 强制力光谱（从软到硬）

```text
软 ←————————————————————————————→ 硬
规则/Skills提示词    /config系统设置    permissions.deny拦截     Hooks事件执行代码
(模型决定遵不遵)      (底座行为,更难忽略)  (直接禁止动作)           (确定性跑,不需模型同意)
```

- 你的"规则+触发条件"如果是**钩子** → 已在最硬档（代码必跑）。
- 如果只是 **rules 的 alwaysApply/globs** → 和官方 rules 是**同一档（软）**，并非更硬。
- 官方"全程中文"之所以"不太一样" → 因它能走 `/config` 系统设置档，比纯规则提示词更底层、更不易被忽略。

### 14.4 用"全程中文"具体对比

**你的方式（规则+触发条件，软）：**

```markdown
# rules/zh.md
---
alwaysApply: true   ← 触发条件：每次会话都注入
---
所有输出用简体中文。
```

→ 这是**软提示词**：指令注入上下文，模型"应该"照做。语言类指令模型服从度高，所以感觉有效；但本质是"劝"。

**官方方式（`/config` 语言，系统设置档）：**

```text
/config → Language → 简体中文
```

→ 这是**系统级基设**：写在模型底座，比上面那条规则更底层，项目级还能覆盖用户级。不依赖"规则被读到"，配置即生效。

**结论**：官方"不太一样"= 把"语言"做成独立**设置项（系统层）**，而非只能靠你写规则去"劝"。

### 14.5 回扣 TVBox 直觉（你之前的感觉是对的）

你曾说"官方目录版（skills）应该运行不起来"——现在能对上：
- 你现有 TVBox = **规则(定边界) + 钩子(事件硬触发脚本)** → 最硬组合，必跑。
- 我建的 skills 版 = **skill(软触发) + 脚本** → 模型"识别后调用"，软，可能不调。

所以**不是 skills 跑不起来，而是它比你钩子版软**。正确做法是软硬结合（见 13.3）：留 skills 做自动发现，补钩子做硬触发。

### 14.6 选型速查

| 你的目标 | 最对路的档位 | 落点 |
|---|---|---|
| 全程中文（软+稳） | **rules(软) + `/config` 语言(系统设置)** 叠加 | `rules/zh.md` + `/config` |
| 禁止某动作（硬） | **`permissions.deny`**（直接拦截） | `settings.json` |
| 到点必跑流程（最硬） | **Hooks 事件执行代码** | `settings.json` 的 `hooks` |
| 需要时智能识别（软） | **Skills / Agents / Commands** | `.codebuddy/skills` 等 |

### 14.7 本章一句话

"规则+触发条件"若指 **hooks** 已是最硬档；若指 **rules 的 alwaysApply/globs** 则与官方 rules 同档（软）。官方在"提示词"这一档之外，还多给了"系统设置"与"权限硬拦截"两档更硬的——这就是"不太一样"的全貌；**最稳做法是按目标选档位，必要时多档叠加**。

---

## 第 15 章 模型进化与经验复用（官方机制）

> 本章回答一个常见误解：**CodeBuddy 的"进化/学习"不是微调模型权重，而是模型外的一套"经验存储与复用"机制**（属于 external state / inference-time processing，不是 model-weight training）。经验不会写进模型大脑，而是写成文件/记忆，下次会话"喂进上下文"让模型表现得像记住了。这正好回扣第 9 章（记忆跨项目）与第 14 章（提示词层）。

### 15.1 本质澄清：不做权重训练，只做"模型外经验沉淀"

官方对"Agent 进化"的界定（腾讯云《Agent 自进化系列》）：
- **任务内适应（intra-task adaptation）**：本次运行里读懂报错、改对输出——Cursor/Codex/WorkBuddy 已擅长。
- **跨任务学习（cross-task learning）**：把"这次踩坑的教训"写入以后还会读到的规则/校验/标准流程，避免下次再犯——这才是"长期成长"的开始。

> 关键：失忆的是默认任务循环，不是系统没有存储器。官方把经验落点设计成并列的"抽屉"，让信息/规则/代码/技能都有地方保存。

### 15.2 经验复用载体（官方 7+ 抽屉，对应第 0.5 章坐标系）

| 抽屉 | 官方位置 | 经验类型 | 跨会话 | 跨设备 / 换账号 |
|---|---|---|---|---|
| **CODEBUDDY.md / AGENTS.md** | 项目级 / 用户级 / local | 静态规范（定死的，最稳） | ✅ | 随 Git / 本地 |
| **Auto Memory** | `~/.codebuddy/memories/{project-id}/` 或 `global/` | AI 自主提取的偏好/事实 | ✅ | 用户级本地偏多 |
| **Typed Memory** | 同上（4 类型结构化） | user/feedback/project/reference | ✅ | 同 Auto |
| **Rules** | `.codebuddy/rules/*.md` | 持续生效的规范 | ✅ | 随项目 / Git |
| **Skills** | `.codebuddy/skills/` | 封装好的可复用流程 | ✅ | 用户级跨项目 |
| **Workflow** | 工作流固化 | 稳定任务步骤 | ✅ | 随项目 |
| **代码/文件/知识库/测试用例/Trace 日志** | 各自位置 | 执行结果、领域信息、正确标准、历史执行 | ✅ | 视载体而定 |
| **self-improvement Skill**（WorkBuddy） | SkillHub 安装 | 记录经验/偏好/修正，后续相似任务优先参考 | ✅ | 见 Skill 说明 |

### 15.3 官方"自动进化"的具体机制

#### 15.3.1 Auto Memory：AI 自己挑经验存（默认开）
```bash
# 三种开关方式（任选）
/config                          # 面板切 Auto Memory 开关
/memory                          # 命令面板管理
# settings.json
{ "memory": { "autoMemoryEnabled": false } }
# 环境变量
export CODEBUDDY_DISABLE_AUTO_MEMORY=1
```
存储与加载：
```
~/.codebuddy/memories/
├── {project-id}/MEMORY.md       # 项目专属记忆索引（前 200 行自动加载）
└── global/MEMORY.md             # 跨所有项目生效
```

#### 15.3.2 Typed Memory：把经验分门别类（默认开）
```markdown
---
name: 输出风格纠正
description: 用户对中文输出与排版的持续纠正
type: feedback                   # ← 最贴"经验复用"的类型：踩坑后纠正，下次别再犯
---
- 全部用简体中文，禁止大段英文
- 结论优先配套可执行操作
- 手机阅读场景用分段文字而非表格
```
4 种类型：`user`（你是谁）/ **`feedback`（你纠正过 AI 的，最该用）** / `project`（项目决策）/ `reference`（外部系统指引）。默认启用；关闭：`memory.typedMemory:false` 或 `CODEBUDDY_TYPED_MEMORY_ENABLED=false`。

#### 15.3.3 缓存与重载（务必知道，否则"没生效"）
| 操作 | 是否清记忆缓存 |
|---|---|
| 进程重启 | ✅ 清空 |
| `/memory` 面板编辑 | ✅ 自动清 |
| `/clear` 命令 | ❌ 只清消息历史，**不清记忆** |
| 手动改记忆文件 | ❌ 需手动重启 |

#### 15.3.4 跨会话 / 跨设备（回扣第 9 章）
- 项目记忆随 Git 团队共享；用户记忆存本地不共享；local 记忆自动 gitignore。
- "经验跨设备不丢"结论不变：**提级为固定 Rules / CODEBUDDY.md 最稳**，纯 Auto Memory 跨设备不保证。

### 15.4 团队级经验治理（腾讯官方团队的进阶实践）

腾讯新闻官方文章讲透"经验即抛"痛点（一次 session 纠偏，下周同事又踩同坑），解法不是单用户记忆，而是**团队经验系统**，核心是 **Review / Dedup / Merge 三层治理链路**：
- **Review**：初版 90% 候选经验为废料，需过滤"临时 workaround"类噪声；
- **Dedup**：去重，避免同一坑重复沉淀；
- **Merge**：合并进团队可复用规范（沉淀成团队 `.codebuddy/rules/` 或 Spec 规约）。

> 对应你团队级实践：把个人 session 纠偏，提纯成团队 Rules / 知识库，让 "AI 带着项目语境进场"，打破"每次进项目从零开始"。

### 15.5 "自我改进"的更激进路径（务必区分状态）

| 路径 | 状态 | 说明 |
|---|---|---|
| **self-improvement Skill** | ✅ 官方 SkillHub 已发布 | WorkBuddy 记录经验/偏好/修正，长期使用越来越贴近习惯；通常自动利用沉淀 |
| **Lessons（session-end flush）** | ⚠️ 社区/候选实现 | `SESSION_END_FLUSH` 会话结束提案候选经验进审查队列；非主流通用版本 |
| **Learned-layer / Code evolution / Council / ToT·MCTS** | ⚠️ 候选研究实现 | 代码变体评估、确定性指挥、显式推理搜索——**明确非官方主版本、未发布**，勿当通用特性使用 |

> 严守边界：第三行来自社区 source-review 文档（作者自注"候选实现、非端到端基准"）。你真机用的 WorkBuddy/CodeBuddy 通用版，只该依赖 15.2–15.4（Auto/Typed Memory + Skills + Rules + self-improvement）。

### 15.6 落地：让经验"真复用"的最小动作

```bash
# 1. 确保 Auto Memory 开着（v2.61.0 后默认开）
/memory            # 确认开关；session 结束会自动候选保存

# 2. 把踩坑纠正固化成 feedback 类型记忆（比纯 Auto 更可控）
/memory save "全部用简体中文；涉及手机阅读用分段文字不用表格" --type feedback --scope global

# 3. 关键经验提级为固定规则，跨设备/换账号都稳（呼应第 9 章）
#    写进 CODEBUDDY.md 或 .codebuddy/rules/，不要只依赖 Auto Memory
```

### 15.7 本章一句话

官方"模型进化/经验复用" = **模型外经验沉淀体系**：核心是 Auto Memory（AI 自主存）+ Typed Memory（分 4 类结构化，尤其 `feedback`）+ Skills/Rules（固化复用）；**不做权重训练**。要跨设备稳、要团队复用，得把经验提级成固定 Rules / 走团队 Review-Dedup-Merge 链路，而非只靠 AI 自动记。

---

# 第 16 章 回滚 / 快照 / 唯一真源：做错规则或功能如何干净退回

## 16.0 本章要解决的真实痛点

> "做某一个规则或者某一个功能时，发现做错了、或这功能不想要了，要回滚到之前的状态；但前面的操作肯定会产生一些垃圾或旧指向，这可能会对我项目产生影响。"——这就是本章要解决的三件事：**回退到之前状态 / 删掉做过的垃圾 / 清掉指向已删文件的旧引用**。

核心结论先行：**官方有两套"真相"**——
- **快照（检查点 Checkpoint）= 本地撤销（local undo）**：会话内、自动、每提示一拍、30 天清理，救即时错误；
- **唯一真源（Git = permanent history + 可提交的 Markdown）= 永久基线**：跨会话、跨设备、跨人，永远在，救"长期/协作/换机器"。

两者互补，**快照不替代真源**。

## 16.1 官方回滚机制 = 检查点（快照 Checkpoint）

官方文档对检查点的定义：

> "当您与 CodeBuddy 协作时，检查点功能会在**每次编辑之前自动捕获代码的状态**。"
> "**每个用户提示都会创建一个新的检查点**。"
> "检查点会**跨会话持久保存**……随会话在 **30 天后自动清理（可配置）**。"
> "你可以把检查点看作'**本地撤销**'，而 **Git 是'永久历史'**'。"
> "检查点**补充版本控制而非替代它**。"

回退入口（两套，同一套语义）：

```bash
# 终端 / CLI：
/rewind            # 打开回退菜单（或在输入框连续按两次 Esc 也行）
# Web UI / IDE：鼠标移到任意一条"用户消息"上 → 点「回退到这里」
```

## 16.2 三种恢复模式（选错会留脏东西，务必分清）

| 模式 | 官方含义 | 解决你的哪个痛点 |
|---|---|---|
| **仅对话** | 回退到某条用户消息，保留代码更改（该消息回填输入框可改后重发） | 想换问法重答，代码先留着 |
| **仅代码** | 还原文件更改，保留对话 | "做过的脏东西"想清掉，聊天留着 |
| **代码和对话都退** | 两者一起恢复到会话中某个之前的时间点 | 方向错了，从那点彻底重做 |

```bash
# 典型用法：方向错了不知道从哪开始
/rewind
# → 在回退菜单里找到"方向还对的最后一条用户消息"
# → 选「代码和对话都退」→ 干净起点立刻回来 → 重新发要求
```

## 16.3 检查点不兜底的 4 件事（回滚坑你的地方，必看）

官方明确写死的边界：

```text
① Bash 命令改动不跟踪：rm / mv / cp / 以及 CodeBuddy 用 bash 新建的文件，检查点管不到
② 外部更改不跟踪：你在 CodeBuddy 之外手动改的、其他并发会话改的，不捕获
③ 不能替代版本控制：检查点 = 本地撤销；Git = 永久历史
④ /compact 压缩后：回退菜单只保留压缩后的提问，压缩前正文不再为运行中回退常驻
```

> 这就是为什么"做过的垃圾"和"旧指向"**光靠官方回退清不干净**——bash 生成的文件、跨文件引用，检查点一概不碰。

## 16.4 项目文件（产物）回退：本地任务才有，云端任务不提供

你做的规则/功能在 WorkBuddy 里叫**产物（artifacts）**——就是任务面板右侧那几个卡片（`SKILL.md`、`install` 脚本、SOP 这类）。

```text
本地任务（桌面 / 手机 App 的本地任务）：
  · 长按你发的消息 → 回退 → 这条消息之后的对话 + 产物一起退回
  · 确认框里，该消息"之后才生成"的产物标【将被删除】→ 确认后从目录消失
  · 已有更早版本的产物标【回退至某版本】（退到旧版而非删）
  · 注意：回退暂不支持部分文件类型，确认框会如实标出哪些回不退

云端任务 / 项目任务（如手机 App 的「云电脑」）：
  · 官方写死——回退 / 编辑 / 刷新「仅用于本地任务，云端任务和项目任务不提供」
  · 所以点不出回退入口不是你操作错，是云端任务压根没这功能
```

诚实提醒：回退只清"产物文件"，**不会改写其他文件里对它的引用**（`CODEBUDDY.md` 提的 skill、`settings.json` 的指向、别的规则 `@` 的被删文件）——这些旧指向回退后照样留着，变成脏引用。

## 16.5 手机 / App 端操作（无命令，点消息）

手机端没有 `/rewind` 命令，动作改成**点按或长按消息**唤出按钮：

```text
长按（或点按）你发的某条消息 → 弹出【复制 / 回退 / 编辑】
  · 回退：这条消息及之后的对话 + 产物一起退回（首条无回退按钮；会弹确认框列产物处理方式）
  · 编辑：改完发送 → 从这条消息重新开始；弹「是否回退产物历史版本?」可取消/不回退/回退

长按某条 AI 回复 → 菜单 →【重新生成】→ 只重跑那条回复（仅出现在最后一条下方）

确认框五种标注里只有【将被删除】不可逆：
  · 含义 = 该文件是"那条消息之后"才生成的，退回去它就不存在 → 从目录消失
  · 所以"想删后来做的工作" → 回退到生成它之前的消息，它自动被标【将被删除】清掉
```

手机端两个坑：**得等这一轮跑完**才能回退；**仅本地任务提供**，云端/项目任务不提供（那种情况回桌面或靠 git）。

## 16.6 唯一真源：Git = permanent history + 可提交 Markdown

官方没直接写 "single source of truth" 这个短语，但用等价对照讲出同一件事：

> "对于永久性版本历史和协作：继续使用版本控制（如 Git）来管理**提交、分支和长期历史**。"
> "检查点设计用于快速的会话级恢复。"（= 临时；真源是永久的 Git）

官方把 `.codebuddy/` 下的规则、配置、记忆都设计成 **committable（可提交到 Git）**——让它们随仓库成为可复现的真源：

```text
记忆真源（Markdown，非数据库）：
  · 存储：~/.codebuddy/memories/{project-id}/（项目记忆）、~/.codebuddy/memories/global/（全局记忆）
  · 每个项目有 MEMORY.md 索引文件，其前 200 行自动加载到会话上下文（= 记忆层索引真源）
配置真源（分层 Markdown）：
  · ~/.codebuddy/CODEBUDDY.md 用户级 / ./CODEBUDDY.md 项目级 / ./CODEBUDDY.local.md 本地级
```

```bash
# —— 把 Git 当唯一真源：做规则/功能前先提交一个干净基线 ——
git init                                   # 项目之初就建仓库（若还没有）
git add -A && git commit -m "baseline: 干净起点"
# 之后随便让 CodeBuddy 改/建文件，出事一条命令回到这个真源
```

## 16.7 git 兜底删除：清垃圾 + 回基线 + 清旧指向（完整代码）

因为检查点不跟踪 bash 生成文件、也不清旧引用，**真正干净只能靠 Git**：

```bash
# 1) 看清本次所有改动（被改 + 新建的垃圾未跟踪文件都列出）
git status
git diff                      # 看具体改了什么

# 2) 还原已跟踪文件的未提交改动
git checkout -- .

# 3) 删除所有未跟踪文件/目录 = 做功能时新建的垃圾（含 bash 生成的）
git clean -fd

# 4) 或彻底回到某提交（连已提交的都回退）
git log --oneline            # 找到做这个功能之前的提交哈希
git reset --hard <commit>

# 5) 清"旧指向"：查出仍引用被删文件/被删功能的脏引用，手动删掉对应行
grep -rn "被删功能名\|被删文件名" .codebuddy/ CODEBUDDY.md 2>/dev/null
```

组合拳（最稳）：先 `/rewind` 选「仅代码」还原 CodeBuddy 编辑工具改的 → 再 `git clean -fd` 清掉 bash 新建的 → 再 `grep` 清旧指向 → 最后 `git status` 确认全清。

## 16.8 回滚加固配置：settings.json + hooks 自动快照

让"快照"更可靠，官方可配的旋钮在 **CodeBuddy Code（CLI / IDE）的 `settings.json`**（分层：`~/.codebuddy/settings.json` 用户级 / `.codebuddy/settings.json` 项目级共享 / `.codebuddy/settings.local.json` 本地不入库）：

```jsonc
// .codebuddy/settings.json
{
  // 1) 检查点/会话历史的保留天数（文档里"30 天自动清理（可配置）"就是它）
  "cleanupPeriodDays": 30,

  // 2) 关掉自动压缩，保留回退菜单完整历史（否则 /compact 后只留压缩后的提问）
  "autoCompactEnabled": false,

  // 3) 直接拦掉检查点管不到的破坏性命令（rm/mv/cp 这类 bash 改动）
  "permissions": {
    "deny": ["Bash(rm:*)", "Bash(mv:*)", "Bash(cp:*)"]
  },

  // 4) hooks：每次写/改/删文件自动 git 提交快照，补上"不跟踪 bash、不清理旧引用"的坑
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": ".codebuddy/scripts/git-autosnapshot.sh" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "delete_file",
        "hooks": [{ "type": "command", "command": ".codebuddy/scripts/git-autosnapshot.sh" }]
      }
    ]
  }
}
```

配套自动快照脚本（社区 `git-autosnapshot` 思路：每次文件改动自动 commit 一个本地快照，限流、只本地不 push）：

```bash
#!/usr/bin/env bash
# .codebuddy/scripts/git-autosnapshot.sh —— 把每次编辑自动存成 git 快照
# 解决检查点不跟踪 bash、不清旧引用的坑：git 跟踪一切 + 全量历史可 grep
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -z "$REPO_ROOT" ] && exit 0                      # 不是 git 仓库就跳过

LAST_FILE="$REPO_ROOT/.codebuddy/.last_snapshot"
NOW="$(date +%s)"
MIN_GAP=60                                          # 限流：60 秒内只提交一次
if [ -f "$LAST_FILE" ]; then
  LAST="$(cat "$LAST_FILE" 2>/dev/null || echo 0)"
  [ $((NOW - LAST)) -lt "$MIN_GAP" ] && exit 0
fi

cd "$REPO_ROOT"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "autosnapshot: $(date '+%Y-%m-%d %H:%M:%S')" >/dev/null 2>&1 || true
fi
echo "$NOW" > "$LAST_FILE"
```

```bash
chmod +x .codebuddy/scripts/git-autosnapshot.sh
```

> 注意：这套 `settings.json` / `hooks` / `cleanupPeriodDays` 是 **CodeBuddy Code（CLI / IDE）** 配置；手机 App 的「云电脑」回退是**内置、无 settings 旋钮**的，没有对应入口。**但这只是指"手敲配置 / 回退 UI 入口"的环境差异——你手机上跟我对话生成的功能文件、配置、脚本，全部跟 Git 走，push 后电脑 / 手机 pull 功能完全一致，不存在"手机功能缺失"一说。**

## 16.9 按痛点分步操作（直接照做）

```text
痛点 A「不知道从哪开始 / 要重做」
  → 本地任务：/rewind 选「代码和对话都退」到方向还对的最后一条消息
  → 云端任务（手机云电脑）：无回退 → 靠 git：git reset --hard <baseline提交>

痛点 B「做过的怎么删（清垃圾）」
  → 本地任务：回退到生成它之前的消息，让它标【将被删除】自动清
  → 仍残留的 bash 文件：git clean -fd
  → 云端任务：右侧「显示详情面板」→「文件变更/全部文件」手动删

痛点 C「旧指向/脏引用」（最隐蔽，回退不管）
  → grep -rn "被删名" .codebuddy/ CODEBUDDY.md  → 手动删对应行

根治：项目一开始 git commit 干净基线；把会话当分支，用 /rename 打里程碑
```

## 16.10 本章一句话

官方回滚 = **检查点（快照，local undo：每提示自动拍、30 天清、只跟踪编辑工具、不替代 git、云端任务无入口）**；唯一真源 = **Git（permanent history）+ 可提交 Markdown（MEMORY.md 索引 / CODEBUDDY.md 分层）**。想"干净退回 + 清垃圾 + 清旧指向"，**快照救会话内即时错误，Git 才是跨设备跨人的永久真相**；做规则/功能前先 `git commit` 基线，出事 `git clean -fd` + `grep` 一条龙。

---

# 第 17 章 经验复用：如何使用 / 与技能进化的关系 / 实现机制 / 手机端实操

## 17.0 章节边界（先说清，免得和技能混）

第 15 章已讲"模型进化/经验复用"概览。本章把它拆成**使用层 / 与技能的关系层 / 实现层**，并补上**手机端实操**——因为官方"经验复用"在桌面端和手机端是两套入口。

> 一句话定调：**经验复用 ≠ 技能进化**。经验复用是官方的"动态学习层"（AI 自主累积），Skills 是"静态固化层"（人写好按需加载）；两者是"经验→技能"的转化关系，官方没有 Skill 自我改写的机制。

## 17.1 经验复用如何使用（桌面端 CodeBuddy Code）

官方把经验复用落在 **Auto Memory（自动记忆）+ Typed Memory（类型化记忆）** 上：

```bash
# 1) 打开记忆管理面板（看已加载哪些、开关、索引、目录）
/memory

# 2) 四种开关方式（任选其一）
  · /config 面板 → 切换 Auto Memory 开关          # 最简单
  · /memory 命令面板 → 切换
  · settings.json: "memory": { "autoMemoryEnabled": false }
  · 环境变量:     CODEBUDDY_DISABLE_AUTO_MEMORY=1

# 3) Typed Memory（默认启用，4 种结构化类型）
  · user      —— 用户角色/目标/偏好/背景
  · feedback  —— 你对 CodeBuddy 的纠正和指导（踩坑纠正归宿，最关键）
  · project   —— 进行中的工作/目标/决策
  · reference —— 外部系统/资源指引
#   禁用类型系统: "memory": { "typedMemory": false } 或 CODEBUDDY_TYPED_MEMORY_ENABLED=false
```

Typed Memory 文件格式（YAML frontmatter + 类型）：

```markdown
---
name: 用户角色
description: 用户的职业背景和技术专长
type: user
---
用户是资深后端工程师，拥有 10 年 Go 语言经验，但首次接触项目的 React 前端部分。
```

存储、索引与查找的官方规则：

```text
存储位置：
  · 项目记忆  ~/.codebuddy/memories/{project-id}/
  · 全局记忆  ~/.codebuddy/memories/global/
  · 每个项目一个 MEMORY.md 索引，其【前 200 行自动加载】到会话上下文
  · 详细内容放独立主题文件（preferences.md / decisions.md），从 MEMORY.md 链接

记忆查找（递归向上）：
  · 从当前工作目录开始，向上递归到根（不含 /），读任何 CODEBUDDY.md / CODEBUDDY.local.md
  · 子树嵌套的 CODEBUDDY.md 不启动时加载，只在读该子树文件时才包含

个人指令导入（不入库）：
  · @~/.codebuddy/my-project-instructions.md —— 团队成员给不提交仓库的私人指令
  · 递归导入最大深度 5 层（代码块/代码范围内的导入不解析）
```

## 17.2 和"技能进化"相关么？—— 直接结论：不等同

| 维度 | 经验复用（Memory） | 技能（Skills） |
|---|---|---|
| 本质 | **动态学习层**：AI 自主决定存什么，跨会话累积 | **静态固化层**：人/团队写好的领域知识包（SKILL.md + 脚本） |
| 是否会"进化" | 会——越用记越多（动态增长） | **官方层面不会自动进化**，写好后靠人手动迭代 |
| 加载机制 | MEMORY.md 前 200 行常驻 + 运行时检索 | 渐进式披露：L1 元数据(~100 token)→L2 正文(<5000)→L3 资源按需 |
| 关系 | 经验之源 | 经验"显性化封装"的产物 |

关键澄清：

```text
① 关系是"转化"不是"自动进化"：Skills 是把你的隐性经验（手法/坑点/SOP）显性化成
   SKILL.md 文件夹，让 AI 按需加载；一旦写成，官方没有"Skill 从使用经验里自动改写自己"的机制。

② self-improvement 技能（SkillHub 零成本技能）本质还是 memory：
   它"记录经验/偏好/修正并在后续参考"——底层是经验复用（memory），不是 Skill 文件自动改写。

③ 社区讲的"Skill 创建→记忆→管理→评估→优化"生命周期、MUSE-Autoskill 论文，
   是概念框架和社区实现，CodeBuddy 官方 Skills 文档未声明这套自动进化。

④ 想"越用越准"的官方正路有两条：
   · 让 memory 动态累积（feedback 类型最关键）
   · 人工把验证过的经验提级写进 SKILL.md / rules，让固化层更准
```

## 17.3 底层如何实现（官方声明 + 社区工程路径）

**官方声明层（CodeBuddy 文档明确写的）**：

```text
1. 存储介质：Markdown 文件 + YAML frontmatter（type/name/description），本地可提交，非数据库
2. 索引常驻：MEMORY.md 前 200 行自动注入上下文 —— 用"索引+链接"压住 token 预算
3. 查找机制：递归向上扫 CODEBUDDY.md + 子树惰性发现，避免全量读仓库
4. 类型系统：Typed Memory 用 4 类 frontmatter 让 AI 判断"该不该用这条记忆"
5. 分层加载（Skills 渐进式披露）：只启动加载 name+description，匹配才读正文，执行才读资源 ——
   官方称复杂任务可降 40%-60% 上下文占用
```

**社区工程路径（说明"还能怎么做"，非官方声明）**：

```text
· Consolidation Pipeline（社区 memory-system）：每晚 23:00 跑 6 阶段
  提取 → 去重(Jaccard≥0.8) → 过滤琐事 → 优先级评分 → 按项目分类 → 写 MEMORY.md(≤200行)
· Hybrid Search（社区 codebuddy）：向量相似度(0.7) + FTS4 关键词(0.3) + 时间衰减 + MMR 重排
  记忆分 Knowledge/Rule/Experience 三类，User/Project 两作用域，存 memory.json
```

## 17.4 手机端如何处理（核心，用户视角）

你在手机（WorkBuddy App），经验复用 = **「记忆」图形功能**，不是桌面端的 `/memory` 命令那套。入口：

```text
点击左下角头像 → 设置 → 左侧菜单「记忆」
```

这一页集中三种能力：

| 功能 | 手机上怎么用 |
|---|---|
| **生成对话记忆**（开关，默认开） | 开着，WorkBuddy 每晚整理当天会话，自动抽取"事实/偏好/人物关系/跟进事项" |
| **来自对话的记忆** | 点开卡片看它记了啥；右上「编辑」→ 对话告诉它"记住/忘记什么"；「删除」清某条 |
| **从其他 AI 导入记忆** | 复制官方提示词 → 丢给旧 AI（GPT/豆包等）让它整理 → 粘贴回「添加到记忆」 |

手机端你能主动做的 5 件事：

```text
① 主动记一条（最实用）：在对话框直接输入
   /remember 我是公众号博主，偏好简洁中文、先结论后展开
   → 它"永远记得"，下次不用重复自我介绍（分云/本地/工作区三层）

② 纠正记错的：设置→记忆→点卡片→编辑→"XX 那条不对，应该改成…"
   （这就是桌面端 feedback 类型的手机等价物——踩坑纠正全靠它）

③ 删过期的：卡片右上删除图标；或一键关闭"生成对话记忆"开关

④ 搬旧 AI 的习惯：记忆页「从其他 AI 导入记忆」→ 按四步走
   复制提示词 → 旧 AI 整理 → 逐项检查(删凭据/隐私) → 粘贴添加

⑤ 长期规矩写死：设置里「给 WorkBuddy 的指令」填一段
   （相当于用户级 rules 的手机版——每次开工前先读，不依赖它"猜"）
```

**手机 vs 桌面端的诚实差异**：

| 能力 | 桌面端（CodeBuddy Code） | 手机端（WorkBuddy App） |
|---|---|---|
| 记忆开关 | `/config`、settings.json、环境变量 | 设置→记忆，「生成对话记忆」开关 |
| 主动记 | `/memory save --type feedback` | `/remember` 对话命令 + 记忆页编辑 |
| 类型系统 | Typed Memory 4 类 frontmatter | 概括成事实/偏好/关系/跟进（不可见类型） |
| 跨设备 | 跟账号云同步 | **同样跟账号云同步** |

> 你**在桌面端手动改 `/memory` 配置的那套，手机端不便手动改**（无手敲命令行、无手改 settings.json 入口）；但**功能文件跟 Git 走，手机上让我在会话里生成 / 执行命令一样可行，跨端一致**。且"记忆数据"本身是**账号云同步**的——桌面纠正的偏好，手机也能用；反之亦然。

**解决最早痛点：换手机记忆丢不丢**——官方跨设备同步基于账号（Google / GitHub OAuth 同账号）：

```text
✅ 会同步：账号设置/偏好、Memory（记忆）、自动化定义、专家·技能配置
❌ 不同步：任务执行本身（在 PC 本地跑）、本地文件
→ 换手机只要用同一个账号登录，记忆跟着走，不丢
```

**手机上另外两个"经验复用"载体（别只盯记忆）**：

```text
1) self-improvement 技能（SkillHub 零成本）：在「专家·技能·连接器 → 技能市场」搜 self-improvement 装，
   装好后 WorkBuddy 自动记录经验/偏好/修正，后续相似任务优先参考，"越用越贴你习惯"。
2) 资料库：对 AI 说"把这份存到资料库"，它就成了你和 AI 的"作品"长期留存，
   新对话说"先读资料库里 XX"就能接上继续做（三端同步）。
   与记忆互补：记忆 = 你的画像；资料库 = 你们做出来的成果。
```

## 17.5 手机端日常清单（建议每周一次）

```text
1. 设置 → 记忆，扫一遍卡片，删过期的、改记偏的（最重要）
2. 重要偏好用 /remember 主动固化一条，别全靠它自动抽
3. 长期规矩写进「给 WorkBuddy 的指令」
4. 换设备 → 同账号登录，记忆自动同步，不用重来
```

## 17.6 本章一句话

官方经验复用 = **Auto Memory（AI 自主存）+ Typed Memory（4 类结构化，feedback 最关键）+ MEMORY.md 前 200 行索引 + 递归查找 + 账号云同步**；它和 Skills 是"动态学习层 vs 静态固化层"的**转化关系**，不是技能自动进化——官方无 Skill 自我改写机制，要"越用越准"靠 memory 累积 + 人手动提级固化。手机端用「设置→记忆」图形界面 + `/remember` + 「给 WorkBuddy 的指令」三件套，数据跟账号走、换手机不丢。

---

# 第 18 章 底座层能接入的东西（平台基座集成的外部/扩展能力）

## 18.0 本章讲什么

"底座层"= WorkBuddy / CodeBuddy 这个 Agent 平台基座能**接入/集成**的外部与扩展能力。这是第 0.5 章"能力层"的**具象化**：MCP / Connector 是能力层的"接入面"，模型是底座，Skills / 专家 / 自动化 / 记忆是能力层的"内生扩展"。分五类讲。

## 18.1 外部服务 —— 连接器 Connector（核心"接入外物"能力）

官方定义：连接器是 WorkBuddy 与外部系统之间的**桥梁**，基于 **MCP 标准协议**把外部能力引入 AI 工作流，让你不用手动切工具就能跨平台操作。

| 类别 | 预置连接器（一键授权） | 接入后能做什么 |
|---|---|---|
| 腾讯系 | QQ 邮箱、腾讯文档、腾讯乐享、腾讯会议、TAPD、腾讯网盘(微云) | 数据查询 / 服务调用 / 文件管理 / 消息通知 |
| 通用 | 网页搜索 | 检索 |
| 第三方 SaaS | 飞书、企业微信、有道云笔记、墨刀、企查查等 | 跨平台协同、查询 |
| **自定义** | 右上角「自定义连接器」→ 装自定义 MCP 服务（JSON 配置） | 私有库/自建 API/合规数据 |

## 18.2 模型底座 —— 自定义模型接入

WorkBuddy 内置主流模型（Auto / 混元 / GLM / MiniMax / Kimi / DeepSeek），同时支持**把第三方模型接进来当底座**：

```text
· 预设供应商：腾讯云 Token Plan / Coding Plan（填套餐 API Key 选模型）
· 自定义 API：手动填 URL / API Key / 模型名（不在列表的服务）
· 本地部署 Ollama：监听 11434 端口、兼容 OpenAI 协议（内网/隐私/离线/零成本）
· 前提：企业管理员"成员自定义模型策略"允许（个人版一般直接可用）
· 配置存本地 workbuddy/models.json，不上传云端
```

## 18.3 知识底座 —— 资料库 / 知识库（RAG 注入）

```text
· 资料库：AI 原生知识管理空间，存"你和 AI 做出来的成果"，跨对话记得、三端同步
· IMA 知识库：外部收集的资料（行业报告/技术文档），RAG 注入到对话
· 上传 文档/网页/公众号/笔记/图片/音频 → 基于库提问、生成文案
```

## 18.4 能力底座 —— 技能 Skills + 专家 + CLI

```text
· 技能 Skills：封装固定 SOP（市场一键装 / 上传包 / 对话描述自动生成）
· 专家 / 专家团：角色切换（人设+方法论+工具链）；专家团多专家并行整合
· CLI 工具：连接器 CLI 方案（mcp.json 替代 cli.json）
```

## 18.5 编排底座 —— 自动化 + 记忆

```text
· 自动化：定时/事件触发，设一次周期跑（早报/周报/资讯简报）
· 记忆 Memory：跨会话/跨设备云同步的画像（见第 17 章）
```

## 18.6 手机端能触到哪些（你最关心的）

```text
✅ 手机 App 直接有入口：连接器、技能、专家、记忆、自动化、自定义模型（设置→模型）
✅ 连接器快捷管理：消息框里就能开关/断开
⚠️ MCP 自定义 JSON 精细配置：主要在桌面/IDE 手敲；手机端可让我在会话里生成配置文件、或用"自定义连接器"引导式配置，不手改 JSON —— 功能跨端一致
```

## 18.7 与坐标系（第 0.5 章）的关系

```text
基础层：本机/账号（语言/outputStyle/记忆云同步/模型底座）
能力层：Rules / Hooks / Permissions / Skills / Agents / Commands / Plugins / MCP(连接器)
                              ↑ MCP 与连接器 = 能力层的"接入面"，把外部系统接进底座
级别：用户级(~/.codebuddy/，跟账号云同步) / 项目级(./.codebuddy/，跟 Git) / 本地级(*.local.json，gitignore)
```

## 18.8 本章一句话

底座层能接入的东西 = **连接器（腾讯系+第三方 SaaS+自定义 MCP）打通外部系统 + 自定义模型当底座（含本地 Ollama）+ 资料库/IMA 注入知识 + Skills/专家/CLI 扩能力 + 自动化/记忆做编排**；手机端除"MCP 手改 JSON"外基本都能触到，本质是能力层"接入面"把外部世界拉进 Agent 底座。

---

# 第 19 章 规则强制链与通道失效（实例：手机 vs 桌面生效判定 + 修复）

## 19.0 本章来源（真实生态诊断，不是空谈）

第 3 章讲了 Rules 的官方机制，第 8 章讲了 Hooks 加固。但"规则写了≠生效"——本章用用户真实仓库 `tvbox-eco`（私有，81 commits，含 23 条常驻核心规则 `rules/core.json`）做实例，讲清**为什么一套设计精良的规则在桌面生龙活虎、在手机基本休眠**，以及怎么把它"搬活"到手机。

> 关键认知：**规则的生效不取决于你写得多硬，而取决于它的"强制形态"落在哪个执行通道，而那个通道在你的端上跑不跑。**

## 19.1 规则强制链真相：守卫形态分类

实测 `rules/core.json` 23 条常驻规则的强制级别与守卫形态分布：

```text
enforce_level 分布：GATE 12 ｜ SCAN 8 ｜ DOC 3
guard_form   分布：hook 8 ｜ GATE 2 ｜ static_scan 3 ｜ scan 2 ｜ declare 3 ｜ manual 5
```

| 守卫形态 | 含义 | 靠什么执行 | 手机/云端跑得动吗 |
|---|---|---|---|
| **hook** | 钩子硬拦（脚本 exit≠0 即拦） | `settings.json` hooks 执行脚本 | ❌ 手机/云端任务不跑钩子 |
| **GATE** | 真实拦截形态（registry_guard 等） | 同样是钩子执行 | ❌ 同上 |
| **static_scan** | 静态扫描脚本 | `Stop`/`PreToolUse` 钩子跑脚本 | ❌ 同上 |
| **scan** | 扫描器（verify/） | 钩子触发扫描 | ❌ 同上 |
| **declare** | 声明注入（进上下文，无拦截） | `UserPromptSubmit` 钩子注入 additionalContext | ❌ 钩子不跑→连"被看到"都做不到 |
| **manual** | 手动/声明（需模型主动读） | 模型自觉去读 `rules/` | ❌ 手机不自动读非官方路径文件 |

## 19.2 手机 vs 桌面 生效判定表（23 条逐类）

```text
桌面（CodeBuddy Code / CLI / IDE，钩子能跑）：
  ✅ hook(8) + GATE(2) + static_scan(3)            → 真拦截 / 真扫描
  ⚠️ declare(3) + scan(2) + manual(5)              → 注入/读了才软生效
  → 整张网在桌面基本全活

手机（WorkBuddy App / 云电脑 云端任务，钩子不跑）：
  ❌ hook(8) / GATE(2) / static_scan(3) / scan(2)  → 死（执行型全灭）
  ❌ declare(3)                                   → 死（注入钩子不跑，连进上下文都没有）
  ❌ manual(5)                                    → 死（不自动读 rules/）
  → 只剩顶层 CODEBUDDY.md 薄壳里 3 句软话（语言/三态/先验环境），且无任何拦截
```

## 19.3 铁证：连"声明类"都死了

M-R215 的 note 原文（实测）：

```text
"原 GATE 接线已摘 per disposition.md｜M-R215 注入经官方 UserPromptSubmit additionalContext
 通道落地（settings.json 注册 UserPromptSubmit→govern.py→action_mr215_inject→additionalContext，
 约 2442 字符开工摘要）"
```

含义：连"声明类"规则（M-R215 开工必读 / M-R130 并行 / M-R136 门禁三关）都**依赖钩子把摘要注入上下文**才能进模型视野。钩子不跑 → 这条注入链也断 → 声明类在手机上连"被模型看到"都做不到，更别说遵守。

> 呼应第 16 章：**回退/编辑/钩子这类"执行型"能力只在 CodeBuddy Code（CLI/IDE）提供，WorkBuddy 手机 App、尤其「云电脑」云端任务不提供。** 规则强制链建立在钩子上，自然在手机上整条熄火。

## 19.4 手机上到底"生效"了什么

只有**顶层 `CODEBUDDY.md`（薄壳）直接写死的 3 句软话**会被自动加载：

```markdown
## 三条不可协商
- **语言**：回复语言跟随用户消息语言（中文 → 全程简体中文）；切换模型、压缩上下文、开新会话都不得重置为英文。
- **判定三态**：命令输出只判真阳性 / 真阴性 / 无法判定；报错、超时、无输出、被拦截一律记"无法判定"。
- **先验环境**：动手前 pwd -P + git log --oneline -1 + cat VERSION，确认自己在真实仓库里。
```

**就这 3 句，且都是"软指令 + 零拦截"**——模型看到了可能照做，但没有任何钩子兜底，所以该漂还是漂（第 17/18 章用户问的"全程中文没实现"正是这么漏的）。其余 20 条全在 `rules/core.json`，手机不自动读该文件，等于没加载。

> 补充坑：`.codebuddy/CODEBUDDY.md`（含 CORE_INJECT 的 23 条派生段）**也不是标准自动加载路径**——它得靠钩子或模型去读，手机上同样靠不住；标准项目级指令只有**顶层 `CODEBUDDY.md`**。

## 19.5 根因一句话

> 这套规则**全靠"钩子执行"或"模型主动去读非自动加载文件"才能生效**。手机/云端任务不跑钩子、只自动加载顶层 `CODEBUDDY.md` 薄壳 → **23 条里真正落地的只有薄壳里 3 句软话，且零拦截**。桌面 CLI 上生龙活虎，手机上基本休眠。和"全程中文失效"是同一个根因。

## 19.6 把规则"搬活"到手机的修复通道（按可靠性）

```text
① 顶层 CODEBUDDY.md 内联（最稳·手机必加载）
   把要强制的条（语言/三态/并行/换模型）【直接写进薄壳】，别再写"去看 rules/ ECOSYS.md"。
   改法示例：
     ## 强制铁律（本仓库每会话无条件遵守，不依赖钩子）
     - 必须全程简体中文回复（术语可保留英文原词）；切模型/会话/压缩都不得重置。
     - 命令输出只判 真阳性/真阴性/无法判定，"没查到"≠"没有"。

② 新建官方自动加载路径 .codebuddy/rules/（你之前漏建，rules/ 在顶层不自动读）
   建 .codebuddy/rules/zh-style.md：
     ---
     description: 项目全程简体中文与输出风格统一强制规则
     alwaysApply: true
     enabled: true
     priority: high
     ---
     1. 全程简体中文回复，术语可保留英文原词。
     2. 先结论后展开，用表格/代码框压缩篇幅。
   → 这是官方真·自动加载路径，手机必读。

③ 手机"给 WorkBuddy 的指令"（账号云同步·跨设备最稳兜底）
   设置 → 给 WorkBuddy 的指令 → "始终用简体中文回复，先结论后展开。"
```

> 三通道叠加原则（呼应第 3/17 章）：**把规则写进"会被自动加载的文件"（顶层 CODEBUDDY.md + `.codebuddy/rules/` + 手机指令），而不是藏在顶层 `rules/`（不自动读）或押在钩子注入上（手机不跑）。**

## 19.7 本章一句话

**规则生效不取决于写得多硬，而取决于它的强制形态落在哪个执行通道、那个通道在你的端上跑不跑。建立在钩子上的规则体系（tvbox-eco 的 23 条）在桌面 CLI 全活、在手机/云端基本休眠——唯一落地的只有顶层 CODEBUDDY.md 薄壳里 3 句零拦截软话；修复=把要强制的条内联进 CODEBUDDY.md + 建官方 `.codebuddy/rules/` + 手机指令，别再押钩子注入。**

---

*整理依据：CodeBuddy 官方文档（memory / Rules / settings / hooks / sub-agents / skills / mcp / plugins / auto-mode / commands / release-notes / **checkpointing（检查点·回滚·快照）** / **WorkBuddy 任务对话（回退·编辑·刷新·产物标注·仅本地任务）** / **移动端任务执行与对话（长按重新生成·停止·队列）** / **best-practices（检查点回滚·会话即分支·Git 永久历史）** / **连接器 Connector（MCP 标准协议·腾讯系+第三方+自定义）** / **自定义模型接入（API/Ollama/models.json）** / **资料库/IMA 知识库（RAG）** / **自动化/记忆（账号云同步）**）+ 跨工具指令文件生态实测（AGENTS.md / CLAUDE.md / .cursor/rules / GEMINI.md / copilot-instructions.md 对照；agents.md 标准；豆包六端云同步官方说明；DeepSeek DSH/DeepSeek-TUI 记忆机制；社区 git-autosnapshot 钩子实践；SkillHub self-improvement 技能）+ **用户真实仓库 tvbox-eco 实测（rules/core.json 23 条 enforce_level/guard_form 分布；.codebuddy/settings.json 钩子接线；顶层与 .codebuddy/CODEBUDDY.md 薄壳；M-R215 摘线改 additionalContext 注入 note）**；**新生态 codebuddy-eco 脚手架实测（以本 SOP 为治理基础、tvbox-eco 为结构借鉴；`.codebuddy/` 官方路径 + 薄壳 CODEBUDDY.md + `zh-style.md` 自动加载规则 + 四去 TVBox 化基建技能 + 轻量 MANIFEST.json + `docs/governance.md` 章节映射 + 规则侧字段级审计（core.json 23 条 / 49 字段 / 6 处描述 / 降级不同步 / 覆盖缺口）+ 三分离实测（core-8 用户级基座 / paths 条件规则 / 台账归位）+ 口径统一元规则与机检实测（registry 真源登记 / M1–M7 / terminology_check / 负向验证）+ 口径统一规则正式条款入 SOP（20.11：适用 / 约束 / 门禁 / 处置，条文只留指针不复制）+ 技能侧机检守护与官方口径核对（20.12：Skills 系统文档 frontmatter 字段 / description 定位 / 触发方式 / 机检第 ⑦ 项）+ 交接包/机读门禁/可视化面板落地（20.13：`--json` 机读输出 / 面板四视图 / 回顾式进度不伪造前瞻式 / 落点独立不进 15 文件骨架））**。*

---

# 第 20 章 技能/规则「接活」实例：从沉睡仓库到手机可触发

> 本章把前 19 章的治理原则**落到一次真实操作**上：什么叫"接活"、两次接活（tvbox-eco 官方路径化、codebuddy-eco 新生态脚手架）怎么做的、薄壳法为何优于整镜像、去 TVBox 化清单、以及接活验证清单。

## 20.0 什么是"接活"

**"接活"= 把技能/规则接入官方自动加载路径**（`.codebuddy/rules/`、`.codebuddy/skills/`、顶层 `CODEBUDDY.md`），让它们**在手机/云端任务里也能被自动加载、真正生效**，而不是躺在顶层自建 `rules/` `skills/`（不自动读）或押在钩子注入上（手机不跑，第 19 章）。

> 一句话判别：**写在"会被自动加载的文件"里 = 接活；藏在顶层非官方路径或押钩子 = 没接活。**

## 20.1 第一次接活：tvbox-eco 官方路径化

**背景**：tvbox-eco 的 23 条规则 + 4 技能全在顶层自建 `rules/` `skills/` + 钩子，手机基本休眠（第 19 章诊断根因）。

**接活动作**（推到官方路径的 5 个文件）：

| 文件 | 内容 |
|---|---|
| `.codebuddy/rules/tvbox-core.md` | frontmatter(`alwaysApply:true,enabled:true,priority:high`)，内联 §1 语言铁律(无条件全程中文)/§2 三态诚实/§3 先验环境/§4 并行纪律/§5 换模型铁律/§6 正本入口/§7 安全红线(不写明文 token)/§8 23 条索引表 |
| `.codebuddy/skills/{learn-hub,machine-bootstrap,probe-hub,tvbox-source-hub}/SKILL.md` | 薄壳入口，frontmatter 含 name+description(触发词)，正文指向顶层 `skills/{name}/` 唯一实现，强调脚本路径相对仓库根 |

**关键决策：薄壳法，不整镜像**。原因：技能脚本引用相对仓库根（如 `python3 skills/probe-hub/scripts/forge.py`），整镜像会路径断裂 + 双真源。故官方路径只放"薄壳入口"，真身仍在顶层 `skills/`，手机读到薄壳 → 去顶层调实现。

## 20.2 第二次接活：codebuddy-eco 新生态脚手架

**背景**：要在新项目复用生态治理经验——以本 SOP 为治理基础、tvbox-eco 为结构借鉴。

**落地产物**（`/workspace/codebuddy-eco/`，详见该目录 `docs/governance.md`）：

| 产物 | 作用 | 对应 SOP |
|---|---|---|
| `.codebuddy/CODEBUDDY.md` 薄壳 | 内联三不可协商 + 5 条强制铁律 | 第 19 章① |
| `.codebuddy/rules/zh-style.md` | 官方自动加载规则(`alwaysApply:true`)，把第 16–19 章治理原则落成条款 | 第 19 章② |
| `.codebuddy/skills/` 四基建技能（去 TVBox 化） | `skill-evolution`(经验复用发动机)/`machine-bootstrap`(唯一真源克隆端)/`feature-gate`(安全迭代阀门)/`artifact-store`(资料库联动产物侧) | 第 17/18 章 |
| `.codebuddy/MANIFEST.json` | 轻量治理清单（依赖图+事件契约，去 god-object） | 第 18 章 |
| `docs/governance.md` | SOP 章节 ↔ 本生态产物逐项映射 + 就绪验证清单 | 全 SOP |

**与 tvbox-eco 的关系：借鉴结构，不搬业务**——只学 `.codebuddy/` 官方路径 + SKILL.md 契约 + MANIFEST 形态；**不借鉴** 23 条钩子强制体系（手机不跑钩子）与 TVBox 专属能力技能（probe-hub/tvbox-source-hub/tvbox-inspect/tvbox-interface）。

## 20.3 接活方法论：薄壳法 vs 整镜像

| 维度 | 薄壳法（已有大仓库推荐） | 整镜像（全新小项目） |
|---|---|---|
| 做法 | 官方路径放薄壳入口，真身留原处 | 整包复制到官方路径 |
| 路径风险 | 低（脚本相对仓库根仍有效） | 高（相对路径易断裂） |
| 真源 | 单一（原处） | 双真源（易漂移） |
| 适用 | 已有生态、脚本引用相对路径 | 无历史包袱的新项目 |

> 结论：已有生态用**薄壳法**；全新项目直接把技能住进 `.codebuddy/skills/`（无需薄壳，本就是官方路径）。

## 20.4 去 TVBox 化清单（技能搬入新生态时）

1. 剥离 `tvbox` / `D包` / `底包` / `线路` 等专属名词与业务契约。
2. `machine-bootstrap` 把写死 clone 目标改为读 `BOOTSTRAP_REPO` 环境变量/参数。
3. `artifact-store` 把"远程"目标从 TVBox space 改为本生态资料库/IMA（第 18 章联动）。
4. `skill-evolution` 清掉 references 残留 TVBox 案例，保留通用进化引擎。
5. 各技能脚本不留 140KB 原版，改"orig 指针 + 改造清单"，按需搬运。

> 原始参考实现见私有仓库 `tvbox342078879/tvbox-eco`：`archive/`(skill-evolution/feature-gate/artifact-store) 与 `skills/machine-bootstrap/`。

## 20.5 接活验证清单

- [ ] 文件落在 `.codebuddy/rules/` 或 `.codebuddy/skills/`（官方路径，非顶层自建）
- [ ] 规则 `alwaysApply:true`；技能 frontmatter 含 `name` + `description`(触发词)
- [ ] 手机端"给 WorkBuddy 的指令"含中文铁律（三通道叠加，第 19 章③）
- [ ] 用中文提问，确认模型全程中文、未因换模型漂
- [ ] 技能触发词能命中（如"换机 / 灰度 / 产物治理"）
- [ ] 安全红线：`grep -R "ghp_\|token"` 全仓无明文凭据落文件

## 20.6 本章一句话

**"接活"= 把技能/规则写进会被自动加载的官方路径（`.codebuddy/rules/`、`.codebuddy/skills/`、顶层 CODEBUDDY.md 薄壳）+ 手机指令三通道叠加，而非藏在顶层非官方路径或押钩子；已有大仓库用薄壳法（真身留原处、官方路径放入口），全新项目直接住官方路径；搬到新生态必须去 TVBox 化（剥离专属名词、参数化 repo、资料库联动）。**

## 20.7 配套：手机"长期用变卡"的官方一手解法（codebuddy-eco 治理层）

> 本节把 20.2 脚手架里的"防卡顿治理"从社区推断升级为**官方一手方法**，依据 CodeBuddy Code **v2.51.0 发布说明** + CLI **Best Practices** + CLI **Memory 文档**。新生态落点：`.codebuddy/rules/zh-style.md` §8（8.1–8.4）+ `.codebuddy/skills/artifact-store/SKILL.md` §6。

### 20.7.1 根因（官方，非社区推断）
手机长期用变卡，不是硬件问题，而是**上下文窗口快速填满 + 记忆/规则全量加载 + 本地数据堆积**：上下文含全部对话、每读过的文件、每条命令输出，越长越易"忘指令/出错"；四层记忆文件全部启动时自动注入；产物/缓存/旧会话不清理则搜索与切换变慢。

### 20.7.2 四类官方解法（优先于人工方案）

| 卡顿根因 | 官方原生解法 | 新生态落点 |
|---|---|---|
| 上下文窗口填满 | `/clear` 纪律（不相关任务间频繁重置，纠错≥2次即重开）；自动压缩 + `/compact <指令>` 定制；Subagents 独立上下文调研（`.codebuddy/agents/`） | `zh-style.md` §8.1 |
| 记忆/规则全量加载 | **v2.51.0 记忆目录摘要（按需加载）+ 自动清理（随会话历史，复用保留期）**；`paths` 条件规则减少 `alwaysApply` 注入；`enabled:false` 临时关闭；`parentDiscovery:false` 防跨目录继承 | §8.2 / §8.3 |
| 本地数据（产物/缓存/旧会话）堆积 | `/clear` + 移动端删/归档会话（≡→任务历史→编辑→垃圾桶→确认删除会话） | `artifact-store` ①③ |
| 盲目拉大窗口 | 200K 默认够用，**1M 不会更聪明，只让每轮消耗成倍增加** | §8.4 |

### 20.7.3 关键修正（不重复造轮子）
- **记忆治理**：上轮曾写"人工冷归档到资料库"，**已被 v2.51.0 原生按需加载 + 自动清理取代**——新生态不再自建冷归档索引，人工只兜底超大主题文件（`artifact-store` §6 对齐清单）。
- **上下文治理**：上轮泛泛"轻量模型优先"，**升级为官方 `/clear` + Subagents + `/compact` 完整体系**（`zh-style.md` §8.1）。
- **APP 缓存冗余 / 版本过旧**：属平台侧，靠定期清缓存 + 重启（保留登录数据），不归本生态。

### 20.7.4 用户侧立即可做（不等脚本）
1. 旧对话不用就新建，重要内容存本地文档/资料库；
2. 简单任务切轻量模型，别默认高阶；
3. 手机设置里清 WorkBuddy **缓存**（保留登录数据）后重启。

> 一句话：手机防卡顿的本质是"**让本地只留热/必要的，冷的与重的交给官方原生机制与资料库**"——记忆交给 v2.51.0，上下文交给 `/clear`+Subagents+`/compact`，产物交给 `artifact-store` 的 LRU。

## 20.8 技能规范化审计：对照官方 Skills 系统规范（codebuddy-eco 四技能）

> 本节把 20.2 落地的 4 个基建技能，按官方 **Skills 系统文档**（`codebuddy.cn/docs/cli/skills`，含 v2.51.0 内联 Shell 能力）逐条复核并规范化。审计对象：`.codebuddy/skills/{skill-evolution,machine-bootstrap,feature-gate,artifact-store}/SKILL.md`。

### 20.8.1 审计发现（能坐实的硬伤，非泛泛建议）

| # | 发现 | 性质 | 官方依据 |
|---|---|---|---|
| 1 | `machine-bootstrap` 脚本路径断裂：写 `bash skills/machine-bootstrap/scripts/bootstrap.sh`（指向顶层 `skills/`），但技能真身在 `.codebuddy/skills/` 下，命令**必然找不到文件** | 🔴 真 bug | `${CODEBUDDY_SKILL_DIR}` 占位符 |
| 2 | 4 个技能全缺 `allowed-tools`：默认等于放全量工具，与安全红线/最小权限相悖 | 🟠 规范缺失 | "合理的工具权限" |
| 3 | frontmatter 用了非标准 `version` 字段（官方字段表无此项） | 🟡 冗余 | Frontmatter 字段表 |
| 4 | `description` 塞十几个 `/` 分隔触发词；官方要求"清晰说明做什么+何时用"，v2.51.0 还会截断过长菜单描述 | 🟠 反模式 | 最佳实践 + v2.51.0 |
| 5 | 4 份完全重复的"语言铁律"整段：薄壳 + `zh-style.md` 已全局强制，每技能再贴一遍＝4 份冗余进 context | 🟠 违背 20.7 轻量原则 | "Avoid Duplication"（IDE Skills 文档） |
| 6 | "去 TVBox 改造清单"逐技能重复、且与 `README.md` 第五节重复；属迁移期笔记非运行时需要 | 🟡 重复 | Progressive Disclosure（长内容勿堆 SKILL.md） |
| 7 | 正文是描述式（"本技能是…"），官方要求**祈使式**指令 | 🟡 效果 | "Imperative Language"（IDE Skills 文档） |
| 8 | 官方 v2.51.0 内联 Shell `!命令` 未用；先验环境本可触发即注入 | 🟢 增强 | v2.51.0 + Skills 文档 |

### 20.8.2 已落地的规范化改造（4 个 SKILL.md 全部重写）

1. **修真 bug**：`machine-bootstrap` 脚本路径改用官方占位符 `${CODEBUDDY_SKILL_DIR}/scripts/bootstrap.sh`，路径随 SKILL.md 位置自动解析，永不断裂。
2. **补 `allowed-tools`**：按职责精确授权——`feature-gate: Read, Write, Edit, Grep, Glob, Bash(git:*)`；`skill-evolution: Read, Write, Edit, Grep, Glob`；`machine-bootstrap` / `artifact-store: Read, Grep, Glob, Bash`。
3. **删非标准 `version`**；`description` 精简为"做什么 + 何时用"一句，触发词移进正文"何时使用"节。〔**20.12 订正**：此条当轮**未真正落地**——4 个 `description` 仍保留 `/` 触发词清单，直到 20.12 才按官方口径补做并加机检 ⑦ 守护；此处保留原记录以示留痕，实际状态以 20.12 为准。〕
4. **去 4 份重复**：语言铁律整段 → 一句"由薄壳 + `zh-style.md` 全局强制，本技能直接继承，不重复声明（省 context）"。
5. **收敛迁移笔记**：逐技能的"去 TVBox 改造清单 + 原始参考"压成一句"脚本移植备注"，统一指向 `README.md` 第五节，注明"脚本为可选件，契约以本文件为准"。
6. **正文改祈使式**：每个技能统一为「何时使用 / 工作流 / 职责与边界 / SOP 对齐」结构。
7. **用上官方内联 Shell**：`machine-bootstrap` §0 加 `!`pwd -P`` 与 `!`git log --oneline -1``，触发即自动注入先验环境。
8. **同步入口描述**：薄壳 `CODEBUDDY.md` 与 `README.md` 里 `artifact-store` 的旧描述（"产物 LRU+远程可搜"）更新为"本地轻量化总闸·防手机卡顿（官方原生优先）"。

### 20.8.3 评估后「有意不加」的两项（照搬反而坏事）

> 关键：官方能力要**结合本生态"手机端可触发"的约束**筛选，不是逐条照抄。

| 官方字段 | 官方建议用途 | 本生态不加的理由 |
|---|---|---|
| `disable-model-invocation: true` | 给"会删/推远端"的不可逆操作，只能手动 `/skill-name` 触发 | 一加就**模型无法自动触发、只能手打斜杠命令**，直接削弱第 19/20 章整套"手机端可触发"设计。改用 `allowed-tools` + 正文"删除前确认"闸约束副作用 |
| `context: fork` | 让技能在隔离 subagent 上下文跑，省主会话 context | 只适合"明确独立任务"。`skill-evolution` 需监控会话复发问题，fork 会**切断对话历史**反而不工作；Subagents 纪律仍由 `zh-style.md` §8.1 承载 |

### 20.8.4 校验结果

- 4 个 SKILL.md 的 `name` / `description` / `allowed-tools` **全部齐全**，无残留 `version` 字段。
- 4 份重复「语言铁律」整段已消除，均改为 1 句继承指针；内联 Shell 命令在位。
- `.codebuddy/MANIFEST.json` JSON 合法；脚本路径占位符替换正确。

> 一句话：**"接活"（20.0–20.6）解决"技能能不能被手机触发"，"防卡顿"（20.7）解决"用久了会不会变重"，"规范化"（20.8）解决"技能本身写得对不对"**——三层递进，至此 codebuddy-eco 从能用、耐用，到符合官方契约。

## 20.9 规则侧分层诊断与改进（与 20.8 成对）

> 20.8 审「技能写得对不对」，本节审「规则写得全不全、好不好、放得对不对」。数据来源：tvbox-eco 私有仓库 `rules/core.json` 23 条常驻规则字段级实测（2026-11-10）+ 官方 Skills / Memory / Best-Practices 文档。与 20.0–20.8 同属「接活实例」主线。

### 20.9.1 实测证据：规则「不全 / 不好」的六类硬伤

| # | 问题 | 实测数据 |
|---|---|---|
| 1 | 字段无 schema | 23 条共用 **49 个不同字段**，多数仅出现 1–2 次 |
| 2 | 同一语义存 6 处 | 描述散落 `summary`(20/23) / `title`(10) / `desc` / `description`(4) / `statement`(12) / `master_line`(17)；M-R206 一条就散 5 个字段 |
| 3 | 降级未同步、自相矛盾 | M-R215 `enforce_level=DOC` 却中文 `等级=GATE`；M-R215 / 130 / 136 已降 DOC 仍留 `gate_hook` |
| 4 | 名实不符 | 部分 `GATE` 级却 `guard_form=manual/declare`（纸面规则挂硬门禁名） |
| 5 | 该补的没补 | `applicable_scope` 仅 **1/23**、`acceptance` 仅 **1/23**、`trigger_paths` 仅 **1/23** |
| 6 | 重复未合并 | 并行 M-R130≈145、三态 M-R57≈60、换模型 M-R301/302/303 三连；M-R110 / 022 与薄壳内联重复 |

> 口径：`core.json` 23 条是「唯一活线真源 / 常驻」；`hot`(21) / `warm`(60) / `cold` 是全册分层快照，`index.json`(280KB) / `registry.json`(325KB) 是退役注册中心，三者不是一回事，别混。

### 20.9.2 根因：三种东西塞进同一文件

| 本该是 | 实际混进 `core.json` | 后果 |
|---|---|---|
| 给**模型**读的常驻纪律 | 语言 / 三态 / 先验…（约 8 条真铁律） | 被元数据淹没 |
| 给**模型**按情境触发的契约 | 特性开关、生态分层、文档治理 | 全 `alwaysApply` 常驻占 context |
| 给**人 / 脚本**读的治理台账 | probe 结果、downgrade_reason、review 日期、owner、first_seen… | 78KB core + 280KB index + 325KB registry，钩子不跑就全休眠 |

所以「不全」不是内容少，是**该常驻的没提炼、台账又没清出去**；「不好」是**无 schema + 降级不同步 + 重复**。叠加第 19 章诊断（项目级 + 押钩子 + 手机不跑），tvbox-eco 同时中三枪：**手机钩子不跑 → 全休眠；33 条 GATE 无落地脚本 → 诚实降 DOC；巨型注册中心 → 违背 20.7 轻量 / 20.8 渐进加载**。

### 20.9.3 改进方案：四层递进 + 官方三维度

**第 1 层 · Schema 归一**：最小 7 字段 `id / summary / scope / mode / level / verify / owner`；`summary` 定为**唯一**描述字段，合并其余 5 处；删中文残留 `等级`。

**第 2 层 · 内容治理**：去重（并行 2→1、三态 2→1、换模型 4→1）；消矛盾（等级同步、清 `gate_hook` 残留、GATE/manual 按 M-R136「不造假门禁」诚实降级）；补缺口（每条补 `scope` 与 `verify`）。

**第 3 层 · 三分离落位（弃用 hot/warm/cold，改官方三维度）**：

| 维度 | 官方机制 | 正确用法 |
|---|---|---|
| **作用域** | 用户级 `~/.codebuddy/rules/` / 项目级 `.codebuddy/rules/` | 基座下沉用户级（一次配置、全项目 / 手机生效、天然去重）；项目级只留本项目契约 |
| **触发** | `alwaysApply:true` / `false` + `paths` / `enabled:false` | 无条件铁律常驻；情境契约用 `paths` 命中才注入；不常驻占 context |
| **强制力** | 软声明 → config → `permissions.deny` → hook | 硬门禁不押 hook（第 19 章手机不跑），改 `permissions.deny` 或技能内「删除前确认」闸 |

> 技能是「能力包」，按「基建 / 能力」两分合理（第 20.2 章）；但**规则是「约束 / 门禁」**，正交维度应是上表三个，硬套两分法会答偏。这是本节比「基座 vs 能力」更准的方向。

**第 4 层 · 覆盖补全（克制）**：对照 SOP 第 0.5 / 16–19 章只补「该常驻却缺」的纪律（坐标系、三通道自检），**不把回滚代码 / 资料库分类细节塞进规则**（那是文档和技能的活），避免重蹈 20.7 的堆叠覆辙。

### 20.9.4 本次落地产物（C → A → B，仅改 codebuddy-eco 与 SOP，不碰 tvbox-eco）

| 项 | 产物 | 内容 |
|---|---|---|
| **C** 基座规则包 | `base/rules/core-8.md` | 去 TVBox 化 **8 条**：①语言 ②三态 ③先验开工 ④并行 ⑤零明文凭证 ⑥事实源 ⑦换模型对账 ⑧正本入口；纯纪律、无台账、`alwaysApply:true` |
| | `docs/base-rule-mapping.md` | 逐条标原 M-R 编号、去 TVBox 化改动、SOP 章节、schema 值、`verify` 判据 + 安装命令 |
| **A** 三分离重构 | `.codebuddy/rules/docs.paths.md` | `alwaysApply:false` + `paths:["docs/**/*.md"]` 条件触发示例（文档同步契约） |
| | `docs/rule-ledger.md` | 台账归位：schema 定义、8 条 schema 值、强制力梯度、去重 / 降级记录、探针结果位、append-only 变更留痕 |
| | `.codebuddy/rules/zh-style.md` | 加 **§0 分层声明**；§1–7 由完整条款压成「继承 `core-8.md` 指针 + 项目专属补充」；**§8 与其 11–20 条原样保留** |
| 同步 | `MANIFEST.json` rules 段 / `CODEBUDDY.md` / `README.md` / `governance.md` | rules 段改四格（`user_base` / `zh-style` / `docs.paths` / `ledger`）；README 加第六节；governance 加第八节 + 验证项 |
| **B** SOP | 本节 20.9 | 收上述实测证据、schema、去重表、三分离映射 |

执行顺序 **C（先定基座内容）→ A（按三分离落位）→ B（审计写进 SOP）**，保证规则包与脚手架同口径。用户级基座以 `base/rules/` 作**可 clone 模板** + `cp` 到 `~/.codebuddy/rules/` 的安装命令（沙箱本机路径带不走）；手机端经账号云同步加载 + 「给 WorkBuddy 的指令」内联兜底（第 19 章③）。

### 20.9.5 两个「有意不为」（结合手机端约束，非遗漏）

| 不为 | 理由 |
|---|---|
| §8 本地轻量纪律**不迁出、不编号改、不改 `paths` 条件** | 它是运行时**元纪律**、每轮都该生效，`paths` 只适合绑文件路径的情境契约（20.8.3 同款判断）；且 SOP 20.7 已批准、被 20.7 / 20.8 与 6 个文件引用，迁移收益小于断链成本。改用**新增** `docs.paths.md` 示范条件触发，零断链 |
| 薄壳 `CODEBUDDY.md` 内联铁律**保留冗余** | 这是第 19 章「三通道叠加、互为兜底」的**有意冗余**（用户级未配置时仍不失守），与 20.8 消除的「技能内重复铁律」性质不同，不能一并删 |

### 20.9.6 校验与收口

- `MANIFEST.json` JSON 合法，`rules` 段四格齐全；`core-8.md` / `zh-style.md` 为 `alwaysApply:true`，`docs.paths.md` 为 `alwaysApply:false` + `paths`，三者 frontmatter 正确。
- `zh-style.md` §8.1–8.4 与第 11–20 条**编号完好**，20.7 全部引用不断链；§1–7 已压成继承指针。
- 8 条基座逐条有 `verify` 判据（补齐旧 `acceptance` 1/23 缺口），台账与规则层物理分离、不进 context。

> 一句话：第 20 章四层递进——**「接活」（20.0–20.6）解决「能不能被手机触发」，「防卡顿」（20.7）解决「用久了会不会变重」，「技能规范化」（20.8）解决「技能写得对不对」，「规则三分离」（20.9）解决「规则放得对不对、全不全」**。技能侧用「基建 / 能力」两分就够，规则侧必须换「作用域 × 触发 × 强制力」三维度——因为规则是门禁、不是能力包。

## 20.10 口径统一性元规则（承接 20.8 / 20.9，跨全生态）

> 前几节每改一处，都要人肉 grep 一遍引用、再逐文件同步描述——这本身就是「口径没统一」的症状。本节把它从「靠人自觉」固化成**一条元规则 + 一张真源登记表 + 一个可机检脚本**，让「统一」变成能跑命令验证的事实。

### 20.10.1 实测：乱在哪（不是担心，是已经发生）

| 证据 | 实测数据 |
|---|---|
| 同义词分层混用 | 「基座 / 基建 / 底座」在 codebuddy-eco 的 7 / 1 / 2 个文件、SOP 的 8 / 5 / 16 次里出现，且**未被定义各自所指**；「三分离 / 三维度」各在 5 个文件出现却含义不同（前者=落位四格，后者=分类三轴） |
| 人工同步面 | `§` 引用共 **47 处**（codebuddy-eco 23 + SOP 24，人工统计口径）；机检脚本连同 `20.x` 章节引用合并扫描为 **66 处（eco）/ 144 处（含 SOP）** |
| 编号空间混用 | `M-R215`(11 次) / `B-01`(7) / `第 19 章`(30) / `20.9`(17) 共存，无命名空间约定 |
| 描述漂移史 | `artifact-store` 从「产物 LRU+远程可搜」改「本地轻量化总闸」时，是逐个文件追着改的（20.8 已记） |

### 20.10.2 设计：为什么必须是「三件套」，一条文字规则不够

47 处同步面靠自觉必然漂——20.2 / 20.7 / 20.8 / 20.9 每轮都在手动追引用，就是活证据。所以：

| 件 | 产物 | 职责 |
|---|---|---|
| ① 元规则（条文真源） | `base/rules/core-8.md` 正文首 **M1–M7** | 跨项目通用纪律，随用户级规则一起生效 |
| ② 唯一真源登记表 | `docs/registry.md` | 每类事实的真源、受控词表、编号空间、影响面清单、有意例外；**第七节 JSON 是机读唯一配置源** |
| ③ 可机检脚本 | `verify/terminology_check.py`（只读） | 把 ②③ 落成可跑命令：**不通过不算完成**（M5） |

> 关键自洽：脚本**不硬编码第二份词表/清单**，全部从 `registry.md` 第七节读取——否则检查器自己就制造了一处口径冗余，正好违反它要守的规则。`docs.paths.md` 工作流第 6 步接入该机检（编辑 `docs/**` 时触发，含 registry 自身）。

### 20.10.3 元规则 M1–M7（真源在 core-8.md，此处只引编号）

| 条 | 一句话纪律 |
|---|---|
| **M1** | 每类事实只在一个文件权威定义；项目维护一份真源登记表；Git 永久历史为真源，`~/.codebuddy/` 副本是安装副本 |
| **M2** | 非真源处只写「文件 + §小节 / 编号」指针，不复制条款全文与数字；需强调写「见 X §Y」 |
| **M3** | 近义/易混概念各登记**唯一所指**，禁跨层误用——不是消灭词本身 |
| **M4** | 编号命名空间分段：`B-01…B-08` / `M-R###`（只读参照）/ `§x` / `第 x 章`·`20.x.y` / `M1…M7`，不跨用、不重号、不跳号 |
| **M5** | 改真源连带同步所有指针点；项目提供机检脚本时跑通才算完成（断链 / 词表 / 编号 / 复制条款四类全绿） |
| **M6** | 发现分歧回**真源**改，不在副本就地打补丁；先答「孤例还是模式」，模式要机制级修复 |
| **M7** | 薄壳内联、手机指令内联等兜底冗余，**显式登记即不算违例**；未登记的重复按 M6 处理 |

### 20.10.4 两处落地修正（相对 20.10 提出时的草案）

| 草案口径 | 落地修正 | 理由 |
|---|---|---|
| 把「基座 / 基建 / 底座」当同义词**合并成一个词** | 改为**分层登记 + 禁跨层误用**：规则层称「基座」、技能层称「基建」、平台层称「底座」 | 三者在本体系里本就指不同层（第 18 章标题即「底座层接入」），粗暴合并会破坏既有章节引用与语义；口径统一 = 定所指，不是消灭词 |
| 元规则写死 `registry.md` / 机检脚本路径 | `core-8.md` 里 M1–M7 写成**跨项目通用纪律**，登记表与脚本标注为「本生态项目级实现」 | `core-8.md` 会被复制到用户级 `~/.codebuddy/rules/`，写死项目相对路径会悬空 |

> M7 不可省：否则规则一上线，20.9.5 刚确认的「薄壳内联冗余」反被判违规，自己打自己。登记表第五节已把薄壳、手机指令、技能入口一句话描述三项登记为有意例外。

### 20.10.5 机检真实结果（三条门禁 + 负向验证）

只读脚本 `verify/terminology_check.py` 六项检查：① 真源登记文件齐备 ② 受控词表跨层误用 ③ 编号命名空间（越界/跳号） ④ § / `20.x` 章节引用断链 ⑤ 铁律正文被复制（M2） ⑥ `MANIFEST.json` 合法。

| 运行 | 扫描 | 结果 | 退出码 |
|---|---|---|---|
| 默认 | 13 个 .md | PASS 6 / WARN 0 / FAIL 0 | **0** |
| `--strict`（WARN 计 FAIL） | 13 个 .md | PASS 6 / WARN 0 / FAIL 0 | **0** |
| `--sop`（连 SOP 一起） | 14 个 .md、144 处引用 | PASS 6 / WARN 0 / FAIL 0 | **0** |

**负向验证**（在 `/tmp` 造故意违规样本，不碰交付物）：词表误用 2 处、编号越界 `FAIL`、§断链、复制铁律各被检出，共 **4 类命中** → 证明检查器有效、不是永远绿灯。`docs.paths.md` 第 6 步已把「两项校验任一不绿不算完成」写成工作流。

> 数字对齐（本规则自守 M5）：上表 `--sop` 的 **144 处**是「落地当次、尚未写入本节」的快照；把 20.10 这一节加进 SOP 后，`§` / `20.x` 引用自然增加，复跑为 **167 处、仍 PASS 6 / 0 / 0、退出码 0**。故引用总数随正文增长而变，非断链，判据看「0 断链 + 退出码」而非某个固定数字。

### 20.10.6 一句话收口

> 第 20 章五层递进：**接活（20.0–20.6）能不能被触发 → 防卡顿（20.7）会不会变重 → 技能规范化（20.8）技能对不对 → 规则三分离（20.9）规则放得对不对 → 口径统一（20.10）改一处会不会乱套**。前四层是「把东西摆对」，这一层是「摆对之后还能一直对」——靠的不是记性，是 `registry.md` 一张表 + 一条能跑绿的机检命令。

---

## 20.11 口径统一性规则 · 正式条款（本 SOP 全局适用）

> **定位分工**：20.10 是「为什么立规、立了什么、怎么落地」的**依据与纪实**；本节是这条规则在 SOP 主文档里的**正式生效条款**，约束的是**今后每一次编辑行为**。它不是第 20 章的第六层，而是 20.10 所立规则的制度化。条文全文按 M2 只留指针、不复制：真源在 `base/rules/core-8.md` 元规则段，一句话索引见 20.10.3。若要逐字读条文，去真源，**不在本 SOP 建第二份**。

### 20.11.1 适用与触发

| 维度 | 规定 |
|---|---|
| 适用对象 | 本 SOP 全文、codebuddy-eco 内全部治理产物（规则 / 技能 / 台账 / 登记表 / README / MANIFEST），以及今后所有新增章节、术语、编号 |
| 触发时机 | 任何一次「新增、改名、删除、改编号、改描述」动作，**动手前**先查登记表定位真源；**收尾时**跑门禁 |
| 不在适用内 | 已按 C7 显式登记的有意例外（清单见 `docs/registry.md` 第五节） |

### 20.11.2 七项约束（指针式，不复制条文）

| 约束 | 必须做的动作 | 条文指针 |
|---|---|---|
| **C1** | 一条事实只在一处权威定义；动笔前先定位真源 | `core-8.md` M1 |
| **C2** | 非真源处只写「文件 + 编号」指针，不贴条文全文与数字 | `core-8.md` M2 |
| **C3** | 近义概念按受控词表用规范词、禁跨层误用；词表见 registry 第二节 | `core-8.md` M3 |
| **C4** | 编号各归其段、不跨用不重号不跳号；命名空间见 registry 第三节 | `core-8.md` M4 |
| **C5** | 改真源连带同步全部指针点，门禁跑通才算完成 | `core-8.md` M5 |
| **C6** | 发现分歧回真源改，不在副本打补丁；先答「孤例还是模式」 | `core-8.md` M6 |
| **C7** | 兜底冗余须显式登记才不算违例；未登记按 C6 处理 | `core-8.md` M7 |

> C1–C7 与 M1–M7 一一对应，此处是**动作清单**不是条文；条款全文在真源，避免两处并存（C2）。

### 20.11.3 门禁（什么算做完）

```bash
# 在 codebuddy-eco 仓库根执行（只读，不写任何文件）
python3 verify/terminology_check.py
python3 verify/terminology_check.py --strict
python3 verify/terminology_check.py --sop ../CodeBuddy-会话中文风格统一-SOP.md
```

判据（承接 20.10.5 的数字对齐说明）：**退出码为 0、六项全 PASS、零 WARN 零 FAIL**；`--strict` 下 WARN 亦计失败。引用总数随正文增长而变，**看 0 断链 + 退出码，不看某个固定数字**。任一不绿，本次编辑不算完成（C5）。

### 20.11.4 违反判定与处置

1. 机检报 WARN 或 FAIL 即判违规，**先修再交**，不带病交付。
2. 分歧回真源改（C6），禁止在副本就地打补丁；先判断孤例还是模式，模式做机制级修复覆盖同类。
3. 新增例外走登记（C7），未登记的重复不豁免。
4. 决不允许为了「过门禁」去改登记表里的受控词表或编号白名单——那是改考卷，不是改答案。

### 20.11.5 规则自我适用（新增本节即首次执行）

按 C4/C5，把本节加进 SOP 这件事本身就走了连带同步，且不留未登记编号：

| 连带点 | 本次动作 |
|---|---|
| 编号登记 | registry 第七节机读区 `sop_sections` 增加 20.11，否则 `--sop` 会把本节引用判为断链 |
| 真源登记 | registry 第一节增加本条款的登记行 |
| 脚注 | 「整理依据」补记本节 |
| 治理映射 | `docs/governance.md` 补对应映射与验证项 |
| 门禁 | 三模式复跑并取真实退出码 |

> 机检结果**不写进本 SOP**（避免制造第二处会随正文漂移的数字，正是 20.10.5 的教训），以执行输出的真实退出码为准。

### 20.11.6 一句话收口

> 20.10 说的是「我们定了这条规则」，20.11 说的是「从现在起它管着每一次改动」——**规则不在脚手架里躺着，在主文档里生效**；而它生效的第一个证据，就是新增本节时 C4 / C5 被自动触发、一个编号都没漏登记。

---

## 20.12 技能侧机检守护（与 20.8 成对）

> 20.8 是一次**人工**规范化：当时按官方 Skills 文档逐条改了 4 个技能。本节回答「改完之后，凭什么保证它不悄悄退化」——诊断发现 20.8 的部分整改**并未真正落地**，根因与规则侧同构：**整改没有变成可机检的契约**。本节按官方口径补做，并把 20.8 的 8 项成果固化成机检第 7 项。

### 20.12.1 诊断：技能侧复现的 6 类问题（实测，非推断）

| # | 发现 | 实测数据 | 对应规则侧哪个病 |
|---|---|---|---|
| 1 | **纪实与实物不符**（最硬） | 20.8.2 第 3 条声称 `description` 已精简、触发词已移进正文，但 4 个技能 `description` **仍全含 `/` 触发词清单**，字数 96 / 114 / 115 / 169 | M-R215「等级标 GATE 实为 DOC」的同构 |
| 2 | **触发词双份存放且不一致** | `description` 一套、正文「何时使用」又一套且用词不同 | 「描述散落 6 处」，改一处必漏另一处 |
| 3 | **一句话短名 4 处各写一份、已分化** | `SKILL.md desc` / 薄壳 / README / MANIFEST role；`feature-gate` 前两处「特性开关+绞杀者切流」、MANIFEST 却是「灰度司·安全迭代」，另两个技能同类别名分化 | 20.10 的「描述漂移史」原样复现 |
| 4 | **机检完全没覆盖技能侧** | `required_files` 11 项里技能项 **0**；脚本正文 `skills` / `SKILL.md` / `allowed-tools` / `frontmatter` 全 **0 次** | **规则侧刚补上的，技能侧是空白** |
| 5 | 4 份逐字重复的继承指针 | 每技能第 9 行 141 字、**四份完全一致**；20.8 消除了「语言铁律整段」却换上 4 份重复指针，且未按 C7 登记例外 | 20.8 声称「去 4 份重复」，去重不彻底 |
| 6 | 迁移笔记重复 + 硬编码私有仓库名 | **4/4** 技能各写一句不同的私有仓库名 + archive 路径，README 第五节另有一份清单 | 「迁移期笔记混进运行时契约」，与唯一真源冲突 |

> **同一根因**：20.8 做完 8 项规范化后，**没有把它变成可机检的契约**。整改悄悄回退、描述慢慢分化，全无人发现——这正是 20.10 说的「同步面靠人肉必然漂」，也是 C1（真源登记）/ C5（机检）直接管的事。规则刚生效，就撞见技能侧没被它覆盖。

### 20.12.2 官方口径核对（避免又造一处「纪实与官方不符」）

按官方 **Skills 系统文档**逐条核对，有一处必须如实标注：

| 项 | 官方原文口径 | 本生态落法 |
|---|---|---|
| frontmatter 字段 | `name` / `description` / `allowed-tools` 在官方字段表里**均标「必填：否」**；`name` 未指定时取目录名 | 「三字段齐全」诚实定为**本生态治理约定**（便于机检 + 最小权限），**不冒充官方必填** |
| `description` 定位 | 「帮助 AI 理解何时使用」的**一句话清晰能力描述**；官方示例（如「PDF 文档解析和转换专家」）从不堆触发词 | 写「做什么 + 何时用」一句；`/` 触发词清单**移出** `description` |
| 触发方式 | Skills 由 **AI 模型自动识别并调用**（对比 Slash Commands 才是用户手打），靠语义匹配而非关键词清单 | 触发词清单唯一真源移到正文「何时使用」节，标注「触发词（唯一真源）」 |
| 工具权限 | 最佳实践「只授予必需的工具权限」，支持 `Bash(git:*)` 等精确匹配 | 保留 20.8 已定的 `allowed-tools` 精确授权 |
| 非标准字段 | 官方字段表**无 `version`** | 保持 20.8 已删的状态，机检 ⑦ 禁止其回潮 |

> 关键：**不把本生态约定写成官方要求**。20.8 曾把「缺 `allowed-tools`」表述为「规范缺失」，严格讲它符合的是官方**最佳实践**而非**必填**；本节按官方口径如实区分，避免文档自己带着一处口径错误去要求别人口径统一。

**规则侧与记忆位置的官方口径补充**（依据官方 **Memory 文档**，非 Skills 文档，故单列一表）：

| 项 | 官方原文口径 | 本生态落法 |
|---|---|---|
| 规则控制字段 | 「规则控制字段」表仅 `enabled`(boolean) / `alwaysApply`(boolean) / `paths`(string\|string[]) **三项**；官方字段表**无 `priority`** | `zh-style.md`、`MANIFEST.json` 的 `priority: high` 已删；`description` 保留为人读元数据，不冒充控制字段；机检 ⑧ 守护 |
| 规则类型判定 | `alwaysApply:true`(任意)→ALWAYS；`false`+有 `paths`→MANUAL 条件触发；`false` 无 `paths`→**不支持、规则不加载** | `zh-style.md`=`true` 常驻、`docs.paths.md`=`false`+`paths` 条件，二者合规；机检 ⑧ 校验「false 必须有 paths」 |
| 项目记忆位置 | 「`./CODEBUDDY.md` **或** `./.codebuddy/CODEBUDDY.md`」——**两处皆官方合法路径** | 薄壳实体固定 `.codebuddy/CODEBUDDY.md`，只放一处（M1）；`MANIFEST`/README/薄壳自述/governance 指针统一，不再称「顶层唯一」 |
| 用户级规则 | `~/.codebuddy/rules/*.md`，在项目规则之前加载 | `core-8.md` 装到该目录，官方路径 |
| 手机端不跑钩子 | 官方 Memory/Skills/Settings 三份文档**均未作此声明**；官方只说 frontmatter `hooks` 仅 `context:fork` 生效、非内置来源默认不注册（`allowUntrustedFrontmatterHooks` 默认 `false`） | 「手机/云端任务不跑钩子」是**本生态第 19 章实测结论**，不是官方口径；已在薄壳/MANIFEST/core-8 标注 |

> **集中订正（覆盖全 SOP 前文，不逐处改写历史纪实）**：前文第 3、8、9、19 章及 20.1 的示例与纪实中出现的 `priority: high`（共 8 处，含 `tvbox-core.md` 的历史 frontmatter），以及「顶层 `CODEBUDDY.md` 唯一路径」「`priority` 让语言规则压过其他规则」等表述，均为**当时的写法或旧生态纪实**。按上表官方口径：`priority` **非官方控制字段、无加载效力**，两处项目记忆位置**皆官方合法**。同理，第 19 章关于「只有顶层 `CODEBUDDY.md` 是标准自动加载路径、`.codebuddy/CODEBUDDY.md` 不是」的诊断，是**旧生态 tvbox-eco 当时环境（钩子体系）下的实测纪实**，官方 Memory 文档已明确两处皆合法，该句不再作为当前口径。此处一律保留原文以示留痕（同 20.8.2 #3 的处理），**当前生效状态以本表 + 20.12.3 / 20.12.4 为准**：`codebuddy-eco` 运行时规则已删 `priority`，薄壳只放 `.codebuddy/CODEBUDDY.md` 一处，机检第 ⑧ 项 `check_rule_contract` 守护其不回潮。
>
> **机检项数**：20.10.5 / 20.11.3 / 20.12.4 中的「六项 / 七项 / 7 项」均为**当时的门禁快照**；按 20.10.5 与 20.11.3 自己立的纪律「不看某个固定数字」，本 SOP 不回写这些历史数字。当前检查项以 `docs/registry.md` 第六节为准（本次新增 ⑧ 规则契约后为 **8 项**），判据恒为「**0 断链 + 退出码 0**」。20.11.2 的「七项约束」指 C1–C7 条款数，与机检项数无关，不随之改动。

### 20.12.3 全套整改（①–⑤）

| 层 | 动作 | 落点 | 官方/规则依据 |
|---|---|---|---|
| ① 补做 20.8 未落地的整改 | 4 个 `description` 重写为「做什么 + 何时用」一句，去掉 `/` 触发词；触发词清单移进正文并标「触发词（唯一真源）」 | 4 个 `SKILL.md` | Skills 文档「清晰的 Skill 描述」 |
| ② 描述定一真源 | 新增 `canonical_short`（4 个一句话短名），薄壳 / README / MANIFEST **三处严格对齐**，消除别名分化；4 份 141 字继承指针压成逐字一致的短指针 | registry 第七节 + 3 入口 + 4 技能 | C1 / M2 |
| ③ **机检扩到技能侧（核心）** | `required_files` 纳入 4 个 `SKILL.md`（11 → 15）；新增 `skill_contract` 机读区；脚本加第 **⑦** 项 `check_skill_contract` | `docs/registry.md` + `verify/terminology_check.py` | C5 / M5 |
| ④ 有意例外登记 | 4 份继承指针、薄壳技能表「触发场景」列按 C7 显式登记；4 处私有仓库名从运行时契约移除，迁移清单统一指向 README 第五节 | registry 第五节 + 4 技能 | C7 / M7 |
| ⑤ 连带同步与留痕 | `sop_sections` 加 20.12；脚注、governance 映射、docs.paths.md 工作流「六项 → 七项」措辞同步；订正 20.8 纪实 | 全生态 | C4 / C5 / M6 |

**机检第 ⑦ 项查什么**（全部配置从 registry 第七节读，脚本不硬编码第二份）：必备/禁用 frontmatter 字段、`description` 触发词堆砌与斜杠数、触发词唯一真源是否在正文、继承指针逐字一致、私有仓库名硬编码、`canonical_short` 在 3 个入口对齐。

### 20.12.4 门禁与负向验证

按 20.11.3 的纪律，**机检结果的具体数字不写进本 SOP**（引用总数随正文增长而变），只记录可复核的结论、以执行输出的真实退出码为准：

- 三模式（默认 / `--strict` / `--sop`）逐条真跑，**退出码均为 0，7 项全 PASS、0 WARN、0 FAIL**。
- **负向验证**（在 `/tmp` 造故意违规样本，不碰交付物）：第 ⑦ 项一次报出多类违规——缺 `allowed-tools`、禁用字段 `version`、`description` 触发词堆砌、正文缺触发词真源标记、继承指针不一致、硬编码私有仓库名、短名未在入口对齐 → 证明检查器有效、不是永远绿灯。
- 「七项」是 registry 第六节的当前口径；检查项增减以该节为准，判据恒为「**0 断链 + 退出码 0**」。

### 20.12.5 有意不为（非遗漏）

| 官方能力 | 不加/不为的理由 |
|---|---|
| 不给技能立「正式生效条款」（对比 20.11） | 技能是**能力包**、不是门禁；`SKILL.md` 本就是官方自动加载的契约本体，SOP 里的 20.2 / 20.8 / 20.12 本就该是**纪实**。照搬规则侧解法会把 20.9 已否决的「技能套规则分层」请回来 |
| `disable-model-invocation` / `context: fork` | 沿用 20.8.3 判断：前者会让模型无法自动触发、削弱手机端设计，后者会切断 `skill-evolution` 依赖的对话历史 |
| 不把真脚本（约 139KB 的 `evolve.py` 等）搬进技能 | Progressive Disclosure：迁移期笔记不进运行时契约，脚本为可选加速件，清单统一指向 README 第五节 |

### 20.12.6 一句话收口

> 第 20 章六层递进：**接活（20.0–20.6）能不能被触发 → 防卡顿（20.7）会不会变重 → 技能规范化（20.8）技能对不对 → 规则三分离（20.9）规则放得对不对 → 口径统一（20.10–20.11）改一处会不会乱套 → 技能守护（20.12）改完会不会悄悄退化**。20.8 靠人改对一次，20.12 靠一条命令让它一直对——**规范化只有变成门禁，才不会退化成纪实**。

---

## 20.13 交接包、机读门禁与可视化面板（P1-2 / P2 落地）

> **总起**：本节把此前只在会话上下文讨论、未落文件的三件事正式登记进治理真源——机检 `--json` 输出、可视化面板四视图、交接包/冷启动演练的治理定位。核心边界一句话：**面板只读真源产物、无事件流，因此只做「回顾式进度」，绝不伪造「前瞻式进度」**。口径依据 20.10–20.12 的三件套与 C1–C7；官方口径的判别方式沿用 20.12.2（`--json`、面板均属**本生态约定**，官方文档未定义这两个能力，不冒充官方）。本节是交付/视图层登记，**不并入 20.12.6 的「六层递进」**——那六层是治理能力递进，本节是让既有成果「看得见、读得动、不撒谎」，维度不同。

### 20.13.1 诊断：为什么单独成节（实测数据，非推断）

| 诊断项 | 实测数据 | 判断 |
|---|---|---|
| 交接包未进 SOP 索引 | `bootstrap-kit/` 20 文件（4 分册 + SOP 快照 + 15 文件快照）已在 `/workspace` 落地、经冷启动演练验证，SOP 全文此前无任何章节登记它 | 治理真源缺一环，换模型/新会话接手按 B-0x 对账时会「查无此物」 |
| 面板方案未落任何文件 | `panel/` 探测退出码 2；「四视图」只在会话讨论里 | 方案停在口头，等于没做 |
| 机检缺机器可读输出 | `verify/terminology_check.py` 只有人读文本，无 `--json` | 面板没有可吃的**真源产物**，只能靠解析文本（脆弱、制造第二份口径，违 M1） |
| 编号空间止于 20.12 | `sop_sections` 机读区末项为 `"20.12"` | 新增 20.13 若不同步登记，`--sop` 会把本节引用判为断链（C4） |

### 20.13.2 `--json`：让门禁结果成为可被读取的真源产物

设计（`verify/terminology_check.py`）：

- 默认**文本输出逐字不变**（PASS 8 / 汇总 / 结论 / 退出码）；新增 `--json` 把**同一套 8 项检查**的结果输出为机器可读 JSON，**不新增检查项、不改判据、不改退出码语义**；可与 `--strict`、`--sop` 组合。
- 输出字段（`schema: codebuddy-eco/verify/v1`）：`snapshot_only`（恒 `true`）、`note`（拉取式只读快照、非实时联动、无事件流、面板只呈现已发生事实）、`config_source`、`strict` / `sop_attached`、扫描量 `scanned_md_files` / `section_refs_total` / `section_refs_broken`、`summary{pass,warn,fail,effective_fail,ok}`、`check_count`、`exit_code`、`checks[]`（逐项 `level/item/detail`）。
- 关键：**面板读 `checks[]` 与 `summary`，不解析文本**——配置真源仍是 `docs/registry.md` 第七节，脚本不硬编码第二份（C5）。

真跑数据（本生态，判据恒为「0 断链 + 退出码 0」，数字随正文增长、不写死）：

| 运行 | `scanned_md_files` | 引用/断链 | `summary` | `exit_code` | stderr |
|---|---|---|---|---|---|
| `--json` | 13 | 99 / 0 | PASS 8 / WARN 0 / FAIL 0 | 0 | 0 字节 |
| `--json --strict --sop` | 14 | 271 / 0 | PASS 8 / 0 / 0 | 0 | 0 字节 |

> 官方口径：`--json` 是**本生态约定**的输出通道；官方 CLI 文档未定义机检 `--json` 能力，故不写成「官方要求」，与 20.12.2 对 `priority` 的处理一致。

### 20.13.3 面板四视图：价值 = 工程进度与情况 / 产出物 / 现状

用户口径固化：**「可视化面板的价值是可以看到工程进度和情况、以及产出物、现状」**。四视图据此落位，每一格都绑定一个真源产物：

| 视图 | 回答什么 | 数据源（真源产物，只读） | 三态纪律 |
|---|---|---|---|
| ① 工程进度与情况（**回顾式**） | 已经做到哪一步 | `git log` 提交时间线 + SOP 已落地章节 `20.0`–`20.13` + 决策 `D1`–`D10` + 里程碑 | 只列**已发生**事实；不预测完成率/百分比/ETA |
| ② 产出物 | 做出了哪些东西 | 文件系统实扫：15 文件本体（按层分类）+ SOP + 20 文件交接包 + 面板自身 | 文件在=有；字节/行数实时取，不写死 |
| ③ 现状 | 此刻健康度 | 机检 `--json`（8 项）+ `git status` / `remote` / `HEAD` + `diff -rq --exclude=.git` + 令牌零明文 + 洁净度 | 一律取**真实退出码**；非 0 如实报 |
| ④ 边界与三态诚实 | 哪些还不知道 | 显式清单：另一沙箱 L2 生效、另一会话状态、凭证销毁时点 | 一律 `UNDETERMINED / 无法判定`，不写成通过 |

顶部**诚实声明**横幅（生成脚本固定写入）：生成时刻（真实时间戳）、**拉取式快照 / 打开或刷新才更新 / 非 websocket 秒级推送**、无事件流、审查侧看不到对面——与旧生态 `panel/data.json` 的 `meta.realtime` / `offline_policy` 口径一致。

### 20.13.4 落点决策（数据支撑：为什么不放进 15 文件骨架）

**决策**：面板生成脚本与 HTML 落 `/workspace/panel/`，与 `codebuddy-eco/`、`bootstrap-kit/`、SOP **同级**，作为**独立交付物**。

| 若塞进 `codebuddy-eco/` 会破坏 | 实测口径分布 |
|---|---|
| 受控骨架「15 文件」 | `required_files`（15 项）、L0 `find=15`、快照逐字节一致、`START-HERE`/`01-D6`/`03-L0` 多处 |
| 机检扫描量与齐备项 | ①真源齐备 15/15、`rglob("*.md")` 的 13/14 口径 |
| M1/M2 | 面板清单会变成第二份「文件清单」，与 registry 第七节重复 |

定位：面板是**读取真源产物的消费者 / 审查侧派生视图**，与 `bootstrap-kit`（20.11「一次性搬运介质」）同类——**不进 registry、不进 git、不进机检范围、不进交接包快照**。因此 15 文件骨架、机检三模式、快照一致性全部保持不变。

**有意不为（非遗漏）**：

| 不做 | 理由 |
|---|---|
| 实时联动 / websocket 秒级推送 | 无常驻进程、无跨会话事件流；官方多端协同是同一 Agent 两视图，审查侧隔离 |
| 前瞻式进度（完成率 / 进度条 / 预计完成） | 无事件流则任何预测数字都是编的；只呈现已提交/已落地事实 |
| 引入事件总线 hub | MANIFEST `event_bus` 仅 note、轻量 emits/depends_on 解耦，不落中心 hub |
| 由面板宣布「对面已生效」 | L2/L3 恒 `UNDETERMINED`，与 20.9–20.12 的诚实边界一致 |
| 把面板纳入运行时骨架 / 机检 / 快照 | 它是派生视图、非运行时契约；若后续要纳入，须按 C4/C5 走编号登记 + 机检 + 全链路同步，属另一个授权项 |

### 20.13.5 连带同步与门禁（C4/C5 自实证）

| 改了什么 | 连带改哪里 |
|---|---|
| 新增 20.13 | `sop_sections` 加 `"20.13"`（否则 `--sop` 断链）、脚注「整理依据」补记、`governance.md` 加第十一节映射 |
| 机检加 `--json` | registry 第六节命令块与说明、`docs.paths.md` 第 6 步（数字仍 8 项，不改） |
| 面板落地 | `panel/build_panel.py` + 生成的 `panel/index.html`；独立目录，不进 15 文件快照 |
| SOP / registry / 脚本改动 | 15 文件骨架快照逐字节同步、SOP 快照同步、交接包四分册状态订正 |

门禁：三模式 + `--json` 组合真跑，`--sop` 因本节新增引用而增长（引用处数随正文变、判据不看固定值）但**0 断链**；负向验证（在 `/tmp` 造违规样本注入 `priority: high`）：`--json` 如实输出 `summary.ok=false` / `exit_code=1` / `summary.fail=1`、`checks[]` 中 ⑧ 规则契约判 FAIL、stderr 0 字节——证明机读门禁与文本门禁一致、非永远绿灯（`ok` 位于 `summary` 内，见 20.13.2 字段表）；判据恒为「**0 断链 + 退出码 0**」。本节自身也是 20.10.5 纪律的第三次实证：补一句订正就多一处 `20.x` 引用，故全文**不回写任何引用总数快照**。

### 20.13.6 一句话收口

> 20.0–20.12 解决「能不能被加载、会不会变重、改完会不会悄悄退化」，20.13 解决「做过的看不看得见、机器读不读得动、看板会不会撒谎」：`--json` 把门禁结果变成真源产物，四视图把**工程进度/产出物/现状**摆到台面，而**回顾式 + 三态 + 非实时声明**保证它只呈现已发生的事实、不编未来——**能被机检验证的才叫现状，看不到对面的就诚实记无法判定**。

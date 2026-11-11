# 基座规则映射台账（base-rule-mapping）

> **给人/脚本读的治理台账，不进 context**。运行时规则只有 `base/rules/core-8.md`（纯纪律 8 条），本文件承载其审计元数据——这正是 SOP 20.9「三分离」第③格：**治理元数据移出规则层**。
> 数据来源：tvbox-eco 私有仓库 `rules/core.json` 23 条常驻规则实测（字段并集 49、描述散落 6 处、降级不同步等），2026-11-10 审计。

## 一、最小 Schema（第 1 层 · Schema 归一）

废弃 tvbox-eco 的 49 字段乱象与中文残留（如 `等级`），统一为 7 字段：

| 字段 | 含义 | 取值 |
|---|---|---|
| `id` | 稳定编号 | `B-01`…`B-08` |
| `summary` | **唯一**描述字段（合并旧 `title`/`desc`/`description`/`statement`/`master_line`） | 一句话 |
| `scope` | 作用域（三维度①） | `用户级` / `项目级` |
| `mode` | 触发（三维度②） | `always` / `paths` |
| `level` | 强制级别 | `DOC` / `SCAN` / `GATE` |
| `verify` | 怎么验真（旧 `acceptance` 仅 1/23，此处补齐） | 可机检判据 |
| `owner` | 责任人 | 角色 |

> 强制力（三维度③）单独记在 `docs/rule-ledger.md`，不塞进每条规则。

## 二、8 条逐条映射（C 产物）

| 新 ID | 基座铁律 | 原 M-R（去重后） | 去 TVBox 化改动 | SOP 章节 | scope | mode | level | verify |
|---|---|---|---|---|---|---|---|---|
| `B-01` | 语言 | M-R110 | 剥 `settings.language` 探针 / 纯文本 hook，留"跟随用户语言 + 四类重置不回退英文" | 第 1/9/19 章 | 用户级 | always | GATE | 换模型后中文提问，输出仍全中文 |
| `B-02` | 三态诚实 | M-R57 + M-R60 | 合并两条重复；剥"基座读取函数"语境，留三态 + 语义不折叠 | 第 19 章 | 用户级 | always | SCAN | 造一条超时命令，输出如实记"无法判定" |
| `B-03` | 先验开工 | M-R215 | 剥《开工必读》总册 / govern 载入，抽象为"先验环境 + 当前主线，跨端无例外" | 第 19 章 | 用户级 | always | GATE | 错误目录动手前，先 `pwd -P` 求证 |
| `B-04` | 并行 | M-R130 + M-R145 | 合并两条重复；剥 `parallel_guard`/transcript 拦截，留判据 + "默认并行不问" | 第 19 章 | 用户级 | always | SCAN | 发 3 个独立读命令，是否同一消息并发 |
| `B-05` | 零明文凭证 | M-R022 | 剥"换机 IaC / bootstrap / gh auth"专属语境，泛化为任何凭证 | 第 16/19 章 | 用户级 | always | GATE | 全仓搜索无 token 明文串 |
| `B-06` | 事实源 | M-R242 + M-R301① | 剥 `core.json`/`fs`/notes 专属名，留"实查取证 + 禁以记忆当事实 + 引证给行号" | 第 0.5/19 章 | 用户级 | always | SCAN | 引用退役断言时，是否给文件+行号 |
| `B-07` | 换模型对账 | M-R206 + M-R301/302/303 | 4 条合并为 1；剥六面对账 / append-only 台账 / 三层识别 / 指纹 / 交接段等重型机制，留"习惯+业务上下文对齐"内核 | 第 17/19 章 | 用户级 | always | GATE | 换模型后能复述当前主线与总目标 |
| `B-08` | 正本入口 | M-R137 | 剥 `tvbox close learn` / `link.py` 专属命令，泛化为"现成入口" | 第 18/19 章 | 用户级 | always | SCAN | 试错 ≥2 次时是否回头查入口 |

## 三、去重裁决台账（第 2 层 · 内容治理）

| 合并组 | 旧条目 | 裁决 |
|---|---|---|
| 并行 | M-R130 ≈ M-R145 | 合为 `B-04` |
| 三态 | M-R57 ≈ M-R60 | 合为 `B-02` |
| 换模型 | M-R206 / M-R301 / M-R302 / M-R303 | 合为 `B-07` |
| 与薄壳重复 | M-R110（语言）、M-R022（安全）与 `CODEBUDDY.md` 薄壳内联 | 薄壳保留**有意冗余**（三通道兜底），core-8 为真源；技能内不再贴第 3 份（20.8 已消除） |

**消矛盾**（旧 core.json 实测）：M-R215 `enforce_level=DOC` 但中文 `等级=GATE` → 统一；M-R215/130/136 已降 DOC 却残留 `gate_hook` → 清；`GATE` 级却 `guard_form=manual/declare` 的按 M-R136「不造假门禁」诚实降级。

## 四、未纳入基座的 tvbox 规则（归类裁决）

| 类 | 条目 | 不纳入理由 |
|---|---|---|
| 🔧 能力规则（绑 TVBox 拓扑/技能名） | M-R001 双核必保、M-R116 大/小生态分层、M-R136 业务技能配钩子、M-R021 特性开关、M-R305 双 Agent 文档治理、M-R304 违规排查令 | 离开 TVBox 生态归零，属项目级情境契约，不进通用基座 |
| ⚠️ 治理台账（本就不该是规则） | GATE/SCAN 台账、探针实跑结果、downgrade_reason、review 日期、`index.json`(280KB)/`registry.json`(325KB)、disposition 处置表 | 给人/脚本读的元数据，归 `docs/rule-ledger.md`，**不进 context** |
| 📐 参考（可选加） | M-R77 SKILL 体积 ≤35KB、M-R241 门禁真实性 | 通用但偏"工程质检"，本次按用户拍板的 8 条清单克制纳入，留待后续 |

## 五、安装 / 复制命令（用户级基座落点）

沙箱内 `~/.codebuddy/rules/` 是**本机、带不走**；故模板放仓库 `base/rules/`，clone 后由用户自行安装：

```bash
# 桌面端（clone 本仓库后，在仓库根执行）
mkdir -p ~/.codebuddy/rules
cp base/rules/core-8.md ~/.codebuddy/rules/core-8.md
# 重开一个会话即自动加载，可用 /context 或读取确认
```

- **手机/云端**：用户级规则经账号云同步自动加载；若担心未同步，在「设置 → 给 WorkBuddy 的指令」里内联 `core-8.md` 的 8 条（第 19 章③ 兜底通道），与项目级薄壳互为冗余。
- **多项目**：只需 `cp` 一次；新项目不必再复制通用铁律，`.codebuddy/rules/` 只写项目专属契约。
- **验证**：`alwaysApply:true` 常驻；换任意项目用中文提问，确认全程中文、三态诚实、先验环境均在。

> 本台账与 `docs/rule-ledger.md` 的关系：本文件管「**基座内容**的来源与映射」，`rule-ledger.md` 管「**全生态规则**的 schema/强制力/探针/变更留痕」，二者都是台账、都不进 context，职责不重叠。

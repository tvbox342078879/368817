# 全生态规则治理台账（rule-ledger）

> **给人/脚本读，不进 context**。SOP 20.9「三分离」第③格：治理元数据（schema / 强制力 / 去重 / 降级 / owner / 探针 / 变更）一律归此处，**不写回规则文件**。
> 规则文件只保留「给模型读的纪律」：用户级 `base/rules/core-8.md`（8 条）、项目级 `.codebuddy/rules/zh-style.md`（项目专属 + §8）、条件规则 `*.paths.md`（情境契约）。

## 一、最小 Schema（正式定义）

| 字段 | 含义 | 取值 |
|---|---|---|
| `id` | 稳定编号 | `B-01`…`B-08`（基座）/ 项目自定义 |
| `summary` | 唯一描述字段 | 一句话，禁再拆 `title`/`desc`/`statement`/`master_line` |
| `scope` | 作用域 | `用户级` / `项目级` |
| `mode` | 触发 | `always` / `paths` |
| `level` | 强制级别 | `DOC` / `SCAN` / `GATE` |
| `verify` | 验真判据 | 可机检 |
| `owner` | 责任人 | 角色 |

> 拒收字段：中文残留（`等级`）、描述冗余字段、探针结果、downgrade_reason、review 日期、first_seen、dedup_decision —— 这些若需保留，写进本台账对应段落，不进规则条目。

## 二、8 条基座的 schema 值

| id | summary | scope | mode | level | verify | owner |
|---|---|---|---|---|---|---|
| `B-01` | 语言跟随用户，四类重置不回退英文 | 用户级 | always | GATE | 换模型后中文提问输出全中文 | 生态维护者 |
| `B-02` | 输出只判三态，语义不折叠 | 用户级 | always | SCAN | 造超时命令如实记"无法判定" | 生态维护者 |
| `B-03` | 动手前先验环境与主线 | 用户级 | always | GATE | 错误目录动手前先 `pwd -P` | 生态维护者 |
| `B-04` | 独立并行、依赖串行、不臆测缺参 | 用户级 | always | SCAN | 3 个独立读命令是否并发 | 生态维护者 |
| `B-05` | 绝不写明文凭证 | 用户级 | always | GATE | 全仓搜索无 token 明文 | 生态维护者 |
| `B-06` | 前提断言实查取证，禁以记忆当事实 | 用户级 | always | SCAN | 引用退役断言给文件+行号 | 生态维护者 |
| `B-07` | 换模型对齐习惯 + 业务上下文 | 用户级 | always | GATE | 换模型后复述当前主线 | 生态维护者 |
| `B-08` | 动作前先查正本入口 | 用户级 | always | SCAN | 试错 ≥2 次回头查入口 | 生态维护者 |

## 三、强制力梯度（三维度③）

| 级别 | 机制 | 本生态采用 |
|---|---|---|
| 1 软声明 | 规则文字 / 薄壳内联 | ✅ 主用（三通道叠加） |
| 2 config | `settings.json` | ✅ 仅 `parentDiscovery:false` 等减负项 |
| 3 `permissions.deny` | 工具级硬禁 | ⭕ 需要时用于不可逆动作 |
| 4 hook | 事件钩子 | ❌ **不押**（手机/云端不跑，第 19 章） |

> 不可逆动作（删/推远端）不靠 hook，改在技能内设"删除前确认"闸 + `allowed-tools` 白名单（20.8）。

## 四、去重裁决台账

| 组 | 旧条目（tvbox-eco） | 裁决 |
|---|---|---|
| 并行 | M-R130 ≈ M-R145 | 合 `B-04` |
| 三态 | M-R57 ≈ M-R60 | 合 `B-02` |
| 换模型 | M-R206 / 301 / 302 / 303 | 合 `B-07` |
| 薄壳重复 | M-R110、M-R022 | 薄壳内联保留（有意兜底冗余）；真源 core-8；技能不贴第 3 份 |

## 五、降级 / 名实不符记录（tvbox-eco 实测，仅作反面参照）

| 现象 | 实测 | 正确处置 |
|---|---|---|
| 降级未同步 | M-R215 `enforce_level=DOC` 但中文 `等级=GATE` | 统一为单一 `level` |
| 降级残留 | M-R215/130/136 已降 DOC 却仍留 `gate_hook` | 清除残留 |
| 名实不符 | 部分 `GATE` 级却 `guard_form=manual/declare` | 按 M-R136「不造假门禁」诚实降级 |
| GATE 无落地 | 33 条 warm/cold GATE 无可执行脚本 → 降 DOC | 无活执行器即不标 GATE |
| 探针实跑 | B2 全量 **PASS 3 / FAIL 1 / UNRUNNABLE 74**，处置 68 条 | 结果记台账，不进规则 |

## 六、未纳入基座的规则（归类）

| 类 | 条目 | 归属 |
|---|---|---|
| 能力规则（绑 TVBox） | M-R001/116/136/021/305/304 | 项目级情境契约，不进通用基座 |
| 治理台账 | index(280KB)/registry(325KB)/disposition/probe 结果 | 本台账 / `docs/`，不进 context |
| 可选参考 | M-R77 SKILL ≤35KB、M-R241 门禁真实性 | 工程质检，后续按需 |

## 七、变更留痕（append-only）

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-11-10 | 建立台账；基座 8 条定稿（C） | SOP 20.9；tvbox-eco core.json 23 条实测 |
| 2026-11-10 | 落地三分离：core-8 / zh-style 瘦身 / docs.paths / 本台账（A） | SOP 20.9 |
| 2026-11-10 | 弃用 hot/warm/cold，改「作用域 × 触发 × 强制力」三维度 | 用户拍板（20.9 方案第 1 点） |

> 与 `docs/base-rule-mapping.md` 分工：本台账管**全生态规则**的 schema/强制力/探针/变更；`base-rule-mapping.md` 管**基座 8 条**的来源、去 TVBox 化映射与安装命令。二者都是台账、都不进 context、职责不重叠。

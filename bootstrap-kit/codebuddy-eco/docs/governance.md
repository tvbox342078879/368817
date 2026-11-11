# 治理映射：SOP 章节 ↔ codebuddy-eco 产物

> 本文档把 [`CodeBuddy-会话中文风格统一-SOP.md`](../../CodeBuddy-会话中文风格统一-SOP.md)（SOP）的治理原则，对应到新生态 `codebuddy-eco` 的具体产物，确保"以 SOP 为基础"不是空话。

## 一、强制链映射（SOP 第 19 章 → 本生态）

| SOP 第19章原则 | 本生态落地产物 |
|---|---|
| ① 薄壳内联铁律（手机必加载） | `.codebuddy/CODEBUDDY.md`（三条不可协商 + 5 条强制铁律，官方 Memory 文档合法路径） |
| ② 官方自动加载规则 | `.codebuddy/rules/zh-style.md`（`alwaysApply:true`） |
| ③ 手机指令兜底 | 设置→给 WorkBuddy 的指令（用户侧，文档提示） |
| 不押钩子注入 | 四技能均声明"不靠钩子强制"，走配置/薄壳 |

## 二、经验复用映射（SOP 第 17 章 → skill-evolution）

| SOP 第17章概念 | 本生态对应 |
|---|---|
| Auto Memory + Typed Memory | `skill-evolution` 的"复发检测→固化"引擎 |
| MEMORY.md 前200行索引 | 技能 CHANGELOG + `MANIFEST.json` 索引 |
| ≠ 技能进化 | 本技能即"技能进化"的自动化执行体 |

## 三、底座层接入映射（SOP 第 18 章 → 四技能）

| SOP 第18章接入物 | 本生态对应技能 |
|---|---|
| 技能（自我生长） | `skill-evolution` |
| 自动化 / 连接器 | `feature-gate`（安全迭代阀门） |
| 资料库联动 | `artifact-store`（本地轻量化总闸：产物 LRU + 记忆冷归档 + 会话隔离） |
| 唯一真源落地 | `machine-bootstrap`（git 克隆端） |

## 四、回滚/快照/唯一真源映射（SOP 第 16 章 → 全生态）

| SOP 第16章概念 | 本生态对应 |
|---|---|
| 检查点（会话内撤销） | 不替代，仅本地 |
| 唯一真源 = Git | 所有交付物/技能/规则进 git；`machine-bootstrap` 是拉取端 |
| 安全红线 | `zh-style.md` §6 + 各技能"零明文 token"声明 |

## 五、Tvbox-eco 借鉴对照（仅结构，不搬业务）

| tvbox-eco 结构 | 本生态借鉴方式 |
|---|---|
| `.codebuddy/skills/*/SKILL.md` 官方路径 | 直接采用（四技能住这） |
| `MANIFEST.json`（依赖图+事件契约） | 采用轻量版，去 god-object |
| `rules/core.json` 23条 + 钩子强制 | **不借鉴**（手机不跑钩子，SOP 第19章已判） |
| probe-hub/tvbox-source-hub 等 TVBox 专属能力 | **不借鉴**（领域专属，离开生态归零） |
| ecosys-conductor 协调者 | 仅学"去中心 hub / 持契约不吞业务"思路 |

## 六、手机防卡顿映射（官方一手根因 → 本生态解法）

依据官方 CLI **Best Practices** + **v2.51.0 发布说明** + **Memory 文档**（非社区推断）。

| 卡顿根因（官方一手） | 官方原生解法（优先） | 本生态兜底 | 落地产物 |
|---|---|---|---|
| 上下文窗口快速填满 | `/clear` 纪律 · 自动压缩 + `/compact` · Subagents 独立上下文 | `zh-style.md` §8.1 立纪律 | §8.1 |
| 记忆/规则全量加载 | v2.51.0 记忆目录摘要(按需加载) + 自动清理(随会话历史) · 条件规则 `paths` · parentDiscovery 关闭 | 超大主题文件人工归档资料库 | §8.2/§8.3 + `artifact-store` ② |
| 本地数据（产物/缓存/旧会话）堆积 | `/clear` + 移动端删/归档会话 | 产物 LRU 归档资料库 | `artifact-store` ①③ |
| 盲目拉大窗口 | 200K 默认够用，1M 不更聪明 | `zh-style.md` §8.4 约束 | §8.4 |
| APP 缓存冗余 / 版本过旧 | 定期清缓存 + 重启（APP 端，非本生态职责） | 用户侧 / 平台 | 用户侧 |

> **关键修正**：本生态**不另建人工"记忆冷归档索引"**（上轮曾写），改为直接复用 v2.51.0 原生"按需加载 + 自动清理"；人工只兜底超大主题文件。详见 `artifact-store` §6 对齐清单。

## 七、验证清单（新生态就绪后跑一遍）

- [ ] `git init` 完成，远程已设
- [ ] `.codebuddy/CODEBUDDY.md` 薄壳存在且含三不可协商（官方路径，只放一处）
- [ ] `.codebuddy/rules/zh-style.md` 存在且 `alwaysApply:true`
- [ ] `base/rules/core-8.md` 已 `cp` 到 `~/.codebuddy/rules/`（用户级基座）
- [ ] `.codebuddy/rules/docs.paths.md` 存在且 `alwaysApply:false` + `paths`（条件触发示例）
- [ ] `docs/rule-ledger.md` / `docs/base-rule-mapping.md` 为台账，不进 context
- [ ] 四技能 SKILL.md 在 `.codebuddy/skills/` 下，frontmatter 完整
- [ ] 手机端设"给 WorkBuddy 的指令"含中文铁律
- [ ] 三通道就位由 L2 三态实测确认（官方无 `--verify` 能力，本生态不提供、不宣称通过）
- [ ] 跑 `python3 verify/terminology_check.py --sop ../CodeBuddy-会话中文风格统一-SOP.md` 退出码 0（SOP 20.11 C5 门禁）
- [ ] 用中文提问，确认模型全程中文、未因换模型漂

## 八、规则侧三分离映射（SOP 20.9 → 本生态）

> 弃用 tvbox-eco 的 `hot/warm/cold` 冷热分层，改官方三维度「作用域 × 触发 × 强制力」；与 20.8（技能规范化）成对。

| 三维度 | 落地产物 | 说明 |
|---|---|---|
| 作用域 · 用户级 | `base/rules/core-8.md` → `~/.codebuddy/rules/` | 8 条通用铁律跨项目去重，一次配置全项目生效 |
| 作用域 · 项目级 | `.codebuddy/rules/zh-style.md` | 瘦身后只留项目专属契约 + §8 通用工程纪律（§1–7 改继承指针） |
| 触发 · 常驻 | `core-8.md` / `zh-style.md`（`alwaysApply:true`） | 无条件铁律才常驻 |
| 触发 · 条件 | `.codebuddy/rules/docs.paths.md`（`alwaysApply:false` + `paths`） | 情境契约命中 `docs/**` 才注入，不常驻占 context |
| 强制力 | 软声明三通道 + `permissions.deny`（可选）；**不押 hook** | 手机/云端不跑钩子（第 19 章），不可逆动作在技能内设确认闸 |
| 台账归位 | `docs/rule-ledger.md` + `docs/base-rule-mapping.md` | schema/去重/降级/owner/探针移出规则层，不进 context |

> **两个有意不为**（结合手机端约束，非遗漏）：① §8 是运行时元纪律，保留项目级常驻、不改 `paths` 条件（paths 只适合绑文件路径的情境契约）；② 薄壳内联铁律保留**有意冗余**（三通道兜底），与 20.8 消除的"技能内重复铁律"性质不同。

## 九、口径统一规则映射（SOP 20.11 → 本生态）

> 20.10 是「立规依据与落地纪实」，20.11 是同一条规则在 SOP 主文档的**正式生效条款**；条文真源仍在 `base/rules/core-8.md`，本生态是执行体，SOP 不复制条文（C2）。

| 条款 | 本生态落地产物 |
|---|---|
| C1 真源登记 | `docs/registry.md` 第一节（唯一真源登记表） |
| C2 引用不复制 | 机检 ⑤ 指纹校验 + 各 SKILL.md 继承声明指针 |
| C3 受控词表 | `docs/registry.md` 第二节（分层登记）+ 第七节机读区 |
| C4 编号命名空间 | `docs/registry.md` 第三节 + `sop_sections` 等机读清单 |
| C5 连带同步 + 机检 | `docs/registry.md` 第四节影响面 + `verify/terminology_check.py` + `docs.paths.md` 第 6 步 |
| C6 违规处置 | 机检四类判定（断链 / 词表 / 编号 / 复制条款），回真源改 |
| C7 有意例外 | `docs/registry.md` 第五节（薄壳、手机指令、技能入口表） |

> **20.11 自身即首次实证**：新增该节时按 C4/C5 同步了 `sop_sections` 编号、登记表新增行、脚注、本节映射与验证项，再跑三模式门禁——规则不是在文档里躺着，是改一处就带动全部指针。

## 十、技能侧机检守护映射（SOP 20.12 → 本生态）

> 20.8 是人工规范化，20.12 让它不再悄悄退化；官方 Skills 文档口径：frontmatter 三字段皆「必填：否」（本生态约定写齐）、`description` 是一句话能力描述、触发靠 AI 语义识别而非关键词清单。

| 20.12 整改层 | 本生态落地产物 |
|---|---|
| ① description 按官方口径 | 4 个 `SKILL.md`：`description` 写「做什么 + 何时用」一句，触发词清单移进正文「触发词（唯一真源）」行 |
| ② 短名定一真源 | `docs/registry.md` 第七节 `skill_contract.canonical_short`；薄壳 / README / MANIFEST 三处对齐；4 份继承指针压短并逐字一致 |
| ③ 机检扩到技能侧 | `docs/registry.md` 第七节 `skill_contract` + `required_files`（4 个 SKILL.md）；`verify/terminology_check.py` 第 ⑦ 项 `check_skill_contract` |
| ④ 有意例外登记 | `docs/registry.md` 第五节（继承指针、触发场景列）；私有仓库名移出运行时契约，清单统一指向 `README.md` 第五节 |
| ⑤ 连带同步 | `sop_sections` 加 20.12、脚注、本节映射、`docs.paths.md` 工作流「六项 → 七项」；20.8 失实纪实已留痕订正 |

> 机检第 ⑦ 项（配置全从 registry 读、脚本不硬编码）：必备/禁用 frontmatter 字段、`description` 触发词堆砌、触发词真源在正文、继承指针一致、私有仓库名硬编码、短名三入口对齐。三模式门禁与负向验证结论见 SOP 20.12.4，**具体数字不写进文档**（随正文增长，判据看退出码与 0 断链）。

### 规则契约（机检第 ⑧ 项）· 按官方 Memory 文档订正

> 对应 SOP 20.12.2 的官方口径核对。20.12 只覆盖了技能侧，规则侧留有两处需按官方口径订正：

| 项 | 官方原文口径 | 本生态整改 |
|---|---|---|
| 规则控制字段 | 仅 `enabled`(boolean) / `alwaysApply`(boolean) / `paths`(string\|string[]) 三项；官方字段表**无 `priority`** | 删 `zh-style.md` 与 `MANIFEST.json` 里的 `priority: high`；`description` 保留为人读元数据，不冒充控制字段 |
| 规则类型判定 | `alwaysApply:true`→ALWAYS；`false`+有 `paths`→MANUAL；`false` 无 `paths`→**不支持、规则不加载** | `docs.paths.md` 已是 `false`+`paths`，合规；`zh-style.md` 已是 `true`，合规 |
| 项目记忆位置 | `./CODEBUDDY.md` **或** `./.codebuddy/CODEBUDDY.md`（两处皆官方合法） | 薄壳实体固定 `.codebuddy/CODEBUDDY.md` 只放一处，`MANIFEST`/README/自述指针统一；不再称「顶层唯一」 |
| 强制链不押钩子 | 官方 frontmatter `hooks` 仅 `context: fork` 生效，非内置来源默认不注册（`allowUntrustedFrontmatterHooks` 默认 `false`） | 「手机/云端任务不跑钩子」是**本生态实测结论**，官方文档未作此声明，已在薄壳/MANIFEST 标注 |

新增机检第 **⑧** 项 `check_rule_contract`：校验两份 `.codebuddy/rules/*.md` 的 frontmatter 只含官方三控制字段 + 元数据、禁 `priority` 等非官方字段、`alwaysApply:false` 必须带 `paths`。配置唯一真源仍是 `docs/registry.md` 第七节 `rule_contract`，脚本不硬编码第二份。工作流第 6 步措辞同步为「共 8 项」。

## 十一、交接包 / 机读门禁 / 面板映射（SOP 20.13 → 本生态）

> 20.13 是交付/视图层登记，不并入 20.12.6 的六层治理递进。`--json` 与面板都是**本生态约定**（官方文档未定义），不冒充官方能力。

| 20.13 落点 | 本生态产物 |
|---|---|
| `--json` 机读输出 | `verify/terminology_check.py` 的 `--json`（同一套 8 项检查的 `checks[]` / `summary`，不新增检查项、判据与退出码不变）；registry 第六节命令块 + `docs.paths.md` 第 6 步 |
| 面板四视图 | `panel/build_panel.py` + 生成的 `panel/index.html`（独立目录，读 git log / --json / 文件实扫 / MANIFEST 等真源产物） |
| 编号登记 | `sop_sections` 加 `"20.13"`、脚注「整理依据」、本节映射（C4） |
| 回顾式边界 | 只呈现已发生事实；另一沙箱 L2 / 另一会话 / 凭证销毁恒 `UNDETERMINED`；非实时、无事件流（20.13.3 / 20.13.4） |

> **有意不为**：面板是审查侧派生视图，与 `bootstrap-kit`（20.11 一次性搬运介质）同类——**不进 `required_files`、不进 git、不进机检范围、不进交接包快照**，因此 15 文件骨架、机检三模式、快照一致性全部保持不变。若后续要纳入运行时骨架，须按 C4/C5 走编号登记 + 机检 + 全链路同步，属另一个授权项。

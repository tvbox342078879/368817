# 口径统一性登记（registry）

> **本文件是「口径」的唯一真源**（元规则 M1）。它不规定业务怎么做，只规定「一个事实在哪写、别处怎么写指针、用哪个词、用哪个编号、改了要连带改哪里」。
> 元规则条文真源在 `base/rules/core-8.md` 正文首；本文件是它指向的**登记表**。机读区见第七节 JSON，`verify/terminology_check.py` 直接读它——**词表/清单只有这一份，脚本不硬编码第二份**。
> 依据 SOP 20.10 / 20.11 / 20.12 / 20.13。

## 一、唯一真源登记表（M1）

> 「真源」= Git 仓库里的文件；`~/.codebuddy/rules/core-8.md` 是它的**安装副本**，不是真源（SOP 第 16 章：Git 永久历史为唯一真源）。

| 事实类别 | 唯一真源 | 别处怎么写 | 禁止 |
|---|---|---|---|
| 8 条通用铁律条文 | `base/rules/core-8.md` | 写「见 `core-8.md` `B-0x`」 | 复制条款全文 |
| 元规则 M1–M7 条文 | `base/rules/core-8.md` 正文首 | 写「见 `core-8.md` 元规则」 | 另写一份规则 |
| 口径统一规则·正式生效条款（适用/约束/门禁/处置） | `CodeBuddy-会话中文风格统一-SOP.md` 20.11 | 写「见 SOP 20.11 Cx」 | 在脚手架里另立一份生效条款；复制条文全文 |
| 项目专属契约 / 分层声明 | `.codebuddy/rules/zh-style.md`（§0、§1–7 补充、§8） | 写「见 `zh-style.md` §x」 | 改写小节编号 |
| 条件触发契约 | `.codebuddy/rules/docs.paths.md` | 写文件名 + `paths` | 复制进常驻规则 |
| 规则 schema / 强制力 / 探针台账 | `docs/rule-ledger.md` | 写「记台账」 | 塞回规则文件 |
| 8 条来源 / 去 TVBox 化映射 | `docs/base-rule-mapping.md` | 写「见映射台账」 | 在别处另列编号 |
| 技能契约（职责/触发/边界） | `.codebuddy/skills/*/SKILL.md` | 写技能名 + 一句话短名 | 在 README 写第二份契约 |
| **技能一句话短名（canonical_short）** | `docs/registry.md` 第七节 `skill_contract.canonical_short` | 薄壳/README/MANIFEST **三处严格对齐**该短名 | 各写别名（如「灰度司」「进化舵」） |
| **技能触发词清单** | 各 `SKILL.md` 正文「触发词（唯一真源）」行 | 引用技能名，不复制触发词 | 塞进 `description` / 在别处再列一份 |
| 依赖图 / 事件 / 四格落位 | `.codebuddy/MANIFEST.json` | 引用字段名 | 手抄一份清单 |
| SOP 章节 ↔ 产物映射 | `docs/governance.md` | 写「见 governance 第 x 节」 | 重复推演映射 |
| 治理原则 / 章节编号 | `CodeBuddy-会话中文风格统一-SOP.md` | 写「第 x 章 / 20.x.y」 | 另起章节号 |
| 本登记表（口径本身） | `docs/registry.md` 本文 | 写「见 registry」 | 在别处再定义词表 |

## 二、受控词表（M3 · 分层登记，非同义合并）

> **落地修正**：不把「基座/基建/底座」粗暴合并成一个词——它们在本体系里**指代不同层**，合并反而破坏 SOP 第 18 章「底座层接入」等既有标题与引用。口径统一 = **给每个词登记唯一所指 + 禁跨层误用**，而不是消灭同义词。

| 规范词 | 唯一所指（层） | 禁用误用（跨层搭配） |
|---|---|---|
| **基座** | 规则层 · 用户级 8 条通用铁律（`core-8.md`） | 「基建规则」「底座规则」「基建技能当基座」 |
| **基建** | 技能层 · 4 个治理技能（skill-evolution 等） | 「基座技能」「用基座指代技能层」 |
| **底座** | 平台层 · 接入能力（连接器/自定义模型/资料库/自动化，SOP 第 18 章） | 「用底座指代规则基座」 |
| **薄壳** | `.codebuddy/CODEBUDDY.md` 项目记忆内联指令（官方 Memory 文档列明的合法路径之一） | 「壳文件」「薄规则」 |
| **真源** | Git 仓库里唯一权威文件 | 「唯一来源」「主本」混用 |
| **接活** | 接入官方自动加载路径使手机/云端生效 | 「激活」「挂载」混用 |
| **台账** | 给人/脚本读、不进 context 的治理元数据 | 「清单」「注册表」混用 |
| **三分离** | 落位四格（用户级/项目级/条件/台账）——**结果** | 与「三维度」互换 |
| **三维度** | 分类三轴（作用域 × 触发 × 强制力）——**方法** | 与「三分离」互换 |

## 三、编号命名空间（M4）

| 前缀 / 形态 | 含义 | 状态 |
|---|---|---|
| `B-01`…`B-08` | 去 TVBox 化基座 8 条 | 已占用，**不得重号、不得跳号** |
| `M-R###` | tvbox-eco 旧规则编号 | **只读参照**，不用于新规则 |
| `§0`–`§8` / `§8.1`–`§8.4` | `zh-style.md` 文件内小节 | 改条款不得改号（20.7 引用锚点） |
| `第 x 章` | SOP 章 | 只增不改 |
| `20.x` / `20.x.y` | SOP 第 20 章节 | 只增不改 |
| `M1`–`M7` | 本元规则条款 | 只增不改 |
| kebab-case 技能名 | `SKILL.md` 的 `name`（官方字段） | 不占用上述编号空间，短名不另编号 |

## 四、引用 / 影响面清单（M2 + M5）

> 改真源后，按此表连带核对其指针点。这正是机检脚本 `check_section_refs` 与 `check_skill_contract` 自动做的事（扫描 § / B- / 文件名引用、断链即报；技能短名三处对齐即报）。

| 改动对象 | 必须核对的指针点 |
|---|---|
| `core-8.md` 任一条 | 4 个 `SKILL.md` 顶部继承指针、`zh-style.md` §1–7 指针、`CODEBUDDY.md` 薄壳、`base-rule-mapping.md`、`rule-ledger.md` |
| `zh-style.md` §8 编号 | SOP 20.7 / 20.8 / 20.9、`governance.md` 第六/八节、`artifact-store/SKILL.md` 4 处、`docs.paths.md` |
| `MANIFEST.json` 条目 | `README.md` 第一节、`governance.md`、`CODEBUDDY.md` 末尾指针 |
| 新增/改名技能 | `MANIFEST.json` skills、`CODEBUDDY.md` 技能表、`README.md` 第二节、`governance.md` |
| **改技能 `description` / 一句话短名** | 4 个 `SKILL.md` + 薄壳/README/MANIFEST 三处短名 + registry 第七节 `canonical_short`（机检 ⑦ 守护） |
| 新增 SOP 章节 | 脚注「整理依据」、`governance.md` 映射、本登记表编号空间 `sop_sections` |

## 五、有意例外登记（M7 · 不算违例）

| 例外 | 理由 | 依据 |
|---|---|---|
| `CODEBUDDY.md` 薄壳内联语言/三态/先验铁律 | 第 19 章三通道叠加兜底；用户级未配置时仍不失守 | SOP 20.9.5 |
| 手机「给 WorkBuddy 的指令」内联 8 条 | 跨端兜底通道，无法引用文件路径 | SOP 第 19 章③ / 20.9 |
| `CODEBUDDY.md` 技能入口表一句话描述 | 便于手机端一眼可见，非契约全文（契约真源在 SKILL.md） | SOP 20.9 |
| **4 份 `SKILL.md` 顶部的继承指针（逐字一致）** | 每技能需自证「铁律从哪继承」，属**指针**而非条文复制；一致性由机检 ⑦ 守护 | SOP 20.9 / M2 / 20.12 |
| **薄壳技能表「触发场景」列** | 手机端触发提示，触发词真源仍在各 `SKILL.md` 正文 | 第 19 章③ / 20.12 |

> 未登记在表中的重复，一律按 M6「回真源改」处理。

## 六、机检（M5 · 不通过不算完成）

```bash
# 在 codebuddy-eco 仓库根执行（只读，不写任何文件）
python3 verify/terminology_check.py
python3 verify/terminology_check.py --strict      # 把 WARN 也升级为 FAIL
python3 verify/terminology_check.py --sop ../CodeBuddy-会话中文风格统一-SOP.md   # 连 SOP 的 § 引用一起校验
python3 verify/terminology_check.py --json                 # 机器可读输出（面板数据源，SOP 20.13.2）
python3 verify/terminology_check.py --json --strict --sop ../CodeBuddy-会话中文风格统一-SOP.md   # 可组合
```

检查项：① 真源登记表列出的文件是否都存在；② § / `B-` / SOP 章节引用是否断链；③ 受控词表跨层误用；④ 编号命名空间是否重号/跳号/越界；⑤ 非真源文件是否复制了 8 条铁律全文（M2）；⑥ `MANIFEST.json` 是否合法；⑦ **技能契约**（4 个 `SKILL.md` frontmatter 合规 / `description` 无触发词堆砌 / 触发词归属正文 / 4 短名三处对齐 / 无私有仓库名硬编码，SOP 20.12）；⑧ **规则契约**（`.codebuddy/rules/*.md` frontmatter 只含官方 Memory 文档「规则控制字段」三项 `enabled` / `alwaysApply` / `paths` + 人读元数据 `description`，禁 `priority` 等非官方控制字段；`alwaysApply:false` 必须有 `paths`，否则官方判定「不加载」，SOP 20.12.2）。

> `--json`（SOP 20.13.2）**不新增检查项**：它是同一套 8 项检查的机器可读输出通道，`checks[]` 逐项给出 `level/item/detail`，判据、退出码、配置真源一律不变；`snapshot_only: true` 明示这是拉取式只读快照、非实时联动、无事件流，供 `panel/` 四视图读取，不预测进度。

## 七、机读真源区（terminology_check.py 读取，勿手写第二份）

```json
{
  "vocab_pairs": [
    ["基建规则", "规则层应称「基座」"],
    ["底座规则", "规则层应称「基座」"],
    ["基座技能", "技能层应称「基建」"],
    ["技能基座", "技能层应称「基建」"],
    ["规则基建", "规则层应称「基座」"],
    ["薄规则", "应称「薄壳」"],
    ["壳文件", "应称「薄壳」"]
  ],
  "required_files": [
    "base/rules/core-8.md",
    ".codebuddy/CODEBUDDY.md",
    ".codebuddy/MANIFEST.json",
    ".codebuddy/rules/zh-style.md",
    ".codebuddy/rules/docs.paths.md",
    "docs/base-rule-mapping.md",
    "docs/governance.md",
    "docs/rule-ledger.md",
    "docs/registry.md",
    "README.md",
    "verify/terminology_check.py",
    ".codebuddy/skills/skill-evolution/SKILL.md",
    ".codebuddy/skills/machine-bootstrap/SKILL.md",
    ".codebuddy/skills/feature-gate/SKILL.md",
    ".codebuddy/skills/artifact-store/SKILL.md"
  ],
  "base_rule_ids": ["B-01", "B-02", "B-03", "B-04", "B-05", "B-06", "B-07", "B-08"],
  "zh_style_sections": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "8.1", "8.2", "8.3", "8.4"],
  "sop_sections": ["16", "17", "18", "19", "20", "20.0", "20.1", "20.2", "20.3", "20.4", "20.5", "20.6", "20.7", "20.8", "20.9", "20.10", "20.11", "20.12", "20.13"],
  "rule_fingerprints": [
    "回复语言跟随用户消息语言",
    "命令/工具输出只判",
    "动手前先确认真实环境",
    "多个独立动作同一条消息一次性并发发出",
    "绝不把任何 token",
    "须先对文件系统/真源实查取证",
    "新模型/新会话接手须先对齐",
    "做动作前先查现成正本入口"
  ],
  "fingerprint_exempt_files": [".codebuddy/CODEBUDDY.md"],
  "allowed_b_prefix": "B-0",
  "skill_contract": {
    "skill_files": [
      ".codebuddy/skills/skill-evolution/SKILL.md",
      ".codebuddy/skills/machine-bootstrap/SKILL.md",
      ".codebuddy/skills/feature-gate/SKILL.md",
      ".codebuddy/skills/artifact-store/SKILL.md"
    ],
    "required_frontmatter": ["name", "description", "allowed-tools"],
    "forbidden_frontmatter": ["version"],
    "description_forbid_substrings": ["当用户说", "时使用"],
    "description_max_slashes": 1,
    "trigger_source_marker": "触发词（唯一真源）",
    "inherit_pointer_text": "三通道全局强制，本技能直接继承、不重复声明",
    "forbid_repo_name_in_skill_files": ["tvbox342078879", "tvbox-eco"],
    "canonical_short": {
      "skill-evolution": "复发问题自动固化成技能",
      "machine-bootstrap": "一键换机/克隆工作副本",
      "feature-gate": "特性开关+绞杀者切流",
      "artifact-store": "本地轻量化总闸·防手机卡顿"
    },
    "short_presence_files": [
      ".codebuddy/CODEBUDDY.md",
      "README.md",
      ".codebuddy/MANIFEST.json"
    ]
  },
  "rule_contract": {
    "rule_files": [
      ".codebuddy/rules/zh-style.md",
      ".codebuddy/rules/docs.paths.md"
    ],
    "official_control_fields": ["enabled", "alwaysApply", "paths"],
    "metadata_fields": ["description"],
    "banned_control_fields": ["priority"],
    "require_paths_when_always_false": true,
    "sop_section": "20.12.2"
  }
}
```

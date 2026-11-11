---
description: 编辑 docs/ 下治理文档时注入的同步契约（文档↔MANIFEST↔governance 一致性）。仅在命中 docs/** 时加载，不常驻。
alwaysApply: false
paths:
  - "docs/**/*.md"
enabled: true
---

# 文档同步契约（条件触发示例）

> 官方 `paths` 条件规则示范：**本文件不常驻**，只在编辑 `docs/**/*.md` 时注入（SOP 20.9 三分离第②格）。对比 `zh-style.md` 的 `alwaysApply:true` 常驻——情境契约用 paths，通用铁律用 always，二者不混。
> 口径纪律以 `base/rules/core-8.md` 元规则 M1–M7 为真源，本文件只接**执行步骤**（M2 引用不复制、不另写一份规则）。

编辑或新增 `docs/` 下治理文档时，执行以下工作流：

1. 同步核对 `.codebuddy/MANIFEST.json` 对应条目（技能/规则/落点是否一致），不留过时描述。
2. 同步核对 `docs/governance.md` 章节映射，引用一律用**小节编号**（如 `zh-style.md §8.1`），不复制条款全文、不留断链。
3. 台账类信息（去重决策、降级记录、owner、探针结果、变更留痕）写 `docs/rule-ledger.md`，**不写回规则文件**。
4. 涉及基座 8 条来源与去 TVBox 化映射，写 `docs/base-rule-mapping.md`，与 `core-8.md` 真源保持一致。
5. 口径类改动（词表/编号/真源登记/影响面）写 `docs/registry.md` 第七节机读区——**这是唯一配置源**，不要在 `verify/terminology_check.py` 里硬编码第二份。
6. 收尾跑两项校验，任一不绿不算完成：
   - `python3 -c "import json;json.load(open('.codebuddy/MANIFEST.json'))"`（JSON 合法）
   - `python3 verify/terminology_check.py --sop ../CodeBuddy-会话中文风格统一-SOP.md`（口径机检 M5 共 8 项：真源齐备 / 词表 / 编号 / §引用断链 / 复制铁律 / MANIFEST / **技能契约** / **规则契约**，见 SOP 20.12 + 20.12.2）
   - 可选：`python3 verify/terminology_check.py --json` 输出机器可读结果供 `panel/` 读取（同一套 8 项、不新增检查项，见 SOP 20.13.2）；新增 SOP 章节须先在 registry 第七节 `sop_sections` 登记编号（C4），否则 `--sop` 判断链。

> 不押钩子：以上靠条件注入 + 自检生效，手机/云端任务同样可用（第 19 章）。机检脚本**只读**，不写任何文件。

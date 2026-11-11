# 02 · 冷启动落地（6 步，逐步可照抄 + 判据）

> 总起：这一步回答「**具体某一步怎么做**」。每步给：做什么 → 命令（可直接复制）→
> 预期输出/判据 → 失败怎么记（三态）。命令默认你已站在**新项目根**，
> 且 `codebuddy-eco/` 与 `CodeBuddy-会话中文风格统一-SOP.md` 已从本包取出、放在同级。
> 依据见 `01-DECISIONS.md`，验收在 `03-ACCEPTANCE.md`。

**摆放前提**（先照这个摆，后面命令才成立）：

```
<新项目根>/                        ← 你 cd 到这里
├── CodeBuddy-会话中文风格统一-SOP.md     ← 从包里取出
└── codebuddy-eco/                       ← 从包里取出（15 文件）
```

---

## 步骤 0 · 先验环境（B-03，动手前先认真实环境）

```bash
pwd -P
ls -a
git log --oneline -1 2>&1 | head -1
```

- 判据：`pwd -P` 输出是新项目根的真实绝对路径；`ls -a` 能看到 `codebuddy-eco/` 和 `CodeBuddy-…SOP.md` 两个同级条目。
- 三态：`git log` 报 `not a git repository` 是**真阴性**（还没 init 属正常），不要当成错误；目录不对就停下，别在临时目录乱改。

## 步骤 1 · 同级校验（最容易断链，先做）

```bash
test -f "CodeBuddy-会话中文风格统一-SOP.md" && echo SOP_OK
test -d codebuddy-eco && echo ECO_OK
find codebuddy-eco -type f | wc -l
```

- 判据：打印 `SOP_OK`、`ECO_OK`；`find` 输出 **15**。
- 依据：包内 6 处 `../SOP` 指针 + 机检 `--sop` 走相对路径（01-D1）。不同级 → 全断。

## 步骤 2 · 建唯一真源（包内快照不含 `.git`，新沙箱必做）

```bash
cd codebuddy-eco
git init
git add .
git -c user.name='eco-local' -c user.email='eco@localhost.invalid' \
  commit -m "eco bootstrap: import codebuddy-eco scaffold"
```

- 判据：`git log --oneline -1` 能看到这条提交；`git status` 干净。
- **零配置前置（本包端到端演练实测）**：全新沙箱通常没有 git 全局身份，
  直接 `git commit -m "..."` 会报 `Author identity unknown`、退出码 **128**（见 01-D9）。
  故用命令内 `-c` 局部占位身份，**不写全局 config、不引入真实账号**，照抄即可通过；
  已有全局身份的沙箱用原三行亦可。
- 三态：新沙箱若禁止建 remote 没关系——本步只建**本地永久历史**，不假设有远端（SOP 16）。
- 如实说明：审查侧**本体**本轮已做过这一步（本地 / 0 remote / 1 提交，见 01-D8）；
  但 `.git` 不随搬运介质走，你拿到的是**不含 `.git` 的 15 文件快照**，所以本步对你仍是必做项。

## 步骤 3 · 放技能与项目级规则（拷目录即生效，不跑服务）

```bash
# 四个技能（官方自动加载路径，放对即被宿主读取）
find .codebuddy/skills -name SKILL.md | sort
# 两格项目级规则 + 薄壳 + 治理清单
ls .codebuddy/rules/ .codebuddy/CODEBUDDY.md .codebuddy/MANIFEST.json
```

- 判据：`find` 列出 4 个 SKILL.md；`ls` 列出 `zh-style.md`、`docs.paths.md` 等。
- 说明：这一步**不需要执行任何安装命令**——技能/规则靠宿主读目录生效（01-D2/D4）。
  不要 `cp skills/...` 到顶层自建目录，那是旧生态的病根。

## 步骤 4 · 装用户级基座（审查侧实测 `~/.codebuddy/rules/` 不存在，必做）

```bash
mkdir -p ~/.codebuddy/rules
cp base/rules/core-8.md ~/.codebuddy/rules/core-8.md
test -f ~/.codebuddy/rules/core-8.md && echo BASE_INSTALLED
```

- 判据：打印 `BASE_INSTALLED`。
- 三态提醒：**沙箱里的 `~/.codebuddy/` 不等于真机**（SOP 里已写过"沙箱写文件≠真机生效"）。
  这步在沙箱只作「验证用」，真机上要在手机/桌面端设置里确认用户级规则被加载；
  在真机没确认前，8 条铁律是否生效记「无法判定」，不许写「已生效」。

## 步骤 5 · 三通道补齐（人工动作，文件带不过去）

- 薄壳：`.codebuddy/CODEBUDDY.md` 已在位（三不可协商 + 5 铁律内联）。
- 手机端：到「设置 → 给 WorkBuddy 的指令」粘贴 8 条通用铁律（SOP 19③ 跨端兜底）。
  **这是人工动作，本包无法代做**；没做就记「无法判定」。
- **薄壳位置已按官方口径统一，无需拍板**：官方 Memory 文档列明项目记忆可存
  `./CODEBUDDY.md` **或** `./.codebuddy/CODEBUDDY.md`（两处皆合法）。本生态实体固定
  `.codebuddy/CODEBUDDY.md`，`MANIFEST.json` 的 `thin_shell.path`、README、薄壳自述、
  governance 指针已全部对齐到该路径，**只放这一处**（M1，不两处都放）。
  用一次中文提问验证它真被读到（见 03-L2）。

## 步骤 6 · 明确「不做」的清单（不许假装通过）

| 不做 | 原因 |
|---|---|
| 押钩子 / 配 hook 事件 | 本生态实测：手机/云端任务不跑钩子（SOP 19；官方文档未作此声明，见 20.12.2） |
| 宣称 `machine-bootstrap --verify` 通过 | 官方 Skills/Memory/Settings 三份文档均无此能力、真脚本 `bootstrap.sh` 未搬入；本生态已删该承诺，三通道就位改用 L2 三态实测 |
| 把 `docs/` 台账塞进 context | 三分离第④格，台账不常驻（20.9） |
| 复制铁律条文到新文件 | 违反 M2，留指针即可 |

---

## 总收口

6 步的依赖是串行的：**0 认环境 → 1 保同级 → 2 建 git → 3 放本体 → 4 装基座 → 5 补三通道 → 6 不做清单**。
其中 **1（同级）、2（git init）、4（装基座）** 是实测数据逼出来的必做项，不是可选；
做完直接进 `03-ACCEPTANCE.md` 跑验收，判据一律看真实退出码与三态，不看口头结论。

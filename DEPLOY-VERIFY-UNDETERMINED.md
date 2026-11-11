# codebuddy-eco 部署与验机 · 状态交接记录

性质: 人工可读状态记录（非机读产出）
说明: deploy_verify.py 与 bootstrap-kit/ 未随本消息物理送达，--check / --apply / --playbook 均未执行；schema codebuddy-eco.deploy_verify/v1 的 report.json 未生成，本文件不冒充其产出
场景: 全新沙箱 / 纯文本跨空环境（零附件实体）
门禁: 命中「没带齐就记无法判定并停下，不要编造」，未进入部署链
本轮写入: 1 份新建状态记录；既有真源 / 快照 / git 历史 / 机检零改动
生成时间: 2026/11/11 10:07:09 GMT+8

## 一、环境探测（真实退出码）

pwd -P: /workspace（退出码 0）
ls -a: . .. .codebuddy（退出码 0）
git log --oneline -1: fatal: not a git repository（退出码 128）
ls -a /root/uploads: . .. .init（退出码 0）
find /root/uploads -type f: /root/uploads/.init（退出码 0）
ls -a /root/.codebuddy/skills/eco-ledger: No such file or directory（退出码 2）
ls -aR /workspace/.codebuddy: 空目录（退出码 0）

## 二、载体在位判定（全盘只读扫描，0 命中）

deploy_verify.py: 不存在
bootstrap-kit/: 不存在
START-HERE.md: 不存在
01-DECISIONS.md: 不存在
02-COLD-START.md: 不存在
03-ACCEPTANCE.md: 不存在
CodeBuddy-会话中文风格统一-SOP.md: 不存在
codebuddy-eco/: 不存在
附件实体: 0（/root/uploads 仅 .init 占位）

## 三、执行链

1 验环境并读包: 已执行（环境三连 + 全盘只读扫描）
1 读四册: 无法判定（文件不在位，读不到）
2 --check: 未执行（执行器缺失）
3 --apply: 未执行（无 report.json，state.needs_apply 不可读）
4 --playbook: 未执行（执行器缺失）
5 L2 生效验收: 无法判定（l2_manual[] 读不到，trigger 无可触发对象）
report.json（codebuddy-eco.deploy_verify/v1）: 未产出

## 四、三态结论

真阳性:
  pwd -P /workspace（0）
  ls -a（0）
  ls -a /root/uploads（0）
  ls -aR /workspace/.codebuddy（0）
  备注: 以上仅证探测命令本身跑通，不证包自洽、不证技能/规则被宿主加载并语义触发

真阴性:
  deploy_verify.py 不存在
  bootstrap-kit/ 不存在
  START-HERE.md / 01-DECISIONS.md / 02-COLD-START.md / 03-ACCEPTANCE.md 共 4 册不存在
  CodeBuddy-会话中文风格统一-SOP.md 快照不存在
  codebuddy-eco/ 不存在
  /root/uploads 附件实体 0
  /root/.codebuddy/skills/eco-ledger 不存在（退出码 2）
  git 历史: 非仓库（退出码 128）
  /workspace/.codebuddy: 空目录

无法判定:
  report.json 的 checks[] / summary / state
  state.needs_apply
  l2_manual[] 逐项 state 与 evidence
  L1 是否全绿、「0 断链 + 退出码 0」是否成立
  L2 是否语义触发
  宿主是否加载用户级基座（~/.codebuddy/rules/）
  另一会话 / 另一沙箱 / 手机端状态: UNDETERMINED

## 五、边界（如实转述，不宣布已生效）

L1 全绿: 未观测；即便全绿只证「包自洽」，不证「技能 / 规则被宿主加载并语义触发」
已生效: 不宣布
口径分歧: 未发生（未进入可改真源阶段）；如后续发生，回 docs/registry.md 第七节、core-8.md 元规则 M6 改真源，不在副本就地打补丁
规则改动后须重启宿主: 不涉及（本轮零规则改动）；/clear 不算
token / 凭证: 未写入任何文件、提交信息、git config 或日志，未打印内容

## 六、需人工随附（仅全新沙箱场景）

deploy_verify.py: 1 份
bootstrap-kit/: 1 套（START-HERE.md、01-DECISIONS.md、02-COLD-START.md、03-ACCEPTANCE.md、CodeBuddy-会话中文风格统一-SOP.md、codebuddy-eco/）
摆放要求: SOP 必须与 codebuddy-eco/ 同级（不同级 6 处指针全断）
同环境新会话: 零附件，文件已在位，直接进第二步

## 七、附件齐备后重跑（原样引用，未另造第二套命令）

python3 deploy_verify.py --root <新项目根> --check --out report.json
python3 deploy_verify.py --root <新项目根> --apply --out report.json
python3 deploy_verify.py --playbook
备注: --root 默认当前工作目录，站在新项目根跑可省略；--apply 仅当 state.needs_apply=true 或为全新沙箱时执行；--check 严格只读
判据: 真实退出码 + 三态；引用处数 / 扫描 .md 数不写死当标准，恒为「0 断链 + 退出码 0」

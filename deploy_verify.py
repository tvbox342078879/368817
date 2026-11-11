#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codebuddy-eco · 新会话部署与验机执行器（机读 / 自包含 / 一次发送）
=====================================================================

【给新会话 AI 的指令 —— 读到本文件即照做，无需向任何其它会话求证】
你是执行侧 AI，零记忆。本文件是用户一次性发来的「部署 + 验机」机读载体。
按以下顺序执行，不要凭印象跳步：

1. 先验环境：pwd -P、ls -a、git log --oneline -1，确认自己在新项目根，别在临时目录乱改。
2. 读交接包四份：START-HERE.md → 01-DECISIONS.md → 02-COLD-START.md → 03-ACCEPTANCE.md
   （若本目录下有 bootstrap-kit/ 则读它；缺包则记「无法判定」并在报告里说明，不要编造）。
3. 先跑只读验机（不改任何文件）：
       python3 deploy_verify.py --root <新项目根> --check --out report.json
   读 report.json：checks[] 是逐条真实退出码与三态，summary 是机读汇总。
4. 需要部署时再跑（会写文件，仅这一条会改环境）：
       python3 deploy_verify.py --root <新项目根> --apply --out report.json
   --apply 做且只做：同级校验、git init + 首次提交（命令内 -c 局部身份，零配置不报 128）、
   装用户级基座到 ~/.codebuddy/rules/、幂等跳过已存在项。
5. 收尾跑 L2 生效验收：读 report.json 的 l2_manual[]，逐项用 trigger 触发，
   按三态（真阳性 / 真阴性 / 无法判定）回填 state 与 evidence；报错/超时/读不到一律「无法判定」。
   填 tri_state_report 模板，输出最终三态报告给用户。
6. 只输出机读流程定义（不执行任何动作）：
       python3 deploy_verify.py --playbook
7. 全程简体中文；token / 凭证不写进任何文件、提交信息、git config 或日志。
8. 边界：不要向原审查侧会话求证——它看不到你、不参与执行、不确认结果。
   L1 全绿只证「包自洽」，不证「技能/规则被宿主加载并语义触发」；
   另一会话/沙箱/手机端状态 = UNDETERMINED。改动规则后须重启宿主，/clear 不算。

【设计口径】
- 判据 = 真实退出码（subprocess.returncode）+ 三态，不是口头结论。
- 判据逻辑不复制：L1 直接复用生态真源机检的 --json 输出并解析合并（M2 引用不复制）。
- 引用处数 / 扫描 .md 数不写死当标准，判据恒为「0 断链 + 退出码 0」。
- --check 严格只读；只有 --apply 才写。令牌只做计数扫描、绝不打印内容。
- 输出 schema: codebuddy-eco.deploy_verify/v1（JSON，ensure_ascii=False）。
- 本文件是 /workspace 顶层独立交付物，不进 codebuddy-eco 机检扫描、不进 15 文件骨架、
  不进 bootstrap-kit 快照、不进 git 历史。
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCHEMA = "codebuddy-eco.deploy_verify/v1"
SOP_NAME = "CodeBuddy-会话中文风格统一-SOP.md"
ECO = "codebuddy-eco"
TOKEN_RE = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")

# ---------------------------------------------------------------------------
# 机读流程定义（--playbook 直接输出；执行时同源驱动，避免第二份口径）
# 每项: id / phase / title / cmd / expect / kind(read|write|manual) / tri_state_hint
# ---------------------------------------------------------------------------
PLAYBOOK = [
    {"id": "S0.pwd", "phase": "S0-env", "title": "确认真实工作目录", "cmd": "pwd -P", "expect": "输出新项目根绝对路径", "kind": "read", "tri_state_hint": "真阴性=目录不对，立即停下"},
    {"id": "S0.ls", "phase": "S0-env", "title": "列出根目录条目", "cmd": "ls -a", "expect": "见 codebuddy-eco/ 与 SOP 同级", "kind": "read", "tri_state_hint": "无法判定=看不到输出"},
    {"id": "S0.git", "phase": "S0-env", "title": "探本地历史", "cmd": "git log --oneline -1", "expect": "有提交; not a git repository 属真阴性(场景B正常)", "kind": "read", "tri_state_hint": "真阴性=尚未 init"},
    {"id": "S1.sop", "phase": "S1-samelevel", "title": "SOP 同级校验", "cmd": "test -f \"../%s\" && echo SOP_OK" % SOP_NAME, "expect": "SOP_OK", "kind": "read", "tri_state_hint": "真阴性=不同级, 6 处指针全断"},
    {"id": "S1.eco", "phase": "S1-samelevel", "title": "骨架目录校验", "cmd": "test -d %s && echo ECO_OK" % ECO, "expect": "ECO_OK", "kind": "read", "tri_state_hint": "真阴性=骨架缺失"},
    {"id": "S1.count", "phase": "S1-samelevel", "title": "受控文件数(排除 .git)", "cmd": "find %s -path %s/.git -prune -o -type f -print | wc -l" % (ECO, ECO), "expect": "15", "kind": "read", "tri_state_hint": "真阴性≠15"},
    {"id": "S2.gitinit", "phase": "S2-git", "title": "建唯一真源", "cmd": "git init && git add . && git -c user.name='eco-local' -c user.email='eco@localhost.invalid' commit -m \"eco bootstrap: import codebuddy-eco scaffold\"", "expect": "退出码 0; 零配置须带 -c 否则 128", "kind": "write", "tri_state_hint": "真阴性=commit 失败"},
    {"id": "S3.skills", "phase": "S3-assets", "title": "4 技能就位", "cmd": "find .codebuddy/skills -name SKILL.md | sort", "expect": "4 个 SKILL.md", "kind": "read", "tri_state_hint": "真阴性≠4"},
    {"id": "S3.rules", "phase": "S3-assets", "title": "规则/薄壳/MANIFEST 就位", "cmd": "ls .codebuddy/rules/ .codebuddy/CODEBUDDY.md .codebuddy/MANIFEST.json", "expect": "退出码 0", "kind": "read", "tri_state_hint": "真阴性=缺文件"},
    {"id": "S4.base", "phase": "S4-userbase", "title": "装用户级基座(唯一人工必做)", "cmd": "mkdir -p ~/.codebuddy/rules && cp base/rules/core-8.md ~/.codebuddy/rules/core-8.md && test -f ~/.codebuddy/rules/core-8.md && echo BASE_INSTALLED", "expect": "BASE_INSTALLED", "kind": "write", "tri_state_hint": "沙箱 ~/.codebuddy ≠ 真机"},
    {"id": "S5.channel", "phase": "S5-threechannel", "title": "手机三通道 + 重启宿主", "cmd": "(人工动作, 文件带不过去)", "expect": "设置→给 WorkBuddy 的指令粘 8 铁律; 规则改动后重启", "kind": "manual", "tri_state_hint": "没做→无法判定"},
    {"id": "L0.files", "phase": "L0-integrity", "title": "L0 受控文件数", "cmd": "find . -path ./.git -prune -o -type f -print | wc -l", "expect": "15", "kind": "read", "tri_state_hint": "真阴性≠15"},
    {"id": "L0.sop", "phase": "L0-integrity", "title": "L0 SOP 同级", "cmd": "test -f \"../%s\" && echo SOP_SAME_LEVEL" % SOP_NAME, "expect": "SOP_SAME_LEVEL", "kind": "read", "tri_state_hint": "真阴性=不同级"},
    {"id": "L0.pyc", "phase": "L0-integrity", "title": "L0 无 pyc 残留", "cmd": "find . -name __pycache__ -type d | wc -l", "expect": "0", "kind": "read", "tri_state_hint": "真阴性≠0"},
    {"id": "L1.default", "phase": "L1-machinecheck", "title": "机检 默认", "cmd": "python3 -B verify/terminology_check.py", "expect": "退出码 0", "kind": "read", "tri_state_hint": "真阴性≠0"},
    {"id": "L1.strict", "phase": "L1-machinecheck", "title": "机检 --strict", "cmd": "python3 -B verify/terminology_check.py --strict", "expect": "退出码 0", "kind": "read", "tri_state_hint": "真阴性≠0"},
    {"id": "L1.sop", "phase": "L1-machinecheck", "title": "机检 --sop", "cmd": "python3 -B verify/terminology_check.py --sop \"../%s\"" % SOP_NAME, "expect": "退出码 0; 0 断链", "kind": "read", "tri_state_hint": "真阴性=断链"},
    {"id": "L1.json", "phase": "L1-machinecheck", "title": "机检 --json(机读)", "cmd": "python3 -B verify/terminology_check.py --json --strict --sop \"../%s\"" % SOP_NAME, "expect": "ok=True exit_code=0", "kind": "read", "tri_state_hint": "解析合并进报告"},
    {"id": "L1.manifest", "phase": "L1-machinecheck", "title": "MANIFEST JSON 合法", "cmd": "python3 -c \"import json;json.load(open('.codebuddy/MANIFEST.json'))\"", "expect": "退出码 0", "kind": "read", "tri_state_hint": "真阴性≠0"},
    {"id": "L2.manual", "phase": "L2-effective", "title": "L2 生效验收", "cmd": "(新会话 AI 按 l2_manual[] 逐项触发)", "expect": "三态回填", "kind": "manual", "tri_state_hint": "默认无法判定, 不伪造"},
]

L2_MANUAL = [
    {"id": "L2.zh", "trigger": "用中文提一个简单问题", "true_positive": "全程简体中文", "true_negative": "出现成段英文", "undetermined": "读不到回复 / 环境异常", "state": "无法判定", "evidence": ""},
    {"id": "L2.base", "trigger": "提一个涉及「命令输出怎么判」的问题", "true_positive": "按三态回答", "true_negative": "答成「没查到=没有」", "undetermined": "无法确认加载", "state": "无法判定", "evidence": ""},
    {"id": "L2.skill", "trigger": "说「这个错反复出现，沉淀成技能」", "true_positive": "skill-evolution 被识别", "true_negative": "完全无反应", "undetermined": "不确定是否触发", "state": "无法判定", "evidence": ""},
    {"id": "L2.cond", "trigger": "编辑 docs/x.md 看 docs.paths.md 是否注入; 编辑非 docs 文件看是否不注入", "true_positive": "命中才注入", "true_negative": "常驻乱注入", "undetermined": "观察不到注入", "state": "无法判定", "evidence": ""},
    {"id": "L2.shell", "trigger": "一次中文提问看薄壳是否被读到", "true_positive": "三不可协商 + 5 铁律有体现", "true_negative": "完全无体现", "undetermined": "读不到", "state": "无法判定", "evidence": ""},
    {"id": "L2.mobile", "trigger": "手机 App 里同样提问", "true_positive": "与桌面一致", "true_negative": "手机端失效", "undetermined": "未在手机验证", "state": "无法判定", "evidence": ""},
]

BOUNDARIES = {
    "另一沙箱 / 另一会话 / 手机端生效": "无法判定",
    "技能文件改动是否需重启": "无法判定（官方 Skills 文档未明说，不类推 Memory 口径）",
    "手机端「给 WorkBuddy 的指令」是否设置": "无法判定（人工动作，文件带不过去）",
    "规则是否被宿主加载并语义触发": "无法判定（需新会话 L2 实测）",
    "审查侧是否参与执行 / 确认结果": "否（不联动、看不到对面）",
    "L1 全绿能证明什么": "仅「包自洽」= 结构 / 规范 / 机检；不证明生效",
}

TRI_STATE_REPORT = {
    "项: 场景": "A（同环境新会话）/ B（全新沙箱）",
    "项: L0 文件数": "？",
    "项: L0 SOP同级": "？",
    "项: L1 默认/strict/含SOP/json/MANIFEST 退出码": "？/？/？/？/？",
    "项: L1 汇总": "PASS ？/ WARN ？/ FAIL ？",
    "项: L2 全程中文": "真阳性 / 真阴性 / 无法判定",
    "项: L2 基座加载": "真阳性 / 真阴性 / 无法判定",
    "项: L2 技能触发": "真阳性 / 真阴性 / 无法判定",
    "项: L2 条件规则命中": "真阳性 / 真阴性 / 无法判定",
    "项: L2 手机端生效": "真阳性 / 真阴性 / 无法判定",
    "项: 总判定": "全部真阳性且 L1 全 0 → 通过；否则记「无法判定」并附原因",
}


def run(cmd, cwd):
    """逐条执行、取真实退出码；不遮蔽 stderr，不吞异常。"""
    try:
        p = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True,
                           text=True, timeout=120)
        return {"exit_code": p.returncode,
                "stdout": (p.stdout or "").strip(),
                "stderr": (p.stderr or "").strip()[:400]}
    except subprocess.TimeoutExpired:
        return {"exit_code": None, "stdout": "", "stderr": "TIMEOUT(120s)"}
    except Exception as e:  # noqa: BLE001
        return {"exit_code": None, "stdout": "", "stderr": "ERROR: %s" % type(e).__name__}


def tri(rc, ok_value=0):
    if rc is None:
        return "无法判定"
    return "真阳性" if rc == ok_value else "真阴性"


def scan_tokens(root):
    """只计数、绝不打印命中内容。"""
    hits = 0
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for fn in files:
            if not fn.endswith((".md", ".py", ".json", ".sh", ".html")):
                continue
            try:
                txt = Path(base, fn).read_text(encoding="utf-8", errors="ignore")
                hits += len(TOKEN_RE.findall(txt))
            except OSError:
                pass
    return hits


def detect_state(root, eco, home):
    """结构化机读前置状态；label 由布尔组合推出，不臆测。"""
    has_eco = eco.is_dir()
    has_sop = (root / SOP_NAME).is_file()
    has_git = (run("git rev-list --count HEAD", eco)["exit_code"] == 0) if has_eco else False
    has_base = (home / ".codebuddy" / "rules" / "core-8.md").is_file()
    # 精确列举缺项，不用「A / B / C」笼统并列造成机读误判
    missing_deployable = [n for n, ok in (("git 历史", has_git), ("用户级基座", has_base)) if not ok]
    missing_manual = [n for n, ok in (("SOP 同级", has_sop),) if not ok]
    if not has_eco:
        label = "UNDETERMINED-缺骨架（需先从 bootstrap-kit 搬运，或 --root 指错）"
        needs_apply = False  # 搬运动作脚本不代做
    elif not missing_deployable and not missing_manual:
        label = "A-已就位（同环境新会话，纯验机 + L2）"
        needs_apply = False
    else:
        label = "B-待部署（缺：%s，需 --apply）" % "、".join(missing_deployable + missing_manual)
        needs_apply = bool(missing_deployable)
    return {"label": label, "has_eco": has_eco, "has_sop_same_level": has_sop,
            "has_git_history": has_git, "has_user_base": has_base,
            "missing_deployable": missing_deployable, "missing_manual": missing_manual,
            "needs_apply": needs_apply,
            "note": "手机三通道 / 重启宿主 / L2 生效恒为人工或新会话侧，脚本不代做"}


def main():
    ap = argparse.ArgumentParser(description="codebuddy-eco 新会话部署与验机（机读）")
    ap.add_argument("--root", default=None, help="新项目根（默认当前工作目录）")
    ap.add_argument("--apply", action="store_true", help="执行写动作（git init / 装基座）")
    ap.add_argument("--check", action="store_true", help="只读验机（默认，不写任何环境文件）")
    ap.add_argument("--playbook", action="store_true", help="只输出机读流程定义 JSON")
    ap.add_argument("--out", default=None, help="报告写入路径；不给则输出 stdout")
    args = ap.parse_args()

    if args.playbook:
        payload = {"schema": SCHEMA + "/playbook",
                   "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                   "note": "机读流程定义；不执行任何动作。每项 cmd 可直接照抄，判据看真实退出码 + 三态。",
                   "step_count": len(PLAYBOOK), "steps": PLAYBOOK,
                   "l2_manual": L2_MANUAL, "boundaries": BOUNDARIES}
        out = json.dumps(payload, ensure_ascii=False, indent=2)
        print(out)
        return 0

    root = Path(args.root).resolve() if args.root else Path.cwd().resolve()
    eco = root / ECO
    home = Path(os.path.expanduser("~"))
    mode = "apply" if args.apply else "check"

    state = detect_state(root, eco, home)
    report = {
        "schema": SCHEMA,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "root": str(root),
        "mode": mode,
        "scenario": state["label"],
        "state": state,
        "sop_same_level_hint": "SOP 须与 codebuddy-eco/ 同级",
        "checks": [],
        "actions": [],
        "pending_actions": [],
        "machine_check": {},
        "token_hits": 0,
        "l2_manual": json.loads(json.dumps(L2_MANUAL, ensure_ascii=False)),
        "boundaries": BOUNDARIES,
        "tri_state_report_template": TRI_STATE_REPORT,
    }

    # --- S0 / S1 / S3 / L0 / L1 只读检查（cwd = eco；缺骨架时降级） ---
    cwd = eco if eco.is_dir() else root
    read_ids = ["S0.pwd", "S0.ls", "S0.git", "S1.sop", "S1.eco", "S1.count",
                "S3.skills", "S3.rules", "L0.files", "L0.sop", "L0.pyc",
                "L1.default", "L1.strict", "L1.sop", "L1.json", "L1.manifest"]
    pb = {s["id"]: s for s in PLAYBOOK}

    # 精确指定工作目录：同级校验用 root 相对路径；`../SOP` 类必须在 eco 下跑
    ROOT_IDS = {"S0.pwd", "S0.ls", "S0.git", "S1.eco", "S1.count"}
    # 环境探测项：S0.git 在场景 B 返回 128 属预期真阴性，不计入门禁失败
    PROBE_IDS = {"S0.pwd", "S0.ls", "S0.git"}

    if not eco.is_dir():
        report["checks"].append({"id": "S1.eco", "phase": "S1-samelevel",
                                 "cmd": pb["S1.eco"]["cmd"], "exit_code": None,
                                 "stdout": "", "state": "真阴性",
                                 "note": "骨架目录不在位；需先从 bootstrap-kit 搬运，或 --root 指错"})
    else:
        for sid in read_ids:
            s = pb[sid]
            q = root if sid in ROOT_IDS else eco
            r = run(s["cmd"], q)
            item = {"id": sid, "phase": s["phase"], "title": s["title"],
                    "cmd": s["cmd"], "exit_code": r["exit_code"],
                    "stdout": r["stdout"][:300], "stderr": r["stderr"],
                    "state": tri(r["exit_code"]),
                    "expect": s["expect"], "tri_state_hint": s["tri_state_hint"]}
            # 计数类判据：stdout 数字需等于期望
            if sid in ("S1.count", "L0.files", "L0.pyc", "S3.skills"):
                want = "4" if sid == "S3.skills" else ("0" if sid == "L0.pyc" else "15")
                got = r["stdout"].splitlines()[-1].strip() if r["stdout"] else ""
                if sid == "S3.skills":
                    got = str(len([x for x in r["stdout"].splitlines() if x.strip()]))
                item["parsed"] = got
                item["state"] = ("真阳性" if r["exit_code"] == 0 and got == want
                                 else ("无法判定" if r["exit_code"] is None else "真阴性"))
            report["checks"].append(item)

            # L1.json 的 --json 输出直接解析合并（判据逻辑复用真源，不复制）
            if sid == "L1.json" and r["exit_code"] == 0 and r["stdout"]:
                try:
                    mc = json.loads(r["stdout"])
                    report["machine_check"] = {
                        "source": "verify/terminology_check.py --json",
                        "schema": mc.get("schema"),
                        "summary": mc.get("summary"),
                        "check_count": mc.get("check_count"),
                        "checks": [{"name": c.get("name"), "status": c.get("status")}
                                   for c in mc.get("checks", [])],
                        "scanned_md_files": mc.get("scanned_md_files"),
                        "section_refs_total": mc.get("section_refs_total"),
                        "section_refs_broken": mc.get("section_refs_broken"),
                        "strict": mc.get("strict"), "sop_attached": mc.get("sop_attached"),
                        "exit_code": mc.get("exit_code"),
                    }
                except (ValueError, TypeError):
                    report["machine_check"] = {"parse": "无法判定", "raw_head": r["stdout"][:200]}

    # --- 写动作：--apply 才执行；--check 只列 pending ---
    write_ids = ["S2.gitinit", "S4.base"]
    for sid in write_ids:
        s = pb[sid]
        cmd = s["cmd"]
        cwd_w = eco
        if not args.apply or not eco.is_dir():
            report["pending_actions"].append({
                "id": sid, "title": s["title"], "cmd": cmd,
                "status": "未执行",
                "reason": "--check 只读模式" if not args.apply else "骨架不在位",
                "state": "无法判定"})
            continue
        # 幂等：git 已有提交则跳过 S2；基座已装则跳过 S4
        if sid == "S2.gitinit" and run("git rev-parse --is-inside-work-tree", eco)["exit_code"] == 0 \
                and run("git rev-list --count HEAD", eco)["exit_code"] == 0:
            report["actions"].append({"id": sid, "cmd": cmd, "status": "skipped-幂等",
                                      "exit_code": 0, "state": "真阳性",
                                      "note": "已有本地提交，跳过 init/commit"})
            continue
        if sid == "S4.base" and (home / ".codebuddy" / "rules" / "core-8.md").is_file():
            report["actions"].append({"id": sid, "cmd": cmd, "status": "skipped-幂等",
                                      "exit_code": 0, "state": "真阳性",
                                      "note": "基座已在位，跳过 cp"})
            continue
        r = run(cmd, cwd_w)
        report["actions"].append({"id": sid, "cmd": cmd, "status": "applied",
                                  "exit_code": r["exit_code"], "stdout": r["stdout"][:200],
                                  "stderr": r["stderr"], "state": tri(r["exit_code"])})

    # --- 人工动作（永远不自动执行） ---
    report["actions"].append({"id": "S5.channel", "title": "手机三通道 + 重启宿主",
                              "status": "人工", "state": "无法判定",
                              "note": "文件带不过去；规则改动后须重启，/clear 不算"})

    # state 为执行前快照；--apply 后重新探测一次，避免机读侧把 needs_apply 误读成"还要再跑"
    report["state_note"] = "state = 执行前快照；state_after = --apply 完成后复测；两者都只反映可自动探测项"
    if args.apply:
        report["state_after"] = detect_state(root, eco, home)

    # --- 令牌零明文（只计数） ---
    report["token_hits"] = scan_tokens(root)

    # --- 机读汇总 ---
    checks = report["checks"]
    rc_all = [c["exit_code"] for c in checks if c["id"].startswith("L1.")]
    l1_all_zero = len(rc_all) == 5 and all(x == 0 for x in rc_all)
    # 全量按 state 计数（三项之和恒等于 checks_total，机读自洽）
    tp = sum(1 for c in checks if c["state"] == "真阳性")
    tn = sum(1 for c in checks if c["state"] == "真阴性")
    und = sum(1 for c in checks if c["state"] == "无法判定")
    tn_ids = [c["id"] for c in checks if c["state"] == "真阴性"]
    # 预期真阴性：S0.git 在场景 B「不是 git 仓库」属正常，不算门禁失败
    expected_tn = {"S0.pwd", "S0.ls", "S0.git"}
    gate_fail = [i for i in tn_ids if i not in expected_tn]
    mc = report["machine_check"]
    report["summary"] = {
        "checks_total": len(checks),
        "checks_true_positive": tp,
        "checks_true_negative": tn,
        "checks_undetermined": und,
        "state_counts_consistent": (tp + tn + und == len(checks)),
        "true_negative_ids": tn_ids,
        "expected_true_negative_ids": [i for i in tn_ids if i in expected_tn],
        "gate_failure_ids": gate_fail,
        "l1_exit_codes": rc_all,
        "l1_all_zero": l1_all_zero,
        "machine_check_ok": mc.get("summary", {}).get("ok") if isinstance(mc.get("summary"), dict) else None,
        "machine_check_pass_warn_fail": [mc.get("summary", {}).get(k) for k in ("pass", "warn", "fail")] if isinstance(mc.get("summary"), dict) else None,
        "section_refs_broken": mc.get("section_refs_broken"),
        "token_hits": report["token_hits"],
        "auto_layer_conclusion": ("真阳性（包自洽：结构/规范/机检）" if (l1_all_zero and not gate_fail)
                                  else ("真阴性（存在门禁失败项，见 gate_failure_ids）" if gate_fail else "无法判定")),
        "effective_layer_conclusion": "无法判定（需新会话按 l2_manual[] 三态实测，本执行器不伪造）",
        "next_actions": [
            "读 state.needs_apply：为 true 时先跑 --apply 补 git 历史与用户级基座",
            "读 l2_manual[]，逐项用 trigger 触发，按三态回填 state 与 evidence",
            "填 tri_state_report_template，输出最终三态报告",
            "不要把「无法判定」写成「真阳性」；不要向原审查侧会话求证",
            "若 auto_layer_conclusion 为真阴性，回 docs/registry.md 查真源（M6），不在副本打补丁",
        ],
    }

    out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(out + "\n", encoding="utf-8")
        # 机读摘要到 stdout，便于管道消费
        print(json.dumps({"schema": SCHEMA, "report_path": str(Path(args.out).resolve()),
                          "mode": mode, "scenario": report["scenario"],
                          "auto_layer_conclusion": report["summary"]["auto_layer_conclusion"],
                          "l1_all_zero": l1_all_zero,
                          "token_hits": report["token_hits"]}, ensure_ascii=False))
    else:
        print(out)
    return 0 if report["summary"]["auto_layer_conclusion"].startswith("真阳性") else 1


if __name__ == "__main__":
    sys.exit(main())

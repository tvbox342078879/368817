#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
口径统一性机检（元规则 M5）——只读，不写任何文件。

配置唯一真源：docs/registry.md 第七节 ```json 机读区。
本脚本不内置第二份词表/编号/清单/技能契约，避免"检查器自己制造口径冗余"。

用法（在 codebuddy-eco 仓库根）:
    python3 verify/terminology_check.py
    python3 verify/terminology_check.py --strict
    python3 verify/terminology_check.py --sop ../CodeBuddy-会话中文风格统一-SOP.md
    python3 verify/terminology_check.py --json            # 机器可读输出（供面板读取真源产物）
    python3 verify/terminology_check.py --json --strict --sop ../...   # 可组合

退出码: 0=通过(允许 WARN)；1=存在 FAIL（--strict 时 WARN 也计 FAIL）。
--json 只切换输出格式，检查项、判据、退出码语义均不变（SOP 20.13.2）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # codebuddy-eco/
REGISTRY = ROOT / "docs" / "registry.md"
MANIFEST = ROOT / ".codebuddy" / "MANIFEST.json"
CORE8 = "base/rules/core-8.md"

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
results = []
META = {}   # --json 输出的扫描元数据（只读收集，不写文件、不引入事件流；SOP 20.13.2）


def add(level, item, detail=""):
    results.append((level, item, detail))


def load_config():
    text = REGISTRY.read_text(encoding="utf-8")
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        add(FAIL, "机读真源区", "registry.md 第七节未找到 ```json 代码块")
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        add(FAIL, "机读真源区", "JSON 解析失败: %s" % e)
        return None


def md_files(extra_sop=None):
    files = sorted(ROOT.rglob("*.md"))
    if extra_sop:
        p = Path(extra_sop)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        if p.exists():
            files.append(p)
        else:
            add(WARN, "--sop 文件", "未找到: %s" % p)
    return files


def strip_code_fences(text):
    """去掉 ``` 代码块（registry 机读区/示例代码不应被当作正文误用或复制）。"""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def check_required_files(cfg):
    missing = [f for f in cfg["required_files"] if not (ROOT / f).exists()]
    checked = len(cfg["required_files"])
    if missing:
        add(FAIL, "① 真源登记表文件齐备", "%d/%d，缺失: %s" % (checked - len(missing), checked, ", ".join(missing)))
    else:
        add(PASS, "① 真源登记表文件齐备", "%d/%d 全部存在" % (checked, checked))


def check_manifest():
    try:
        d = json.loads(MANIFEST.read_text(encoding="utf-8"))
        add(PASS, "⑥ MANIFEST.json 合法", "rules 段 %d 格" % len(d.get("rules", {})))
    except Exception as e:
        add(FAIL, "⑥ MANIFEST.json 合法", str(e))


def check_vocab(cfg, files):
    """② 受控词表跨层误用。排除 registry.md 自身（它是定义这些禁用示例的地方）。"""
    pairs = [(bad, why) for bad, why in cfg["vocab_pairs"]]
    hits = []
    for f in files:
        if f.name == "registry.md":
            continue
        body = strip_code_fences(f.read_text(encoding="utf-8", errors="ignore"))
        for bad, why in pairs:
            if bad in body:
                hits.append("%s: 「%s」(%s)" % (f.relative_to(ROOT) if ROOT in f.parents else f.name, bad, why))
    if hits:
        add(WARN, "② 受控词表跨层误用", "%d 处: %s" % (len(hits), " | ".join(hits[:6])))
    else:
        add(PASS, "② 受控词表跨层误用", "扫描 %d 个 .md，0 处误用" % len(files))


def check_ids(cfg, files):
    """③ 编号命名空间：B-xx 不得越界/未登记，8 条不得跳号。"""
    allowed = set(cfg["base_rule_ids"])
    seen, out_of_range = set(), []
    for f in files:
        if f.name == "registry.md":
            continue
        body = strip_code_fences(f.read_text(encoding="utf-8", errors="ignore"))
        for bid in re.findall(r"B-\d{2}", body):
            seen.add(bid)
            if bid not in allowed:
                out_of_range.append("%s: %s" % (f.name, bid))
    missing = sorted(allowed - seen)
    if out_of_range:
        add(FAIL, "③ 编号命名空间", "越界/未登记: %s" % ", ".join(out_of_range[:8]))
    elif missing:
        add(WARN, "③ 编号命名空间", "8 条中有 %d 个未在正文出现: %s" % (len(missing), ", ".join(missing)))
    else:
        add(PASS, "③ 编号命名空间", "B-01..B-08 共 8 个，无越界/无跳号")


def check_section_refs(cfg, files):
    """④ §/20.x 章节引用断链。范围写法 §1–7 的右端也纳入校验。"""
    allowed = set(cfg["zh_style_sections"])
    sop_l2 = {s for s in cfg["sop_sections"] if re.fullmatch(r"20\.\d+", s)}
    bad, total = [], 0
    for f in files:
        body = strip_code_fences(f.read_text(encoding="utf-8", errors="ignore"))
        toks = re.findall(r"§\s*(\d+(?:\.\d+)?)", body)
        # 范围右端（§1–7 / §8.1–8.4）补入校验
        for _a, b in re.findall(r"§\s*(\d+(?:\.\d+)?)\s*[–—\-~]\s*(\d+(?:\.\d+)?)", body):
            toks.append(b)
        for t in toks:
            total += 1
            if t not in allowed:
                bad.append("%s: §%s" % (f.name, t))
        # SOP 20.x(.y) 引用：一级/二级须在 sop_sections，三级 y 任意
        for s in re.findall(r"(?<![\d.])20\.\d+(?:\.\d+)?", body):
            total += 1
            parts = s.split(".")
            key = ".".join(parts[:2])
            if key not in sop_l2:
                bad.append("%s: %s" % (f.name, s))
    META["section_refs_total"] = total
    META["section_refs_broken"] = len(bad)
    if bad:
        add(WARN, "④ 章节引用断链", "%d/%d 处未解析: %s" % (len(bad), total, " | ".join(bad[:8])))
    else:
        add(PASS, "④ 章节引用断链", "扫描 %d 处 §/20.x 引用，0 断链" % total)


def check_fingerprints(cfg, files):
    """⑤ M2 引用不复制：非真源/非豁免文件不得出现 8 条铁律的正文指纹。"""
    exempt = set(cfg.get("fingerprint_exempt_files", []))
    fps = cfg["rule_fingerprints"]
    hits = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix() if ROOT in f.parents else f.name
        if rel == CORE8 or rel == "docs/registry.md" or rel in exempt:
            continue
        body = strip_code_fences(f.read_text(encoding="utf-8", errors="ignore"))
        for fp in fps:
            if fp in body:
                hits.append("%s: 「%s」" % (rel, fp))
    if hits:
        add(WARN, "⑤ 铁律正文被复制(M2)", "%d 处（应改为指针）: %s" % (len(hits), " | ".join(hits[:6])))
    else:
        add(PASS, "⑤ 铁律正文被复制(M2)", "非真源文件 0 处复制；薄壳内联为 M7 已登记例外")


def check_skill_contract(cfg):
    """⑦ 技能契约（SOP 20.12）：frontmatter 合规 / description 按官方口径 / 触发词归属正文 / 继承指针一致 / 短名三处对齐。

    配置全部来自 registry 第七节 skill_contract，本函数不硬编码第二份清单。
    """
    sc = cfg.get("skill_contract")
    if not sc:
        add(WARN, "⑦ 技能契约", "registry 第七节缺 skill_contract 机读配置")
        return
    problems = []
    skill_files = sc["skill_files"]

    for rel in skill_files:
        p = ROOT / rel
        if not p.exists():
            problems.append("%s 缺失" % rel)
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        # frontmatter：取首个 --- ... --- 区块
        fm_match = re.search(r"\A---\s*\n(.*?)\n---", text, re.S)
        fm = fm_match.group(1) if fm_match else ""
        name = rel.split("/")[-2]

        # (1) 必备/禁用 frontmatter 字段
        for k in sc["required_frontmatter"]:
            if not re.search(r"^%s\s*:" % re.escape(k), fm, re.M):
                problems.append("%s: 缺 %s" % (name, k))
        for k in sc["forbidden_frontmatter"]:
            if re.search(r"^%s\s*:" % re.escape(k), fm, re.M):
                problems.append("%s: 含禁用字段 %s" % (name, k))

        # (2) description 按官方口径：不堆 / 触发词、不含"当用户说/时使用"
        dmatch = re.search(r"^description\s*:\s*(.+)$", fm, re.M)
        if not dmatch:
            problems.append("%s: 缺 description" % name)
        else:
            desc = dmatch.group(1)
            for bad in sc["description_forbid_substrings"]:
                if bad in desc:
                    problems.append("%s: description 含触发词堆砌「%s」" % (name, bad))
            if desc.count("/") > sc["description_max_slashes"]:
                problems.append("%s: description 含 %d 个 /（触发词清单）" % (name, desc.count("/")))

        # (3) 触发词唯一真源在正文、不在 description
        body = text[fm_match.end():] if fm_match else text
        if sc["trigger_source_marker"] not in body:
            problems.append("%s: 正文缺触发词唯一真源标记" % name)

        # (4) 继承指针逐字一致（4 份）
        if sc["inherit_pointer_text"] not in body:
            problems.append("%s: 继承指针缺失/不一致" % name)

        # (5) 私有仓库名不得硬编码进运行时契约
        for bad in sc["forbid_repo_name_in_skill_files"]:
            if bad in body:
                problems.append("%s: 硬编码私有仓库名 %s" % (name, bad))

    # (6) canonical_short 一句话短名在三个入口文件严格对齐
    presidents = {}
    for rel in sc["short_presence_files"]:
        p = ROOT / rel
        presidents[rel] = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
    for name, short in sc["canonical_short"].items():
        for rel, content in presidents.items():
            if short not in content:
                problems.append("短名「%s」未在 %s 对齐" % (short, rel))

    if problems:
        add(FAIL, "⑦ 技能契约", "%d 处: %s" % (len(problems), " | ".join(problems[:8])))
    else:
        add(PASS, "⑦ 技能契约", "%d 技能 frontmatter/description/触发词/指针合规，%d 短名 × %d 入口对齐"
            % (len(skill_files), len(sc["canonical_short"]), len(sc["short_presence_files"])))


def check_rule_contract(cfg):
    """⑧ 规则契约（SOP 20.12.2）：按官方 Memory 文档「规则控制字段」表校验 .codebuddy/rules/*.md。

    官方字段表只有 enabled / alwaysApply / paths 三项；description 为人读元数据。
    alwaysApply:false 且无 paths 时，官方判定「不支持，规则不会加载」。
    配置全部来自 registry 第七节 rule_contract，本函数不硬编码第二份清单。
    """
    rc = cfg.get("rule_contract")
    if not rc:
        add(WARN, "⑧ 规则契约", "registry 第七节缺 rule_contract 机读配置")
        return
    problems = []
    official = set(rc["official_control_fields"])
    metadata = set(rc.get("metadata_fields", []))
    allowed = official | metadata
    banned = set(rc.get("banned_control_fields", []))

    for rel in rc["rule_files"]:
        p = ROOT / rel
        if not p.exists():
            problems.append("%s 缺失" % rel)
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm_match = re.search(r"\A---\s*\n(.*?)\n---", text, re.S)
        if not fm_match:
            problems.append("%s: 缺 frontmatter 区块" % rel)
            continue
        fm = fm_match.group(1)
        keys = re.findall(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:", fm, re.M)
        for k in keys:
            if k in banned:
                problems.append("%s: 非官方控制字段 %s" % (rel, k))
            elif k not in allowed:
                problems.append("%s: 未登记字段 %s" % (rel, k))
        aa = re.search(r"^alwaysApply\s*:\s*(\S+)", fm, re.M)
        has_paths = re.search(r"^paths\s*:", fm, re.M) is not None
        if rc.get("require_paths_when_always_false") and aa and aa.group(1).strip().lower() == "false" and not has_paths:
            problems.append("%s: alwaysApply:false 缺 paths（官方判定不加载）" % rel)

    if problems:
        add(FAIL, "⑧ 规则契约", "%d 处: %s" % (len(problems), " | ".join(problems[:8])))
    else:
        add(PASS, "⑧ 规则契约", "%d 规则 frontmatter 符合官方三控制字段 + 元数据，无 priority/无悬空条件规则"
            % len(rc["rule_files"]))


def main():
    ap = argparse.ArgumentParser(description="口径统一性机检（只读）")
    ap.add_argument("--strict", action="store_true", help="WARN 也计为 FAIL")
    ap.add_argument("--sop", default=None, help="附带校验的 SOP 路径")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="输出机器可读 JSON（供面板读取真源产物）；检查项/判据/退出码不变")
    args = ap.parse_args()

    META["strict"] = args.strict
    META["sop_attached"] = bool(args.sop)
    if not args.as_json:
        print("=== 口径统一性机检 (registry 第七节为唯一配置源) ===")
    cfg = load_config()
    if cfg is None:
        _report(args.strict, args.as_json)
        return
    files = md_files(args.sop)
    META["scanned_md_files"] = len(files)
    if not args.as_json:
        print("扫描范围: %d 个 .md%s\n" % (len(files), "（含 SOP）" if args.sop else ""))

    check_required_files(cfg)
    check_manifest()
    check_vocab(cfg, files)
    check_ids(cfg, files)
    check_section_refs(cfg, files)
    check_fingerprints(cfg, files)
    check_skill_contract(cfg)
    check_rule_contract(cfg)
    _report(args.strict, args.as_json)


def _report(strict, as_json=False):
    n_fail = sum(1 for r in results if r[0] == FAIL)
    n_warn = sum(1 for r in results if r[0] == WARN)
    n_pass = sum(1 for r in results if r[0] == PASS)
    effective_fail = n_fail + (n_warn if strict else 0)
    ok = effective_fail == 0
    exit_code = 0 if ok else 1

    if as_json:
        payload = {
            "schema": "codebuddy-eco/verify/v1",
            "snapshot_only": True,
            "note": "拉取式只读快照，非实时联动、无事件流；面板只呈现已发生事实，不预测进度",
            "config_source": "docs/registry.md 第七节机读真源区",
            "strict": strict,
            "sop_attached": META.get("sop_attached", False),
            "scanned_md_files": META.get("scanned_md_files", 0),
            "section_refs_total": META.get("section_refs_total", 0),
            "section_refs_broken": META.get("section_refs_broken", 0),
            "summary": {"pass": n_pass, "warn": n_warn, "fail": n_fail,
                        "effective_fail": effective_fail, "ok": ok},
            "check_count": len(results),
            "exit_code": exit_code,
            "checks": [{"level": lv, "item": item, "detail": detail}
                       for lv, item, detail in results],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        sys.exit(exit_code)

    # 文本模式：逐字保持原输出，判据与退出码不变
    for lv, item, detail in results:
        mark = {PASS: "[PASS]", WARN: "[WARN]", FAIL: "[FAIL]"}[lv]
        print("%s %s — %s" % (mark, item, detail))
    print("\n汇总: PASS=%d  WARN=%d  FAIL=%d%s" % (n_pass, n_warn, n_fail, "  (--strict: WARN 计 FAIL)" if strict else ""))
    print("结论: %s" % ("通过" if ok else "未通过"))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

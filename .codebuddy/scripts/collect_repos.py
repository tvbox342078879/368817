#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_repos.py —— 拉取你搜集的各配置仓库（壳+配置源），抽取 sites/lives 源地址。
把仓库登记在下方 REPOS 字典里即可；克隆失败不影响其他仓库。
"""
import os
import json
import glob
import subprocess

# ===== 在这里登记你搜集的配置仓库 =====
REPOS = {
    "repoA": "https://github.com/xxx/tvbox-repoA",
    "repoB": "https://github.com/yyy/tvbox-repoB",
    # "repoC": "https://github.com/zzz/tvbox-repoC",
}
# =====================================
BASE = os.path.expanduser("~/tvbox_repos")


def pull(name: str, url: str) -> str:
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        subprocess.run(["git", "-C", p, "pull", "--ff-only"],
                       check=False, capture_output=True)
    else:
        os.makedirs(BASE, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", url, p],
                       check=False, capture_output=True)
    return p


def main():
    urls = []
    for name, url in REPOS.items():
        p = pull(name, url)
        for f in glob.glob(os.path.join(p, "**", "*.json"), recursive=True):
            try:
                cfg = json.load(open(f, encoding="utf-8"))
            except Exception:
                continue
            for s in cfg.get("sites", []):
                u = s.get("api") or s.get("url")
                if u:
                    urls.append(u)
            for l in cfg.get("lives", []):
                if l.get("url"):
                    urls.append(l["url"])

    urls = sorted(set(urls))
    with open("sources.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=2)
    print(f"抽取源 {len(urls)}  → sources.json")


if __name__ == "__main__":
    main()

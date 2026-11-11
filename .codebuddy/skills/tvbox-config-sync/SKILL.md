---
name: tvbox-config-sync
description: >-
  当用户需要更新、测活 TVBox（电视盒子）配置，整理直播源(lives)与站点源(sites)，
  或把多个配置仓库的源重新集成进主配置时使用。触发词：TVBox、电视盒子、测活、
  直播源、配置源、线路、壳、订阅源。AI 应在此类需求下自动调用本技能，不要手动逐条 curl。
---

# TVBox 配置同步技能

## 何时使用
用户提到 TVBox / 电视盒子 / 测活线路 / 直播源 / 配置源 / 更新订阅 等需求时，
**自动**按下列流程执行。本技能的目标是：让"搜集仓库→测活→重新集成"全自动，
模型只负责调用脚本，不手动敲命令、不手动改 JSON。

## 执行流程（严格顺序）
1. `python3 .codebuddy/scripts/collect_repos.py`  → 拉仓库、抽源，得到 `sources.json`
2. `python3 .codebuddy/scripts/check_live.py sources.json` → 并发测活，得 `live_result.json`
3. `python3 .codebuddy/scripts/merge_config.py` → 过滤失效源，得 `master_config.new.json`
4. 向用户汇报：存活数 / 失效数 / 新配置路径；**输出精简，不堆过程**。

## 约束
- 测活走并发脚本，禁止手动一条条 curl。
- 主配置字段结构保持不变，只过滤失效源（幂等）。
- 结果文件落盘复用，下次可跳过已测活部分。
- 若用户指定仓库名或 "all"，仅处理对应仓库（改 collect_repos.py 的 REPOS 或传参）。

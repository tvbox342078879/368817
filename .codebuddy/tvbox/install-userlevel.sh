#!/usr/bin/env bash
# ===== 把本项目的 TVBox 能力装到【用户级】，所有项目会话自动可用 =====
# 用法：bash .codebuddy/tvbox/install-userlevel.sh
set -e

DST="$HOME/.codebuddy"
SRC="$(cd "$(dirname "$0")/.." && pwd)"   # 项目内 .codebuddy 目录

mkdir -p "$DST/skills" "$DST/agents" "$DST/commands" "$DST/scripts"

cp -r "$SRC/skills/tvbox-config-sync" "$DST/skills/"
cp    "$SRC/agents/tvbox-agent.md"    "$DST/agents/"
cp    "$SRC/commands/tvbox-sync.md"   "$DST/commands/"
cp    "$SRC/scripts/"*.py             "$DST/scripts/"

echo "✅ 已安装到 $DST"
echo "   之后所有项目会话都会自动加载 tvbox-config-sync 技能 / tvbox-agent / /tvbox-sync 命令。"
echo "   新开一个会话即可生效（规则/技能只在会话启动时加载）。"

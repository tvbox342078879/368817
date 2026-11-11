# TVBox 配置同步能力包 · 放置与打包说明

本目录（`/workspace/.codebuddy/`）里已经放好了一套"自动搜集仓库 → 测活线路 → 重新集成配置"的能力。
它包含：

```
.codebuddy/
├── skills/tvbox-config-sync/SKILL.md   ← 自动识别+流程编排（核心，自动加载）
├── agents/tvbox-agent.md               ← 隔离的专职工人（AI 可调用）
├── commands/tvbox-sync.md              ← 手动 /tvbox-sync 一键触发
├── scripts/
│   ├── collect_repos.py                ← 拉仓库、抽源
│   ├── check_live.py                   ← 并发测活线路
│   └── merge_config.py                 ← 存活源集成进主配置
└── tvbox/
    ├── master_config.example.json      ← 主配置示例（复制成 master_config.json 使用）
    ├── install-userlevel.sh            ← 一键装到用户级（所有项目可用）
    └── README.md                       ← 本文件
```

---

## 一、它怎么"自动加载"？（不用你每次 @）

只要这些文件在 CodeBuddy 认的目录里，**每次开新会话会自动加载**，无需你手动引用：

- **Skill**（`skills/`）→ AI 在你说"更新tvbox/测活线路"时**自动识别并调用**
- **Agent**（`agents/`）→ AI 可把它当专职工人派出去干活
- **Command**（`commands/`）→ 你打 `/tvbox-sync` 直接触发

加载层级（决定了"在哪个范围生效"）：

| 放哪 | 生效范围 | 怎么做到 |
|---|---|---|
| 项目内 `.codebuddy/`（当前位置） | **仅本项目** | 随项目 Git 走，clone 即带 |
| 用户目录 `~/.codebuddy/` | **你所有项目** | 见下方"装到用户级" |

> 注意：规则/技能只在**会话启动时**加载。改完或新装后，要**开个新会话**才生效。

---

## 二、怎么"放进去"？—— 三种放置方式

### 方式 A：项目级（当前已就绪，最简单）
文件已经在 `/workspace/.codebuddy/` 了。直接：
```bash
# 把示例主配置复制成真正用的主配置（放项目根目录）
cp .codebuddy/tvbox/master_config.example.json master_config.json
```
然后**开个新会话**，对 CodeBuddy 说："帮我更新 TVBox 配置"，它就会自动跑。
提交到 Git 后，别人 clone 你的项目也自动带上这套能力。

### 方式 B：用户级（所有项目都能用，推荐跨项目）
运行一键脚本：
```bash
bash .codebuddy/tvbox/install-userlevel.sh
```
它会把 `skills/ agents/ commands/ scripts/` 复制到 `$HOME/.codebuddy/`。
之后**任何项目**开新会话都有这套能力。（呼应你之前"跨项目带能力"的诉求。）

或手动复制等价命令：
```bash
DST="$HOME/.codebuddy"
mkdir -p "$DST/skills" "$DST/agents" "$DST/commands" "$DST/scripts"
cp -r .codebuddy/skills/tvbox-config-sync "$DST/skills/"
cp    .codebuddy/agents/tvbox-agent.md  "$DST/agents/"
cp    .codebuddy/commands/tvbox-sync.md "$DST/commands/"
cp    .codebuddy/scripts/*.py           "$DST/scripts/"
```

### 方式 C：团队共享（做成插件，协作者的 CodeBuddy 自动安装）
把下面四个目录打成一个"插件包"目录：
```
tvbox-plugin/
├── commands/tvbox-sync.md
├── agents/tvbox-agent.md
├── skills/tvbox-config-sync/SKILL.md
└── scripts/*.py
```
然后在项目 `.codebuddy/settings.json` 里声明（详见主 SOP 第 11.1 章）：
```json
{
  "enabledPlugins": { "tvbox-plugin@team-tools": true }
}
```
协作者装好插件即自动获得能力，不用手动拷文件。

---

## 三、怎么"打包"？(分发给人 / 换设备 / 团队)

所谓"打包"，本质就是把这四个目录**整体带走**。三种打包粒度：

1. **跟项目走（最自然）**：方式 A 的文件就在项目里，`git commit` 后本身就是包，
   换设备 `git clone` 即恢复（除项目记忆，见主 SOP 第 2.5 章）。
2. **打成压缩包**：`zip -r tvbox-pack.zip .codebuddy/skills .codebuddy/agents .codebuddy/commands .codebuddy/scripts`
   发给人/存云盘，解压到对方项目的 `.codebuddy/` 即可。
3. **做成插件（团队）**：方式 C，适合多人协作长期维护。

---

## 四、使用前必改的两处

1. **登记你的仓库**：编辑 `.codebuddy/scripts/collect_repos.py` 顶部的 `REPOS` 字典，
   把你的配置仓库地址填进去（现在是占位 `xxx/yyy`）。
2. **准备主配置**：把 `master_config.example.json` 复制为项目根的 `master_config.json`，
   填入你自己的站点源/直播源。

---

## 五、怎么验证装好了

开新会话，输入：
```
/tvbox-sync all
```
或自然语言："帮我测活 TVBox 线路并重新集成配置"。
正常会输出：`存活 N  失效 M  → live_result.json` 与 `已生成 master_config.new.json`。

若模型没自动识别，可显式说："用 tvbox-config-sync 技能执行"。

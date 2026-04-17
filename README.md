# Hypothesis Tracker

[![Release](https://img.shields.io/github/v/release/Benboerba620/hypothesis-tracker?sort=semver)](https://github.com/Benboerba620/hypothesis-tracker/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> 🔗 **"零代码 AI 投研三件套" 之一** ｜ Part of the zero-code AI investment research toolkit
> [知识库底座 karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) · [日常盯盘 daily-watchlist](https://github.com/Benboerba620/daily-watchlist) · 假设追踪 hypothesis-tracker

> AI-powered investment hypothesis tracking system for Claude Code. Track theses, record trades, accumulate evidence, and extract rules from patterns.
> 面向 Claude Code 的 AI 投资假设追踪系统。追踪假设、记录交易、积累证据、从模式中提炼规则。

[Latest Release](https://github.com/Benboerba620/hypothesis-tracker/releases) | [Changelog](./CHANGELOG.md)
[中文](#中文) | [English](#english)

# 中文

> **买完就慌？** 这个系统帮你把"我觉得会涨"变成可追踪、可证伪的投资假设。每笔交易关联假设，每条证据更新确定性，亏了知道为什么亏，赚了知道赚的什么钱。
>
> **状态**：v1.0.0。你负责思考和决策；Claude 负责结构化记录、原则校验、反馈闭环。

## 核心理念

**假设是一等公民**，不是随手记的笔记。

| 传统做法 | Hypothesis Tracker |
|----------|-------------------|
| 买了一只股票，理由记在脑子里 | 每个投资主题是一个假设文件，有明确的证伪条件 |
| 看到利好/利空消息，凭感觉调整 | 每条证据记录到时间线，确定性%强制量化判断 |
| 交易和研究脱节 | 每笔交易自动回写关联假设，形成闭环 |
| 同样的错误反复犯 | 模式确认 3 次以上自动提议升级为规则 |

## 三个命令

| 命令 | 做什么 |
|------|--------|
| `/ht-new` | 创建新假设（引导填写核心逻辑、证伪条件、初始确定性） |
| `/ht-trade` | 记录交易（自然语言输入 → 原则校验 → 假设回写 → 交易日志） |
| `/ht-status` | 假设看板（确定性概览、近期变化、持仓关联、预警提醒） |

## 适合谁？

- 想要一套 **结构化的假设追踪系统**，但不想自己从零搭
- 想让 **每笔交易都有据可查**：为什么买、什么时候该跑、假设还在不在
- 想从交易记录中 **自动提炼投资规则**，而不是反复犯同样的错
- 已经在用 [karpathy-claude-wiki](https://github.com/Benboerba620/karpathy-claude-wiki) 或 [daily-watchlist](https://github.com/Benboerba620/daily-watchlist)，想补上"假设追踪"这一环

## 安装

**直接按你的情况选一条路：**

| 你是谁 | 走哪条路 |
|---|---|
| 🪟 **Windows 用户 + 编程小白** | [一键安装（PowerShell）](#-windows-一键安装推荐) |
| 🍎 **macOS / Linux 用户** | [一键安装（bash）](#-macos--linux-一键安装) |
| 🧑‍💻 **会用 Git / 命令行** | [手动安装](#手动安装) |
| 🤖 **想让 AI agent 帮你装** | 把 [`INSTALL-FOR-AI.md`](./INSTALL-FOR-AI.md) 的链接发给 Claude Code，说"帮我装这个" |

### 🪟 Windows 一键安装（推荐）

```powershell
git clone https://github.com/Benboerba620/hypothesis-tracker.git
cd hypothesis-tracker
.\scripts\install.ps1 -TargetDir "你想装到的目录"
```

> 如果 PowerShell 报错"禁止运行脚本"，先执行：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 🍎 macOS / Linux 一键安装

```bash
git clone https://github.com/Benboerba620/hypothesis-tracker.git
cd hypothesis-tracker
bash scripts/install.sh --target-dir "你想装到的目录"
```

### 手动安装

1. Clone 或下载 ZIP
2. 把 `scripts/`, `skills/`, `templates/`, `examples/`, `config/` 复制到你的工作目录
3. 把 `skills/*.md` 放到 `.claude/skills/`
4. 把 `config/*.example.*` 复制为不带 `.example` 的版本
5. 创建 `hypothesis/` 和 `portfolio/journal/` 目录
6. 在 `portfolio/` 下创建 `trades.csv` 和 `holdings.csv`（表头见模板）
7. 在 CLAUDE.md 中添加指向 skills 的指针

## 假设文件长什么样？

每个假设是一个 Markdown 文件（`hypothesis/H1-xxx.md`），包含：

```markdown
---
certainty: 75          # 确定性 0-100%
status: 观察中
created: 2026-04-15
tags: [hypothesis, active]
aliases: [H1]
---

# H1: AI 算力持续增长

## 核心逻辑
云厂商 capex 持续上调 + AI 应用 toB 爆发...

## 证伪条件
- [ ] 主要云厂商削减资本开支
- [ ] 算力利用率下降

## 📊 确定性变化日志
| 日期 | 确定性 | 变化 | 触发事件 |
|------|--------|------|----------|
| 2026-04-15 | 75% | 新建 | 假设建立 |

## 📰 证据时间线
### 2026-04-15
- 🟢 **某公司发布强劲财报** — capex 超预期
```

完整示例见 [`examples/H1-example-thesis.md`](./examples/H1-example-thesis.md)。

## 交易原则校验

`/ht-trade` 记录交易时会自动校验你在 `config/hypothesis-tracker-rules.md` 中设定的投资规则：

- **硬拦截**：新建仓必须设止损价，否则不写入
- **软提醒**：仓位集中度、加仓次数、现金比例等超限时提醒

所有阈值可在 `config/hypothesis-tracker.yaml` 中调整。

## Obsidian 集成（可选）

如果你使用 Obsidian，可以启用 Bases 看板：

1. 在 `config/hypothesis-tracker.yaml` 中设 `obsidian.enabled: true`
2. 把 `examples/hypothesis-tracker.base` 复制到 `hypothesis/` 目录
3. 在 Obsidian 中打开 `.base` 文件，即可看到假设看板

## 配置参考

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `hypothesis.default_certainty` | 50 | 新假设的默认确定性 |
| `risk_rules.max_single_stock_pct` | 30 | 单票占 NAV 上限 % |
| `risk_rules.max_positions` | 8 | 最大持仓数量 |
| `risk_rules.max_add_count` | 3 | 最大加仓次数（含建仓） |
| `risk_rules.min_cash_pct` | 10 | 最低现金比例 % |
| `rules.auto_propose_threshold` | 3 | 模式确认几次后提议为规则 |

完整配置见 [`config/hypothesis-tracker.example.yaml`](./config/hypothesis-tracker.example.yaml)。

## 和其他项目的关系

```
daily-watchlist          →  每日监控，发现异动
    ↓
hypothesis-tracker       →  追踪假设，记录交易，积累证据
    ↓
karpathy-claude-wiki     →  沉淀知识，归档研究
```

三个项目可以独立使用，也可以串联。

---

# English

> **Bought a stock and immediately started worrying?** This system turns "I think it'll go up" into trackable, falsifiable investment hypotheses. Every trade links to a hypothesis, every piece of evidence updates certainty, and you always know why you won or lost.

## Core Idea

**Hypotheses are first-class objects**, not casual notes.

- Each investment theme becomes a hypothesis file with explicit kill conditions
- Evidence accumulates in a timeline with color-coded signals (🟢 positive / 🟡 neutral / 🔴 negative)
- Certainty % forces you to quantify your conviction
- Every trade auto-links back to its hypothesis, creating a feedback loop
- Patterns confirmed 3+ times get proposed as investment rules

## Three Commands

| Command | What it does |
|---------|-------------|
| `/ht-new` | Create a new hypothesis (guided: core logic, kill conditions, initial certainty) |
| `/ht-trade` | Record a trade (natural language → principle check → hypothesis feedback → journal) |
| `/ht-status` | Hypothesis dashboard (certainty overview, recent changes, position mapping, alerts) |

## Quick Start

```bash
git clone https://github.com/Benboerba620/hypothesis-tracker.git
cd hypothesis-tracker

# Windows
.\scripts\install.ps1 -TargetDir "your-workspace"

# macOS / Linux
bash scripts/install.sh --target-dir "your-workspace"
```

Then in Claude Code:
1. `/ht-new` — create your first hypothesis
2. `/ht-trade` — record a trade
3. `/ht-status` — view your dashboard

## How It Fits Together

```
daily-watchlist          →  Daily monitoring, spot movers
    ↓
hypothesis-tracker       →  Track theses, record trades, accumulate evidence
    ↓
karpathy-claude-wiki     →  Archive knowledge, build long-term memory
```

All three projects work independently or together.

## License

[MIT](./LICENSE)

---

Built by [@Benboerba620](https://github.com/Benboerba620) with Claude Code.

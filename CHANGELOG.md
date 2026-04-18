# Changelog

## [1.1.0] - 2026-04-18

### Added
- 假设模板新增"子假设拆解"区块，支持多情景概率分支（如 H2a 30% / H2b 50% / H2c 20%），适用于复杂假设的概率树建模
- 证伪条件从自由文本 checkbox 升级为结构化三元组：指标 + 阈值（证伪触发点）+ 时间窗口，避免"基本面恶化"这类模糊条件
- 月度 Kill Thesis 回顾区块结构化：每月强制回答三个问题（最可能的失败因素 / 被忽视的反面证据 / 错误代价与转向信号）
- 概率校准说明段：记录个人信心 vs 历史 base rate 的差距及折中理由，避免闭门造车式的信心分值
- `examples/H2-example-complex-thesis.md` — 展示新模板完整功能的复杂假设示例
- 关联标的"角色"字段明确三分类：核心标的 / 关联标的 / 验证标的

### Changed
- `skills/hypothesis-tracker-new.md` v1.0 → v1.1：引导用户把证伪条件细化成三元组，询问是否需要子假设拆解与概率校准

### Translated
- `CONTRIBUTING.md` 和 `CODE_OF_CONDUCT.md` 清理为纯中文，移除中英双语残留

## [1.0.0] - 2026-04-15

### Added
- 假设文件模板（frontmatter + 确定性日志 + 证据时间线）
- `/ht-trade` — 交易记录 + 原则校验 + 假设反馈闭环
- `/ht-status` — 假设看板 + 持仓关联
- `/ht-new` — 新建假设引导
- `sync_hypothesis.py` — 假设扫描（支持 `--json`）
- `trade_stats.py` — 交易统计（支持按假设/标的/月份过滤）
- `check_setup.py` — 安装验证
- Trading System 规则框架（Layer 1-4：建仓/加仓/止损/卖出）
- 双平台安装器（PowerShell + bash）
- Obsidian Bases 看板（可选集成）
- 脱敏示例假设文件（AI Infrastructure Scaling）

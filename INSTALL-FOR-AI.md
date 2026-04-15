# Hypothesis Tracker — AI Agent 安装协议

> 本文件供 Claude Code 或其他 AI agent 读取。用户把这个链接发给 agent，说"帮我装这个"即可。

---

## Phase 1: 澄清（Clarification）

安装前先确认以下信息：

1. **安装位置**：装到哪个目录？（默认 `./hypothesis-tracker`）
2. **是否已有工作空间**：目标目录是否已有 CLAUDE.md 或其他项目？
3. **投资市场**：主要交易哪些市场？（美股/A股/港股/其他）
4. **是否使用 Obsidian**：目标目录是否在 Obsidian vault 内？
5. **是否已有假设文件**：有没有已存在的假设需要导入？

---

## Phase 2: 安装（Install）

### Windows (PowerShell)

```powershell
git clone https://github.com/Benboerba620/hypothesis-tracker.git
cd hypothesis-tracker
.\scripts\install.ps1 -TargetDir "{TARGET_DIR}"
```

### macOS / Linux (bash)

```bash
git clone https://github.com/Benboerba620/hypothesis-tracker.git
cd hypothesis-tracker
bash scripts/install.sh --target-dir "{TARGET_DIR}"
```

安装器会自动：创建目录结构、复制脚本和模板、生成配置文件、初始化 CSV、注入 CLAUDE.md、运行检查。

---

## Phase 3: 补全配置（Config Completion）

安装器自动生成以下文件，用户可能需要编辑：

| 文件 | 说明 | 是否必须编辑 |
|------|------|-------------|
| `config/hypothesis-tracker.yaml` | 主配置（市场、风控阈值） | 建议检查 |
| `config/hypothesis-tracker-rules.md` | 投资规则框架 | 可选，按需定制 |
| `config/hypothesis-tracker.env` | 环境变量（预留） | 暂不需要 |

**关键配置项**：
- `trading.markets`：根据用户的市场调整
- `risk_rules`：风控参数（单票上限、加仓次数等）
- `language`：cn 或 en

---

## Phase 4: 融合 CLAUDE.md

安装器已自动处理。检查 `{TARGET_DIR}/CLAUDE.md` 包含 `## Hypothesis Tracker` 段落即可。

**注意**：不要把本文件（INSTALL-FOR-AI.md）或仓库的 CLAUDE.md 整体复制到用户工作区。安装器注入的是轻量指针，只有 ~12 行。

---

## Phase 5: 验证（Validation）

运行安装检查：

```bash
python {TARGET_DIR}/scripts/check_setup.py
```

所有项目应显示 `[OK]`。

额外验证：
- `examples/H1-example-thesis.md` 存在且可读
- `python {TARGET_DIR}/scripts/sync_hypothesis.py` 能正常运行（无假设文件时输出"读取 0 个假设文件"）

---

## Phase 6: 交付（Handoff）

向用户确认安装完成，展示：

```
✅ Hypothesis Tracker 已安装到 {TARGET_DIR}

已创建：
- 📁 hypothesis/     — 假设文件存放处
- 📁 portfolio/      — 交易记录和日志
- 📁 config/         — 配置和规则
- 📁 .claude/skills/ — 3 个 Claude Code skills

推荐的下一步：
1. 检查配置：config/hypothesis-tracker.yaml
2. 看看示例：examples/H1-example-thesis.md
3. 创建你的第一个假设：运行 /ht-new
4. 记录交易：运行 /ht-trade
5. 查看看板：运行 /ht-status
```

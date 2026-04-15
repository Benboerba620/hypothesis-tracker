# Hypothesis Tracker — 假设看板

展示所有假设的状态概览、近期变化和持仓关联。

---

## 元数据

| 字段 | 值 |
|------|-----|
| **触发命令** | `/ht-status` |
| **兼容别名** | `/ht-dashboard`, `/hypothesis-status` |
| **触发词** | "假设状态"、"hypothesis status"、"dashboard"、"看板" |
| **版本** | v1.0 |
| **依赖文件** | scripts/sync_hypothesis.py, scripts/trade_stats.py, hypothesis/, portfolio/ |

---

## 执行步骤

### Step 1: 扫描假设

运行 `python scripts/sync_hypothesis.py --json` 获取所有假设的 ID、确定性、状态、标题。

如果没有假设文件 → 提示用户用 `/ht-new` 创建第一个假设，结束。

### Step 2: 展示假设概览

输出表格：

```
📊 假设看板

| ID | 名称 | 确定性 | 状态 | 活跃天数 |
|----|------|--------|------|----------|
| H1 | AI Infrastructure | 🟢 93% | 强化中 | 101 |
| H2 | ... | 🟡 65% | 观察中 | 45 |
```

### Step 3: 近期变化

逐个读取假设文件，检查"📊 确定性变化日志"表格，提取最近 7 天内有变化的条目：

```
📈 近 7 天变化：
- H1：93% → 93%（→）— 行业研究机构确认硬件配比变化
- H3：70% ↑ 75%（+5%）— 新数据验证电力需求
```

无变化 → 显示"近 7 天无确定性变化"。

### Step 4: 交易统计

运行 `python scripts/trade_stats.py --json` 获取交易统计。

如有交易记录，展示：
```
📋 交易统计：
  本月交易：{N} 笔
  涉及标的：{tickers}
```

如无交易记录 → 显示"暂无交易记录"。

### Step 5: 持仓-假设关联

读取 `portfolio/holdings.csv`（如存在），展示当前持仓按假设分组：

```
🔗 持仓-假设关联：
  H1 AI Infrastructure：TICKER_A（核心仓）, TICKER_B（观察仓）
  H3 电力瓶颈：TICKER_C（核心仓）
  无关联假设：TICKER_D
```

如无持仓 → 跳过此步。

### Step 6: 提醒

- 超过 30 天无证据更新的假设 → ⚠️ 提醒
- 确定性 <30% 且持有相关仓位 → ⚠️ 提醒考虑是否退出
- 确定性 >90% 但无持仓 → 💡 提示是否有交易机会

### Step 7: Obsidian 提示（可选）

读取 `config/hypothesis-tracker.yaml`，如 `obsidian.enabled: true`：
```
💡 Obsidian 看板已启用，可在 Obsidian 中打开 hypothesis/hypothesis-tracker.base 查看交互式看板
```

# Hypothesis Tracker — 交易记录

记录交易，自动更新持仓，执行原则校验，形成假设反馈闭环。

---

## 元数据

| 字段 | 值 |
|------|-----|
| **触发命令** | `/ht-trade` |
| **兼容别名** | `/ht-record`, `/hypothesis-trade` |
| **触发词** | "记录交易"、"买了"、"卖了"、"建仓"、"平仓"、"加仓"、"减仓"、"record trade"、"bought"、"sold" |
| **版本** | v1.0 |
| **依赖文件** | portfolio/holdings.csv, portfolio/trades.csv, config/hypothesis-tracker.yaml, config/hypothesis-tracker-rules.md |

---

## 输入方式

用户用自然语言描述交易，Claude 解析并确认。

**示例输入**：
- "今天 15.5 买了 500 股 XYZ，觉得行业周期见底"
- "卖了一半 ABC，22 块，到第一目标了"
- "平仓 DEF，逻辑止损，假设证伪"
- "加仓 MSFT 10股 @410，AI CapEx 继续超预期"

---

## 执行步骤

### Step 1: 解析交易信息

从自然语言中提取：
- **ticker**：股票代码（如不明确，询问）
- **market**：交易市场（从 `hypothesis-tracker.yaml` 的 `trading.markets` 推断）
- **action**：BUY / SELL / ADD（加仓）/ REDUCE（减仓）/ CLOSE（平仓）
- **shares**：股数
- **price**：成交价
- **currency**：货币（从 market 配置推断）
- **reasoning**：交易理由

### Step 2: 确认并追问

向用户确认解析结果，同时追问：

**买入时追问**：
- "这笔交易的 kill thesis 是什么？什么情况下你会认为买错了？"
- "关联哪个假设？"（如能推断则预填）

**卖出/平仓时追问**：
- "结果怎么样？一句话复盘。"（填入 outcome_note）

### Step 2.5: 原则校验（自动触发，嵌入 Step 2 确认流程）

读取 `config/hypothesis-tracker.yaml` 中的 `risk_rules` 和 `config/hypothesis-tracker-rules.md`，自动对照检查。

**硬拦截**（必须回答才能继续写入）：

| 检查 | 逻辑 |
|------|------|
| 价格止损 | BUY（新建仓）时，用户必须给出 stop_loss 价格（如 `stop_loss_required: true`）。不填不写入 |

**软提醒**（展示提醒，不阻断写入）：

| 检查 | 逻辑 |
|------|------|
| 仓位层级 | 交易后该标的占 NAV 多少？标注：观察仓 1-3% / 核心仓 5-10% / 重仓 15-25% / 超限 |
| 加仓次数 | ADD 操作：扫描 trades.csv 该 ticker 的 BUY+ADD 记录，≥ `max_add_count` → ⚠️ 已达加仓上限 |
| 新证据确认 | ADD 操作：用户的 reasoning 中是否有明确的新证据？如不清楚，追问"上次买完后发生了什么新的事？" |
| 禁止摊低亏损 | ADD 操作且当前持仓浮亏时 → ⚠️ "没有仓位的话今天会以这个价格新建仓吗？" |
| 止损上移 | ADD 操作完成后 → 提醒重新计算止损位，至少保住前批次本金 |
| 单票集中度 | 交易后单票 > `max_single_stock_pct`% NAV → ⚠️ |
| 单 thesis 集中度 | 交易后同一 thesis 总敞口 > `max_single_thesis_pct`% → ⚠️ |
| 现金比例 | 买入后现金 < `min_cash_pct`% → ⚠️ |
| 持仓数量 | BUY（新建仓）且现有持仓已 ≥ `max_positions` → ⚠️ "超出持仓上限，挤掉哪个？" |

**卖出/减仓额外检查**：

| 检查 | 逻辑 |
|------|------|
| 止盈线确认 | SELL/REDUCE 且标的盈利 + 在目标价以下 → 追问"thesis 还在吗？目标价以下不提前跑" |

**输出格式**（嵌入 Step 2 确认消息中）：
```
📋 原则校验：
✅ 价格止损：$50（减半）/ $47（清仓）
ℹ️ 仓位层级：交易后 XXX 占 ~12% NAV → 核心仓
⚠️ 加仓次数：第 3 次（含建仓），已达上限
✅ 单票集中度：12%，未超 30%
✅ 现金比例：交易后 ~15%
```

### Step 3: 写入数据

1. **追加到 trades.csv**：新增一行交易记录
   - 列：`date,ticker,market,action,shares,price,currency,reasoning,kill_thesis,outcome_note`
2. **更新 holdings.csv**：
   - BUY/ADD → 新增行或更新 shares/avg_cost
   - SELL/REDUCE → 减少 shares，shares=0 时标记 status=CLOSED
   - CLOSE → 标记 status=CLOSED

### Step 4: 输出确认

```
✅ 已记录：{action} {shares}股 {ticker} @{price} {currency}
📊 当前持仓：{ticker} {total_shares}股，均价 {avg_cost}
📝 Kill thesis：{kill_thesis}
```

### Step 5: 假设回查（自动触发）

**交易本身就是最强的反馈信号。** 记录完交易后，自动执行假设回查。

1. **查找关联假设**：
   - 扫描 `hypothesis/` 下所有假设文件，匹配 ticker 或行业关键词
   - 如 Step 2 中用户已提到关联假设，直接使用

2. **展示并追问**（嵌入 Step 4 输出中）：
   ```
   🔗 关联假设：
   - H3 电力瓶颈（确定性 75%）
   - H7 供应链重估（确定性 65%）

   这笔交易对上述假设有什么影响？
   1. 强化（哪个假设更确定了）
   2. 削弱（哪个假设动摇了）
   3. 无关（纯交易机会）
   ```

3. **回写**：
   - 用户回答后，更新对应假设文件的确定性变化日志：
     ```markdown
     | {YYYY-MM-DD} | [Trade Signal] | {TICKER} {action}：{用户的一句话反馈} | 强化/削弱/无关 H{n} | {一句话原因} |
     ```
   - **SELL / REDUCE / CLOSE 专项**：同时写入 P/L%：
     ```markdown
     | {YYYY-MM-DD} | [Trade P/L] | {TICKER} {+XX% / -XX%} | 强化/削弱 H{n} | {一句话原因} |
     ```
   - 如信心水平有变化，更新假设文件头部的确定性百分比
   - 如为平仓/止损且假设被证伪 → 建议用户记录教训

4. **无关联假设时**：
   - 静默跳过，不追问
   - 仅在 trades.csv 的备注中标注"无关联假设"

### Step 6: 交易日志（自动触发）

每次 `/ht-trade` 执行后，自动在 `portfolio/journal/` 下写入或追加当日日志。

**文件命名**：`YYYY-MM-DD.md`（同一天多笔交易追加到同一文件）

**日志格式**（参考 `templates/hypothesis-tracker-journal-template.md`）：

```markdown
## {HH:MM} {ACTION} {TICKER} {shares}股 @{price}

**方向判断**：{为什么现在做这笔交易}
**关联假设**：H{n} {假设名}（确定性 {X}%）
**市场上下文**：{当时的关键背景}
**仓位计划**：{目标仓位 / 分批策略 / 止损位}
**情绪自检**：{FOMO / 恐惧 / 冷静执行计划 / 其他}
```

**规则**：
- 日志侧重**决策过程和心理状态**，trades.csv 侧重结构化记录，两者互补
- 如果用户在对话中表达了情绪或犹豫，经用户确认后如实记录
- 平仓/止损交易额外加一行 `**复盘**：{一句话}`

---

## 闭环机制：outcome_note 补填

当用户平仓或提到某笔交易的结果时，Claude 主动：
1. 在 trades.csv 中找到对应的建仓记录
2. 补填 outcome_note 字段
3. 如果是亏损交易，追问："这笔交易的教训是什么？"

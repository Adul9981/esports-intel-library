# 预测市场网格交易项目框架

## 核心范围

第一版按两个核心层次推进：

```text
1. 规律探索层：先发现市场现象。
2. 策略构建层：再把可重复现象沉淀成交易策略。
```

执行管理层作为通用模块存在，负责资金、挂单、止盈、锁盈和复盘。

规律探索层保持简洁克制，不追求一开始全自动判断所有比赛。

执行管理层采用固定金额制：

```text
单场固定预算
每轮固定预算
每档买入固定美元金额
每档卖出固定成本金额
彩票仓固定成本金额
```

## 当前工作流

```text
用户发比赛 / 截图 / 链接 / 语音描述
-> 识别市场现象 P1 / P2 / P3 / P4 / P5 / P6
-> 将成熟现象路由到交易策略 S1 / S2 / S3 / S4
-> 叠加执行管理模块：固定金额、网格、止盈、D2锁盈、彩票仓
-> 生成 trade_config.json
-> 交给 grid_plan_runner.py
-> 复用已有自动交易程序的钱包和下单模块
-> 自动挂多档买单
-> 买单成交后按卖出计划立即挂多档卖单
-> 浮盈扩大后接入 D2 自动锁盈
-> 保留固定金额的彩票仓
-> 交易结束后生成复盘，反哺下一次策略判断
```

当前策略构建层以 S1 / S2 为稳定入口，对应旧 A / B。
S3 对应旧 C，可在实验开关下小额验证。
S4 对应旧 D，先用于持仓管理建议。
旧 E 已下沉为 P5_BO_SERIES_COMEBACK，只是整场反转现象标签，不直接下单。

## 用户最小输入模式

第一版产品交互尽量克制，用户只需要给：

```text
市场链接
Game / Map / 小局编号
想买的方向，或让系统判断方向
策略类型：S1 / S2，或旧 A / B，或自然语言描述比赛形态
固定金额，可省略
```

价格、买入阶梯、卖出阶梯和彩票仓由系统按策略模板自动生成。

理想的语音输入形态：

```text
这场 Game 2 我想买 PlayTime，像强队回撤，帮我按默认金额执行。
这个比赛有点四六开拉扯，弱势方掉到三十多了，帮我看看能不能接。
我赛前买了热门方 60c，现在跌下来了，不想直接止损，帮我做持仓管理。
```

默认由系统负责：

```text
识别 token_id
判断当前价格是否还适合该策略
生成买入阶梯
生成卖出阶梯
换算 shares
dry-run 展示计划
确认后调用执行层
```

只有三种情况需要额外确认：

```text
同一个链接匹配到多个可买方向
策略类型和价格区间明显冲突
即将进入实盘挂单
```

实盘前的确认只确认交易对象和计划，不让用户填写复杂参数。

## 分层命名

完整分层见：

```text
PHENOMENON_STRATEGY_FRAMEWORK.md
```

旧命名映射：

```text
A -> S1_REVERSAL_GRID
B -> S2_FAVORITE_DIP_GRID
C -> S3_DOMINANT_PULLBACK_GRID
D -> S4_POSITION_MANAGEMENT
E -> P5_BO_SERIES_COMEBACK
D2 -> 执行管理模块
P  -> 执行节奏模块
```

## 策略模式库

### 当前可执行策略

S1 / S2 是任务 1 的执行重点，已经进入固定金额网格配置和下单链路。

### S1：低价反转网格，旧 A

适合：

```text
目标方已经真实逆风
价格跌到 20-30c
或极端跌到 10c 以下
```

第一版默认：

```text
单场预算：$100
每轮预算：$25
最多轮数：2

买入：
30c 买 $10
25c 买 $10
20c 买 $5

卖出：
40c 卖出 $7.5 成本份额
50c 卖出 $7.5 成本份额
60c 卖出 $6.25 成本份额

彩票仓：
保留 $3.75 成本份额
```

### S2：热门回撤网格，旧 B

适合：

```text
赛前热门 >65%，最好 >75%
局内临时跌到 60-80c
```

第一版默认：

```text
单场预算：$100
每轮预算：$25
最多轮数：1

买入：
当前价附近买第一档
低 4-5c 再买第二档

卖出：
买入价 +12c 卖出 $10 成本份额
买入价 +22c 卖出 $10 成本份额
98c 卖出 $3.75 成本份额

彩票仓：
保留 $1.25 成本份额
```

跌破 40c 后，S2 失效，不继续按 S2 加仓，必须重新判断是否切换到 S1。

### P5：BO3/BO5 整场反转，旧 E

定位：

```text
P5 不是主策略。
主策略仍然是 S1 / S2 / S3 / S4。
P5 只说明：这个 Match / Series Winner 属于 BO3/BO5 整场反转背景，值得优先观察。
```

适合：

```text
BO3 / BO5 的 Match Winner / Series Winner。
目标方第一局失利，或前半段明显落后。
整场价格被阶段性压低，但系列赛仍有反转空间。
```

第一版路由：

```text
P5 + P1：目标方 5c-30c，路由到 S1。
P5 + P3：目标方 30c-45c，中位反转，先建议/模拟，预算低于标准 S1。
P5 + P2：热门方 55c-70c，路由到 S2。
```

执行纪律：

```text
P5 叠加的交易成交后必须接 D2 自动锁盈。
第一档成交后，不只是挂普通止盈；
如果价格进入 60c-80c，系统要继续检查剩余暴露是否超过彩票仓上限。
```

### 待设计策略

C / D 是真实需求中很重要的两类，但第一版不直接自动实盘。
它们先用于识别、讨论、生成建议和复盘，等规则稳定后再接入执行层。

### S3：强势小回撤网格，旧 C

适合：

```text
赛前热门方或比赛中优势方一路压制
价格多数时间处于 70-90c
市场仍有流动性，spread 可接受
不是已经 95c 以上的终局价格
```

初步思路：

```text
不追极高价。
只在优势方回撤到 70-78c 左右时小额接。
目标是 85-95c 分批卖出。
单笔收益较低，但要求胜率和流动性更高。
临近终局、盘口薄、价格 90c 以上时不新开。
```

待验证问题：

```text
如何判断“理财局”不是终局前追高。
回撤到多少才有足够盈亏比。
高价区间 spread 和滑点对收益侵蚀有多大。
是否需要比 S1/S2 更小的固定金额。
```

### S4：已有持仓救援 / 成本管理，旧 D

适合：

```text
用户赛前或早盘已经买入某一方
价格下跌后不想简单止损
希望系统帮助补仓、减仓、反弹卖出或保留彩票仓
```

初步思路：

```text
先识别已有持仓：买入方向、平均成本、当前价格、已挂订单。
不默认继续加仓。
先判断是否还有波动空间和流动性。
如果仍有反弹空间，设置减仓卖单，优先降低风险。
只有价格和形态符合 S1/S2/S3 时，才考虑小额补仓。
反弹时先回收部分本金，再留小彩票仓。
```

待验证问题：

```text
如何读取并区分用户已有仓位和本策略新仓位。
补仓是否会放大亏损。
何时应该建议减仓而不是加仓。
如何把“关闭订单”和“平仓”与救援策略严格区分。
```

## 文件结构

```text
/Users/ad/Documents/polymarket
├── AGENTS.md
├── README.md
├── docs/
│   ├── AGENTS.md                 # 文档管理规范
│   ├── framework/                # PROJECT_FRAMEWORK / PHENOMENON_STRATEGY_FRAMEWORK / STRATEGY_PATTERN_LIBRARY
│   ├── runbook/                  # V1_RUNBOOK / V1_1_TRADE_COMMAND_GUIDE / V1_1_PROFIT_LOCK
│   ├── task/                     # PROJECT_PROGRESS / TASK2_AUTOMATION_CANDIDATE_FLOW / V2_VALIDATION_HANDOFF
│   ├── data/                     # DATA_COLLECTION_GUIDE
│   └── research/                 # 历史研究材料
├── config/
│   ├── strategy_templates.json
│   ├── discovery_patterns.json
│   ├── market_watchlist.json
│   └── risk_limits.json
├── schemas/
│   ├── trade_config.schema.json
│   └── opportunity_candidate.schema.json
├── tools/
│   ├── grid_config_generator.py
│   ├── polymarket_strategy_backtester.py
│   ├── grid_plan_runner.py
│   └── event_marker.py
├── examples/
│   └── manual_trade_request.example.json
├── runtime/
│   ├── trade_config.json
│   └── markers/
└── reports/
```

## 文件职责

```text
docs/framework/PROJECT_FRAMEWORK.md
项目框架和固定金额制规则。

docs/task/PROJECT_PROGRESS.md
分阶段项目管理进度库，记录任务 1-5 的状态、验收标准和下一步。

docs/runbook/V1_RUNBOOK.md
任务 1 交易执行专用手册，用于新会话运行 V1，不承载复杂策略讨论。

docs/runbook/V1_1_PROFIT_LOCK.md
V1.1 自动锁盈升级说明，记录 D2 浮盈保护的规则、原则和实现状态。

docs/framework/STRATEGY_PATTERN_LIBRARY.md
策略模式库，记录 S1/S2/S3/S4 和未来新策略的成熟度、适用形态、风险和升级条件。

config/strategy_templates.json
S1/S2 两类策略的共用模板，代码内仍兼容旧 A/B。

config/discovery_patterns.json
任务 2 规律探索层的辅助标签配置，当前底层兼容旧 E_BO3_SERIES_COMEBACK，产品输出映射为 P5_BO_SERIES_COMEBACK。

schemas/trade_config.schema.json
执行脚本读取 trade_config.json 的字段约定。

tools/grid_config_generator.py
根据用户输入生成 trade_config.json。

tools/polymarket_strategy_backtester.py
读取 Polymarket 链接，抓取公开历史价格，验证某场 Game Winner 是否符合策略 S1 / S2，并输出固定金额网格回测报告。

tools/market_scanner.py
任务 2 机会扫描器。当前支持本地回测样本扫描和 Polymarket 公共数据实时只读扫描；建议策略输出 S1/S2，现象标签输出 P5，只输出候选，不下单。

tools/grid_plan_runner.py
读取 trade_config.json，复用已有 Polymarket 机器人执行多档买入、多档止盈和彩票仓。

runtime/trade_config.json
当前准备交给执行程序的一次交易配置。

英雄联盟比赛交易策略.html
历史策略研究和 S1/S2 策略数据依据。

英雄联盟比赛自动交易产品逻辑及原型.html
自动交易产品原型。
```

## 与已有自动交易程序的接口

已有自动交易程序位置：

```text
/Users/ad/Documents/polydata/polymarket_trading_bot_strategy
```

当前策略库不直接保存钱包私钥，也不复制交易认证逻辑。
执行时由 `tools/grid_plan_runner.py` 调用已有机器人项目里的：

```text
config.py
trading.py
market_resolver.py
```

`trade_config.json` 需要包含：

```text
market_slug
side
amount_mode
buy_ladders
sell_plan
lottery_cost_basis_usd
max_cycles
stop_new_entry_below
stop_new_entry_above
```

执行约定：

```text
buy_ladders.amount_usd：
每档买入固定美元金额。

sell_plan.sell_cost_basis_usd：
从已成交买入批次里，按该成本金额对应的 shares 计算卖出数量。

lottery_cost_basis_usd：
保留不普通止盈的固定成本份额。
```

运行前需要补齐真实 `token_id`，或使用 `--resolve-token` 根据 `market_slug + side` 自动解析。
如果自动解析匹配到多个方向，必须人工指定 `--token-id`，避免买错边。

示例：

```text
python3 tools/grid_plan_runner.py \
  --plan runtime/trade_config_A_example.json \
  --token-id <目标方向 token_id> \
  --dry-run
```

确认 dry-run 展示的买卖计划无误后，再去掉 `--dry-run` 启动实盘执行。

## 当前第一版不做

```text
不全自动选择所有比赛
不自动识别复杂战局数据
不按账户比例动态加仓
不无限网格
不直接绕过人工判断启动大额交易
```

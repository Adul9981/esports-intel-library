# Σp 错价扫描器 v0 规格（可交给实现者）

最后更新：2026-08-15

目标：只读监控 Polymarket 负风险多选项市场，发现"整套 YES 价格之和 Σp 偏离 $1"的机会，
输出候选与统计日志。**本扫描器只读公开数据、不下单、不碰私钥。**

实现：tools/forensics_sigma_scan.py（v1.1 精度增强版，2026-08-15 落盘）

## 0. v1.1 精度增强（从 e46m3 拆解会话与实测校准而来）

```text
1. 标记价只做粗筛，判定一律用订单簿可成交成本（e46m3 拆解核心结论：
   "标记价格跟订单簿挂单价有差异"）。实测 NFL 冠军盘 mark Σp=1.0555，
   订单簿可执行边仅 +0.026/份（约标记边的 47%）。
2. 只统计真实成交过的腿：lastTradePrice + bestBid 双非空。
   gamma 的 funded 字段在列表接口不可靠（NFL 有 $34 万流动性仍返回 false）。
3. 组内按 negRiskMarketID 去重；Σp>2.5 或 <0.5 标记 suspicious（多组聚合假象），
   不进候选。例：NBA Rookie of the Year 81 腿 Σp=26.5、UCL 7.55 均为假象。
4. 二级精筛逐腿走 ask 阶梯凑 X，任一腿深度不足/盘口为空 => 整套不可成交
   （修复：MLB 冠军盘 7 腿 NO 空盘口曾误报 +6.77/份净利）。
5. 新增 mark_edge vs exec_edge 对照，暴露"标记边被订单簿吃掉多少"。
6. 发现模式（--discover）分页扫事件列表 + 关键词过滤，定位短窗口
   电竞/比分/天气盘；死盘（默认价 0.5、无买盘、组流动性 < $25）直接排除。
7. Convert 费率可配置（--convert-fee-bps）。V2 Convert 按 feeBips 扣费
   （现金与 YES 均为 X−fee），2026-08-15 链上实测 NFL/NBA/MLB/EPL/UCL 组 = 0 bps。
8. YES 方向（Σp<1）加穷尽性/久期提示：无 field 腿且 >90 天结算 => 标
   pass_long_dated（残差概率或久期价值，不是即时套利）。
9. 单边筛选模式：--direction gt --threshold 0.05 只输出 Σp>1.05 的
   完整集套利候选（买全套 NO -> Convert -> 现金 (n-1)X）。
10. 已结束未结算的僵尸盘（endDate 已过仍 closed=false，如 UN 秘书长
    2026-02-28 结束仍可被列出）直接排除；CLOB 盘口 404 的腿视为无盘口，
    不整组崩溃。
11. 手续费用 Polymarket 官方公式（docs.polymarket.com/trading/fees.md）：
    fee = C × feeRate × p × (1−p)，天气/体育 feeRate=0.05、政治/金融 0.04、
    地缘 0；gas 默认 $0.05/轮（--gas-usd）；taker 返佣默认 0（--taker-rebate）。
    v1.0 的"固定 2% 摩擦"假设已废弃（过于保守，实测真实费用约占 NO 名义
    金额 0.5%~0.6%）。
```

## 0.1 实测校准基准（e46m3 数据，docs/forensics/data/e46m3/stats.json）

```text
5000 次 Convert / 12 天：中位 $0.70，最大 $2,274；天气温度档占 39%，
体育比分盘 48 次/单笔中位 $19.85（比赛日集中）；24×7 全天候。
吉达组 Σp=1.0395~1.0740；比分组 Σp=1.02~1.07。
结论：高效机会在"短窗口 + 4% 以上偏离"的天气/比分盘，冠军未来盘边太薄
（MLB 116 次 Convert 中位 $0.02 尘埃仓）——扫描器应对未来盘从严。
```

## 1. 核心概念与数学

一组互斥且穷尽的结果（如 11 个温度档、17 个足球比分、31 支冠军候选）共享一个负风险组
（negRiskMarketID）。每个结果是一个二选一市场（YES/NO）。

```text
Σp = 组内所有盒子 YES 价格之和
理论：Σp = 1（只有一个盒子赢，只有一张 YES 中奖）
Σp > 1：整套 NO 被标便宜（买 NO 组合 -> Convert 兑现）
Σp < 1：整套 YES 被标便宜（买 YES 完整集 -> 持有/合并兑现）
```

Convert 兑付为平台固定公式：交 n 条 NO（每盒 X 份）-> 现金 (n−1)×X + 补集 YES。
因此**风险只在买入端**：赚不赚取决于"真实可成交成本 < 规则兑付"。

## 2. 两级扫描（核心设计）

### 第一级：标记价粗筛（每 15–30 分钟）

```text
对白名单内每个组：
  1. 从 gamma 事件拉结构（negRisk=true、腿数 >= 5 才入选）
  2. 用 prices-history 最近价（或 gamma outcomePrices）算 mark Σp
  3. 命中条件：|mark Σp − 1| > 粗筛阈值（默认 2%）
命中后才进入第二级；未命中不消耗盘口请求
```

### 第二级：订单簿精筛（命中后立即，秒级）

```text
对命中组的每个盒子：
  1. 拉 /book?token_id=，取卖一价 ask
  2. 按目标数量 X 做逐档加权：cost_i = Σ(档位价 × 该档数量) 直到凑够 X
  3. 检查深度：每个盒子的 ask 深度 >= X，否则该盒按"可买数量"打折
  4. 算"可成交成本"：
     买 NO 侧：total_cost = Σ cost_i(NO)
     买 YES 侧：total_cost = Σ cost_i(YES)
```

### 出手判定（默认参数，后续由回测校准）

```text
NO 侧（子集转换，重要）：Convert 只需提供任一子集 S（k 条腿 × X 份），
      兑付现金 (k−1)×X + 补集 YES。因此不是"买全套"：
      1. 对每腿拉 NO ask，深度 >= X 的腿才可用；
      2. 可用腿按成本升序排列，取前 k 条（k >= 最小腿数，默认 5）；
      3. 若 Σcost(S) < (k−1)×X×(1−摩擦) − 安全垫 则出手。
      例：k=7, X=1：cost < $6 × 0.98 − 0.01 = $5.87 才出手
      （e46m3 实测吉达组正是转 7 条腿，不是全组）
YES 侧（完整集）：需全部腿，total_cost < X × (1 − 摩擦) − 安全垫
摩擦 = 官方手续费（feeRate×p×(1−p)）+ 燃气 + 安全垫，不再用固定 2%。
例：n=10、NO 均价 0.85、X=1：手续费 ≈ 10×0.05×0.85×0.15 ≈ $0.064，
   加燃气 $0.05 与安全垫后，成本 < $8.89 才出手。
```

已实现的参考实现：tools/forensics_arb_scanner.py（含子集逻辑与 live_sump 对照）。

## 3. 数据源与接口（实测可用的参数）

```text
市场结构：GET https://gamma-api.polymarket.com/events?slug=<slug>
  字段：markets[].negRiskMarketID / clobTokenIds / outcomes / outcomePrices
  注意：clobTokenIds、outcomes、outcomePrices 是 JSON 字符串，需解析
  约定：token0 = YES，token1 = NO（顺序对应 outcomePrices）

订单簿：GET https://clob.polymarket.com/book?token_id=<token>
  取 bids/asks 数组，逐档价 × 数量

标记价：GET https://clob.polymarket.com/prices-history?market=<token>&interval=1m&fidelity=10
  已结算市场也返回；interval=1d&fidelity=1 对短生命周期市场才给 1 分钟粒度
  标记价只用于粗筛，下单决策一律用订单簿 ask

事件列表：GET https://gamma-api.polymarket.com/events?closed=false&limit=500&order=volume&ascending=false
  筛选 negRisk=true 的事件/市场，或按已知 slug 白名单
```

公共接口需内置重试（3–6 次退避）；publicnode RPC 需浏览器 User-Agent（仅链上解码用）。

注意：gamma 的 outcomePrices 可能是陈旧标记价（实测与实时订单簿可差 0.3+），
只用于粗筛；精筛必须用实时订单簿，并建议输出 live_sump（由订单簿最优 ask
推算的实时 Σp）与 mark_sump 对照。

## 4. 白名单与扫描频率

```text
市场池（优先）：
  1. 天气温度档（每天多个城市，窗口小时级）——主目标
  2. 足球比分盘（开赛前 1–2 小时到赛中，窗口约 1 小时）
  3. 冠军未来盘（MLB/NBA 等，窗口 4–10 分钟爆发）——v1.1 增强

频率：
  粗筛：15–30 分钟（天气/比分盘够用；30 个市场约 1,400 次请求/天）
  精筛：命中后立即
  增强（v1.1）：白名单小池 1–5 分钟精扫，或订阅 CLOB WebSocket 事件
```

## 5. 输出与落盘

每次扫描一行 JSONL（runtime/forensics/scan_YYYY-MM-DD.jsonl）：

```json
{"ts": 1786460000, "group": "jeddah-8-12", "n_legs": 11,
 "mark_sump": 1.059, "ask_sump": 1.063, "ask_cost": 8.97,
 "side": "NO", "verdict": "pass/fail", "depth_ok": true,
 "notes": ""}
```

每日/每周统计报告（reports/forensics_scan_*.md）：

```text
1. 错价出现频率：每市场每天命中次数
2. 持续时间：Σp 连续高于阈值的小时数分布
3. 可成交性：命中中 ask 成本 vs 标记价的差（滑点），深度不足的比例
4. 模拟毛利：见第 6 节回测
```

Σp>1.05 专项候选：reports/sigma_p_gt105_candidates_YYYY-MM-DD.json
（合并白名单+发现模式命中，附订单簿精筛验证列：mark_edge/exec_edge/verdict）。

## 5.1 实测：标记 Σp 与可执行边（2026-08-15，15 组精筛）

```text
结论：当前所有 Σp>1.05 候选的"标记边"在订单簿层面均不成立。
15 组精筛全部 fail / infeasible：
  NFL 冠军 +0.026/份（标记 +0.0555）；NBA 冠军 +0.015；MLB 冠军 7 腿无 NO 盘口；
  马德里天气 +0.0012（标记 +0.075）；巴黎 −0.021；阿姆斯特丹 −0.039；
  MLB 本垒打王 −0.114；NFL MVP 0.0000；阿拉斯加州长 −0.029；
  MLS 金靴 −0.302；MLB 二垒打王 −0.687；民主党副总统 −0.040；
  辛克菲尔德杯 3 腿无盘口；金球奖 +0.008；共和党提名 YES 侧仅 pass_long_dated。
含义：gamma outcomePrices 的标记价系统性滞后于订单簿；判定必须用 ask。
``` 

## 6. 回测模块（同仓库，只读）

```text
用 prices-history 全窗口重放：
  每分钟算 mark Σp；命中后假设按 ask+滑点成交（无历史 ask 时用 1% 保守加成）
  模拟：买全套 NO（或 YES）-> Convert -> 现金 (n−1)X
  毛利 = (n−1)X − total_cost；扣摩擦后得净毛利
输出：触发次数、单轮毛利分布、累计净期望、阈值敏感性（1%/2%/3%）
```

## 7. 边界与纪律

```text
1. 只读：不创建订单、不签名、不碰私钥
2. 判定只用订单簿可成交成本，不用标记价
3. 数量 X 受盘口深度约束；深度不足宁可不做
4. 扫描结果只是候选，真实执行仍需走项目成熟度与风控
```

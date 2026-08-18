# 交易知识库

用途：沉淀每一笔真实交易的复盘、经验教训和可复用样本，供后续交易前参考。

## 目录结构

```text
knowledge/
  README.md                  # 本索引
  TRADE_REVIEW_TEMPLATE.md   # 复盘模板
  reviews/                   # 每笔已复盘交易
  reviews/index.md           # 自动生成的复盘索引
  trades/                    # 结构化交易数据（便于统计分析进化）
  trades/SCHEMA.md           # 数据字段与教训标签词表
  PSYCHOLOGY_NOTES.md        # 交易心理记录（情绪模式与规则对冲）
```

## 交易心理记录

- [PSYCHOLOGY_NOTES.md](PSYCHOLOGY_NOTES.md)：记录 all-in 冲动、止损执行、信心分级等真实心理样本，用规则对冲情绪风险。

## 情报层登记

- [EDGE_LOG.md](EDGE_LOG.md)：边际信息登记——每笔交易的"为什么买"（信息差类型/来源/时效），后台统计"有信息差 vs 纯信心"的胜率与期望，输出到 D5 仓位上限与方向过滤。
- [EXPECTATION_VERIFICATION.md](EXPECTATION_VERIFICATION.md)：预期情形盘中验证闭环——赛前画像假说转可观测信号，盘中确认/否定后决定仓位上限与形态路由。
- [DO_DONT_LISTS.md](DO_DONT_LISTS.md)：正面/负面清单——做对的 13 项（DO）反复强化、做错的 17 项（DON'T）硬拦截；复盘时对照勾选，计数回填，样本沉淀到 EXPERIENCE_INSIGHTS。
- [EXPERIENCE_INSIGHTS.md](EXPERIENCE_INSIGHTS.md)：已确认经验清单——联赛/队伍/形态/执行/情报五类结论，每条带样本量与验证状态。
- [INTEL_SIGNALS.md](INTEL_SIGNALS.md)：主观情报信号（虎牙解说/主播/弹幕）人读摘要；机器源在 [intel_signals.json](intel_signals.json)（字段契约 schemas/intel_signal.schema.json）。
- [INTEL_SIGNAL_TEMPLATE.md](INTEL_SIGNAL_TEMPLATE.md)：信号采集模板与录入示例（工具 tools/record_intel_signal.py；统计 tools/intel_stats.py）。
- [COMMENT_ANALYSIS_RULES.md](COMMENT_ANALYSIS_RULES.md)：评论区情报抓取与分析规则库——series 层抓取方法、评论↔赔率时间线对照、情绪信号判定边界。
- [COMMENTERS.md](COMMENTERS.md)：评论者画像——活跃评论者（如 EurekaWTI）的发言风格、esports 发言时间线、lead-lag 检验与可信度积累。
- [EXPERIENCE_INSIGHTS.md](EXPERIENCE_INSIGHTS.md)：已确认经验清单——个人交易 / 观察心得收编，
  每条带来源、样本量与验证状态（已确认 / 待验证 / 观察中），验证任务清单挂跑量目标。
- [STREAMER_PROFILES.md](STREAMER_PROFILES.md)：虎牙博主/解说档案（957 / 毛毛 / 米勒 / 硕硕 的 uid、内容类型、可信度初判与采集优先级）。
- [DANMU_INTEL.md](DANMU_INTEL.md)：弹幕情报库——虎牙直播弹幕提炼的队伍情绪、选手状态、盘口/局势讨论、灰信号与弹幕密度峰值（低可信度、需聚合，只作情报参考）。
- [DANMU_USERS.md](DANMU_USERS.md)：高价值弹幕用户档案——发言专业、可持续跟踪的账户（按昵称聚合，uid 关联待调）。
- [DANMU_CAPTURE_RULES.md](DANMU_CAPTURE_RULES.md)：弹幕抓取规则与交易模式——开停时机、工具、分析维度、交易应用、红线（新会话必读）。
- [DANMU_README.md](DANMU_README.md)：弹幕情报体系总索引——完整链路（抓取→监控→分析→画像→复盘→平台）+ 文件地图 + 标准工作流（新会话先看这里）。
- [DANMU_POLYMARKET_ROADMAP.md](../docs/task/DANMU_POLYMARKET_ROADMAP.md)：弹幕情报 × Polymarket 行情对接路线图（六阶段，当前在阶段 1 验证）。
- [CHAMPION_PROFILES.md](CHAMPION_PROFILES.md)：英雄画像（BP 阶段情报）——英雄特性 -> 预期情形与交易含义（卡莎后期大核等）。
- [MARKET_DIRECTION_CONSISTENCY.md](MARKET_DIRECTION_CONSISTENCY.md)：预测市场方向一致性研究（最高优先级）——到期前 30d/15d/48h/24h 等时间口径的领先方向与最终结果一致性、延续概率，按板块分层（sports/crypto/politics/esports），对标局内四阶段框架。

## 结构化交易数据

- [2026-08-04 交易数据集](trades/2026-08-04_trades.json)：20 笔结构化记录（含策略、模板、投入、盈亏、退出执行、教训标签）。
- [2026-08-07 交易数据集](trades/2026-08-07_trades.json)：2 笔手动交易（口述估值，WE vs TT G1、BFX vs BRO G1，含尾盘极限反转 / 下狗反转 / Moneyline 死亡螺旋新样本）。
- 字段定义与标签词表见 [trades/SCHEMA.md](trades/SCHEMA.md)。
- 用途：胜率/分组/亏损模式分析，作为策略模板与风控规则的进化输入。

2026-08-04 关键统计（结构化数据口径）：

```text
总笔数：20（含 2 笔用户老仓/手动）
系统管理笔数：18 → 胜 10 / 负 8
主要亏损模式：chased_high + caught_falling_knife（多笔叠加）
最大盈利：BRO G1 +90、T1 整场 +45（系统仓）
最大亏损：BRO 决胜局 -60、YB G2 -37、BW G2 -34
```

2026-08-05 关键统计（结构化数据口径，见 [trades/2026-08-05_trades.json](trades/2026-08-05_trades.json)）：

```text
总笔数：12（已结算 10，进行中 2）
已结算战绩：胜 1 / 负 9，净约 -491.7 USDC
最大盈利：HLE 整场 +34.8（止盈梯+止损执行正确）
最大亏损：LGD 整场 -165.2（all-in 冲动+追高+接飞刀）
主要亏损模式：chased_high + caught_falling_knife + partial_tp_then_zero
新增流程教训：价格必须用 CLOB（gamma 滞后 20c+）；止盈成交后立即配对；
高位（>80c）加仓一票否决；单日回吐 -150 熔断停新仓。
```

2026-08-06 关键统计（见 [trades/2026-08-06_trades.json](trades/2026-08-06_trades.json)）：

```text
总笔数：9（已结算 8，进行中 1）
已结算战绩：胜 4 / 负 4，净约 +16.1 USDC
最大盈利：NRG G2 +25.4；最大亏损：Royer S1 -18.5
主要教训：热门碾压局止盈过早（T1A +9.6 后价格冲到 90+）；
体育冷门侧只做小彩票仓；单场仓位控制在现金 50% 内。
```

2026-08-07 关键统计（结构化数据口径，见 [trades/2026-08-07_trades.json](trades/2026-08-07_trades.json)）：

```text
总笔数：2（均为手动，口述估值）
WE vs TT G1：观点 TT 反转、执行买 WE 接刀，约 -50（抢救回 20）
BFX vs BRO G1：98.5c 未止盈被翻盘归零（金额未记录），BRO 1.5c -> 99.95c
新样本：尾盘极限反转（98.5c -> 0.05c 仅 1 分钟）、下狗反转（TT Moneyline 29.5c -> 99.95c、
  BRO 1.5c -> 99.95c）、Moneyline 死亡螺旋（BFX 75.5c -> 0.05c）
```

## 最近复盘

| 日期 | 交易 | 状态文件 |
| --- | --- | --- |
| 2026-08-08 | SK vs NAVI（LEC）：G1 NAVI 完全碾压、G2 SK 翻盘（NAVI 69.5c→0.05c 22 分钟）；Moneyline 83.5c→58.5c（1:1，G3 待补）；LEC 弹幕情报（常打满/明眼）+ 弹幕主观情绪分析用例（1 分钟快照 docs/data/snapshots/lol-sk-navi-2026-08-08/） | [复盘文件](reviews/2026-08-08_lol-sk-navi_game1-2.md) |
| 2026-08-08 | 全天汇总：T1/HLE、EYE/PHA、NS/DNF ×2；今日约 -400~600；正面样本（NS G1 止损+翻转）+ 反面样本（NS G2 all-in）；形态气候=高波动混合日 | [2026-08-08_day_review.md](reviews/2026-08-08_day_review.md) |
| 2026-08-08 | NS vs DNF G1：DNF 赢（NS 97.5c→0.05c 被翻约 4 分钟，DNF 2.5c→99.95c）；NS -1.5 快速止损 + 翻转 DNF 10-20c $30 翻到 100+ 美金（正面执行样本，1 分钟快照 docs/data/snapshots/lol-ns-dnf-2026-08-08/） | [复盘文件](reviews/2026-08-08_lol-ns-dnf-2026-08-08_game1_ns.md) |
| 2026-08-08 | CS2 EYE vs PHA 整局：5:5 开 -> EYE 86.5c/PHA 13.5c -> PHA 逆转 -> 五五开回归（1:1，G3 进行中）；PHA 13.5c = 强强对话价值买入正例（1 分钟快照 docs/data/snapshots/cs2-eye-pha-2026-08-08/） | [复盘文件](reviews/2026-08-08_cs2-eye-pha_moneyline.md) |
| 2026-08-08 | T1 vs HLE（HLE 2:1 赢系列赛）：G2 B3 假反弹新样本（16.5c→78.5c→0.05c）+ 单局vs整局案例；G3 赛前买 T1 全程浮亏未卖归零（损失厌恶）；Moneyline 72.5c→47.5c→1.5c→0.05c（1 分钟快照 docs/data/snapshots/lol-t1-hle1-2026-08-08/） | [复盘文件](reviews/2026-08-08_lol-t1-hle1-2026-08-08_game2_t1.md) |
| 2026-08-07 | BLG vs TES：TES 2:0 赢系列赛；G1 BLG 93-94.5c 约 8 分钟（1 万经济领先）后 15 分钟被反超归零，Moneyline 84.5c→0.05c；队伍画像 BLG 领先会浪/送（1 分钟快照 docs/data/snapshots/2026-08-07_lol-blg-tes/） | [复盘文件](reviews/2026-08-07_lol-blg-tes_game1.md) |
| 2026-08-07 | FOX(BFX) vs BRO G1：BRO 2:0 赢系列赛；G1 BFX 98.5c→0.05c 仅 1 分钟（BRO 1.5c→99.95c），Moneyline 75.5c→0.05c 死亡螺旋；用户 All in 未止盈，不后悔（1 分钟快照 docs/data/snapshots/2026-08-07_lol-fox1-bro2/） | [复盘文件](reviews/2026-08-07_lol-fox1-bro2_game1_bfx.md) |
| 2026-08-07 | WE vs TT G1：TT 2:1 赢系列赛（29.5c→99.95c）；WE 10-15c 接刀 $70 抢救回 $20 亏约 $50，观点对但执行错位（1 分钟快照 docs/data/snapshots/2026-08-07_lol-we-tt/） | [复盘文件](reviews/2026-08-07_lol-we-tt_game1_we.md) |
| 2026-08-06 | 晚间手动：T1/DK 连赢约 +200（提现 200）；WE/AL 假赛感双翻盘约 +600（G1 低点 6.5c、G2 低点 0.65c，1 分钟粒度核验，快照 docs/data/snapshots/2026-08-06_lol-we-al/），合计约 +700（口述估值） | [复盘文件](reviews/2026-08-06_evening_we-al_t1-dk.md) |
| 2026-08-04 | BRO vs Kiwoom DRX BO3 Moneyline（第三局决胜局），脚本 40-50c 接刀后崩溃，BRO 归零（行情+口述） | [复盘文件](reviews/2026-08-04_lol-bro2-drx-2026-08-04_game3_bro.md) |
| 2026-08-04 | HLE vs GEN 胜负盘，手动重仓 130 USDC @ 77c，无卖出保护，接近归零（口述记录） | [复盘文件](reviews/2026-08-04_lol-hle-gen-match-winner_hle_manual.md) |
| 2026-08-04 | T1 vs HLE Game 1 Winner，A 型，买 T1，30 USDC（已结束） | [复盘文件](reviews/2026-08-04_lol-t1-hle1-2026-08-04-game1_t1.md) |
| 2026-08-04 | T1 vs HLE Game 3 Winner，手动信心溢价买 T1，无完整分批计划，小额卖出部分后盈利（运气成分，金额待补充） | [复盘文件](reviews/2026-08-04_lol-t1-hle1-2026-08-04-game3_t1.md) |
| 2026-08-05 | 全天多场批量复盘（12 笔），已结算 -491.7，追高/接飞刀/部分止盈后归零三大模式 | [复盘文件](reviews/2026-08-05_day_review.md) |
| 2026-08-06 | 全天复盘（9 笔），已结算 4 胜 4 负净 +16.1，止盈过早为本日主要教训 | [复盘文件](reviews/2026-08-06_day_review.md) |

HLE 手动重仓本场结论：

```text
手动重仓的典型反面样本：7:3 市场 77c 接高位，无止盈无止损，三个心理关卡（80c 目标锚定 / 40-50c 损失厌恶 / 20-30c 沉没成本）全部被"再等等"通过，最终接近归零。与 08-03 NS vs T1 复盘是同一个模式。
```

T1 vs HLE Game 1 本场结论：

```text
方向判断比策略执行更重要：真正符合 A 型深反形态的是 HLE（12c → 100），不是 T1。
网格执行正确（30-20c 接、50-60c 出，净赚约 2 USDC）；原有 T1 底仓归零为主要亏损。
```

T1 vs HLE Game 3 本场结论：

```text
流程与亏损单相同（信心溢价入场 + 无完整退出计划），仅结果不同；盈利单也是风险样本，不能当作流程被验证。
```

BRO vs Kiwoom DRX 第三局本场结论：

```text
决胜局 Moneyline 中位接刀 + 脚本崩溃后无交易所挂单保护，BRO 从 67c 约 30 分钟内崩到 0.05c 归零。
止盈/止损单必须挂在交易所层面——脚本会崩，挂单不会；决胜局只允许赛前底仓 + 20-30c 小彩票仓结构。
```

2026-08-06 晚间本场结论：

```text
conviction + 深反翻盘：WE 两局 13c/20c 均价接深跌（低点 <10c/2c），翻盘兑现约 +600；
CLOB 1 分钟核验：G1 低点 6.5c@13:58、G2 低点 0.65c@15:16，G2 低点到结算仅约 6 分钟；
与 08-05 接刀 9 连负同形态，差异是"假赛感"边际信息 + 运气；样本继续累计，仓位仍要彩票仓化 + 交易所级保护。
```

## 复盘流程

1. 交易结束（关单或平仓）后运行：

```text
python3 tools/append_knowledge_review.py \
  --state-file <状态文件路径> \
  --result "<最终结果>" \
  --lessons "<教训要点>"
```

2. 复盘文件写入 `knowledge/reviews/`，`reviews/index.md` 自动更新。

## 已完成复盘

见 [reviews/index.md](reviews/index.md)。

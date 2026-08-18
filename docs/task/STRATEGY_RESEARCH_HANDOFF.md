# 策略研究工作交接（2026-08-07）

用途：给新的"策略研究会话"一个自包含入口。本文件汇总现状、材料位置、已定稿结论与未决问题；细节以各链接文件为准。

## 1. 一句话现状

```text
策略研究已从"现象观察"推进到"6 个策略结构 + 3 个现象标签 + 7 个执行模块"的体系；
当前主攻中位80（S1-标准 / S2 / P-早建仓），S1-深反暂缓；
执行链路已跑通真实流程（KT vs Gen.G Game 1 中位80-S2，因未回撤到 45c 档零成交，属正常未触发）。
```

## 2. 策略全量清单（2026-08-07 梳理）

独立入场-出场策略结构 6 种：

| 策略 | 价格走势特征 | 状态 | 关键证据 |
| --- | --- | --- | --- |
| S1-深反（彩票类） | <10-15c 深跌（含 5c/1c 极值）→ 翻盘 50-100c | 暂缓（设计保留） | WE 6.5c/0.65c、IG/NIP <5c、HLE 12c、Dota VG/YB 回测 +196% |
| S1-标准（中位80-S1） | 20-50c 深跌 → 反弹 60-85c | 已定稿 | BO3 首局落后样本、08-05 接刀反面 |
| S2（中位80-S2） | 热门 65-80c 回撤到 40-50c → 修复 | 已定稿、主攻 | LNG/IG +37%、NAVI +33.5%、HLE 整场 +34.8、NRG/BESTIA |
| S3（强势小回撤/理财局） | 强方 70-90c 小回撤 → 续涨 85-95c | 实验（L2，需确认） | HLE vs GEN 手动单（反面） |
| S4（持仓救援） | 已有仓位亏损 | 仅建议 | 08-05 部分止盈后归零 |
| P-早建仓 | 开局五五开 50-60c → 一路领先买不到 | 已定稿（模块） | T1/DK 赛前全仓、KT/GenG 首次挂单 |

现象/发现标签 3 种：

```text
P5_BO_SERIES_COMEBACK：BO3/BO5 0-1 落后、Moneyline 被压 <30c（甚至 <10c）→ 系列赛翻盘（路由到 S1/S2）。
尾盘崩塌 / 被翻盘：领先方 80-90c 尾盘几分钟崩盘（NS/T1 79.5→0.5、BRO G3 67→0.05、HLE Challengers 86.5→36.5）——D2 锁盈论据 + 任务 6 被翻盘率。
领先确认早买：五五开开局一路领先（即 P-早建仓的现象侧）。
```

执行模块 7 个：D2 锁盈、D3 止损状态机、D4 进场三件套、D5 信心溢价仓位、D6 每日回吐、P 赛前底仓、滚动降成本。

## 3. 项目库策略材料清单（按用途分类）

框架与定义：

```text
docs/framework/PHENOMENON_STRATEGY_FRAMEWORK.md  P/S/M 三层总规则（规律探索层/策略构建层/执行模块）
docs/framework/PROJECT_FRAMEWORK.md              固定金额制、工作流
docs/framework/STRATEGY_PATTERN_LIBRARY.md       策略模式与成熟度（S1-深反/S1-标准/S2/S3/S4、P5、D2-D6）
docs/framework/STRATEGY_SYSTEM_OVERVIEW.md       执行入口级总览（中位80 定义、收益率、可实现性）
docs/framework/STRATEGY_MASTER_LIST.md           策略总清单（小局/整局分层口径，最新；含 WE vs TT、BFX vs BRO 新样本）
```

现象与发现配置：

```text
config/discovery_patterns.json   E_BO3_SERIES_COMEBACK 发现标签（core_signals、路由 S1/S2、种子样本 3 个）
config/market_watchlist.json     LoL/CS2/Dota 赛事白名单与时间窗
```

策略模板与风控：

```text
config/strategy_templates.json   中位80-S1 / 中位80-S2 / S1-深反模板（生成器唯一事实源）
config/risk_limits.json          单场 80、单日 200、并发 3、autopilot 关闭
schemas/trade_config.schema.json 交易配置字段约定
schemas/opportunity_candidate.schema.json 机会候选输出结构
```

回测与验证产物（reports/）：

```text
strategy_ab_backtest_summary_2026-08-03.md       A/B 样板回测小结（LNG/IG、DNF/BRO）
bo3_first_map_loss_reversal_backtest_2026-08-04.md BO3 首局落后专题（LoL/CS/Dota 三样本，E/P5 起源）
<game>_<match>_strategy_a/b_backtest.*            各场 A/B 回测（cs2/dota2/lol 共 15+ 份）
deep_reversal_ladder_backtest_2026-08-07.md       S1-深反阶梯回测（WE 数据）
midband_backtest_2026-08-07.md                    中位组合回测（保底收益率、止损触发率、数据粒度局限）
strategy_c_extreme_lottery_candidate.md           候选策略：极端低价反转彩票（几美分级；注意与 S3 命名冲突）
strategy_discovery_validation_2026-08-03.md       发现层验证
risk_management_lessons_2026-08-03.md             风控教训
```

自动化流程与执行：

```text
docs/task/TASK2_AUTOMATION_CANDIDATE_FLOW.md      自动化候选三层框架（触发/决策/投递）
docs/runbook/V1_RUNBOOK.md / V1_1_TRADE_COMMAND_GUIDE.md / V1_1_PROFIT_LOCK.md  V1 执行手册
docs/task/V2_VALIDATION_HANDOFF.md                任务 2 live 验证交接
tools/prepare_grid_trade.py + tools/grid_config_generator.py  计划生成（已改为读取模板配置）
tools/grid_plan_runner.py                          执行器（已加余额预检）
tools/market_scanner.py / event_marker.py          发现与打点
```

数据资产：

```text
docs/data/snapshots/2026-08-06_lol-we-al/          WE vs AL 1 分钟快照（G1/G2/Moneyline）
docs/data/snapshots/2026-08-07_lol-hle-drxc/        HLE Challengers 1 分钟快照（双翻盘+尾盘崩塌样本）
knowledge/trades/2026-08-04~06_trades.json         结构化交易记录（43 笔）
docs/research/lol_match_classification.csv          2026-06 LoL 比赛分类（150 场，赛制/优先级）
docs/research/英雄联盟比赛交易策略.html / esports_volatility_product_spec.md / grid_trading_mvp_notes.md  早期产品与研究
```

复盘知识库：

```text
knowledge/reviews/  8 份正式复盘（含 08-05 亏损日、08-06 晚间 +700 深反正面样本）
knowledge/PSYCHOLOGY_NOTES.md  交易心理记录
knowledge/TRADE_REVIEW_TEMPLATE.md  复盘模板
```

## 4. 关键决策记录（2026-08-04 -> 08-07）

```text
- A/B 统一为 S1/S2 命名；旧 E 下沉为 P5 现象标签。
- S1 拆两档（深反彩票 / 标准中位）；S2 修正为"赛中回撤 40-50c 才买"（原 72/68c 高位买入错误）。
- 新增 P-早建仓模块（50-60c 早买），"赛前买一部分"不建独立策略。
- 中位80（Mid80）命名：中位入场、80% 成本回收、20% 彩票；止损跌破成本一半。
- 单场预算 80（验证后可升 100）；半自动边界：开赛前定策略后买入/监控/挂止盈全自动。
- S1-深反与环节 4（彩票机器）暂缓；环节 5（执行层可行性评估）待办。
- 生成器改为读取 config/strategy_templates.json；执行器加余额预检。
```

## 5. 未决问题 / 下一步（新会话优先）

```text
1. 命名统一：已理清（2026-08-09）——"策略 C 极端低价彩票"归并为 S1-深反极值子类；
   S3 已并入 S2（热门回撤接）；旧报告已标注历史状态，不再作为独立策略。
2. 数据粒度：08-05/08-06 市场公开接口只有 5-13 分钟粒度，止损率测算不可靠；
   需 1 分钟/事件级数据（短生命周期市场有，或接打点/朋友数据）——环节 5 数据粒度评估。
3. 方向过滤：已形式化（2026-08-09）——config/strategy_templates.json B_FAVORITE_DIP
   新增 entry_requires_direction_evidence=true（赛前热门 >=65% / P5 上下文 / 主观看好小仓）；
   批量反事实复核佐证：S2 无方向过滤 36/44 触发止损，平均 -12.6。
4. 深反重启条件：P5+P1 案例累计 5-10 个（当前约 6 个）后评估。
5. 任务 6 被翻盘率/翻盘率情报引擎（依赖样本统计）。
6. 自动化候选流（任务 2）live 验收 + 环节 4 彩票机器（深反恢复后）。
   彩票机器触发样本当前 single_15=5 / single_10=7 / cum_15=12，距 20-30 小额实测目标
   尚有差距，优先以 cum_15 模式继续积累。
7. 四阶段执行框架（2026-08-10 登记，未验证，用户修正版）：0-10 小仓方向判断、
   10-20 方向确定+决策（反转策略主窗口）、20-30 方向确定+决策（顺势/减仓，彩票 25+）、
   30+ 基本确定结果（锁盈/止损窗口）。待用 1 分钟数据验证
   H1（0-10 噪声大）/ H2（10-20 信号提升胜率）/ H3（20-30 与 30+ 收敛 + 尾盘反转率）/
   H4（极值低点时间分布，彩票是否集中在 25+）。
   详见 docs/task/THREE_WINDOW_EXECUTION_FRAMEWORK.md；作为模式研究/策略研究/
   数据积累/情报库（比赛时间线情报卡）四线共用研究项。
8. G1 热门赢后 Over 2.5 低价价值仓（2026-08-10 登记，未验证）：
   结构先验 = 打满率（LOL 49-54%，LCK 强队 G1 赢后送弱队率约 50%），
   Over 28-30c 命中盈亏平衡 28-30% -> 历史先验下 +EV 候选；
   执行要点：28-30c 挂单不追单（快速下影线 2-3 分钟窗口，手动追单追不上）；
   需按赛区/赛制分层积累样本验证。案例：HLE vs GEN 08-10（15:14-15:16 下影线 22.5c）。
9. 让一追二特征分析（2026-08-10 登记，未验证，并入分层回测 v2）：
   现象：G1 输家整场最低 <=12-20c 后赢下系列赛（HLE 11.5c、K27 6c、MOUZ 11c、
   DNS 11.5c、DK 23.5c 同族）。
   定价逻辑（+EV 要点）：整场 12-20c 买入，命中率约 30%
   （G1 输后系列胜率 LOL 28-39% / DOTA 35%，非"高胜率"），赔率 5-9 倍；
   命中率 30% > 盈亏平衡 12-20% -> 期望为正（中胜率、高赔率）。
   候选特征：①赛制（淘汰赛/资格赛生死战打满倾向高）；②实力差距（赛前 45-60c
   近五五开更易让一追二，大热门 G1 输后易 0:2 崩）；③关键位置选手状态
   （HLE 上单 / MOUZ 中单 / DNS 嘟嘟，样本 2/2 应验）；④G2 深水区启动确认
   （单局上穿 0.3/0.5）；⑤游戏差异（DOTA 深水区反转样本密度高）。
   验证：并入四阶段回测 v2 分层（赛制 x 赛前强弱区间 x 游戏），累计 30+ 样本后定仓位。
   执行纪律：彩票/归零预算 + 启动确认；"高收益"成立、"高胜率"不成立。
```

## 7. 下一个开发项：1 分钟 bar 监控 + 挂单决策程序（2026-08-08 已确认可行）

```text
可行性实测（2026-08-08，活跃市场实时验证）：
- 比赛/市场进行中，用窄窗口（最近 10-15 分钟）+ interval=1d&fidelity=1 拉 prices-history，
  返回 60 秒间隔、最后一条数据延迟约 40-60 秒——比赛过程中即可用，无需等结算。

使用前提：
- 查询窗口必须窄（宽窗口会被降采样到 5-13 分钟），监控程序用滑动的窄窗口轮询。
- 1 分钟 bar 有约 1 分钟延迟：只用于"挂单入场 / 策略状态判断"，
  止损 / 回撤保护仍用实时中间价（98.5c -> 0.05c 只要 1 分钟，bar 追不上）。

设计方向（不用单独设计文档，开发时按此实现）：
- 新建 tools/bar_monitor_runner.py（或扩展 grid_plan_runner 增加策略引擎钩子）。
- 每 60 秒拉最近 10-15 分钟 1 分钟 bar -> 策略引擎判断当前状态
  （价格进入哪个区间 / 是否切策略 / 是否挂单）-> 只挂或调整 resting 限价单，绝不市价追。
- 复杂策略 = 引擎里的模块：输入 1 分钟 bar 流，输出挂单动作，不动现有执行链路。

状态：v1 已建（2026-08-09，tools/bar_monitor_runner.py）。

```text
v1 已实现：
- 每 60 秒拉最近 15 分钟窄窗口 1 分钟 bar（prices-history interval=1d&fidelity=1，
  兜底 interval=1m&fidelity=10）+ /book 实时中间价。
- 策略状态引擎：S1 深反 / 中位80 / S2 热门回撤，档位与止损线读
  config/strategy_templates.json + config/risk_limits.json。
- 只推荐 resting 限价单（价格低于实时中间价，绝不市价追）；止损/回撤保护用实时中间价。
- 默认 dry-run，动作写入 runtime/bar_monitor_actions.jsonl + 最近一条快照；
  状态在 runtime/bar_monitor_state/<slug>.json（成交档位不重复推荐）。
- 离线验收：tests/fixtures/bar_*.json 四场景（入区挂单 / 穿档估算成交 / 破止损切 S1 评估 /
  S1 深反多档挂单），三轮回放确认无重复买单。

用法：
    python3 tools/bar_monitor_runner.py --slug <event-slug> --strategy B_FAVORITE_DIP --watch
    ./runtime/run_bar_monitor.command <event-slug> --outcome <队名> --watch

待办（v2）：

```text
--execute 已实现（2026-08-09）：bar_monitor_runner --execute 生成 pending trade_config 并调
  grid_plan_runner --dry-run；--execute-live 为真实挂单（需用户显式确认；仍保持唯一下单入口）。
D3 状态机已落地（2026-08-09）：d2_trailing_active / d3_stop_triggered / re_entry_eval，
  跟踪止损按模板（S2 高 0.80->0.72、0.75->0.68；S1 深反 0.85->0.75、0.70->0.58）。
形态标签已接入（2026-08-09）：窗口 bar 流经 classify_pattern --market-type 输出
  pattern_labels，写入动作记录与状态；classify_pattern 新增 --market-type 参数。
V2 执行闭环 v1 已建（2026-08-09）：--autopilot（信号->计划->dry-run->待确认）、
  --execute-live（确认后挂单 + 自动拉起 monitor）、计划内交易所级止损单（D3 落地）、
  风控闸前置（开关/白名单/预算/并发/去重）。定义与验收协议见 docs/task/V2_EXECUTION_LOOP.md；
  待真实比赛 live 验收（08-13/14 LCK 窗口或指定真实比赛）。
```
```
```

## 8. 框架待补清单（六点，2026-08-08 已逐项落地/登记）

```text
1. 形态频率统计 / 形态气候（点 1）：已写入 REVERSAL_PATTERN_LIBRARY + 情报库功能点。
   -> 形态分类工具 tools/classify_pattern.py 已建（启发式 v1.1，全快照频率统计已产出）。
2. 双边形态刻画（点 2）：已写入复盘模板（TRADE_REVIEW_TEMPLATE）+ 形态通用字段。
3. 赛前情报层（点 3）：情报库功能点已登记；TEAM_PROFILES 已结构化（队伍/风格/形态倾向/证据/信任）。
4. 可成交性 / 滑点参数化（点 4）：已写入 LOTTERY_MACHINE 过滤条件。
   -> 参数已入 config/risk_limits.json market_filters（成交量下限 5 万、深度比 2x、滑点 1/3c）。
5. 未知形态通道（点 5）：已写入 REVERSAL_PATTERN_LIBRARY（未匹配 -> 观察池 -> 登记流程）。
   -> 分类工具输出"未知"标签即观察池入口；取数流水线已接入（取数 -> 自动分类 -> 未知入池），
      全快照回填完成，观察池 10 个样本待复核。
6. 止损后重新进场触发条件（点 6）：已细化到 STRATEGY_PATTERN_LIBRARY D3（5 条触发条件）。
术语统一：下狗 = 赛前低赔率方；落后侧/下盘 = 盘中暂时落后方（已写入形态库）。
```

## 9. 第二轮待补（2026-08-08 用户裁定）

```text
7. 反事实复盘（用户认可有价值，已做）：tools/counterfactual_review.py；
   演示：FOX/BRO BFX G1 规则化执行 +6.68 vs 实际 -100，差值 106.68（98.5c 不锁盈的流程成本）。
8. 策略期望值追踪（已定规则）：颜色/仓位每累计 10 笔真实交易或每周刷新一次，不每次刷新；
   赛前预期价缺失登记为 TODO（归属执行层，半自动决策输入）。
9. 赛前价值发现（归属已定）：执行层（半自动决策输入）——"赛前预期价 vs 开盘价"价差检测待建。
10. 取数完整性校验（已做）：fetch_price_snapshot.py 内置校验（双方价格和≈1、时间戳单调/重复、
    结算/分辨率标注）；回填发现：多处时间戳重复 1 个、HLE/SHU-NRG Moneyline 未结算异常。
11. 心理规则进执行器（待办）：PSYCHOLOGY_NOTES 的"连续亏损自动降档 / all-in 冷静期"等
    转化为执行器自动风控（D6 扩展）。
```

## 10. 主观情报库建设（主播/解说/弹幕信号，单独会话）

```text
用户确认要做"直播间主播发言 + 弹幕 -> 结构化赛前/赛中情报库"（2026-08-08）。
完整方案：docs/task/INTEL_SIGNAL_LIBRARY_PLAN.md（数据源分层、信号标签、字段、
采集三阶段、验证闭环、填充映射、待办清单）。
已填充：INTEL_SIGNALS.md（WB/LNG 中单熟练度、T1/HLE 上单核心 + 状态低迷）、
TEAM_PROFILES.md（HLE 行）、TASK6 4.7（产品功能点）。
单独会话启动路径见方案第 9 节。
```

## 6. 新会话启动路径

```text
建议阅读顺序：
AGENTS.md -> 本文件 -> docs/framework/STRATEGY_SYSTEM_OVERVIEW.md
-> docs/framework/STRATEGY_PATTERN_LIBRARY.md -> docs/task/PROJECT_PROGRESS.md
-> 按需进入 config / reports / knowledge / docs/data。
```

# 弹幕情报体系总索引（情报库平台 · 主观数据源）

最后更新：2026-08-18

定位：虎牙直播弹幕是情报库平台（TASK6）的**主观情报数据源**之一——
与解说信号、评论数据并列，提供"观众集体智慧"层。本文件是弹幕情报的
总入口，把所有工作串成一条链：抓取 → 监控 → 分析 → 画像 → 复盘 → 平台。

## 完整链路

```text
直播弹幕（虎牙，实时 WebSocket）
  -> tools/fetch_huya_danmu.py 抓取（JSONL 落盘 docs/data/danmu/<博主>/）
  -> tools/danmu_live_monitor.py 实时监控（5 分钟刷新 HTML，页面自动刷新）
  -> tools/danmu_intel.py 情报提炼（队伍/选手/盘口/局势/灰信号/密度峰值）
  -> tools/danmu_report.py HTML 简报 / 整场复盘
  -> 画像沉淀：TEAM_PROFILES.md（队伍）/ DANMU_USERS.md（高价值用户）
  -> 知识库：DANMU_INTEL.md（情报汇总）/ DANMU_CAPTURE_RULES.md（规则）
  -> 平台衔接：TASK6 情报库（弹幕为数据源，集体智慧信号为功能点）
  -> 交易衔接：DANMU_POLYMARKET_ROADMAP.md（弹幕×行情对照，分阶段推进）
```

## 文件地图

### 数据

```text
docs/data/danmu/shuoshuo/2026-08-17_323444.jsonl  （TH vs Navi 场，2262 条）
docs/data/danmu/shuoshuo/2026-08-18_323444.jsonl  （KC vs GX 场，1903 条）
```

### 工具

```text
tools/fetch_huya_danmu.py    实时弹幕抓取（WebSocket，断线重连，持续模式）
tools/danmu_intel.py         情报提炼（含 analyze_deep 深度主题分析）
tools/danmu_live_monitor.py  实时监控（每 5 分钟刷新 HTML）
tools/danmu_report.py        弹幕数据 -> HTML 简报
```

### 文档（知识库 + 规划）

```text
knowledge/DANMU_CAPTURE_RULES.md   抓取规则与交易模式（新会话必读）
knowledge/DANMU_INTEL.md           弹幕情报汇总（每场记录）
knowledge/DANMU_USERS.md           高价值弹幕用户档案
knowledge/STREAMER_PROFILES.md     虎牙博主档案（957/毛毛/米勒/硕硕）
knowledge/TEAM_PROFILES.md         队伍画像（弹幕情报沉淀处）
docs/task/DANMU_POLYMARKET_ROADMAP.md  弹幕×Polymarket 对接路线图
docs/task/INTEL_SIGNAL_LIBRARY_PLAN.md 主观情报库建设方案
docs/task/TASK6_INTELLIGENCE_LIBRARY_PRODUCT.md  情报库平台框架
```

### 报告（HTML）

```text
reports/intel_danmu_index.html                        报告索引页（平台入口）
reports/intel_danmu_2026-08-17_323444.html            08-17 简报
reports/intel_danmu_full_2026-08-17_323444.html       08-17 TH vs Navi 完整复盘
reports/intel_danmu_live_KC-GX_2026-08-18.html        08-18 实时监控（进行中页面）
reports/intel_danmu_KC-GX_G1_2026-08-18.html          08-18 第一局小结
reports/intel_danmu_KC-GX_full_2026-08-18.html        08-18 KC vs GX 整场复盘
```

## 标准工作流（每场比赛）

```text
1. 博主开播且解说比赛 -> 启动 tools/fetch_huya_danmu.py（新 JSONL 文件）
2. 启动 tools/danmu_live_monitor.py（HTML 页面，5 分钟自动刷新）
3. 局间/关键节点 -> 出局间小结（可选）
4. 比赛结束（弹幕大量 888/88/晚安 + 数据停止增长）-> 停抓、停监控
5. 整场复盘 HTML + 更新 DANMU_INTEL.md / TEAM_PROFILES.md / DANMU_USERS.md
```

## 与情报库平台（TASK6）的衔接

```text
数据源：弹幕数据登记为平台"主观情报"数据源（见 TASK6 文档第 6 节）。
功能点：
  1. 集体智慧信号（灰信号聚合：质疑条数 + 卡盘数字重合度）
  2. 弹幕密度峰值 = 比赛关键时刻（事件时间线）
  3. 高价值用户观点（DANMU_USERS.md 跟踪）
  4. 队伍/选手微观画像（喂 TEAM_PROFILES / 平台画像卡）
对外展示原则：只展示聚合结论与统计，不裸展示弹幕流与用户身份。
```

# 虎牙弹幕抓取规则与交易模式（知识库）

最后更新：2026-08-18

本文沉淀"弹幕 -> 交易情报"的完整工作流：抓取规则、数据规范、分析维度、
交易应用模式与红线。新会话按本文执行，先读 knowledge/DANMU_INTEL.md 与
DANMU_USERS.md 了解数据与人员档案。

## 1. 抓取规则（什么时候开、什么时候停）

```text
开抓时机：博主开播且正在解说比赛时（直播页面标题含"XX vs XX"、弹幕讨论比赛内容）。
停抓时机：比赛结束（弹幕出现"GG/结束/下班"或观众讨论下一场时）即停，等下一场再开。
直播间清单：STREAMER_PROFILES.md（957 / 毛毛 / 米勒 / 硕硕）；按需扩展。
数据落盘：docs/data/danmu/<博主>/<日期>_<房间>.jsonl（JSONL 一行一条）。
字段：ts（秒级时间戳）/ nick（昵称）/ text（内容）；（uid 待解，Tars 字段未对上）。
```

## 2. 抓取工具与运行环境

```text
工具：tools/fetch_huya_danmu.py（实时 WebSocket，纯 Python，无浏览器无逆向）。
依赖：复用 /tmp/real-url（GitHub wbt5/real-url）的虎牙 Tars/WebSocket 实现；
  运行环境 /tmp/intel-whisper-venv（aiohttp / requests / pycryptodome）。
命令：PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python \
  /tmp/intel-whisper-venv/bin/python tools/fetch_huya_danmu.py \
  --url <直播间> --out <jsonl>        # 0=持续到 Ctrl-C
注意：PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python 必须带（绕过旧 protobuf）；
  断线自动重连（客户端内置）；禁止同时跑两个抓取进程写同一文件（实测会混行）。
```

## 3. 分析维度与工具

```text
tools/danmu_intel.py：提炼 队伍情绪 / 选手状态 / 盘口数字 / 局势线索 /
  灰信号 / 弹幕密度峰值，输出 runtime/danmu_intel.json。
tools/danmu_report.py：生成 SAP/Apple 风格 HTML 简报（reports/intel_danmu_*.html）。
画像沉淀：队伍 -> TEAM_PROFILES.md；选手 -> DANMU_INTEL.md 记录；
  高价值用户 -> DANMU_USERS.md。
```

## 4. 交易应用模式（弹幕怎么变成交易情报）

```text
1. 弹幕密度峰值 = 比赛关键时刻：高活跃分钟（>=均值+2σ 且 >=6 条）通常是
   团战/翻盘/争议事件，与 Polymarket 价格异动强相关——作"事件检测"信号，
   后续与价格序列对照（待接入）。
2. 信息差信号：观众"嘴上看衰" vs 比分/盘面领先的分裂（如 TH 被看衰却赢 FNC、
   或 TH 0:2 被横扫但让分盘被讨论）——提示市场情绪与实力判断错位。
3. 盘口讨论：观众直接聊让分/人头盘（-6.5 / 8-2 / 总人头），反映大众关注点，
   与 Polymarket 让分/胜负盘情绪对照。
4. 高价值用户跟踪：DANMU_USERS.md 中的专业用户（TokyoLll / LuLu13 等）观点
   作为可聚合的"准信源"，跨场次累计可信度。
5. 版本/赛区观察：如"中路大核刷钱、LEC 不打架"——影响比赛形态与策略路由。
```

## 5. 红线与纪律

```text
1. 弹幕低可信度、需聚合：单条不算信号，>=3 条同向才作参考。
2. 灰信号 = 集体智慧信号（2026-08-18 升级）：直播间梗（小卖部/健身房/接=接广告）
   是噪音；"假赛/剧本/菠菜/卡盘"类质疑是**有价值的观众集体信号**——
   聚合计数 + 时间分布 + 与盘口/价格对照，标注"观众质疑，非结论"；
   质疑集中且伴随盘口异常时，作为风险升级提示，仍不直接当作假赛证据。
3. 区分多场比赛：弹幕会同时聊多场（如 LEC 场里出现 LCK/其他队名），
   局势分析必须严格限定当前场，跨场信息单独归类。
4. 比赛识别存疑时标注：比分/结果从弹幕推断时写"据弹幕推断，待官方确认"。
5. 弹幕只作情报参考，不改变止损/止盈纪律（与 D5 一致）。
6. 比赛结束即停抓，不长时间空跑。
7. 市场存在性检查：先确认比赛在 Polymarket 有市场再做价格对照
   （LEC 等无市场比赛只做情报沉淀，见 DANMU_POLYMARKET_ROADMAP.md）。
```

## 6. 赛制常识（影响局势判断）

```text
- LEC 近期 BO3 无 1-1、只有 2-0（用户确认 + 弹幕印证"最近lec都没有11，都是20"）。
- 低人头/放资源/保枪打法在 LEC 常见（版本：中路大核刷钱，除 LPL 外不打架）。
- 弹幕中"8-2"、"10个头"等为人头盘/总击杀讨论，不是小局比分。
```

# 数据采集目标清单（给数据合作伙伴）

最后更新：2026-08-11

用途：给抓取历史数据的合作伙伴一份明确的"赛事 / 队伍 / 规格"清单，
按清单筛比赛，避免抓到数据质量不高、口径错误的样本。
说明：本清单为草稿 v1；队伍名单以官方赛程为准（本仓库已见样本用 ✓ 标记，优先采集）。

## 1. 赛事清单（按优先级）

| 联赛 | 赛事 / 范围 | 赛制 | 市场类型 | 优先级 | 说明 |
| --- | --- | --- | --- | --- | --- |
| LPL | 夏季赛常规赛 + 季后赛（近 2-3 个月起） | BO3（决赛 BO5） | Game + Match | 高 | 高波动 + 假赛风险观察重点 |
| LCK | 夏季赛常规赛 + 季后赛 | BO3（决赛 BO5） | Game + Match | 高 | 反转可信度高 |
| LCK CL | LCK 挑战者联赛（T1A / DRXC / HLE Challengers / DNSC / KTC 等） | BO3 | Game + Match | 中高 | 本仓库已有样本 |
| LEC | 夏季赛常规赛 + 季后赛 | BO3 | Game + Match | 高 | 打满率 49.2%，G1->G2 统计重点；存在"明眼"观察 |
| CS2 | IEM / BLAST / EWC 等顶级赛事 | BO3（决赛 BO5） | Game + Match | 高 | 深反可信；本仓库已见 FOKUS/PAR/Liquid/FNC/BESTIA 等 |
| CS2 | 其他中型赛事 | BO3 | Game + Match | 中 | 注意低成交量降级 |
| Dota2 | The International / ESL One | BO3 | Game + Match | 高 | 本仓库已见 XG/GG/YB/VG/MOUZ/GLYPH |
| Dota2 | 其他系列赛 | BO3 | Game + Match | 中 | 同上 |

时间范围建议：**近 2-3 个月起步，目标累计 200+ 场**（当前本地仅 20+ 场快照）。

## 2. 队伍清单（草稿，以官方名单为准）

### LPL（✓ = 本仓库已见样本）

```text
BLG ✓、TES ✓、JDG ✓、WE ✓、AL ✓、IG ✓、LNG ✓、WBG ✓、NIP ✓、TT ✓、
EDG ✓、LGD ✓、CFO ✓、GZ ✓ + 其余官方参赛队（OMG/FPX/UP/RNG/RA 等以当季名单为准）
```

### LCK（含挑战者）

```text
T1 ✓、Gen.G ✓、HLE ✓、DK ✓、KT ✓、NS（Nongshim RedForce）✓、BRO（Brion）✓、
DRX ✓、BFX/FOX（BNK FearX）✓、DNF（slug 待确认官方名）✓、KDF 等以官方名单为准
挑战者：T1A ✓、DRXC（DRX Challengers）✓、HLE Challengers ✓、DNSC ✓、KTC ✓
```

### LEC

```text
G2、Fnatic ✓、Karmine Corp ✓、Team Vitality、SK Gaming ✓、GIANTX ✓、
Movistar KOI、Natus Vincere ✓、Team Heretics、Rogue（以官方名单为准）
```

### CS2（赛事级强队 + 本仓库已见）

```text
Spirit、Vitality、NAVI、FaZe、G2、MOUZ、Astralis、Liquid ✓、Fnatic ✓、
FOKUS ✓、PARIVISION ✓、BESTIA ✓、Eyeballers ✓、Ace ✓、VAN ✓、LONE ✓、VAE ✓、OG ✓、NRG ✓、
K27 ✓（slug 待确认官方名）、SHU ✓（slug 待确认）
```

### Dota2

```text
XG（Xtreme Gaming）✓、Gaimin Gladiators ✓、Team Spirit、Yakult Brothers（YB）✓、
Vici Gaming（VG）✓、MOUZ ✓、GLYPH ✓、LevelUP ✓、PR1 ✓（slug 待确认）、YES ✓（slug 待确认）
+ 官方参赛队（Tundra / BetBoom / Team Liquid 等）
```

## 3. 抓取规格（每个市场）

```text
1. 市场类型：Game Winner（小局）+ Match Winner / Moneyline（整场）都要；
   BO3 第三局起没有独立 Game Winner 市场，只有 Moneyline。
2. 粒度：优先 1 分钟（高成交量市场才有）；低成交量市场接受 5-10 分钟并标记粒度。
3. 字段：时间戳、价格、（可选）订单簿深度 / spread、结算结果（100c = 胜 / 0c = 负）。
4. 窗口：比赛进行中用窄窗口（最近 10-15 分钟）拉取，宽窗口会被降采样到 5-13 分钟。
5. 每场记录：event_slug、market_slug、双方队伍名、BO 赛制、小局编号。
```

## 4. 质量门槛与避坑（必读）

```text
1. 低成交量市场 = 数据与执行双打折：成交量 <5 万 USDC 的市场可能只有 5-10 分钟粒度，
   优先选高成交量（如 BLG G1 143 万 USDC 才有 1 分钟）。
2. 结算必须复核：曾出现 Moneyline 互补报价冲突（99.95 vs 0.513/0.486），
   疑似结算前尾部重定价或抓取窗口异常——标"结算待确认"，不能直接当最终结果。
3. 队伍别名 / slug 坑：BFX=FOX（BNK FearX）、NS=Nongshim RedForce、
   DRXC=DRX Challengers、HLE Challengers 与主队 HLE 要区分、GEN=Gen.G、
   YES/PR1/DNF/K27/SHU 等 slug 待确认官方名后统一。
4. 10 分钟采样会漏极值（IG vs NIP 案例：5c 以下极值只出现在 1 分钟粒度），
   深反统计尽量用 1 分钟数据。
5. 时间窗口：active events 按 startDate 正序会混入大量长期未结算旧事件，
   需正序 + 倒序双向抓取并按时间窗口过滤。
6. 每场存档命名统一：<日期>_<游戏>-<双方缩写>-<日期>（如 2026-08-07_lol-blg-tes），
   避免重复与混淆。
```

## 5. 交付格式（对齐本仓库）

```text
1. 每场 JSONL：价格时间序列（时间戳 + 价格）+ 结算结果 + 元信息（slugs / 队伍 / BO / 小局）。
2. 汇总索引：比赛 -> 市场 -> 文件路径，供 tools/ 直接读取回填。
3. 标注粒度（1m / 5m / 10m）与数据质量（高 / 中 / 低）。
4. 存到 docs/data/snapshots/ 或单独目录，命名按第 4 节第 6 条。
```

# 拆解案例跟踪表

目标：一场一场拆解 e46m3（及后续目标交易者）的公开交易。每场拆完填一张拆解卡，
并回流策略库与知识库。

## 已拆

| 日期 | 事件 | 要点 | 拆解卡 |
| --- | --- | --- | --- |
| 2026-08-12 | 吉达最高温 8/12（温度档） | 完整集套利实证：Σp 1.0475~1.0640，13 次 Convert，5 笔链上解码 | [2026-08-12_jeddah_temperature](2026-08-12_jeddah_temperature/README.md) |
| 2026-08-15 | GX vs VIT Game 2 赢家地址分析（假赛嫌疑场） | 425 个赢家侧买家；深水 ≤0.15 共 145 人/$8.5k；大额买家全是系统性深水抄底机器（"高手"成立）；未发现一次性组织者账户；盘后 0.999 流 $161k 拆分 | [2026-08-15_lol-gx-vit-game2-address](2026-08-15_lol-gx-vit-game2-address/README.md) |
| 2026-08-14 | EDG vs LGD（LPL Ascend 组）盘口异动 | LGD 盘口 20 分钟 0.57→0.99（买单 96 万份 vs 卖单 16 万份）；fkigedgjdgwbg 以 0.95~0.999 追买 $277,608；拉盘主力 0xe16e8a3c... 等（疑似"假赛信息"跟进，待用户确认场次） | 数据见 data/fkigedgjdgwbg/ |
| 2026-08-16 | 赢家账户对照分析（Gen.G vs T1 & DRX vs BRO） | 两场共同赢家 889 个；跨场赢家场均 pnl $3,559 vs 单场赢家 $658（5.4 倍）；大赢家模式=全剧本+均衡仓位；深水低吸整场盘倍数最高；已建 Top15 跟踪名单 | [2026-08-18_lol-winner-accounts-t1gen-drxbro](2026-08-18_lol-winner-accounts-t1gen-drxbro/README.md) |

图解版（三案例对照，含天气/足球/棒球链上账目与 Σp 图）：
reports/convert_mechanism_explainer_2026-08-12.html

## 待拆（按优先级）

| 优先级 | 事件 | 原因 | 状态 |
| --- | --- | --- | --- |
| P0 | EDG vs LGD 8/14 拉盘钱包关联排查 | 已定位 0xe16e8a3c.../0xb0417f.../0xa16a13... 等大额买单；需查与 fkigedgjdgwbg 是否同源（链上资金流/共址） | 待拆 |
| P0 | CF Villarreal C vs Levante UD - Exact Score | 比分盘 12 次 Convert；图解版已验证 Σp=1.02~1.07 与链上账目 | 待补正式拆解卡 |
| P1 | SD Raiders FC vs. Macarthur FC - Exact Score | 单笔最大（250 份额 -> $1,500） | 待拆 |
| P1 | Palermo FC vs. Juventus Turin - Exact Score | 已有一笔链上解码（25 份额 -> $50） | 待拆 |
| P1 | AZ vs. ADO Den Haag - Exact Score | 多笔转换，含 24.997 份额 -> $150 | 待拆 |
| P2 | MLB World Series Champion 2026 | 116 次 Convert 但中位 $0.02（尘埃），验证"未来盘低价值"判断 | 待拆 |
| P2 | 吉达 8/11 温度组 | 与 8/12 对照，验证 Σp 漂移是否常态 | 待拆 |

## 进度规则

```text
1. 拆解前在"状态"列标记"拆解中"，避免并发重复。
2. 拆完更新本表（移到已拆 + 一行要点）。
3. 每 5 场生成 cases/SUMMARY.md 提升复盘。
4. 选题规则见 DISSECTION_GUIDE.md 第 1 节。
```

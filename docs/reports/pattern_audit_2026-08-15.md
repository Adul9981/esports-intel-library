# 形态库巡检（2026-08-15）

快照序列：187 条；快照组：49 组（较上次新增 8 组：cs2-fut-mouz-2026-08-14, dota2-ts8-aur1-2026-08-13, lol-gx-vit-2026-08-14, lol-mvk-cfo-2026-08-14, lol-ns-bro2-2026-08-14, lol-shft-sk-2026-08-14, lol-t1-dk-2026-08-14, lol-t1a-dkc-2026-08-13）

## 1. 已知形态复验计数

| 形态 | 累计样本 | 上次 | 本周期新增验证 |
| --- | --- | --- | --- |
| B4_直线阴跌 | 66 | 57 | +9 |
| A2_中位U型反转 | 44 | 42 | +2 |
| C2_五五开开局碾压 | 21 | 15 | +6 |
| A3_折价修复 | 16 | 16 | +0 |
| A1_V型极值反转 | 15 | 15 | +0 |
| 未知 | 15 | 12 | +3 |
| 热门全程压制 | 13 | 13 | +0 |
| A4_下狗整场反转 | 12 | 11 | +1 |
| A5_W型双底 | 12 | 9 | +3 |
| B4_低开阴跌 | 10 | 10 | +0 |
| B2_死亡螺旋 | 9 | 7 | +2 |
| A6_反弹确认 | 8 | 8 | +0 |
| A7_强强对话错杀 | 4 | 4 | +0 |
| C2_早期缩距/热门确立 | 1 | 1 | +0 |
| B1_尾盘崩塌 | 1 | 1 | +0 |

## 2. 新形态发现（未知序列聚类）

无候选新形态（未知序列未达 3 个相似图形，继续观察）。

未知序列清单（15 条）：
- 2026-08-07_lol-hle-drxc/moneyline_hle_price_1m（pre 0.285 / end 0.395 / low 0.055 / x50 2）
- cs2-bb3-faze-2026-08-12/winner_bb3_price_1m（pre 0.485 / end 0.305 / low 0.05 / x50 2）
- cs2-bb3-faze-2026-08-12/winner_faze_price_1m（pre 0.515 / end 0.695 / low 0.495 / x50 2）
- cs2-eye-pha-2026-08-08/moneyline_eyeballers_price_1m（pre 0.715 / end 0.495 / low 0.47 / x50 3）
- cs2-prv-b8-2026-08-12/winner_b8_price_1m（pre 0.445 / end 0.245 / low 0.085 / x50 6）
- cs2-shu1-nrg-2026-08-07/cs2-shu1-nrg-2026-08-07_nrg_price_1min（pre 0.93 / end 0.513 / low 0.513 / x50 0）
- cs2-shu1-nrg-2026-08-07/cs2-shu1-nrg-2026-08-07_spirit_hu_price_1min（pre 0.07 / end 0.486 / low 0.0005 / x50 0）
- dota2-pr1-mouz-2026-08-10/moneyline_mouz_price_1m（pre 0.59 / end 0.835 / low 0.11 / x50 6）
- lol-drxc-foxy-2026-08-11/moneyline_drxc_price_1m（pre 0.605 / end 0.565 / low 0.495 / x50 2）
- lol-gx-vit-2026-08-14/moneyline_vit_price_1m（pre 0.565 / end 0.6075 / low 0.545 / x50 0）
- lol-ns-bro2-2026-08-14/moneyline_ns_price_1m（pre 0.535 / end 0.895 / low 0.495 / x50 2）
- lol-shft-sk-2026-08-14/moneyline_sk_price_1m（pre 0.565 / end 0.885 / low 0.525 / x50 0）
- lol-sk-navi-2026-08-08/moneyline_natus_vincere_price_1m（pre 0.635 / end 0.585 / low 0.585 / x50 0）
- lol-sk-navi-2026-08-08/moneyline_sk_gaming_price_1m（pre 0.365 / end 0.415 / low 0.105 / x50 0）
- lol-t1-hle1-2026-08-08/moneyline_t1_price_1m（pre 0.455 / end 0.475 / low 0.385 / x50 6）

## 3. 结论与建议

- 样本仍不足以对单形态下统计结论（目标 >=10/形态），继续每 2-3 天巡检累计。
- 新形态候选按 REVERSAL_PATTERN_LIBRARY 三.6 流程登记（图形 -> 观察池 -> 回测 -> 入库）。

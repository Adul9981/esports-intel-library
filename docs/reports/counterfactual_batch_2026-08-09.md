# 反事实复盘批量（规则化执行 vs 快照全量）

生成时间：2026-08-09T04:46:07.043163+00:00

序列数：47（docs/data/snapshots）。预算每套 $100。

规则参数：

- S2_FAVORITE_DIP：entry 0.45 / TP 0.62（80% 成本）/ stop 0.351
- S1_DEEP_REVERSAL：entry 0.08 / TP 0.5（80% 成本）/ stop 0.008

## 逐序列

| 快照 | 序列 | S2 规则结果 | S2 盈亏 | S1 规则结果 | S1 盈亏 |
| --- | --- | --- | --- | --- | --- |
| 2026-08-06_lol-we-al | game1_we_price_1m | 触发止损 | -22.0 | 止盈达成 | 649.87 |
| 2026-08-06_lol-we-al | game2_we_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| 2026-08-06_lol-we-al | moneyline_we_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-blg-tes | game1_blg_price_1m | 止盈达成 | 10.24 | 触发止损 | -90.0 |
| 2026-08-07_lol-blg-tes | game1_tes_price_1m | 触发止损 | -22.0 | 止盈达成 | 649.87 |
| 2026-08-07_lol-blg-tes | game2_blg_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| 2026-08-07_lol-blg-tes | game2_tes_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-blg-tes | moneyline_blg_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| 2026-08-07_lol-blg-tes | moneyline_tes_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-fox1-bro2 | game1_bfx_price_1m | 止盈达成 | 10.24 | 触发止损 | -90.0 |
| 2026-08-07_lol-fox1-bro2 | game1_bro_price_1m | 触发止损 | -22.0 | 止盈达成 | 649.87 |
| 2026-08-07_lol-fox1-bro2 | game2_bfx_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| 2026-08-07_lol-fox1-bro2 | game2_bro_price_1m | 止盈达成 | 54.64 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-fox1-bro2 | moneyline_bfx_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| 2026-08-07_lol-fox1-bro2 | moneyline_bro_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-hle-drxc | game1_hle_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| 2026-08-07_lol-hle-drxc | game2_hle_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-hle-drxc | moneyline_hle_price_1m | 触发止损 | -22.0 | 止盈达成 | 498.75 |
| 2026-08-07_lol-we-tt | game1_tt_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-we-tt | game1_we_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| 2026-08-07_lol-we-tt | moneyline_tt_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| 2026-08-07_lol-we-tt | moneyline_we_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| cs2-eye-pha-2026-08-08 | map1_eyeballers_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| cs2-eye-pha-2026-08-08 | map1_phantom_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| cs2-eye-pha-2026-08-08 | map2_eyeballers_price_1m | 止盈达成 | 10.24 | 触发止损 | -90.0 |
| cs2-eye-pha-2026-08-08 | map2_phantom_price_1m | 止盈达成 | 54.64 | 未入场（价格从未到 entry） | - |
| cs2-eye-pha-2026-08-08 | moneyline_eyeballers_price_1m | 未入场（价格从未到 entry） | - | 未入场（价格从未到 entry） | - |
| cs2-eye-pha-2026-08-08 | moneyline_phantom_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| lol-ns-dnf-2026-08-08 | game1_dn_soopers_price_1m | 触发止损 | -22.0 | 止盈达成 | 649.87 |
| lol-ns-dnf-2026-08-08 | game1_nongshim_red_force_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| lol-ns-dnf-2026-08-08 | game2_dn_soopers_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| lol-ns-dnf-2026-08-08 | game2_nongshim_red_force_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| lol-ns-dnf-2026-08-08 | handicap_ns15_nongshim_red_force_price_1m | 止盈达成 | 10.24 | 触发止损 | -90.0 |
| lol-ns-dnf-2026-08-08 | moneyline_dn_soopers_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| lol-ns-dnf-2026-08-08 | moneyline_nongshim_red_force_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| lol-sk-navi-2026-08-08 | game1_natus_vincere_price_1m | 未入场（价格从未到 entry） | - | 未入场（价格从未到 entry） | - |
| lol-sk-navi-2026-08-08 | game1_sk_gaming_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| lol-sk-navi-2026-08-08 | game2_natus_vincere_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| lol-sk-navi-2026-08-08 | game2_sk_gaming_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| lol-sk-navi-2026-08-08 | moneyline_natus_vincere_price_1m | 未入场（价格从未到 entry） | - | 未入场（价格从未到 entry） | - |
| lol-sk-navi-2026-08-08 | moneyline_sk_gaming_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| lol-t1-hle1-2026-08-08 | game1_hle_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| lol-t1-hle1-2026-08-08 | game1_t1_price_1m | 止盈达成 | 54.64 | 未入场（价格从未到 entry） | - |
| lol-t1-hle1-2026-08-08 | game2_hle_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| lol-t1-hle1-2026-08-08 | game2_t1_price_1m | 触发止损 | -22.0 | 触发止损 | -90.0 |
| lol-t1-hle1-2026-08-08 | moneyline_hle_price_1m | 触发止损 | -22.0 | 未入场（价格从未到 entry） | - |
| lol-t1-hle1-2026-08-08 | moneyline_t1_price_1m | 止盈达成 | 31.33 | 未入场（价格从未到 entry） | - |

## 汇总

### S2_FAVORITE_DIP

- 触发止损: 36
- 止盈达成: 8
- 未入场（价格从未到 entry）: 3
- 序列数 44，平均规则盈亏 -12.6 USDC，盈利 8/44

### S1_DEEP_REVERSAL

- 未入场（价格从未到 entry）: 22
- 触发止损: 20
- 止盈达成: 5
- 序列数 25，平均规则盈亏 +51.9 USDC，盈利 5/25


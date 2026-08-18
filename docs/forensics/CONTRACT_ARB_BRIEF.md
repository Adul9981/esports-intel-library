# 合约规则套利研究窗口 · 新会话启动包

最后更新：2026-08-15

本文件是"合约规则套利研究"专项会话的第一读文档。新会话先读本文件，
再读 KNOWLEDGE_BASE.md、STRATEGY_LIBRARY.md、SCANNER_SPEC.md，然后按
"会话启动清单"开工。

## 0. 本窗口定位与红线（先读这个）

目标：研究 Polymarket 官方合约（CTF Exchange V2 及配套合约）的**规则与实现**，
寻找两类可捕捉机会：

```text
A. 规则套利（市场侧，合法、可复制）：
   合约规则是固定的，价格是市场给的。规则保证的价值 vs 市场标价之间的差
   就是可捕捉的"漏洞"。例：完整集 Σp≠1、Convert 兑付、Merge 恒等式、
   结算后 Redeem 价差、返佣叠加。不做任何攻击性交易。

B. 代码级漏洞（白帽，合法、有赏金）：
   若在合约实现中发现真实缺陷（如舍入/溢出/状态机问题），只做"发现并上报"，
   走 Polymarket 官方赏金计划（Cantina 最高 $500 万），严禁利用漏洞取款。
```

红线（任何情况下不做）：

```text
1. 不构造攻击性交易盗取/抽走合约资金（刑事犯罪，且资金可追踪）。
2. 不上报→不利用：发现代码缺陷先写报告提交赏金，不先打后报。
3. 实盘动作（下单/Convert/Merge）只在走完本仓库执行流程后做，默认只读分析。
4. 不读取/移动私钥；不修改 polydata 仓库。
```

## 1. 官方合约清单（Polygon）

| 合约 | 地址 | 角色 |
| --- | --- | --- |
| CTF Exchange V2 | 0xE111180000d2663C0091e4f400237545B87B996B | V2 撮合+托管主合约（2026-04-28 上线） |
| NegRiskAdapter | 0xada2005600dec949baf300f4c6120000bdb6eaab | 负风险组 Convert/整套逻辑 |
| NegRisk 辅助/交易所 | 0xd91e80cf2e7be2e162c6513ced06f1dd0da35296 | 负风险辅助执行 |
| 条件代币 CTF | 0x4d97dcd97ec945f40cf65f87097ace5ea0476045 | ERC1155 份额代币 |
| USDC.e | 0x2791bca1f2de4661ed88a30c99a7a9449aa84174 | V1 抵押品（迁移前） |
| pUSD | 0xc011a7e12a19f7b1f670d46f03b03f3342e82dfb | V2 内部抵押品 |
| 负风险抵押 token | 0x3a3bd7bb9528e159577f7c2e685cc81a765002e2 | neg-risk 抵押凭证 |

源码与文档：

```text
V2 源码：      https://github.com/Polymarket/ctf-exchange-v2
合约文档：     https://docs.polymarket.com/resources/contracts.md
Quantstamp 审计：certificate.quantstamp.com 搜 "Polymarket CTF Exchange V2"
赏金（Cantina）：最高 $500 万（智能合约）/ $25 万（Web）
赏金（Immunefi）：最高 $100 万（旧计划，范围较小）
```

## 2. 核心规则与套利数学（已用链上账目验证）

### 完整集定价 Σp

一组互斥且穷尽的结果（n 个盒子）共享负风险组。规则保证：

```text
规则 1：n 张 YES 全买齐 = 必然拿 $1（只有一张中奖）
规则 2：NO(i) ≡ 除 i 外全部 YES（Convert 免费互换，等价关系）
规则 3：同一盒子的 YES+NO = $1（任何时候 Merge）
理论 Σp = 1
```

市场把 Σp 标错时出现结构性套利：

```text
Σp > 1  -> 整套 NO 被标便宜：买全套 NO -> Convert（现金 + 补集 YES）-> Merge
Σp < 1  -> 整套 YES 被标便宜：买 YES 完整集（Split/市价）-> 持有或 Merge
```

### Convert 兑付公式（固定，公平）

交结果集合 S 的 NO（n 条腿 × X 份）-> 现金 (n−1)×X + 补集 S^c 的 YES（每腿 X 份）。

```text
任意结果下转换前后价值相等 -> Convert 本身不产生利润
利润 = 买入端差价：真实成交成本 < 规则兑付价值
毛利 ≈ X × |Σp − 1|（未计摩擦），吉达 8/12 实测 Σp=1.0475~1.064
```

### 已确认可复制的形态

```text
S-F1 完整集套利（e46m3 主模式，L1/L2 待升）：
  买全套 NO（Σp>1 时）-> Convert 得现金+补集 YES -> Merge 配对 -> 再循环
  单轮约 30 秒；利润 = X×(Σp−1)；需订单簿 ask 成本 < 兑付×(1−摩擦)
返佣叠加：MAKER/TAKER_REBATE + 等级返佣可再增厚 1~2%（e46m3 近 100 笔 $2,546）
```

## 3. 公开审计与已知问题（白帽线索库）

### Quantstamp 审计（V2，2026-03 报告）

```text
结论：未发现高危；主要为 Informational 级发现，例如：
  POL-EX-4：calculateTakingAmount() 溢出可导致错误结算金额（Informational）
  建议：COMPLEMENTARY 路径的取值处理、Gas 优化等
```

### 历史漏洞/异常记录

```text
1. Nonce 漏洞（V1，PolyNode 研究）：V1 订单 nonce 可被操纵 -> 已在 V2 移除
   nonce 字段修复（V2 无 incrementNonce 攻击面）。
2. py-clob-client #338（2026-04-28 V2 切换后）：~35% 市价买单链上结算 revert
   （固定 1.3M gas 逻辑回退，盈利单不对称）-> 执行层问题，不是资金漏洞。
3. pUSD 迁移（2026-04-28）：V1 USDC.e -> V2 pUSD，停盘约 1 小时；
   迁移期间的抵押品包装/解包是潜在研究点。
```

## 4. 白帽上报路线（发现代码缺陷时的唯一出路）

```text
平台：Cantina（https://cantina.xyz）Polymarket 计划
范围：Polygon 上 18 个合约——V1/V2 CTFExchange 及 NegRisk 版、费用模块、
      条件代币框架、pUSD 抵押品包装/解包、UMA 预言机适配器等
上限：智能合约 $5,000,000；Web/基础设施 $250,000
明确 Out of scope：第三方预言机数据错误、预言机操纵/闪电贷利用、
      测试文件、仅影响测试网等
流程：写清影响 + 复现步骤 + PoC（只读/测试网）-> 提交 -> 等官方处理
      禁止先打后报、禁止在主网利用。
```

## 5. 新会话研究议程（按优先级）

```text
P0 合约规则套利候选（市场侧，只读）：
  [ ] 对活跃负风险组跑 Σp 一级粗筛（脚本已跑通，快照 reports/sigma_p_scan_2026-08-15.json）
  [ ] 对命中组做订单簿 ask 二级精筛，验证"可成交成本 < 兑付 − 摩擦"
  [ ] 候选池：NFL 2027 冠军(Σp≈1.056)、NBA 2027 冠军(1.048)、MLB 2026(1.030)、
      Ballon d'Or(1.025)、以色列总理(<0.95 反向) 等；注意长尾冠军盘流动性薄
  [ ] 检查结算后 Redeem 价差：已结算未领取的赢家 YES 是否低于 $1 可买
  [ ] 检查 pUSD 抵押品包装/解包价差（V2 迁移后新面）

P0 合约实现研究（白帽，只读源码）：
  [ ] 拉取 ctf-exchange-v2 源码，通读 exchange/mixins/Trading.sol 撮合与结算路径
  [ ] 复核 POL-EX-4（calculateTakingAmount 溢出）在 V2 是否仍存在、影响面
  [ ] 检查 Convert/Merge/Redeem 的舍入与边界（X=1、极小份额、n=1 组）
  [ ] 检查 neg-risk 组的 Convert 公式在"腿数变化/结算中"窗口的状态机
  [ ] 产出"规则套利机会清单 + 疑似缺陷清单"，缺陷走 Cantina 上报

P1 回测与验证：
  [ ] 用 e46m3 历史账本回测 S-F1 在扣费/滑点后的真实净利
  [ ] 扫描器结果连续 3 天快照，评估 Σp 错价的频率与幅度分布
```

## 6. 数据源与工具（沿用知识库已验证接口）

```text
市场结构：https://gamma-api.polymarket.com/events?slug=...
          negRiskMarketID / clobTokenIds / outcomes / outcomePrices（JSON 字符串需解析）
订单簿：  https://clob.polymarket.com/book?token_id=...
标记价：  https://clob.polymarket.com/prices-history?market=...
成交：    https://data-api.polymarket.com/trades|positions|activity
链上：    https://polygon-bor-rpc.publicnode.com（需浏览器 UA）
浏览器：  https://polygonscan.com/address/<合约地址>#code（读字节码/ABI）
```

## 7. 相关文档索引

```text
知识库：      docs/forensics/KNOWLEDGE_BASE.md（第 0 节通俗版必读）
策略库：      docs/forensics/STRATEGY_LIBRARY.md（S-F1 完整集套利）
扫描器规格：  docs/forensics/SCANNER_SPEC.md（两级扫描，交给实现者）
案例跟踪：    docs/forensics/cases/README.md
官方地址鉴别：注意 CTF Exchange V2（0xe111...）profile 页是托管汇总，不是交易者
```

## 8. 会话启动清单（新会话第一步）

```text
1. [x] 读本文件 -> KNOWLEDGE_BASE.md 第 0 节 -> SCANNER_SPEC.md。
2. [x] 核对第 1 节合约地址与字节码存在性（eth_getCode，7+2 地址全部有效；
       修正 0xada2 名称标注，补充 0xe222 V2 负风险交易所）。
3. [x] 复跑 Σp 粗筛（tools/forensics_sigma_scan.py），对比 2026-08-15 快照。
4. [x] 对 NFL/NBA/MLB/金球奖/共和党提名盘做订单簿二级精筛，
       结果写入研究日志 docs/forensics/CONTRACT_ARB_LOG.md。
5. [x] 通读 ctf-exchange-v2 + neg-risk-ctf-adapter 源码；
       疑似缺陷清单：无新增可报级缺陷（POL-EX-4 复核为 Informational）。
```

研究日志：docs/forensics/CONTRACT_ARB_LOG.md（每次研究后更新）。

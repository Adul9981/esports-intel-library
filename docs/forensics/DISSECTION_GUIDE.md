# 逐场拆解流程与反馈提升机制

最后更新：2026-08-12

目标：一场一场拆解 e46m3（及其他目标交易者）的公开交易，把"他具体怎么做的"还原成
可复制的规则，并持续用新案例校准规则。

## 1. 选题（拆哪一场）

从 cases/README.md 待拆清单取优先级最高的场次。优先级规则：

```text
1. 该地址在事件内有 CONVERSION/SPLIT/MERGE 动作（可拆 Convert 机制）
2. 负风险多选项组（腿数 >= 5）
3. 已结算或接近结算（能算最终盈亏）
4. 动作密度高（一次拆解信息量大）
```

## 2. 取数（只读）

按 KNOWLEDGE_BASE.md 第 4 节接口清单执行：

```text
1. 事件结构：gamma /events?slug=<slug>（组 ID、clobTokenIds、outcomes）
2. 该地址全部成交：/trades?user=<addr>&eventId=<id>&takerOnly=false&start=1
3. 该地址活动：/activity?user=<addr>&eventId=<id>&type=CONVERSION,SPLIT,MERGE,REDEEM,TRADE
4. 价格历史：/prices-history（组内每个 token，1 分钟粒度）
5. 持仓：/positions?user=<addr>
```

原始数据落盘 docs/forensics/data/e46m3/（只增不改）。

## 3. 链上解码

对每笔 CONVERSION（及关键 MERGE/SPLIT/REDEEM）：

```text
1. 取 transactionHash -> publicnode RPC（带浏览器 UA）
2. 解码 CTF TransferBatch：输入腿（用户交出）/ 输出腿（用户收回）
3. 解码 ERC20 Transfer：USDC/pUSD 流向
4. token id -> 档位/方向（gamma clobTokenIds 映射）
5. 填入拆解卡的"链上账目"
```

方法细节与坑见 KNOWLEDGE_BASE.md 第 5 节。

## 4. 计算

```text
1. Σp 时间序列：组内各档 YES 价格逐分钟求和（min/max、每次 Convert 时点取值）
2. 每轮循环现金流：买入成本 vs Convert 现金 + Merge 现金
3. 单轮毛利：X × (Σp − 1)（理论值）与实际现金流对照
4. 结算盈亏：赢档份额 × $1 − 累计成本（已结算场次）
```

## 5. 填写拆解卡

新建 cases/YYYY-MM-DD_<slug>/README.md，模板：

```markdown
# 拆解卡：<事件标题>

## 基本信息
| 项 | 值 |
| --- | --- |
| 事件 slug | |
| 组 ID / 腿数 | |
| 时间窗 | |
| 结算结果 | |

## 他的动作时间线
| 时间 | 类型 | 方向/档位 | 数量 | 价格/金额 | 交易哈希 |

## Σp 证据
min / max / 每次 Convert 时点取值

## 链上账目（关键交易）
输入腿 / 输出腿 / 现金 / 对手方

## 盈亏拆解
每轮现金流入流出、毛利、估算

## 模式标签
S-F1 / S-F2 / ...（可多标签）

## 可复制点
触发条件、参数、仓位、频率

## 风险与失败模式

## 结论与下一步验证
```

## 6. 反馈闭环（每场）

```text
1. 对照 STRATEGY_LIBRARY.md：命中策略 -> 更新样本数/成熟度/参数；
   新模式 -> 登记 L0 观察。
2. 新知回流 KNOWLEDGE_BASE.md：新规则、新账号、新接口、新坑。
3. 更新 cases/README.md 跟踪表（已拆/待拆/优先级）。
4. 更新 docs/task/PROJECT_PROGRESS.md 任务 7 状态。
```

## 7. 提升复盘（每 5 场或每周）

输出 cases/SUMMARY.md：

```text
1. 模式稳定度：同一策略在 N 场中命中次数、毛利区间
2. 平均毛利与摩擦：滑点、返佣占比
3. 风险信号：哪些场次接近失效
4. 参数调整建议：Σp 阈值、单轮金额、频率
5. 下一步验证任务：新场次选题
```

## 8. 升级门槛

```text
策略从 L1 建议升 L2 回测：需要 >= 3 场同模式案例 + Σp 历史回测
策略从 L2 升 L3 小额实盘：需要回测通过 + 用户确认 + 项目风控放行
任何升级先更新 STRATEGY_LIBRARY.md 与 PROJECT_PROGRESS.md
```

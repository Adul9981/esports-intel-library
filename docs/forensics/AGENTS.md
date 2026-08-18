# docs/forensics/ 模块规则

职责：交易者拆解域——把外部交易者的公开行为拆成可复现的规则，沉淀为知识库与策略库，
为项目自身策略提供"对手方视角"的可复制素材。

启动顺序：先读根 AGENTS.md，再读本文件，然后按任务类型读：

```text
查概念/规则/账号/数据源  -> KNOWLEDGE_BASE.md
查可复制策略与成熟度      -> STRATEGY_LIBRARY.md
逐场拆解流程与模板        -> DISSECTION_GUIDE.md
用户行为标签库（试点）    -> USER_LABELING.md
扫描器实现规格            -> SCANNER_SPEC.md
已拆/待拆案例跟踪         -> cases/README.md
原始数据                 -> data/
```

## 结构

```text
docs/forensics/
  AGENTS.md               # 本文件：模块规则
  KNOWLEDGE_BASE.md       # 基础知识库：概念、规则、账号档案、数据源、关键发现
  STRATEGY_LIBRARY.md     # 策略库：从拆解中沉淀的可复制策略（成熟度分级）
  DISSECTION_GUIDE.md     # 逐场拆解流程 + 拆解卡模板 + 反馈提升机制
  SCANNER_SPEC.md         # Σp 错价扫描器 v0 规格（可交给外部实现者）
  data/                   # 基础资料库：原始数据与账号资料（只增不改）
  cases/                  # 逐场拆解案例
    README.md             # 案例跟踪表（已拆/待拆/优先级）
    YYYY-MM-DD_<slug>/    # 每场一个目录，README.md 为拆解卡
```

## 纪律

1. 只读公开数据：Data API / Gamma / CLOB / Polygon RPC 均为只读；本模块不下单、不碰私钥。
2. 结论分级：每条结论标注证据等级——链上解码（最硬）/ 接口数据 / 行为推断（最软）。
3. 复盘诚实：拆解卡只记录事实与可复制点；盈利与亏损同等对待；推断必须标注"推断"。
4. 数据只增不改：data/ 原始 JSON 落盘后不覆盖（补数据另存新文件）；案例按日期新增。
5. 拆解产出必须回流：新规则进 KNOWLEDGE_BASE，新模式进 STRATEGY_LIBRARY，进度进 PROJECT_PROGRESS。
6. 复制有门槛：任何策略进入项目实盘前，必须走成熟度升级（L0 观察 -> L1 建议 -> L2 回测 ->
   L3 小额实盘 -> L4 稳定），并遵守项目风控红线。
7. 文档一律中文；数据文件与代码注释以英文为主。

## 复盘闭环（反馈与提升）

每场拆解完成后：

```text
填写拆解卡（cases/YYYY-MM-DD_<slug>/README.md）
  -> 对照 STRATEGY_LIBRARY 更新样本数/成熟度/参数
  -> 新知回流 KNOWLEDGE_BASE（规则/账号/接口/坑）
  -> 更新 cases/README.md 跟踪表
  -> 更新 docs/task/PROJECT_PROGRESS.md 任务 7 状态
```

每 5 场或每周做一次提升复盘（cases/SUMMARY.md）：模式稳定度、平均毛利、风险信号、参数调整、
下一步验证任务。详见 DISSECTION_GUIDE.md。

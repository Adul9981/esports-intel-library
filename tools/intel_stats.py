#!/usr/bin/env python3
"""Intel signal credibility statistics: source type x signal tag x verification.

Reads knowledge/intel_signals.json and reports:
  - totals by source type / tag / verification status
  - cross table source type x tag
  - verification rates per source type and per tag (among non-pending)
  - market-verification coverage (signals with a price snapshot)

Sample caveat: conclusions only after >=15-20 records per group; the current
output is for registration and directional observation only. Use --json for
machine-readable output (TASK6 情报卡"今日信号"后台统计).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEL_JSON = ROOT / "knowledge" / "intel_signals.json"

SOURCE_LABELS = {
    "caster_co": "二路解说",
    "caster_official": "官方解说",
    "streamer": "主播",
    "official": "官方",
    "community": "社区/朋友",
    "danmaku": "弹幕",
    "user_observation": "用户观察",
}
TAG_LABELS = {
    "style": "风格/打法",
    "form": "状态",
    "proficiency": "熟练度",
    "bp": "BP/阵容",
    "tempo": "节奏/阅读",
    "event": "事件/风险",
}
VERIFY_LABELS = {
    "pending": "待验证",
    "confirmed": "应验",
    "partially_confirmed": "部分应验",
    "refuted": "未应验",
}


def load_signals() -> list[dict]:
    store = json.loads(INTEL_JSON.read_text(encoding="utf-8"))
    return store.get("signals", [])


def group_counts(signals: list[dict], key: str, labels: dict) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for s in signals:
        val = s
        for part in key.split("."):
            val = val.get(part, None) if isinstance(val, dict) else None
            if val is None:
                val = "unknown"
                break
        if isinstance(val, list):
            for v in val:
                counts[v] += 1
        else:
            counts[val] += 1
    return {labels.get(k, k): counts[k] for k in sorted(counts)}


def cross_table(signals: list[dict]) -> tuple[list[str], dict[str, dict[str, int]]]:
    rows = sorted({s.get("source_type", "?") for s in signals})
    cols = sorted({t for s in signals for t in s.get("tags", [])})
    table = {r: {c: 0 for c in cols} for r in rows}
    for s in signals:
        r = s.get("source_type", "?")
        for t in s.get("tags", []):
            table[r][t] += 1
    return [SOURCE_LABELS.get(r, r) for r in rows], {
        SOURCE_LABELS.get(r, r): {TAG_LABELS.get(c, c): table[r][c] for c in cols}
        for r in rows
    }


def verified_stats(signals: list[dict], key: str) -> dict[str, dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for s in signals:
        val = s.get(key, "unknown")
        if isinstance(val, list):
            for v in val:
                groups[v].append(s)
        else:
            groups[val].append(s)
    out: dict[str, dict] = {}
    for g, items in sorted(groups.items()):
        n = len(items)
        statuses = [s.get("verification", {}).get("status", "pending") for s in items]
        pending = statuses.count("pending")
        confirmed = statuses.count("confirmed")
        partial = statuses.count("partially_confirmed")
        refuted = statuses.count("refuted")
        judged = confirmed + refuted
        rate = confirmed / judged if judged else None
        out[g] = {
            "n": n,
            "pending": pending,
            "confirmed": confirmed,
            "partially_confirmed": partial,
            "refuted": refuted,
            "confirmed_rate": rate,
        }
    return out


def build_report(signals: list[dict]) -> dict:
    verified = [s for s in signals if s["verification"]["status"] != "pending"]
    has_price = sum(
        1
        for s in signals
        if s.get("market_verification", {}).get("price_before") is not None
        or s.get("market_verification", {}).get("price_after") is not None
    )
    return {
        "total": len(signals),
        "by_source": group_counts(signals, "source_type", SOURCE_LABELS),
        "by_tag": group_counts(signals, "tags", TAG_LABELS),
        "by_verification": group_counts(
            signals, "verification.status", VERIFY_LABELS
        ),
        "source_x_tag": cross_table(signals)[1],
        "per_source": verified_stats(signals, "source_type"),
        "per_tag": verified_stats(signals, "tags"),
        "market_verification_coverage": has_price,
        "sample_caveat": "每组 >=15-20 条才出统计结论；当前仅登记与方向观察",
    }


def print_report(r: dict) -> None:
    print(f"主观情报信号统计（knowledge/intel_signals.json，共 {r['total']} 条）\n")
    print("== 按来源类型 ==")
    for k, v in r["by_source"].items():
        print(f"  {k:<8} {v}")
    print("\n== 按信号标签 ==")
    for k, v in r["by_tag"].items():
        print(f"  {k:<8} {v}")
    print("\n== 按应验状态 ==")
    for k, v in r["by_verification"].items():
        print(f"  {k:<8} {v}")
    print("\n== 来源类型 x 信号标签 ==")
    rows = sorted(r["source_x_tag"])
    cols = sorted({c for row in r["source_x_tag"].values() for c in row})
    header = "  " + "".join(f"{c:<10}" for c in ["来源\\标签"] + cols)
    print(header)
    for row in rows:
        cells = r["source_x_tag"][row]
        print("  " + f"{row:<10}" + "".join(f"{cells.get(c, 0):<10}" for c in cols))
    print("\n== 应验率（排除待验证）==")
    for section, data in (("按来源", r["per_source"]), ("按标签", r["per_tag"])):
        print(f"  {section}：")
        for g, st in data.items():
            rate = f"{st['confirmed_rate'] * 100:.0f}%" if st["confirmed_rate"] is not None else "n/a"
            print(
                f"    {g:<8} n={st['n']} 应验 {st['confirmed']} / "
                f"部分 {st['partially_confirmed']} / 未应验 {st['refuted']} "
                f"（应验率 {rate}）"
            )
    print(
        f"\n市场验证覆盖：{r['market_verification_coverage']}/{r['total']} 条有采集前后价格"
    )
    print(f"样本提醒：{r['sample_caveat']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="情报信号可信度统计")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args()
    signals = load_signals()
    report = build_report(signals)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Classify 1-minute/5-minute price series into reversal-pattern-library labels.

Read-only heuristic classifier (发现回测链). Labels follow
docs/framework/REVERSAL_PATTERN_LIBRARY.md (A1-A6 / B1-B4 / C1-C3 / 未知).

Usage:
    python3 tools/classify_pattern.py --snapshot docs/data/snapshots/2026-08-07_lol-fox1-bro2
    python3 tools/classify_pattern.py --file <jsonl> [--side Label]
    python3 tools/classify_pattern.py --snapshots docs/data/snapshots  # 汇总全部快照

输出：每侧形态标签 + 关键指标（低点/高点/触底时机/反弹斜率/50% 穿越/低于阈值时长）。
启发式 v1.3：规则基于已确立形态定义，样本累计后需校准阈值。
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_series(path: str) -> list[tuple[float, float]]:
    pts = []
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        ts = row["timestamp"].replace("Z", "+00:00")
        pts.append((datetime.fromisoformat(ts).timestamp(), float(row["price"])))
    pts.sort()
    return pts


def crossings_50(pts: list[tuple[float, float]]) -> int:
    n = 0
    for i in range(1, len(pts)):
        a, b = pts[i - 1][1], pts[i][1]
        if (a - 0.5) * (b - 0.5) < 0:
            n += 1
    return n


def time_after_min(pts, level: float) -> float | None:
    lo = min(pts, key=lambda x: x[1])
    for p in pts:
        if p[0] >= lo[0] and p[1] >= level:
            return (p[0] - lo[0]) / 60.0
    return None


def market_type_of(name: str) -> str:
    low = name.lower()
    if "moneyline" in low or low == name.replace("_", "-") and "game" not in low and "map" not in low:
        return "moneyline"
    return "game"


def classify(pts: list[tuple[float, float]], market_type: str = "game") -> dict[str, Any]:
    pre = pts[0][1]
    end = pts[-1][1]
    lo = min(pts, key=lambda x: x[1])
    hi = max(pts, key=lambda x: x[1])
    c50 = crossings_50(pts)
    dur_below = {}
    for lv in (0.10, 0.20, 0.30):
        seg = [p for p in pts if p[1] <= lv]
        dur_below[lv] = ((seg[-1][0] - seg[0][0]) / 60.0) if seg else 0.0
    t50 = time_after_min(pts, 0.50)
    t70 = time_after_min(pts, 0.70)
    t99 = time_after_min(pts, 0.995)
    span_min = (pts[-1][0] - pts[0][0]) / 60.0

    # 形态判定（启发式 v1.3，顺序重要；A4 仅整场 Moneyline，B1/B2 按市场层级分）
    labels: list[str] = []
    if hi[1] >= 0.85 and end <= 0.10 and hi[0] is not None:
        collapse_min = (pts[-1][0] - hi[0]) / 60.0
        if market_type == "moneyline":
            labels.append("B2_死亡螺旋")
        elif collapse_min <= 30:
            labels.append("B1_尾盘崩塌")
        else:
            labels.append("B2_死亡螺旋")
    if lo[1] <= 0.10 and end >= 0.70:
        labels.append("A1_V型极值反转")
    if 0.13 <= lo[1] <= 0.35 and end >= 0.70:
        labels.append("A2_中位U型反转")
    if pre >= 0.60 and lo[1] >= 0.35 and end >= 0.90:
        labels.append("A3_折价修复")
    if market_type == "moneyline" and pre <= 0.45 and end >= 0.90:
        labels.append("A4_下狗整场反转")
    if lo[1] <= 0.45 and t50 is not None and end <= 0.05:
        labels.append("B3_假反弹后归零")
    if pre > lo[1] + 0.20 and t50 is None and end <= 0.10:
        labels.append("B4_直线阴跌")
    if 0.20 <= lo[1] and hi[1] <= 0.80 and c50 >= 4:
        labels.append("C1_中位震荡")
    if pre <= 0.40 and end >= 0.70 and not any(l.startswith("A") for l in labels):
        labels.append("C2_早期缩距/热门确立")
    if pre >= 0.60 and lo[1] >= 0.55 and end >= 0.95:
        labels.append("热门全程压制")
    if 0.35 <= pre <= 0.62 and lo[1] >= 0.33 and end >= 0.95 and not any(l.startswith(("A", "B")) for l in labels):
        labels.append("C2_五五开开局碾压")
    # A5 W 型双底：两个局部低点（粗略：低点后反弹 >=15c 再回落至低点+5c 内）
    a5 = False
    if lo[1] <= 0.45:
        lo_idx = min(range(len(pts)), key=lambda i: pts[i][1])
        rebound = next((p[1] for p in pts[lo_idx:] if p[1] >= lo[1] + 0.15), None)
        if rebound is not None:
            after = [p for p in pts[lo_idx:] if p[1] >= rebound]
            if after:
                t_reb = after[0][0]
                dip2 = min((p[1] for p in pts if p[0] > t_reb), default=None)
                if dip2 is not None and dip2 <= lo[1] + 0.05 and dip2 >= lo[1] - 0.03:
                    a5 = True
    if a5:
        labels.append("A5_W型双底")
    if lo[1] < 0.10 and t50 is not None and t50 <= 10:
        labels.append("A6_反弹确认")
    if lo[1] <= 0.20 and end <= 0.10 and t50 is None and hi[1] <= 0.40:
        labels.append("B4_低开阴跌")
    if 0.42 <= pre <= 0.58 and lo[1] <= 0.30 and end >= 0.45 and not any(l.startswith(("A", "B")) for l in labels):
        labels.append("A7_强强对话错杀")
    if not labels:
        labels.append("未知")

    return {
        "pre": round(pre, 4),
        "end": round(end, 4),
        "low": round(lo[1], 4),
        "low_time": datetime.fromtimestamp(lo[0], tz=timezone.utc).strftime("%H:%M"),
        "high": round(hi[1], 4),
        "high_time": datetime.fromtimestamp(hi[0], tz=timezone.utc).strftime("%H:%M"),
        "cross50": c50,
        "t50_min": round(t50, 1) if t50 is not None else None,
        "t70_min": round(t70, 1) if t70 is not None else None,
        "t99_min": round(t99, 1) if t99 is not None else None,
        "dur_below": {str(int(lv * 100)): round(d, 1) for lv, d in dur_below.items()},
        "span_min": round(span_min, 1),
        "labels": labels,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify price series into pattern-library labels.")
    parser.add_argument("--snapshot", default="", help="目录（docs/data/snapshots/<slug>）")
    parser.add_argument("--file", default="", help="单个 JSONL 文件")
    parser.add_argument("--snapshots", default="", help="全部快照根目录，输出汇总统计")
    parser.add_argument("--side", default="", help="单文件时标注方向名")
    parser.add_argument("--market-type", default="", help="game|moneyline（--file 模式用；默认按文件名推断）")
    args = parser.parse_args()

    rows = []
    if args.file:
        mtype = args.market_type or ("moneyline" if "moneyline" in args.file else "game")
        r = classify(load_series(args.file), mtype)
        print(json.dumps({**{"side": args.side, "file": args.file}, **r}, ensure_ascii=False, indent=1))
        return 0

    targets: list[tuple[str, str, str]] = []
    if args.snapshot:
        for f in sorted(Path(args.snapshot).glob("*.jsonl")):
            targets.append((Path(args.snapshot).name, str(f), f.stem))
    elif args.snapshots:
        for d in sorted(Path(args.snapshots).iterdir()):
            if d.is_dir():
                for f in sorted(d.glob("*.jsonl")):
                    targets.append((d.name, str(f), f.stem))
    else:
        raise SystemExit("需要 --snapshot / --file / --snapshots 之一")

    print(f"{'快照':<30}{'文件':<42}{'低点':<7}{'高点':<7}{'穿越':<4}{'到50':<6}{'到100':<7}形态")
    from collections import Counter
    freq = Counter()
    for snap, path, name in targets:
        try:
            mtype = "moneyline" if "moneyline" in name else "game"
            r = classify(load_series(path), mtype)
        except Exception as exc:
            print(f"{snap:<30}{name:<42} ERR {str(exc)[:40]}")
            continue
        for lab in r["labels"]:
            freq[lab] += 1
        print(
            f"{snap:<30}{name[:40]:<42}{r['low']:<7}{r['high']:<7}{r['cross50']:<4}"
            f"{str(r['t50_min']):<6}{str(r['t99_min']):<7}{'/'.join(r['labels'])}"
        )
    print("\n形态频率统计：")
    for lab, n in freq.most_common():
        print(f"  {lab:<22} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

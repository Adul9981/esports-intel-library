#!/usr/bin/env python3
"""Pattern library audit: re-validation counts + new-pattern discovery.

Runs every 2-3 days (or on demand) to answer two questions:
  1. How many times has each existing pattern been re-validated?
  2. Are there new patterns emerging (unknown series clustered by shape;
     >=3 similar unknowns -> candidate per the 未知形态通道 rule)?

Usage:
    python3 tools/pattern_audit.py

Output:
    reports/pattern_audit_YYYY-MM-DD.md   report
    reports/pattern_audit_baseline.json   baseline for the next delta
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from classify_pattern import classify, load_series

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "docs" / "data" / "snapshots"
REPORTS = ROOT / "reports"
DEFAULT_BASELINE = REPORTS / "pattern_audit_baseline.json"


def shape_signature(r: dict) -> tuple:
    """Rough shape signature used to cluster unknown series."""
    return (int(r["pre"] * 10), int(r["end"] * 10), int(r["low"] * 20), r["cross50"] >= 4)


def audit(snapshots_root: Path):
    freq: Counter = Counter()
    series: list[dict] = []
    unknowns: list[dict] = []
    for d in sorted(snapshots_root.iterdir()):
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.jsonl")):
            # 兼容新旧命名：旧格式 game1_we_price_1m.jsonl；新格式 slug__N__Team.jsonl。
            is_old = "price" in f.stem
            is_new = "__0__" in f.stem or "__1__" in f.stem
            if not (is_old or is_new):
                continue
            if "classification" in f.stem or "validation" in f.stem:
                continue
            name = f"{d.name}/{f.stem}"
            try:
                mtype = (
                    "moneyline"
                    if "moneyline" in f.stem or ("__" in f.stem and "-game" not in f.stem)
                    else "game"
                )
                r = classify(load_series(str(f)), mtype)
            except Exception as exc:
                print(f"skip {name}: {exc}", file=sys.stderr)
                continue
            row = {"snapshot": name, **r}
            series.append(row)
            for lab in r["labels"]:
                freq[lab] += 1
            if r["labels"] == ["未知"]:
                unknowns.append(row)
    return dict(freq), series, unknowns


def write_report(path: Path, today: str, freq: dict, baseline: dict, series_n: int, snap_names: list, unknowns: list):
    prev_freq = baseline.get("freq", {})
    prev_snaps = set(baseline.get("snapshots", []))
    new_snaps = [s for s in snap_names if s not in prev_snaps]

    lines = [f"# 形态库巡检（{today}）", ""]
    lines.append(f"快照序列：{series_n} 条；快照组：{len(snap_names)} 组"
                 f"（较上次新增 {len(new_snaps)} 组：{', '.join(new_snaps) or '无'}）")
    lines.append("")
    lines.append("## 1. 已知形态复验计数")
    lines.append("")
    lines.append("| 形态 | 累计样本 | 上次 | 本周期新增验证 |")
    lines.append("| --- | --- | --- | --- |")
    for lab, n in sorted(freq.items(), key=lambda x: -x[1]):
        prev = prev_freq.get(lab, 0)
        lines.append(f"| {lab} | {n} | {prev} | +{n - prev} |")

    groups = defaultdict(list)
    for u in unknowns:
        groups[shape_signature(u)].append(u)
    candidates = {sig: g for sig, g in groups.items() if len(g) >= 3}
    lines.append("")
    lines.append("## 2. 新形态发现（未知序列聚类）")
    lines.append("")
    if candidates:
        lines.append("候选新形态（同图形 >=3 个，按未知形态通道登记流程处理）：")
        for sig, g in sorted(candidates.items(), key=lambda x: -len(x[1])):
            lines.append(f"- signature {sig} x{len(g)}：{', '.join(x['snapshot'] for x in g)}")
    else:
        lines.append("无候选新形态（未知序列未达 3 个相似图形，继续观察）。")
    if unknowns:
        lines.append("")
        lines.append(f"未知序列清单（{len(unknowns)} 条）：")
        for u in unknowns:
            lines.append(f"- {u['snapshot']}（pre {u['pre']} / end {u['end']} / low {u['low']} / x50 {u['cross50']}）")
    lines.append("")
    lines.append("## 3. 结论与建议")
    lines.append("")
    lines.append("- 样本仍不足以对单形态下统计结论（目标 >=10/形态），继续每 2-3 天巡检累计。")
    lines.append("- 新形态候选按 REVERSAL_PATTERN_LIBRARY 三.6 流程登记（图形 -> 观察池 -> 回测 -> 入库）。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshots", default=str(SNAPSHOTS), help="snapshots root")
    ap.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="baseline json path")
    args = ap.parse_args()

    snap_root = Path(args.snapshots)
    baseline_path = Path(args.baseline)
    baseline = (
        json.loads(baseline_path.read_text(encoding="utf-8"))
        if baseline_path.exists()
        else {"date": "", "snapshots": [], "freq": {}}
    )

    freq, series, unknowns = audit(snap_root)
    snap_names = sorted({s["snapshot"].split("/")[0] for s in series})
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = REPORTS / f"pattern_audit_{today}.md"
    write_report(out, today, freq, baseline, len(series), snap_names, unknowns)

    baseline_path.write_text(
        json.dumps({"date": today, "snapshots": snap_names, "freq": freq}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    groups = Counter(shape_signature(u) for u in unknowns)
    n_candidates = sum(1 for g in groups.values() if g >= 3)
    print(f"巡检完成：{len(series)} 条序列；报告 {out}")
    top = sorted(freq.items(), key=lambda x: -x[1])[:8]
    print("形态频率 top：", ", ".join(f"{k} {v}" for k, v in top))
    print(f"未知序列：{len(unknowns)} 条；候选新形态组：{n_candidates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""EDGE LOG statistics: group recorded edges by info type / edge vs conviction.

Reads knowledge/edges.json (one record per trade edge) and prints a summary.
Sample caveat: conclusions only after >=15-20 records per group; the current
output is for registration and directional observation only.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDGES = ROOT / "knowledge" / "edges.json"


def summarize(items: list[dict]) -> tuple[int, int, float, float | None]:
    n = len(items)
    wins = sum(1 for x in items if x.get("outcome") == "win")
    with_pnl = [x for x in items if x.get("pnl") is not None]
    pnl = sum(x["pnl"] for x in with_pnl)
    avg = pnl / len(with_pnl) if with_pnl else None
    return n, wins, pnl, avg


def main() -> int:
    rows = json.loads(EDGES.read_text(encoding="utf-8"))
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_type[r.get("type", "other")].append(r)
    by_edge = {"edge": [], "conviction": []}
    for r in rows:
        by_edge["edge" if r.get("type") != "conviction" else "conviction"].append(r)

    print(f"EDGE LOG 统计（knowledge/edges.json，共 {len(rows)} 条）\n")
    print("== 按信息差类型 ==")
    print(f"{'类型':<14}{'n':<4}{'胜':<4}{'总盈亏':<10}{'平均盈亏':<10}")
    for typ in sorted(by_type):
        n, w, p, a = summarize(by_type[typ])
        avg_s = f"{a:+.1f}" if a is not None else "n/a"
        print(f"{typ:<14}{n:<4}{w:<4}{p:+.1f}    {avg_s}")
    print("\n== 有信息差 vs 纯信心 ==")
    for key, label in (("edge", "有信息差"), ("conviction", "纯信心")):
        n, w, p, a = summarize(by_edge[key])
        avg_s = f"{a:+.1f}" if a is not None else "n/a"
        print(f"{label:<8} n={n:<3} 胜 {w}  总盈亏 {p:+.1f}  平均 {avg_s}")

    print(
        "\n样本提醒：分组结论需 >=15-20 条/组；当前仅登记与方向观察。\n"
        "已知偏差：回填样本多为口述估值、与仓位大小混杂（未归一化）；pnl 为 null 的条目只计数不计盈亏。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

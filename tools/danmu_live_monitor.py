#!/usr/bin/env python3
"""Live danmaku monitor: analyze a growing JSONL every N seconds and refresh an HTML page.

Reads the JSONL being appended by tools/fetch_huya_danmu.py, runs the intel
analysis every --interval seconds (default 300 = 5 min), and rewrites an
auto-refreshing SAP/Apple-style HTML page. Only reads the JSONL (no conflicts
with the writer process).

Usage:
  python3 tools/danmu_live_monitor.py \
      --input docs/data/danmu/shuoshuo/2026-08-18_323444.jsonl \
      --html reports/intel_danmu_live_KC-GX_2026-08-18.html \
      --title "KC vs GX 弹幕实时监控" --interval 300
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import time
from collections import Counter
from pathlib import Path

import danmu_intel


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def render_page(intel: dict, deep: dict, title: str, updated: str) -> str:
    m = intel["meta"]
    bursts = intel.get("density_bursts", [])
    peak_html = "、".join(f'{esc(b["minute_utc"])} UTC {b["count"]} 条/分' for b in bursts[:3])

    blocks = ""

    # 1) 队伍情报
    teams = sorted(intel["teams"].items(), key=lambda kv: -kv[1]["mentions"])[:4]
    if teams:
        rows_html = ""
        for n, d in teams:
            tone = "分歧" if d["pos"] and d["neg"] else ("正面" if d["pos"] > d["neg"] else "负面")
            sample = "".join(f'<li>{esc(s)}</li>' for s in d["samples"][:3])
            rows_html += (
                f'<div class="row"><b>{esc(n)}</b> 提及 {d["mentions"]} · 情绪：{tone}'
                f'（正 {d["pos"]} / 负 {d["neg"]}）<ul>{sample}</ul></div>'
            )
        blocks += f'<section class="card"><h2>队伍情报</h2>{rows_html}</section>'

    # 2) 局势
    sit = intel["situation"]
    if sit["count"]:
        samples = "".join(f'<li>{esc(s)}</li>' for s in sit["samples"][:4])
        peak_line = f'<p class="meta">关键时刻：{peak_html}</p>' if peak_html else ""
        blocks += f'<section class="card"><h2>局势分析</h2>{peak_line}<ul>{samples}</ul></section>'

    # 3) 选手状态
    players = sorted(intel["players"].items(), key=lambda kv: -kv[1]["mentions"])[:4]
    if players:
        rows_html = ""
        for n, d in players:
            tone = "正面" if d["pos"] > d["neg"] else ("负面" if d["neg"] > d["pos"] else "分歧")
            sample = "".join(f'<li>{esc(s)}</li>' for s in d["samples"][:2])
            rows_html += f'<div class="row"><b>{esc(n)}</b> {tone}（正 {d["pos"]} / 负 {d["neg"]}）<ul>{sample}</ul></div>'
        blocks += f'<section class="card"><h2>选手状态</h2>{rows_html}</section>'

    # 4) 盘口讨论
    odds = intel["odds_discussion"]
    if odds["count"]:
        samples = "".join(f'<li>{esc(s)}</li>' for s in odds["samples"][:4])
        blocks += f'<section class="card"><h2>盘口讨论（{odds["count"]} 条）</h2><ul>{samples}</ul></section>'

    # 5) 集体质疑（灰信号）
    gray = intel["gray_signals"]
    gray_focus = [s for s in gray["samples"] if any(k in s for k in ["假", "剧本", "买了", "送分", "卡盘", "演"])]
    if gray["count"] and gray_focus:
        samples = "".join(f'<li>{esc(s)}</li>' for s in gray_focus[:4])
        blocks += f'<section class="card"><h2>集体质疑（{gray["count"]} 条灰信号，观众视角）</h2><ul>{samples}</ul></section>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<title>{esc(title)}</title>
<style>
:root{{--bg:#f5f5f7;--card:#fff;--ink:#1d1d1f;--sub:#86868b;--accent:#0071e3;--line:#e8e8ed}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,sans-serif;line-height:1.55;padding:24px 16px 56px}}
.wrap{{max-width:820px;margin:0 auto}}
h1{{font-size:24px;font-weight:700;margin-bottom:4px}}
.sub{{color:var(--sub);font-size:13px;margin-bottom:18px}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}}
.stat{{background:var(--card);border-radius:14px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
.stat .num{{font-size:22px;font-weight:700;color:var(--accent)}}
.stat .lbl{{color:var(--sub);font-size:12px}}
.card{{background:var(--card);border-radius:14px;padding:16px;margin-bottom:12px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
h2{{font-size:16px;font-weight:600;margin-bottom:8px}}
.meta{{color:var(--sub);font-size:12px;margin-bottom:8px}}
.row{{padding:6px 0;border-bottom:1px solid var(--line);font-size:13px}}
.row:last-child{{border-bottom:none}}
.s{{color:var(--sub);font-size:12px}}
.burst{{padding:6px 0;border-bottom:1px solid var(--line);font-size:13px}}
.burst .t{{color:var(--accent);font-weight:600;margin-right:8px}}
.dm{{padding:5px 0;border-bottom:1px solid var(--line);font-size:13px}}
.nick{{color:var(--accent);font-weight:600;margin-right:6px}}
li{{margin-left:18px;font-size:13px}}
.note{{color:var(--sub);font-size:11px;margin-top:16px;line-height:1.7}}
@media(max-width:640px){{.stats{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><div class="wrap">
<h1>{esc(title)}</h1>
<p class="sub">最后更新：{esc(updated)} · 页面每 5 分钟自动刷新 · 数据源 {esc(m['window_utc'][0])} 起</p>
<div class="stats">
<div class="stat"><div class="num">{m['total']}</div><div class="lbl">弹幕累计</div></div>
<div class="stat"><div class="num">{m['active_users']}</div><div class="lbl">用户</div></div>
<div class="stat"><div class="num">{m['density_per_min']}/分</div><div class="lbl">平均密度</div></div>
<div class="stat"><div class="num">{len(bursts)}</div><div class="lbl">峰值事件</div></div>
</div>
{blocks}
<p class="note">弹幕为低可信度信号需聚合；灰信号（假赛/剧本类）只作风险标注非证据；比赛结果待官方确认。<br>
工具：tools/danmu_live_monitor.py · 规则：knowledge/DANMU_CAPTURE_RULES.md</p>
</div></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="弹幕实时监控（5 分钟刷新 HTML）")
    parser.add_argument("--input", required=True, help="JSONL 弹幕文件（抓取进程在写）")
    parser.add_argument("--html", required=True, help="输出 HTML 路径")
    parser.add_argument("--title", default="直播间弹幕实时监控")
    parser.add_argument("--interval", type=int, default=300, help="刷新间隔秒（默认 300）")
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.html)
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"监控启动：{inp} -> {out}，每 {args.interval}s 刷新一次", flush=True)
    while True:
        rows = []
        if inp.exists():
            rows = [
                json.loads(line)
                for line in inp.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        intel = danmu_intel.analyze(rows) if rows else danmu_intel.analyze([])
        deep = danmu_intel.analyze_deep(rows) if rows else danmu_intel.analyze_deep([])
        updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        out.write_text(
            render_page(intel, deep, args.title, updated), encoding="utf-8"
        )
        print(f"[{updated}] 已刷新 {out}（{len(rows)} 条弹幕）", flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())

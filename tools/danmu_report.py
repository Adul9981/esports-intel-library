#!/usr/bin/env python3
"""Generate a lightweight SAP/Apple-style HTML briefing from a Huya danmaku JSONL.

Reads one JSONL file (ts/nick/text, produced by tools/fetch_huya_danmu.py) and
emits a mobile-first HTML page with: overview stats, hot topics, match/odds
related signal samples, keyword frequency, and a data-source note.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
from collections import Counter
from pathlib import Path


TOPIC_KEYWORDS = {
    "阵容/BP": ["阵容", "BP", "选", "英雄", "ban", "pick"],
    "队伍评价": ["菜", "强", "怂", "懦夫", "无敌", "发瘟", "拉胯", "翻盘"],
    "选手状态": ["姑妈", "guma", "poby", "hype", "mithy", "zeus", "faker", "chovy", "米卢", "状态"],
    "盘口/数字": ["人头", "让分", "盘", "48", "6.5", "7.5", "700", "接", "小卖部"],
    "比赛进程": ["龙魂", "经济", "一波", "大龙", "小龙", "塔", "开局", "比分"],
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_rows(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_html(rows: list[dict], title: str, source: str) -> str:
    users = Counter(r["nick"] for r in rows)
    ts_list = [r["ts"] for r in rows]
    t0, t1 = min(ts_list), max(ts_list)
    win = datetime.datetime.fromtimestamp(t0).strftime("%m-%d %H:%M")
    wend = datetime.datetime.fromtimestamp(t1).strftime("%m-%d %H:%M")
    minutes = max((t1 - t0) / 60, 0.5)
    density = round(len(rows) / minutes, 1)

    topic_blocks = ""
    for topic, kws in TOPIC_KEYWORDS.items():
        hits = [r for r in rows if any(k.lower() in r["text"].lower() for k in kws)]
        if not hits:
            continue
        samples = hits[:6]
        sample_html = "".join(
            f'<div class="dm"><span class="nick">{esc(r["nick"])}</span>'
            f'<span class="txt">{esc(r["text"])}</span></div>'
            for r in samples
        )
        topic_blocks += (
            f'<section class="card"><h2>{topic}</h2>'
            f'<p class="meta">命中 {len(hits)} 条（样本 {len(samples)} 条）</p>'
            f"{sample_html}</section>"
        )

    top_words = Counter()
    word_list = [
        "T1", "DNS", "TH", "KT", "HLE", "GEN", "LPL", "LCK", "LEC",
        "姑妈", "guma", "Poby", "hype", "蛇女", "寒冰", "牛头", "皇子",
        "泰坦", "阵容", "菜", "强", "怂", "无敌", "翻盘", "龙魂",
        "经济", "人头", "让分", "接", "48", "6.5", "7.5",
    ]
    for r in rows:
        for kw in word_list:
            if kw.lower() in r["text"].lower():
                top_words[kw] += 1
    top_html = "".join(
        f'<span class="kw">{esc(k)}<b>{c}</b></span>'
        for k, c in top_words.most_common(24)
    )

    active = "、".join(f"{n}({c})" for n, c in users.most_common(6))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
:root {{ --bg:#f5f5f7; --card:#ffffff; --ink:#1d1d1f; --sub:#86868b; --accent:#0071e3; --line:#e8e8ed; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:var(--bg); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,sans-serif; line-height:1.55; padding:24px 16px 48px; }}
.wrap {{ max-width:760px; margin:0 auto; }}
h1 {{ font-size:24px; font-weight:700; letter-spacing:-0.01em; margin-bottom:6px; }}
.sub {{ color:var(--sub); font-size:14px; margin-bottom:20px; }}
.stats {{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin-bottom:20px; }}
.stat {{ background:var(--card); border-radius:16px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
.stat .num {{ font-size:28px; font-weight:700; color:var(--accent); }}
.stat .lbl {{ color:var(--sub); font-size:13px; margin-top:2px; }}
.card {{ background:var(--card); border-radius:16px; padding:18px; margin-bottom:14px; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
h2 {{ font-size:17px; font-weight:600; margin-bottom:2px; }}
.meta {{ color:var(--sub); font-size:12px; margin-bottom:10px; }}
.dm {{ padding:7px 0; border-bottom:1px solid var(--line); font-size:14px; }}
.dm:last-child {{ border-bottom:none; }}
.nick {{ color:var(--accent); font-weight:600; margin-right:8px; }}
.kw {{ display:inline-block; background:#f0f4ff; color:var(--accent); border-radius:999px; padding:5px 12px; margin:3px 4px 3px 0; font-size:13px; }}
.kw b {{ margin-left:5px; opacity:.7; }}
.note {{ color:var(--sub); font-size:12px; margin-top:18px; line-height:1.7; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{esc(title)}</h1>
  <p class="sub">数据源：{esc(source)} · 弹幕为低可信度信号，需聚合参考</p>
  <div class="stats">
    <div class="stat"><div class="num">{len(rows)}</div><div class="lbl">弹幕总数</div></div>
    <div class="stat"><div class="num">{len(users)}</div><div class="lbl">活跃用户</div></div>
    <div class="stat"><div class="num">{win} – {wend}</div><div class="lbl">抓取窗口</div></div>
    <div class="stat"><div class="num">{density}</div><div class="lbl">条/分钟</div></div>
  </div>
  <section class="card">
    <h2>高频关键词</h2>
    <p class="meta">按出现次数排序（弹幕文本匹配）</p>
    <div>{top_html}</div>
  </section>
  {topic_blocks}
  <section class="card">
    <h2>活跃用户</h2>
    <p class="meta">发言最多（示例）</p>
    <div class="dm">{esc(active)}</div>
  </section>
  <p class="note">
    说明：本页由 tools/danmu_report.py 从 JSONL 弹幕数据自动生成。<br>
    弹幕可信度低（需聚合、去噪），直播间梗（如"小卖部/健身房"）不属于比赛情报；
    每条弹幕可溯源到 JSONL 原文，仅供情报参考，不作为交易依据。
  </p>
</div>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="弹幕数据 -> HTML 情报简报")
    parser.add_argument("--input", required=True, help="JSONL 弹幕文件")
    parser.add_argument("--title", default="直播间弹幕情报简报")
    parser.add_argument("--out", required=True, help="输出 HTML 路径")
    args = parser.parse_args()

    rows = load_rows(Path(args.input))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(rows, args.title, str(Path(args.input))), encoding="utf-8")
    print(f"已生成：{out}（{len(rows)} 条弹幕）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

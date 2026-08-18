#!/usr/bin/env python3
"""Fetch 1-minute Polymarket price snapshots for an esports event into docs/data/snapshots/.

Read-only data collection tool (发现回测链, 永远只读):

1. Gamma /events?slug=... -> event + markets (token ids, outcomes).
2. CLOB /prices-history?market=<TOKEN_ID>&startTs=..&endTs=..&interval=1d&fidelity=1
   -> 1-minute price series (falls back to interval=1m&fidelity=10).
3. Write JSONL per market+side + README with key points.

Known pitfalls handled:
- clobTokenIds / outcomes in gamma are JSON-encoded strings -> json.loads.
- "market" parameter is the TOKEN id (asset id), NOT the condition id.
- interval=1d&fidelity=1 returns true 1-minute bars only for short-lived markets;
  long-lived markets are down-sampled (~5-13 min) -> median spacing is reported
  in README so resolution is transparent.
- SSL flakiness -> retries.

Usage:
    python3 tools/fetch_price_snapshot.py --slug lol-blg-tes-2026-08-07
    python3 tools/fetch_price_snapshot.py --url <polymarket-url>
    python3 tools/fetch_price_snapshot.py --slug <slug> --start-ts 1786... --end-ts 1786...
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = PROJECT_ROOT / "docs" / "data" / "snapshots"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

PROP_KEYWORDS = (
    "Both Teams",
    "Slay Baron",
    "Slay a Dragon",
    "Destroy Inhibitors",
    "Quadra Kill",
    "Penta Kill",
    "Odd/Even",
    "Handicap",
    "Total Games",
    "Team to Win Map",
)


def http_json(url: str, tries: int = 6) -> Any:
    last: Exception | None = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "polymarket-snapshot/0.1"})
            with urllib.request.urlopen(req, timeout=40) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5)
    raise RuntimeError(f"fetch fail {url}: {last}")


def parse_list(market: dict[str, Any], key: str) -> list[Any]:
    value = market.get(key)
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return []
    return value or []


def is_winner_market(market: dict[str, Any]) -> bool:
    question = market.get("question", "") or ""
    slug = market.get("slug", "") or ""
    if any(k in question for k in PROP_KEYWORDS):
        return False
    return "Winner" in question or slug.endswith(("game1", "game2", "game3")) or "BO3" in question


def fetch_history(token_id: str, start_ts: int, end_ts: int) -> list[dict[str, Any]]:
    for interval, fidelity in (("1d", 1), ("1m", 10)):
        params = urllib.parse.urlencode(
            {"market": token_id, "startTs": start_ts, "endTs": end_ts, "interval": interval, "fidelity": fidelity}
        )
        try:
            history = http_json(f"{CLOB}/prices-history?{params}").get("history", [])
            if history:
                return history
        except Exception:
            continue
    return []


def median_spacing(history: list[dict[str, Any]]) -> int:
    if len(history) < 2:
        return 0
    deltas = [history[i + 1]["t"] - history[i]["t"] for i in range(len(history) - 1)]
    return int(statistics.median(deltas))


def fmt_utc(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_hm(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M")


def write_readme(outdir: Path, event: dict[str, Any], markets: list[dict[str, Any]], notes: list[str]) -> None:
    lines = [
        f"# {event.get('title')} 赔率快照",
        "",
        f"来源：Polymarket CLOB `/prices-history`（1 分钟粒度，工具 tools/fetch_price_snapshot.py）",
        "",
        f"事件：`{event.get('slug')}`",
        "",
        "文件：",
        "",
        "```text",
    ]
    for market in markets:
        outcomes = parse_list(market, "outcomes")
        for index in range(len(parse_list(market, "clobTokenIds"))):
            side = outcomes[index] if index < len(outcomes) else f"outcome{index}"
            fname = f"{market.get('slug', 'market')}__{index}__{side.replace(' ', '_')}.jsonl"
            lines.append(f"{fname}")
    lines += [
        "```",
        "",
        "关键点位（UTC，价格 = 该侧）：",
        "",
        "```text",
    ]
    for market in markets:
        outcomes = parse_list(market, "outcomes")
        prices = parse_list(market, "outcomePrices")
        lines.append(f"{market.get('question', market.get('slug'))}：{outcomes} -> {prices}")
    lines += ["```", "", "说明：", "", "```text"]
    lines += notes
    lines += ["```", ""]
    (outdir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _classify_and_report(outdir: Path) -> None:
    """取数后自动跑形态分类：输出已知/未知标签，未知进观察池清单。"""
    outdir = Path(outdir)
    try:
        import classify_pattern as cp
    except Exception as exc:  # noqa: BLE001
        print(f"[classify] 跳过形态分类：{exc}")
        return
    rows: list[dict[str, Any]] = []
    unknowns: list[str] = []
    for f in sorted(outdir.glob("*.jsonl")):
        if f.name == "README.md":
            continue
        try:
            pts = cp.load_series(str(f))
            mtype = "moneyline" if "moneyline" in f.name else "game"
            r = cp.classify(pts, mtype)
        except Exception as exc:  # noqa: BLE001
            print(f"[classify] {f.name} ERR {exc}")
            continue
        rows.append(
            {"file": f.name, "labels": r["labels"], "low": r["low"], "high": r["high"], "low_time": r["low_time"]}
        )
        print(f"[classify] {f.name}: {'/'.join(r['labels'])}")
        if "未知" in r["labels"]:
            unknowns.append(f.name)
    if rows:
        (outdir / "classification.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8"
        )
    if unknowns:
        print("[classify] 未知形态（进观察池）：" + ", ".join(unknowns))
    else:
        print("[classify] 无未知形态")


def _validate_snapshots(outdir: Path) -> None:
    """数据完整性校验：双方价格和≈1、时间戳单调/不重复、结算/分辨率标注。"""
    outdir = Path(outdir)
    issues: list[str] = []
    groups: dict[str, list[tuple[str, list[dict[str, Any]]]]] = {}
    for f in sorted(outdir.glob("*.jsonl")):
        if f.name in ("README.md", "classification.jsonl", "validation.jsonl"):
            continue
        rows = [json.loads(line) for line in open(f, encoding="utf-8")]
        if not rows:
            issues.append(f"{f.name}: 空文件")
            continue
        groups.setdefault(rows[0]["market_slug"], []).append((f.name, rows))

    for market, items in groups.items():
        if len(items) == 2:
            maps = []
            for _, rows in items:
                maps.append({r["timestamp"]: r["price"] for r in rows})
            common = sorted(set(maps[0]) & set(maps[1]))
            bad = [t for t in common if abs(maps[0][t] + maps[1][t] - 1) > 0.05]
            if bad:
                issues.append(f"{market}: 双方价格和偏差>5% 共 {len(bad)}/{len(common)} 个共同时间戳")
        for name, rows in items:
            ts = [r["timestamp"] for r in rows]
            if ts != sorted(ts):
                issues.append(f"{market}/{name}: 时间戳乱序")
            if len(set(ts)) != len(ts):
                issues.append(f"{market}/{name}: 时间戳重复 {len(ts) - len(set(ts))} 个")
            end = rows[-1]["price"]
            if 0.02 < end < 0.98:
                issues.append(f"{market}/{name}: 末价 {end} 未结算/异常（需复核）")
    if issues:
        (outdir / "validation.jsonl").write_text(
            "\n".join(json.dumps({"issue": x}, ensure_ascii=False) for x in issues) + "\n", encoding="utf-8"
        )
    for issue in issues:
        print(f"[validate] {issue}")
    if not issues:
        print("[validate] 数据完整性校验通过")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch 1-minute price snapshots for an esports event.")
    parser.add_argument("--slug", default="", help="Polymarket event slug, e.g. lol-blg-tes-2026-08-07")
    parser.add_argument("--url", default="", help="Polymarket market URL (slug extracted automatically)")
    parser.add_argument("--outdir", default="", help="Output dir (default docs/data/snapshots/<slug>)")
    parser.add_argument("--start-ts", type=int, default=0, help="Start unix ts (default: now-24h)")
    parser.add_argument("--end-ts", type=int, default=0, help="End unix ts (default: now)")
    args = parser.parse_args()

    slug = args.slug
    if args.url:
        slug = args.url.rstrip("/").split("/")[-1]
    if not slug:
        raise SystemExit("需要 --slug 或 --url")

    event = http_json(f"{GAMMA}/events?slug={urllib.parse.quote(slug)}")
    if not isinstance(event, list) or not event:
        raise SystemExit(f"事件不存在或为空：{slug}")
    event = event[0]

    now = int(time.time())
    start_ts = args.start_ts or now - 24 * 3600
    end_ts = args.end_ts or now

    markets = [m for m in event.get("markets", []) if is_winner_market(m)]
    if not markets:
        raise SystemExit(f"事件 {slug} 没有可用的 Winner/Moneyline 市场")

    outdir = Path(args.outdir) if args.outdir else SNAPSHOT_ROOT / slug
    outdir.mkdir(parents=True, exist_ok=True)

    notes: list[str] = []
    for market in markets:
        outcomes = parse_list(market, "outcomes")
        tokens = parse_list(market, "clobTokenIds")
        for index, token in enumerate(tokens):
            history = fetch_history(token, start_ts, end_ts)
            if not history:
                notes.append(f"{market.get('slug')} 第{index}侧：无价格历史（窗口外或市场无数据）")
                continue
            spacing = median_spacing(history)
            if spacing > 120:
                notes.append(
                    f"{market.get('slug')} 第{index}侧：中位间隔 {spacing}s（非 1 分钟，市场生命周期过长被降采样）"
                )
            side = outcomes[index] if index < len(outcomes) else f"outcome{index}"
            fname = f"{market.get('slug', 'market')}__{index}__{side.replace(' ', '_')}.jsonl"
            with (outdir / fname).open("w", encoding="utf-8") as fh:
                for point in history:
                    row = {
                        "timestamp": fmt_utc(point["t"]),
                        "event_slug": slug,
                        "market_slug": market.get("slug"),
                        "side": side,
                        "price": point["p"],
                    }
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            low = min(history, key=lambda x: x["p"])
            high = max(history, key=lambda x: x["p"])
            print(
                f"{market.get('slug')} | {side[:24]:<24} | pts={len(history):<5} "
                f"间隔={spacing}s | 低={low['p']}@{fmt_hm(low['t'])} 高={high['p']}@{fmt_hm(high['t'])}"
            )

    write_readme(outdir, event, markets, notes)
    _classify_and_report(outdir)
    _validate_snapshots(outdir)
    print(f"快照已写入：{outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

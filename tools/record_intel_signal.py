#!/usr/bin/env python3
"""Record and verify subjective intel signals (Huya casters / streamers / danmaku).

Stage-1 manual pipeline for the subjective intel library:
  - add:   append a new signal to knowledge/intel_signals.json
  - verify: backfill post-match verification status for an existing signal

The JSON store follows schemas/intel_signal.schema.json; this tool performs a
lightweight validation without external dependencies.

Usage:
  python3 tools/record_intel_signal.py add --date 2026-08-08 --match lol-... \
      --source-person "957" --source-type caster_co --credibility high \
      --quote "..." --tag proficiency --object "Team X" --object-type team \
      --direction "..." --phase in_game
  python3 tools/record_intel_signal.py verify --id IS-2026-08-08-001 \
      --status confirmed --note "..."
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEL_JSON = ROOT / "knowledge" / "intel_signals.json"

SOURCE_TYPES = {
    "caster_co",
    "caster_official",
    "streamer",
    "official",
    "community",
    "danmaku",
    "user_observation",
}
CREDIBILITY = {"high", "medium", "low"}
TAGS = {"style", "form", "proficiency", "bp", "tempo", "event"}
OBJECT_TYPES = {"team", "player", "league", "unknown"}
PHASES = {"pre_match", "in_game", "post_match"}
VERIFY_STATUS = {"pending", "confirmed", "partially_confirmed", "refuted"}
TIMEFRAMES = {"durable", "short_lived"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_store() -> dict:
    if not INTEL_JSON.exists():
        return {"version": "1.0", "updated_at": now_utc(), "signals": []}
    return json.loads(INTEL_JSON.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    store["updated_at"] = now_utc()
    INTEL_JSON.write_text(
        json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def next_id(date: str, signals: list[dict]) -> str:
    prefix = f"IS-{date}-"
    max_seq = 0
    for s in signals:
        if s.get("id", "").startswith(prefix):
            m = re.search(r"-(\d{3})$", s["id"])
            if m:
                max_seq = max(max_seq, int(m.group(1)))
    return f"{prefix}{max_seq + 1:03d}"


def validate_add(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date or ""):
        errors.append("--date 格式应为 YYYY-MM-DD")
    if not args.match:
        errors.append("--match 必填（比赛 slug）")
    if not args.source_person:
        errors.append("--source-person 必填（来源人/来源房间）")
    if args.source_type not in SOURCE_TYPES:
        errors.append(f"--source-type 必须在 {sorted(SOURCE_TYPES)}")
    if args.credibility not in CREDIBILITY:
        errors.append(f"--credibility 必须在 {sorted(CREDIBILITY)}")
    if not args.quote:
        errors.append("--quote 必填（原话摘录）")
    if not args.tags:
        errors.append("--tag 至少一个（可重复传）")
    for t in args.tags:
        if t not in TAGS:
            errors.append(f"--tag {t} 不在 {sorted(TAGS)}")
    if not args.object:
        errors.append("--object 必填（队伍/选手/待确认）")
    if args.object_type not in OBJECT_TYPES:
        errors.append(f"--object-type 必须在 {sorted(OBJECT_TYPES)}")
    if not args.direction:
        errors.append("--direction 必填（方向含义；无法确定时写'只记录不交易'）")
    if args.phase not in PHASES:
        errors.append(f"--phase 必须在 {sorted(PHASES)}")
    if args.minute is not None and (args.minute < 1 or args.minute > 180):
        errors.append("--minute 应在 1-180")
    if args.timeframe not in TIMEFRAMES:
        errors.append(f"--timeframe 必须在 {sorted(TIMEFRAMES)}")
    for name, val in (("--price-before", args.price_before), ("--price-after", args.price_after)):
        if val is not None and not (0.0 <= val <= 1.0):
            errors.append(f"{name} 应在 0-1")
    return errors


def cmd_add(args: argparse.Namespace) -> int:
    errors = validate_add(args)
    if errors:
        for e in errors:
            print(f"错误：{e}", file=sys.stderr)
        return 2

    store = load_store()
    signal_id = next_id(args.date, store["signals"])
    record = {
        "id": signal_id,
        "date": args.date,
        "event_slug": args.match,
        "source_person": args.source_person,
        "source_type": args.source_type,
        "credibility": args.credibility,
        "quote": args.quote,
        "tags": sorted(set(args.tags)),
        "object": args.object,
        "object_type": args.object_type,
        "direction": args.direction,
        "beneficial_side": args.beneficial_side,
        "timing": {
            "phase": args.phase,
            "minute": args.minute,
            "stream_offset_min": args.stream_offset,
            "utc": args.utc,
            "note": args.timing_note,
        },
        "market_verification": {
            "market": args.market,
            "price_before": args.price_before,
            "price_after": args.price_after,
            "note": args.market_note,
        },
        "verification": {
            "status": "pending",
            "note": "赛后回填是否应验",
            "verified_at": None,
        },
        "timeframe": args.timeframe,
        "expected_patterns": args.expected_patterns,
        "related_signal_ids": args.related_ids,
        "linked_profiles": args.linked_profiles,
        "source_url": args.source_url,
        "recorded_at": now_utc(),
        "note": args.note,
    }

    if args.dry_run:
        print(f"[dry-run] 将新增 {signal_id}")
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0

    store["signals"].append(record)
    save_store(store)
    print(f"已新增信号 {signal_id}（{args.source_person} / {args.quote[:40]}）")
    print(f"库位置：{INTEL_JSON}（共 {len(store['signals'])} 条）")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    store = load_store()
    for s in store["signals"]:
        if s["id"] == args.id:
            s["verification"]["status"] = args.status
            s["verification"]["note"] = args.note
            s["verification"]["verified_at"] = now_utc()
            save_store(store)
            print(f"已回填 {args.id} -> {args.status}")
            print(f"依据：{args.note}")
            return 0
    print(f"错误：未找到信号 {args.id}", file=sys.stderr)
    return 2


def split_multi(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="主观情报信号录入/回填工具")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="新增一条信号")
    add.add_argument("--date", required=True, help="采集日期 YYYY-MM-DD")
    add.add_argument("--match", required=True, help="比赛 slug，如 lol-t1-hle1-2026-08-08")
    add.add_argument("--source-person", required=True, help="来源人/来源房间")
    add.add_argument("--source-type", required=True, choices=sorted(SOURCE_TYPES))
    add.add_argument("--credibility", required=True, choices=sorted(CREDIBILITY))
    add.add_argument("--quote", required=True, help="原话摘录（短摘录）")
    add.add_argument("--tag", action="append", default=[], help="信号标签，可重复传")
    add.add_argument("--object", required=True, help="对象（队伍/选手/待确认）")
    add.add_argument("--object-type", required=True, choices=sorted(OBJECT_TYPES))
    add.add_argument("--direction", required=True, help="方向含义（利好哪侧）")
    add.add_argument("--beneficial-side", default=None, help="结构化利好侧（队伍名，可选）")
    add.add_argument("--phase", required=True, choices=sorted(PHASES))
    add.add_argument("--minute", type=int, default=None, help="比赛分钟")
    add.add_argument("--stream-offset", type=int, default=None, help="直播/录播流偏移分钟")
    add.add_argument("--utc", default=None, help="采集时刻 UTC ISO8601")
    add.add_argument("--timing-note", default=None)
    add.add_argument("--market", default=None, help="市场 game1/game2/moneyline")
    add.add_argument("--price-before", type=float, default=None, help="采集前价格 0-1")
    add.add_argument("--price-after", type=float, default=None, help="采集后价格 0-1")
    add.add_argument("--market-note", default=None)
    add.add_argument("--timeframe", default="short_lived", choices=sorted(TIMEFRAMES))
    add.add_argument("--expected-pattern", action="append", default=[], help="可映射形态，可重复")
    add.add_argument("--related-id", action="append", default=[], help="关联信号 id，可重复")
    add.add_argument("--linked-profile", action="append", default=[], help="沉淀画像引用，可重复")
    add.add_argument("--source-url", default=None, help="直播间/录播链接")
    add.add_argument("--note", default=None)
    add.add_argument("--dry-run", action="store_true", help="只校验与预览，不写库")
    add.set_defaults(func=cmd_add)

    verify = sub.add_parser("verify", help="回填赛后应验结果")
    verify.add_argument("--id", required=True, help="信号 id，如 IS-2026-08-08-001")
    verify.add_argument("--status", required=True, choices=sorted(VERIFY_STATUS))
    verify.add_argument("--note", required=True, help="应验/未应验依据")
    verify.set_defaults(func=cmd_verify)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "add":
        args.tags = [t for raw in args.tag for t in split_multi(raw)]
        args.expected_patterns = [p for raw in args.expected_pattern for p in split_multi(raw)]
        args.related_ids = [r for raw in args.related_id for r in split_multi(raw)]
        args.linked_profiles = [l for raw in args.linked_profile for l in split_multi(raw)]
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

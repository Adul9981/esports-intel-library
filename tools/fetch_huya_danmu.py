#!/usr/bin/env python3
"""Fetch live danmaku from a Huya room via the real-url WebSocket client.

Lightweight live-danmaku collector (no browser, no protocol reverse-engineering):
reuses the open-source Tars/WebSocket implementation from
https://github.com/wbt5/real-url (clone kept at /tmp/real-url/danmu).

Dependencies (installed in the intel venv /tmp/intel-whisper-venv):
  aiohttp, requests, pycryptodome

Usage:
  /tmp/intel-whisper-venv/bin/python tools/fetch_huya_danmu.py \
      --url https://www.huya.com/323444 --seconds 60 --out /tmp/danmu.json
  /tmp/intel-whisper-venv/bin/python tools/fetch_huya_danmu.py \
      --url https://www.huya.com/323444 --out docs/data/danmu/2026-08-17.jsonl

--seconds 0 (default) means run until Ctrl-C; each danmaku is appended to
--out as JSONL immediately (safe on interrupt). Only user danmaku (text) is
collected; gifts / enters are skipped.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

DANMU_LIB = Path("/tmp/real-url/danmu")


async def collect(url: str, seconds: int, out_path: Path | None) -> int:
    sys.path.insert(0, str(DANMU_LIB))
    from danmaku import DanmakuClient  # local import: external lib

    q: asyncio.Queue = asyncio.Queue()
    dc = DanmakuClient(url, q)
    fh = open(out_path, "a", encoding="utf-8") if out_path else None
    start = time.time()
    count = 0

    async def pump() -> None:
        nonlocal count
        while True:
            if seconds and time.time() - start >= seconds:
                break
            try:
                m = await asyncio.wait_for(q.get(), timeout=1)
                if m["msg_type"] == "danmaku":
                    count += 1
                    rec = {
                        "ts": round(time.time(), 2),
                        "nick": m.get("name", ""),
                        "uid": m.get("uid", 0),
                        "text": m["content"],
                    }
                    print(f"[{count}] {m['name']}: {m['content']}", flush=True)
                    if fh:
                        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        fh.flush()
            except asyncio.TimeoutError:
                pass

    pump_task = asyncio.create_task(pump())
    start_task = asyncio.create_task(dc.start())
    try:
        await pump_task
    except KeyboardInterrupt:
        pass
    finally:
        start_task.cancel()
        if fh:
            fh.close()
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="虎牙直播间实时弹幕抓取（轻量）")
    parser.add_argument("--url", required=True, help="直播间链接，如 https://www.huya.com/323444")
    parser.add_argument("--seconds", type=int, default=0, help="抓取时长（秒，0=持续到 Ctrl-C）")
    parser.add_argument("--out", default=None, help="JSONL 输出路径（可选，边抓边写）")
    args = parser.parse_args()

    count = asyncio.run(collect(args.url, args.seconds, Path(args.out) if args.out else None))
    label = f"{args.seconds}s" if args.seconds else "本次会话"
    print(f"\n== {label} 共 {count} 条弹幕 ==")
    if args.out:
        print(f"数据已追加：{args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

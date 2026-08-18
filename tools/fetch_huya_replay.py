#!/usr/bin/env python3
"""Download a Huya live replay (直播录像) audio for the intel pipeline.

Note: Huya replay CDN segments are region-restricted (mainland-China IPs only;
non-CN IPs get 404 on segments while the m3u8 playlist is readable). Run this
tool from a mainland-China network (the user's machine or a domestic VPS).

Usage:
  python3 tools/fetch_huya_replay.py --id 1121405272
  python3 tools/fetch_huya_replay.py --url https://www.huya.com/video/play/1121405272.html
  python3 tools/fetch_huya_replay.py --id 1121405272 --format 360P --out /tmp

Writes:
  <out>/huya_<id>_<date>.m4a            audio-only (96k)
  <out>/huya_<id>_<date>.meta.json      title / duration / upload date / live-record info
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="下载虎牙直播录像音频（需中国大陆网络）")
    parser.add_argument("--id", help="视频 ID，如 1121405272")
    parser.add_argument("--url", help="视频链接（与 --id 二选一）")
    parser.add_argument("--format", default="360P", choices=["360P", "720P", "1080P"])
    parser.add_argument("--out", default="/tmp", help="输出目录（默认 /tmp）")
    args = parser.parse_args()

    if args.id and args.url:
        print("错误：--id 与 --url 二选一", file=sys.stderr)
        return 2
    url = args.url or f"https://www.huya.com/video/play/{args.id}.html"
    vid = args.id or url.rstrip("/").split("/")[-1].replace(".html", "")

    # 1) metadata
    meta_raw = run(["yt-dlp", "-J", "--no-warnings", url])
    if not meta_raw:
        print("错误：yt-dlp 无法解析视频（确认网络/链接）", file=sys.stderr)
        return 1
    meta = json.loads(meta_raw)
    date = str(meta.get("upload_date", "unknown"))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / f"huya_{vid}_{date}"
    (out_dir / f"huya_{vid}_{date}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    print(f"标题：{meta.get('title')}")
    print(f"时长：{meta.get('duration', 0)/3600:.2f} 小时 | 上传：{date}")

    # 2) download audio
    cmd = [
        "yt-dlp",
        "-f", args.format,
        "--extract-audio", "--audio-format", "m4a", "--audio-quality", "5",
        "--retries", "10", "--fragment-retries", "10", "--socket-timeout", "30",
        "-o", f"{stem}.%(ext)s",
        url,
    ]
    print("开始下载（中国大陆网络）...")
    code = subprocess.run(cmd).returncode
    if code != 0:
        print("下载失败，检查网络是否为大陆 IP（虎牙回放分片限制区域）", file=sys.stderr)
        return code
    print(f"完成：{stem}.m4a")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

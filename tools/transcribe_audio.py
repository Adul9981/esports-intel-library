#!/usr/bin/env python3
"""Transcribe recorded live-stream audio to Chinese text (intel pipeline stage 2).

Uses faster-whisper locally (no cloud dependency). Run with the intel venv:
  /tmp/intel-whisper-venv/bin/python tools/transcribe_audio.py <audio_or_video_file>

Outputs timestamped segments to stdout; optionally writes a transcript file.
VAD filtering is on by default to skip silence/static (common in intermission).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="本地转录直播音频（faster-whisper）")
    parser.add_argument("input", help="音频/视频文件路径")
    parser.add_argument("--model", default="large-v3-turbo", help="Whisper 模型名")
    parser.add_argument("--language", default="zh", help="语言（默认中文）")
    parser.add_argument("--vad", action="store_true", default=True, help="VAD 过滤静音")
    parser.add_argument("--no-vad", action="store_false", dest="vad")
    parser.add_argument("--out", default=None, help="转录文本输出路径（可选）")
    parser.add_argument("--json", action="store_true", help="同时输出 JSON 段落到 stdout")
    parser.add_argument("--hf-home", default="/tmp/hf-cache", help="HF 模型缓存目录")
    args = parser.parse_args()

    from faster_whisper import WhisperModel  # local import: venv-only dependency

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        args.input, language=args.language, vad_filter=args.vad
    )
    print(f"# 转录信息: 语言={info.language} 概率={info.language_probability:.2f} "
          f"音频时长={info.duration:.1f}s 模型={args.model}")

    lines: list[str] = []
    json_segments: list[dict] = []
    for s in segments:
        text = s.text.strip()
        if not text:
            continue
        line = f"[{s.start:7.1f}-{s.end:7.1f}] {text}"
        print(line)
        lines.append(f"[{s.start:.1f}-{s.end:.1f}] {text}")
        json_segments.append(
            {"start": round(s.start, 2), "end": round(s.end, 2), "text": text}
        )

    if args.out:
        Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"# 转录已保存: {args.out}")
    if args.json:
        print("\n# JSON\n" + json.dumps(json_segments, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

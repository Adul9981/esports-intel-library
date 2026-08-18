#!/usr/bin/env python3
"""Daily pattern review + inactivity/content warnings (automation entry point).

Requirement mapping:
  1. 每天执行形态复盘: runs tools/pattern_audit.py (re-validation counts per
     pattern + new-pattern candidate detection), reports the audit report path.
  2. 连续几天没有输入 -> 预警: tracks the last date with new user input
     (reviews / trades / edges / snapshots); escalates warnings at 3 / 5 / 7 days
     so the user can judge: temporarily not playing, giving up, or a special case.
  3. 每天正常扫描: if new content exists, note it (update flow is done by the
     agent/automation reading this output); if no content for >=3 days, remind.

State: runtime/pattern_review_state.json
Usage (daily): python3 tools/daily_pattern_review.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "runtime" / "pattern_review_state.json"

# Warning thresholds (days without new input / content).
WARN_DAYS = (3, 5, 7)

INPUT_DIRS = (
    ROOT / "knowledge" / "reviews",
    ROOT / "knowledge" / "trades",
    ROOT / "docs" / "data" / "snapshots",
    ROOT / "knowledge" / "edges.json",
)


def latest_input_date() -> date:
    """Latest modification date across user-facing inputs."""
    latest = date(1970, 1, 1)
    for p in INPUT_DIRS:
        if p.is_file():
            latest = max(latest, datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).date())
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    latest = max(latest, datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).date())
    return latest


def new_content_since(state: dict) -> list[str]:
    """New snapshot groups / reviews / trades files vs last run."""
    seen = set(state.get("seen_files", []))
    found = []
    roots = [
        ROOT / "docs" / "data" / "snapshots",
        ROOT / "knowledge" / "reviews",
        ROOT / "knowledge" / "trades",
    ]
    for root in roots:
        for f in sorted(root.rglob("*")):
            if f.is_file() and str(f) not in seen:
                found.append(str(f))
    return found


def run_audit() -> tuple[int, str]:
    """Run pattern_audit.py and return (returncode, tail of output)."""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "pattern_audit.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()[-800:]


def warn_text(label: str, days: int) -> str:
    if days >= 7:
        return f"🔴 已连续 {days} 天没有新{label}。若为放弃请归档交接；若为特殊情况请说明；若只是暂停请确认恢复时间。"
    if days >= 5:
        return f"🔶 已连续 {days} 天没有新{label}，项目进入停滞观察期。请判断：暂时不玩 / 放弃 / 特殊情况？"
    return f"⚠️ 已连续 {days} 天没有新{label}。是暂时不玩、放弃、还是有特殊情况？建议确认后决定是否调整。"


def main() -> int:
    today = date.today()
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    last_input = latest_input_date()
    last_input_str = state.get("last_input_date", "")
    no_input_days = (today - last_input).days if last_input_str == str(last_input) else 0
    no_content_days = state.get("no_content_days", 0)

    found = new_content_since(state)
    if found:
        no_content_days = 0
    else:
        no_content_days += 1

    print(f"== 每日形态复盘（{today}）==")
    rc, tail = run_audit()
    print(f"形态巡检：{'成功' if rc == 0 else '失败（rc=%d）' % rc}")
    print(tail)

    if found:
        print(f"\n✅ 发现新内容 {len(found)} 项（快照/复盘/交易）——按既有流程更新形态库/策略库/HTML。")
        for f in found[:8]:
            print(f"   - {f}")
        if len(found) > 8:
            print(f"   ... 共 {len(found)} 项")
    else:
        print("\n今日扫描：无新内容（无新快照/复盘/交易）。")

    if no_input_days in WARN_DAYS:
        print(f"\n{warn_text('输入', no_input_days)}")
    if no_content_days in WARN_DAYS:
        print(f"\n{warn_text('内容', no_content_days)}")

    # Persist state: register all currently known input files + last input date.
    seen = set()
    for root in [ROOT / "docs" / "data" / "snapshots", ROOT / "knowledge" / "reviews", ROOT / "knowledge" / "trades"]:
        seen.update(str(f) for f in root.rglob("*") if f.is_file())
    seen.add(str(ROOT / "knowledge" / "edges.json"))
    state.update(
        {
            "last_run": str(today),
            "last_input_date": str(last_input),
            "no_content_days": no_content_days,
            "seen_files": sorted(seen),
        }
    )
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

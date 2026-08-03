#!/usr/bin/env python3
"""Computes the current/next Takt release phase for today and writes current.json
for TRMNL to poll. Run daily via GitHub Actions (or cron)."""
import json
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).parent
RELEASES = json.loads((HERE / "releases.json").read_text())


def parse(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def find_release(today: date):
    for i, r in enumerate(RELEASES):
        start, end = parse(r["start"]), parse(r["end"])
        if start <= today <= end:
            total = (end - start).days + 1
            elapsed = (today - start).days + 1
            nxt = RELEASES[i + 1] if i + 1 < len(RELEASES) else None
            return {
                "status": "in_phase",
                "release": r["release"],
                "start": r["start"],
                "end": r["end"],
                "day": elapsed,
                "total_days": total,
                "days_remaining": (end - today).days,
                "next_release": nxt["release"] if nxt else None,
                "next_start": nxt["start"] if nxt else None,
            }
        if today < start:
            gap_days = (start - today).days
            return {
                "status": "between_phases",
                "release": r["release"],
                "start": r["start"],
                "end": r["end"],
                "days_until_start": gap_days,
            }
    return {"status": "no_upcoming_release"}


def main():
    today = date.today()
    result = find_release(today)
    result["today"] = today.isoformat()
    out = HERE / "current.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(out.read_text())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate prices/latest.json for today's post and print the generate.py command.

Usage: python3 tools/check_price.py --after <UTC ISO time the workflow was triggered>
Exit 0 + prints the render command if OK; exit 1 + reason otherwise.

Mon-Fri (Asia/Bahrain): stamp must be <= 5 min old now, and the file must have been
fetched after --after (so it is from this run, not an old one).
Saturday: stamp must be Friday's close (NY date = Friday, NY time >= 16:00); render --closing.
"""
import argparse, datetime as dt, json, pathlib, sys
from zoneinfo import ZoneInfo

ap = argparse.ArgumentParser()
ap.add_argument("--after", required=True)
a = ap.parse_args()

P = pathlib.Path(__file__).resolve().parent.parent / "prices" / "latest.json"
d = json.loads(P.read_text())
utc = dt.timezone.utc
now = dt.datetime.now(utc)
bh = now.astimezone(ZoneInfo("Asia/Bahrain"))
after = dt.datetime.fromisoformat(a.after.replace("Z", "+00:00"))
fetched = dt.datetime.fromisoformat(d["fetched_utc"].replace("Z", "+00:00"))
stamp = dt.datetime.fromtimestamp(d["stamp_unix"], utc)
stamp_ny = stamp.astimezone(ZoneInfo("America/New_York"))
age = (now - stamp).total_seconds() / 60


def fail(msg):
    print("FAIL:", msg, "|", json.dumps(d))
    sys.exit(1)


if d.get("source") != "kitco":
    fail("source is not kitco")
if fetched < after:
    fail(f"price file is old (fetched {d['fetched_utc']}, before trigger {a.after})")
if not (d["low"] <= d["bid"] <= d["high"]):
    fail("low <= bid <= high does not hold")
wd = bh.weekday()  # Mon=0 .. Sun=6
if wd == 6:
    fail("today is Sunday in Bahrain - no post")
closing = wd == 5
if closing:
    friday = (bh - dt.timedelta(days=1)).date()
    if stamp_ny.date() != friday or stamp_ny.hour < 16:
        fail(f"Saturday needs Friday's close, got stamp {d['stamp_ny']}")
else:
    if age > 5 or age < -1:
        fail(f"stamp {d['stamp_ny']} is {age:.1f} min old (max 5)")

date = bh.strftime("%Y-%m-%d")
print(f"OK bid={d['bid']} change={d['change']} low={d['low']} high={d['high']} "
      f"stamp={d['stamp_ny']} age={age:.1f}min closing={closing}")
print(f"python3 generate.py --price {d['bid']:.2f} --change {d['change']:.2f} --low {d['low']:.2f} "
      f"--high {d['high']:.2f} --date {date} --out posts/{date}.png" + (" --closing" if closing else ""))

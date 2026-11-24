#!/usr/bin/env python3
"""Fetch the live gold quote (USD/oz) from Kitco and write prices/latest.json.

Runs on GitHub Actions (workflow gold-price.yml). Reads the quote Kitco embeds in
its page (__NEXT_DATA__ -> GetMetalQuoteV3, symbol AU, currency USD).
Exits non-zero (and writes nothing) if the quote is missing or inconsistent.
"""
import datetime as dt, json, pathlib, re, sys, time, urllib.request
from zoneinfo import ZoneInfo

URLS = ["https://www.kitco.com/charts/gold?nocache=1",
        "https://www.kitco.com/charts/gold?nocache=2",
        "https://www.kitco.com/charts/gold?nocache=3"]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
OUT = pathlib.Path(__file__).resolve().parent.parent / "prices" / "latest.json"


def find_quote(obj):
    if isinstance(obj, dict):
        q = obj.get("GetMetalQuoteV3")
        if isinstance(q, dict) and q.get("symbol") == "AU" and q.get("currency") == "USD" and q.get("results"):
            return q["results"][0]
        for v in obj.values():
            r = find_quote(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_quote(v)
            if r:
                return r
    return None


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html",
                                               "Accept-Language": "en-US,en;q=0.9"})
    body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.S)
    if not m:
        raise ValueError("no __NEXT_DATA__ in page")
    q = find_quote(json.loads(m.group(1)))
    if not q:
        raise ValueError("no AU/USD quote in page data")
    bid, low, high, chg, ts = (q.get(k) for k in ("bid", "low", "high", "change", "timestamp"))
    if None in (bid, low, high, chg, ts):
        raise ValueError(f"missing field in quote: {q}")
    if not (low <= bid <= high):
        raise ValueError(f"inconsistent: low {low} bid {bid} high {high}")
    stamp = dt.datetime.fromtimestamp(ts, dt.timezone.utc)
    now = dt.datetime.now(dt.timezone.utc)
    return {
        "source": "kitco", "url": url,
        "bid": round(bid, 2), "ask": q.get("ask"), "change": round(chg, 2),
        "change_pct": round(q.get("changePercentage", 0), 4),
        "low": round(low, 2), "high": round(high, 2),
        "stamp_unix": ts,
        "stamp_utc": stamp.isoformat().replace("+00:00", "Z"),
        "stamp_ny": stamp.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M %Z"),
        "fetched_utc": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "age_minutes_at_fetch": round((now - stamp).total_seconds() / 60, 1),
    }


errors = []
for i, url in enumerate(URLS):
    try:
        data = fetch(url)
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(data, indent=2) + "\n")
        print(json.dumps(data, indent=2))
        sys.exit(0)
    except Exception as e:  # noqa: BLE001
        errors.append(f"{url}: {e!r}")
        print("FAILED", errors[-1], file=sys.stderr)
        if i < len(URLS) - 1:
            time.sleep(20)
sys.exit("all Kitco tries failed:\n" + "\n".join(errors))

#!/usr/bin/env python3
"""Diagnostic: fetch the Kitco gold page and print what is in it (no parsing decisions)."""
import re, sys, urllib.request, html

URL = "https://www.kitco.com/charts/gold?nocache=1"
req = urllib.request.Request(URL, headers={
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en;q=0.9"})
try:
    r = urllib.request.urlopen(req, timeout=30)
    body = r.read().decode("utf-8", "replace"); print("STATUS", r.status, "LEN", len(body))
except Exception as e:
    print("FETCH ERROR", repr(e)); body = getattr(e, "read", lambda: b"")().decode("utf-8", "replace"); print(body[:1500]); sys.exit(1)

for kw in ["__NEXT_DATA__", "__next_f", "Bid", "Ask", "Day's Range", "Day&#x27;s Range", "Last updated", "NY Time", "cloudflare", "captcha"]:
    print(f"{kw!r}: {body.count(kw)}")
def show(pat, n=4, w=300):
    for m in list(re.finditer(pat, body))[:n]:
        s = body[max(0, m.start()-w): m.end()+w]
        print(f"--- {pat} @{m.start()}\n{s}\n")
for p in [r"Last updated", r"NY Time", r"Day(&#x27;|')s Range", r'"bid"', r'"high"', r'"low"', r'"change"', r'"timestamp"']:
    show(p)

#!/usr/bin/env python3
"""Daily gold price Instagram post generator (@ahmedoraibi).

Usage:
  python3 generate.py --price 3944.40 --change -42.60 --low 3924.30 --high 4001.20 \
      --date 2026-11-12 --out posts/2026-11-12.png [--closing]

Prices are USD per troy ounce (spot). Output: 1080x1350 PNG + caption .txt next to it.
"""
import argparse, datetime, pathlib, asyncio

OZ_G = 31.1034768
USD_BHD = 0.376  # fixed peg
KARATS = [(24, "الأعلى نقاءً · سبائك"), (22, "مشغولات خليجية"), (21, "الأكثر تداولاً"), (18, "مجوهرات")]
DAYS = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس",
          "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
HERE = pathlib.Path(__file__).resolve().parent


def compute(price, change, low, high):
    g24 = price / OZ_G * USD_BHD
    prev = price - change
    return {
        "g24": g24,
        "karats": [(k, label, g24 * k / 24) for k, label in KARATS],
        "oz_bhd": price * USD_BHD,
        "pct": change / prev * 100 if prev else 0,
        "g_change": change / OZ_G * USD_BHD,
        "bar10": g24 * 10,
        "pos": 0 if high == low else max(0, min(1, (price - low) / (high - low))),
    }


def fonts_css():
    f = HERE / "fonts"
    out = []
    for fam, file_prefix, weights in [
        ("Rubik", "rubik", [400, 500, 600, 700]),
        ("Plex", "ibm-plex-sans-arabic", [400, 500, 600, 700]),
    ]:
        for w in weights:
            for sub in ("arabic", "latin"):
                p = f / f"{file_prefix}-{sub}-{w}-normal.woff2"
                if p.exists():
                    out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{p.as_uri()}')}}")
    for w in (400, 500, 600, 700):
        p = f / f"ibm-plex-mono-latin-{w}-normal.woff2"
        out.append(f"@font-face{{font-family:'Mono';font-weight:{w};src:url('{p.as_uri()}')}}")
    return "\n".join(out)


def build_html(a, d, closing):
    v = d_vals
    up = a.change >= 0
    arrow = "▲" if up else "▼"
    cls = "up" if up else "down"
    word = "ارتفاع" if up else "انخفاض"
    date_ar = f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month-1]} {d.year}"
    k = {kk: val for kk, _, val in v["karats"]}
    ch = lambda kk: v["g_change"] * kk / 24
    tag = "سعر الإقفال" if closing else "4:00 م"

    def card(kk, sub):
        return f"""<div class="kc"><div class="kh"><span class="kb">{kk}K</span><span class="kn">عيار {kk}</span></div>
        <div class="kv">{k[kk]:.3f}</div><div class="ku">د.ب / غرام</div>
        <div class="kd {cls}">{arrow} {abs(ch(kk)):.3f}</div></div>"""

    return f"""<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>
{fonts_css()}
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#F3EFE2;--ink:#1C1F26;--gold:#A67C1E;--gold2:#E0BC62;--muted:#77756D;--line:#E3DCC9;--card:#FCFAF4;--green:#2E8B5A;--red:#C0473B;--g2:#4CC48A;--r2:#F08A7E}}
body{{width:1080px;height:1350px;background:var(--bg);font-family:'Plex',sans-serif;color:var(--ink);position:relative;overflow:hidden}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:90px 90px;opacity:.5}}
.wrap{{position:relative;padding:60px 66px 0;height:100%;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.brand{{display:flex;align-items:center;gap:12px;font-size:28px;color:#4a4a48;font-weight:500}}
.pill{{font-family:'Mono';font-weight:600;font-size:22px;letter-spacing:3px;color:var(--gold);background:#EFE3BF;border:1.5px solid #D9C48E;border-radius:40px;padding:11px 24px;display:flex;align-items:center;gap:12px;direction:ltr}}
.pill i{{width:10px;height:10px;border-radius:50%;background:var(--gold)}}
h1{{font-family:'Rubik';font-weight:700;font-size:92px;line-height:1.1;margin-top:30px}}
h1 em{{font-style:normal;color:var(--gold)}}
.date{{font-size:32px;font-weight:500;color:#3a3a38;margin-top:4px;display:flex;align-items:center;gap:16px}}
.hero{{margin-top:34px;background:var(--ink);border-radius:36px;padding:38px 46px;color:#fff;position:relative;overflow:hidden}}
.bars{{position:absolute;left:30px;bottom:40px;width:310px;height:258px}}
.hh{{display:flex;justify-content:space-between;align-items:center}}
.hl{{display:flex;align-items:center;gap:16px}}
.hb{{font-family:'Rubik';font-weight:700;font-size:30px;color:var(--ink);background:var(--gold2);border-radius:14px;padding:6px 16px;direction:ltr}}
.hn{{font-size:34px;font-weight:600}}
.hs{{font-size:22px;color:#A9A69C;margin-top:2px}}
.time{{font-family:'Plex';font-weight:600;font-size:21px;color:var(--gold2);background:var(--ink);border-radius:30px;padding:8px 20px}}
.hv{{display:flex;align-items:baseline;gap:20px;margin-top:22px}}
.hv b{{font-family:'Rubik';font-weight:700;font-size:170px;line-height:.95;color:var(--gold2);letter-spacing:-3px}}
.hv span{{font-size:36px;color:#D8D5CB;font-weight:500}}
.hc{{display:inline-flex;margin-top:22px;font-size:26px;font-weight:600;border-radius:30px;padding:8px 22px}}
.hc.up{{color:var(--g2);background:#4cc48a1f}} .hc.down{{color:var(--r2);background:#f08a7e1f}}
.row{{display:flex;gap:18px;margin-top:20px}}
.kc{{flex:1;background:var(--card);border:1.5px solid var(--line);border-radius:28px;padding:26px 28px}}
.kh{{display:flex;align-items:center;gap:12px}}
.kb{{font-family:'Rubik';font-weight:700;font-size:20px;color:var(--gold);background:#F1E6C6;border-radius:10px;padding:4px 10px;direction:ltr}}
.kn{{font-size:26px;font-weight:700}}
.kv{{font-family:'Rubik';font-weight:700;font-size:58px;margin-top:18px;line-height:1}}
.ku{{font-size:20px;color:var(--muted);margin-top:8px}}
.kd{{font-family:'Rubik';font-size:21px;font-weight:600;margin-top:14px;direction:rtl}}
.up{{color:var(--green)}} .down{{color:var(--red)}}
.mc{{flex:1;background:var(--card);border:1.5px solid var(--line);border-radius:28px;padding:24px 28px}}
.mt{{font-size:22px;color:var(--muted);font-weight:500}}
.mv{{font-family:'Rubik';font-weight:700;font-size:44px;margin-top:10px;direction:ltr;text-align:right}}
.note{{margin-top:auto;font-size:21px;color:var(--muted);text-align:center;padding-bottom:16px}}
.foot{{display:flex;justify-content:space-between;align-items:center;border-top:1.5px solid #D6CDB5;padding:22px 0 44px}}
.handle{{font-family:'Mono';font-size:28px;color:#4a4a48;direction:ltr}}
.src{{font-size:20px;color:var(--muted)}}
</style></head><body><div class="grid"></div><div class="wrap">
<div class="top">
  <div class="brand"><svg width="30" height="34" viewBox="0 0 30 34"><rect x="3" y="10" width="7" height="14" fill="#C99A2E"/><rect x="6" y="4" width="1.6" height="26" fill="#C99A2E"/><rect x="18" y="8" width="7" height="12" fill="none" stroke="#1C1F26" stroke-width="2"/><rect x="20.7" y="3" width="1.6" height="26" fill="#1C1F26"/></svg>أحمد العريبي</div>
  <div class="pill">XAU/USD <i></i></div>
</div>
<h1>سعر <em>الذهب</em> اليوم</h1>
<div class="date">{date_ar}<span class="time">{tag}</span></div>

<div class="hero">
  <svg class="bars" viewBox="0 0 360 300" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="gt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF1BF"/><stop offset=".45" stop-color="#F2CF6B"/><stop offset="1" stop-color="#C9962A"/></linearGradient>
<linearGradient id="gf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E7B948"/><stop offset="1" stop-color="#9C6E14"/></linearGradient>
<linearGradient id="gs" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B8871F"/><stop offset="1" stop-color="#7A540C"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".55" r=".5"><stop offset="0" stop-color="#E0BC62" stop-opacity=".35"/><stop offset="1" stop-color="#E0BC62" stop-opacity="0"/></radialGradient>
<g id="bar">
 <polygon points="20,0 150,0 170,60 0,60" fill="url(#gf)"/>
 <polygon points="30,-38 140,-38 150,0 20,0" fill="url(#gt)"/>
 <polygon points="150,0 140,-38 160,22 170,60" fill="url(#gs)" opacity=".0"/>
 <rect x="52" y="-30" width="66" height="22" rx="4" fill="none" stroke="#B88A24" stroke-width="2" opacity=".7"/>
 <text x="85" y="-14" font-family="Rubik" font-weight="700" font-size="13" fill="#9C6E14" text-anchor="middle">999.9</text>
 <polygon points="34,-34 70,-34 54,-4 26,-4" fill="#fff" opacity=".35"/>
</g>
</defs>
<ellipse cx="180" cy="160" rx="180" ry="140" fill="url(#glow)"/>
<use href="#bar" x="20" y="250"/>
<use href="#bar" x="190" y="250"/>
<use href="#bar" x="105" y="190"/>
<g fill="#FFF6D6"><path d="M300 60 l5 14 14 5 -14 5 -5 14 -5 -14 -14 -5 14 -5z"/><path d="M60 110 l3 9 9 3 -9 3 -3 9 -3 -9 -9 -3 9 -3z" opacity=".8"/><path d="M262 140 l2.5 7 7 2.5 -7 2.5 -2.5 7 -2.5 -7 -7 -2.5 7 -2.5z" opacity=".7"/></g>
</svg>
  <div class="hh">
    <div class="hl"><span class="hb">21K</span><div><div class="hn">غرام عيار 21</div><div class="hs">الأكثر طلباً في البحرين · دينار بحريني</div></div></div>
  </div>
  <div class="hv"><b>{k[21]:.3f}</b></div>
  <div class="hc {cls}">{arrow} {word} {abs(ch(21)):.3f} د.ب عن أمس</div>
</div>

<div class="row">{card(24,'')}{card(22,'')}{card(18,'')}</div>

<div class="row">
  <div class="mc"><div class="mt">الأونصة بالدولار</div><div class="mv">${a.price:,.2f}</div></div>
  <div class="mc"><div class="mt">التغير اليومي</div><div class="mv {cls}">{'+' if up else '−'}{abs(v['pct']):.2f}%</div></div>
</div>

<div class="note">سعر الغرام الخام حسب السعر العالمي المباشر · بدون المصنعية</div>
<div class="foot"><div class="src">المصدر: السعر الفوري العالمي · 1$ = 0.376 د.ب</div><div class="handle">@ahmedoraibi</div></div>
</div></body></html>"""


def caption(a, d, closing):
    v = d_vals
    date_ar = f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month-1]} {d.year}"
    trend = "📈 ارتفاع" if a.change >= 0 else "📉 انخفاض"
    head = "سعر إقفال الذهب" if closing else "سعر الذهب اليوم"
    lines = [f"✨ {head} في البحرين | {date_ar}", "",
             f"⭐ عيار 21: {v['karats'][2][2]:.3f} د.ب",
             f"🥇 عيار 24: {v['karats'][0][2]:.3f} د.ب",
             f"🥇 عيار 22: {v['karats'][1][2]:.3f} د.ب",
             f"🥇 عيار 18: {v['karats'][3][2]:.3f} د.ب", "",
             f"🌍 الأونصة: ${a.price:,.2f} ({trend} {abs(v['pct']):.2f}%)", "",
             "ℹ️ الأسعار للغرام الخام حسب السعر العالمي المباشر، ولا تشمل المصنعية.", "",
             "#سعر_الذهب #الذهب #البحرين #اسعار_الذهب_اليوم #ذهب #XAUUSD #gold #bahrain"]
    return "\n".join(lines)


async def render(html, out):
    from playwright.async_api import async_playwright
    tmp = out.with_suffix(".html")
    tmp.write_text(html, encoding="utf-8")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome") if pathlib.Path("/usr/bin/google-chrome").exists() else await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        await pg.goto(tmp.as_uri())
        await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=str(out))
        await b.close()
    tmp.unlink()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--price", type=float, required=True)
    ap.add_argument("--change", type=float, required=True)
    ap.add_argument("--low", type=float, required=True)
    ap.add_argument("--high", type=float, required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--closing", action="store_true")
    a = ap.parse_args()
    d = datetime.date.fromisoformat(a.date)
    d_vals = compute(a.price, a.change, a.low, a.high)
    out = pathlib.Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(render(build_html(a, d, a.closing), out))
    out.with_suffix(".txt").write_text(caption(a, d, a.closing), encoding="utf-8")
    print(out)
    print(out.with_suffix(".txt").read_text(encoding="utf-8"))

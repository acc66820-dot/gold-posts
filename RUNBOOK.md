# Daily gold post — runbook (Instagram @ahmedoraibi, 8:00 AM Bahrain)

**Schedule:** Mon–Fri = live price at 8:00 AM. Saturday = Friday's closing price at 8:00 AM (valid Sat + Sun). **No post on Sunday** — if today (Asia/Bahrain) is Sunday, stop immediately without posting or notifying.

Run this end to end, unattended. Timezone: Asia/Bahrain (UTC+3). Metricool brand blogId: `7116567`.
Golden rule: **never publish a price that isn't verified live.** If any check fails, do not schedule a post — notify the user instead (SendUserMessage, and PushNotification if available) with the reason.

## 1. Setup
- Make sure the code is the LATEST from GitHub: if `gold-posts/` already exists, run `git fetch origin main && git checkout -B main origin/main && git reset --hard origin/main` (a fresh `git clone` fails on an existing folder and leaves stale code). Then confirm `generate.py` has `USD_BHD = 0.38` and `FACTORS = {24: 0.0321, 22: 0.0294, 21: 0.028, 18: 0.024}` — if not, do not post; notify the user.
- Check `python3 -c "import playwright"` and `/usr/bin/google-chrome`. If playwright is missing: `pip install --break-system-packages playwright && python3 -m playwright install chromium`.

## 2. Wait until 07:55 Bahrain time
- `TZ=Asia/Bahrain date` — if earlier than 07:55, sleep until 07:55:00 (Bash with a long timeout).
- If it's already later than 08:10, do NOT post. Notify the user that the run started too late.

## 3. Get the live price (within 5 minutes of fetching)
Always add a cache-buster so WebFetch doesn't serve a cached copy: `?nocache=<unix epoch seconds>`.

- **Primary — Kitco:** `https://www.kitco.com/charts/gold?nocache=<epoch>`
  Extract: bid price per ounce (USD), day's change ($), low, high, and the page date/time stamp (New York time).
- **Kitco is the only source** (user's decision, 16 Nov 2026). No second-source check.
- Do NOT use investing.com (it has shown undated, stale prices).

Accept the price only if Kitco's stamp is today and no more than 5 minutes old (07:55 Bahrain = 04:55 UTC = 23:55 New York the previous day in winter / 00:55 in summer — compare carefully in UTC), and bid, change, low and high are all present and consistent (low ≤ bid ≤ high).
If a check fails, wait 60 seconds and re-fetch (new epoch), up to 3 tries. Still failing → no post, notify the user.

**Saturday:** the market is closed. Kitco shows Friday's close (stamp ≈ Friday 17:00 New York); the 5-minute rule does not apply, but the stamp must be that Friday close. Use Friday's day change. Render with `--closing` (the post says it's Friday's closing price and stays the same Saturday and Sunday).

## 4. Render
```
python3 generate.py --price <bid> --change <day change $> --low <low> --high <high> --date <YYYY-MM-DD Bahrain> --out posts/<YYYY-MM-DD>.png [--closing]
```
This writes the PNG and `posts/<date>.txt` (the caption). Open the PNG with Read and check it visually: numbers present, nothing overlapping, 21K is the hero. Sanity check (BHD/gram = USD/oz price × factor × 0.38): 24K ×0.0321, 22K ×0.0294, 21K ×0.028, 18K ×0.024.

## 5. Publish the image
```
git add posts/<date>.png posts/<date>.txt && git commit -m "Gold post <date>" && git push
```
(on rejection: `git pull --rebase` then push). Image URL:
`https://raw.githubusercontent.com/acc66820-dot/gold-posts/main/posts/<date>.png`
Confirm with `curl -sI <url>` that it returns 200 (may take ~30s after push).

## 6. Schedule on Metricool
Call `createScheduledPost` with blogId `7116567`, date `<date>T08:00:00+03:00` and info:
```json
{"autoPublish": true, "draft": false, "text": "<contents of posts/<date>.txt>",
 "media": ["<raw URL>"], "providers": [{"network": "instagram"}],
 "publicationDate": {"dateTime": "<date>T08:00:00", "timezone": "Asia/Bahrain"},
 "instagramData": {"type": "POST"}, "firstCommentText": "", "shortener": false,
 "smartLinkData": {"ids": []}, "descendants": [], "hasNotReadNotes": false, "mediaAltText": []}
```
If it's already 07:59 or later, use now + 2 minutes instead of 08:00.
Then confirm with `getScheduledPosts` that the post is there.

## 7. Report
Send the user one short message: 21K price, ounce price, and that it's scheduled for 8:00 AM (or why it was skipped).

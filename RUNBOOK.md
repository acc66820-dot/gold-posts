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

## 3. Get the live price (via GitHub Actions — no web fetch by Claude)
Claude does NOT open Kitco itself (WebFetch needs a human approval that nobody gives in an unattended run — that's why the 18 and 24 Nov runs failed). Instead the GitHub workflow `gold-price.yml` reads Kitco (`https://www.kitco.com/charts/gold?nocache=1..3`) and commits `prices/latest.json` (bid, change, low, high, Kitco stamp).
**Kitco is the only source** (user's decision, 16 Nov 2026). Do NOT use investing.com or any other site.

At 07:55 Bahrain, up to 3 tries, 60 s apart:
1. `AFTER=$(date -u +%Y-%m-%dT%H:%M:%SZ)` then trigger the workflow with the GitHub MCP tool `actions_run_trigger` (method `run_workflow`, owner `acc66820-dot`, repo `gold-posts`, workflow_id `gold-price.yml`, ref `main`).
2. Poll for up to ~2 min: `git pull -q --rebase origin main && python3 tools/check_price.py --after $AFTER` every 15 s until it prints `OK`.
3. `check_price.py` enforces the rules and prints the exact `generate.py` command to use:
   - Mon–Fri: Kitco stamp no more than 5 min old (compared in UTC), file fetched after the trigger, low ≤ bid ≤ high.
   - Saturday: stamp must be Friday's close (NY Friday, ≥ 16:00); adds `--closing`. Use Friday's day change.
   - Sunday: fails → no post.
If all 3 tries fail (workflow error — check its log with `actions_list`/`get_job_logs` — or a FAIL from check_price.py) → no post, notify the user with the reason.
(The workflow also runs on its own at ~07:50 Bahrain Mon–Sat as a backup; that file only counts if check_price.py accepts it.)

## 4. Render
```
<the command printed by tools/check_price.py>   # = generate.py --price <bid> --change <change> --low <low> --high <high> --date <YYYY-MM-DD> --out posts/<YYYY-MM-DD>.png [--closing]
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

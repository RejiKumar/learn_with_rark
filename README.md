# RARK Shorts bot

Makes one 30–40 s tech Short (1080×1920) three times a day on GitHub Actions and uploads it to the RARK YouTube channel with the YouTube Data API. Nothing runs on your own computer after setup.

Each run: pick the next topic from `topics/`, build the scenes (Three.js in headless Chrome), make the voice (edge-tts), render with ffmpeg, check it, upload, and record it in `state/published.json`.

Built on the MIT-licensed [viral-agent](https://github.com/hadi-a-azeez/viral-agent) skills (see `skills/LICENSE-viral-agent-MIT`).

## One-time setup (you do these, because they involve your accounts)

1. **Create a private GitHub repository** and push this folder to it.
2. **Google Cloud:** create a project, enable *YouTube Data API v3*, set up the OAuth consent screen, add yourself as a test user, and create an OAuth client of type *Desktop app*. Download it as `client_secret.json` into `scripts/`.
   - Move the consent screen to **In production** (an unverified app is fine for your own use). In *Testing* status, Google expires the token after 7 days and the uploads stop.
3. **Get the token once** on your computer: `pip install google-auth-oauthlib`, then `python scripts/auth_once.py`, and sign in with the Google account that owns the channel.
4. **Add three GitHub secrets** (Settings → Secrets and variables → Actions): `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`. Never commit them or paste them into chat. Delete `client_secret.json` afterwards.
5. **Test without uploading:** Actions → Daily tech Short → Run workflow, leave *upload* off. Download the video from the run's artifacts and watch it.
6. **Test one upload:** run it again with *upload* on.

## Things to know

- **Uploads start private.** Google restricts videos uploaded through an API project that has not passed its audit to private. Either request the audit (YouTube API Services compliance audit form) or open each video in YouTube Studio and make it public or schedule it. Set the repository variable `YT_PRIVACY` to `public` or `unlisted` only after the audit.
- **Review before posting.** Mass-produced repetitive content can be limited by YouTube. Watch each video, and add your own value.
- **Times:** the cron lines in `.github/workflows/daily-shorts.yml` are UTC and set for India time (07:15, 12:45, 19:45). GitHub may delay scheduled runs by several minutes, and it pauses schedules in a repo with no activity for 60 days.
- **Topics:** 12 topics last 4 days at 3 a day. When they run out, the workflow fails on purpose instead of repeating. Add new files to `topics/` (copy an existing one).
- **Voice:** it uses Microsoft's unofficial read-aloud service through `edge-tts`. It may block cloud IP addresses, so test (step 5) before trusting it.
- **Stop it:** disable the workflow in the Actions tab.

## Files

- `topics/*.json`: one Short each (script, visuals, YouTube title and description).
- `scripts/make_video.py`: topic → video. `scripts/upload.py`: video → YouTube. `scripts/pick_topic.py`: next topic.
- `scripts/scenes_template.js`: the visual templates (phone, door, padlock, sign, bulb).
- `skills/`: the rendering, voice and quality-check tools.

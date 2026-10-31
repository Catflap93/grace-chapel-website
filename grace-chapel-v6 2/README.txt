Grace Chapel V5 — preview

Open using a local web server (not by double-clicking sermons.html) so the browser can load data/sermons.json.
Mac Terminal: cd into this folder, then run: python3 -m http.server 8000
Visit http://localhost:8000

The catalogue currently contains two user-provided verified YouTube links. This is NOT a complete channel archive and is NOT yet auto-updating.

To sync the full public YouTube channel: enable YouTube Data API v3 in Google Cloud, create an API key, set YOUTUBE_API_KEY in your environment and run python3 scripts/sync_youtube.py. The script reads public metadata and does not need Joshua's YouTube login. It can be scheduled in CI to update data/sermons.json and redeploy the site. Keep the API key secret and never add it to the website files.

If the script cannot confidently detect a preacher/date, it leaves it blank. data/sermon-overrides.json allows manual correction keyed by video ID. The current homepage has two static featured examples.

Keep the existing WordPress website running until launch.

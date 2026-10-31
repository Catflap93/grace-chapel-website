# Grace Chapel — automatic sermon sync

The site includes a GitHub Actions workflow (`.github/workflows/sync-sermons.yml`) that runs daily at 07:20 UTC, or manually via **Actions → Refresh Grace Chapel sermons → Run workflow**. It downloads public metadata from the `@goodnews4folkestone` YouTube channel, updates `data/sermons.json`, and commits changes. A Cloudflare Pages project connected to this GitHub repository will redeploy when the file changes.

## One-time setup (do not share credentials in chat)

1. Create a private GitHub repository, and upload **all files**, including the hidden `.github` folder.
2. In Google Cloud Console, create/select a project, enable **YouTube Data API v3**, and create an API key. Restrict the key to **YouTube Data API v3**. This reads public videos and does **not** require Joshua's channel login.
3. In the GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it `YOUTUBE_API_KEY` and paste the key. Do not commit the key or put it in the site files.
4. In GitHub **Actions**, enable workflows if prompted, then run **Refresh Grace Chapel sermons** manually. Check the run log and `data/sermons.json`.
5. Connect the GitHub repository to Cloudflare Pages (Git integration). Set framework preset **None**, build command **blank**, and output directory **/** (repository root). If Cloudflare requires a build command, use `exit 0`.
6. Check the temporary `*.pages.dev` URL before changing `gracechapel.uk` DNS. Leave WordPress live until approved.

## Editing metadata

If a preacher, passage, or preaching date is missing/wrong, add an override in `data/sermon-overrides.json` keyed by the 11-character YouTube video ID. Example:

```json
{
  "BIn6iBzFqns": {"preacher": "John Antalika", "preached": "2026-10-25", "book": "Ephesians", "series": "Ephesians"}
}
```

Commit the change and run the sync again. Missing details remain blank instead of being guessed. The date shown is the preaching date if detected, not the YouTube upload date.

## Notes

- The full archive cannot be downloaded until a YouTube API key is configured and the workflow runs successfully. The bundled two-sermon catalogue is a preview only.
- The sync includes all public channel uploads; review the results for any videos that are not sermons.
- GitHub scheduled workflows may be delayed or paused after inactivity. Check periodically.
- GitHub repository and Cloudflare Pages accounts should be controlled by Grace Chapel, with Joshua's own access.

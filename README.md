# changlog

GitHub Actions workflow that generates a **Japanese weekly summary** from [GitHub Changelog](https://github.blog/changelog/) using its RSS feed.

## How it works

| Trigger | Behaviour |
|---|---|
| **Scheduled** (every Sunday 00:00 JST) | Computes `since` / `until` automatically (today − 6 days → today), fetches the GitHub Changelog RSS feed, and writes a 1-week Japanese summary |
| **`workflow_dispatch`** | Uses the `since` / `until` inputs you provide; falls back to the same auto-compute logic if left blank |

The generated `CHANGELOG.md` is uploaded as a workflow artifact, retained for **90 days**.

## File structure

```
.
├── .github/
│   └── workflows/
│       └── generate-changelog.yml   # Main workflow
├── scripts/
│   └── generate_github_changelog.py # RSS fetch and summary generator
└── README.md
```

## Configuration

### Date window

Edit the `Compute JST date window` step in the workflow to change the lookback period.  
Default: **7 days** (today inclusive).

The workflow filters GitHub Changelog posts by JST publication date, then renders a Markdown digest with:

- post date
- changelog type (Japanese labels such as `リリース`, `改善`, `廃止`)
- labels (`Copilot`, `Application Security`, etc.)
- title and link
- summary text (Japanese when AI token is configured)

### Japanese summary mode

By default, the workflow outputs Japanese format (`--language ja`).

- If `GITHUB_MODELS_TOKEN` secret is set and `use_ai=true`, it calls GitHub Models and generates Japanese summaries.
- If token is missing, the workflow still succeeds and outputs the original English summary text as fallback.

Recommended model:

- `openai/gpt-5-mini`

### Data source

The workflow reads from the official RSS feed:

- `https://github.blog/changelog/feed/`

## Manual run

1. Go to **Actions → Generate Changelog → Run workflow**.
2. Optionally fill in `since` and `until` (format `YYYY-MM-DD`).
3. Optionally set `use_ai` (`true` / `false`) and `ai_model`.
3. Download the `CHANGELOG.md` artifact from the finished run.

## Local run

You can run the same summary generator locally:

```bash
python3 scripts/generate_github_changelog.py --since 2026-03-05 --until 2026-03-11 --language ja --output CHANGELOG.md
```

Run with GitHub AI:

```bash
export GITHUB_MODELS_TOKEN=YOUR_TOKEN_WITH_MODELS_READ
python3 scripts/generate_github_changelog.py --since 2026-03-05 --until 2026-03-11 --language ja --use-github-ai --ai-model openai/gpt-5-mini --output CHANGELOG.md
```

## Requirements

- Workflow runner: `ubuntu-latest`.
- Python 3 is used with the standard library only.
- No extra secrets or permissions beyond `contents: read` are required.
- For AI Japanese summaries, add repo secret `GITHUB_MODELS_TOKEN` (token must include `models:read`).
- If no posts match the requested date window, the workflow still succeeds and uploads a minimal `CHANGELOG.md` stating that no entries were found.

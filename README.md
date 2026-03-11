# changelog-workflow

GitHub Actions workflow that automatically generates a changelog for the **last 14 days** (JST) using [git-cliff](https://git-cliff.org).

## How it works

| Trigger | Behaviour |
|---|---|
| **Scheduled** (every Sunday 00:00 JST) | Computes `since` / `until` automatically (today − 13 days → today) |
| **`workflow_dispatch`** | Uses the `since` / `until` inputs you provide; falls back to the same auto-compute logic if left blank |

The generated `CHANGELOG.md` is uploaded as a workflow artifact, retained for **90 days**.

## File structure

```
.
├── .github/
│   └── workflows/
│       └── generate-changelog.yml   # Main workflow
├── cliff.toml                        # git-cliff configuration
└── README.md
```

## Configuration

### Date window

Edit the `Compute JST date window` step in the workflow to change the lookback period.  
Default: **14 days** (today inclusive).

### Commit format

`cliff.toml` at the repo root controls how commits are parsed and grouped.  
Commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) spec for best results.

Common groups and their prefixes:

| Prefix | Section |
|---|---|
| `feat:` | Features |
| `fix:` | Bug Fixes |
| `docs:` / `doc:` | Documentation |
| `perf:` | Performance |
| `refactor:` | Refactoring |
| `test:` | Testing |
| `chore:` / `ci:` | Miscellaneous |
| body contains `security` | Security |
| `revert:` | Reverts |

## Manual run

1. Go to **Actions → Generate Changelog → Run workflow**.
2. Optionally fill in `since` and `until` (format `YYYY-MM-DD`).
3. Download the `CHANGELOG.md` artifact from the finished run.

## Requirements

- Workflow runner: `ubuntu-latest` (uses GNU `date` for date arithmetic).
- No extra secrets or permissions beyond `contents: read` are required.

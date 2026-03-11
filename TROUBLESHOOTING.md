# Changelog Workflow Troubleshooting Manual

This manual summarizes the issues we just encountered, with quick diagnosis and fix steps.

## 1) Push command fails (Exit 128)

### Symptom
- Command like `git push github-action-changelog` fails with Exit 128.

### Root Cause
- The branch name was used as a remote name.
- Correct remote is usually `origin`.

### Fix
1. Check current branch:
   - `git branch --show-current`
2. Check remotes:
   - `git remote -v`
3. Push correctly:
   - `git push -u origin github-actions-changelog`

### Verification
- `git status --short --branch` shows branch tracking `origin/github-actions-changelog`.

---

## 2) Workflow failed with git-cliff arguments

### Symptom
- `git-cliff --since/--until` or related range arguments fail in CI/local run.

### Root Cause
- CLI argument mismatch across git-cliff versions.

### Fix
- Replace git log based generation with RSS-based changelog pipeline.
- Use `scripts/generate_github_changelog.py` to fetch from:
  - `https://github.blog/changelog/feed/`

### Verification
- Script runs successfully and writes weekly content into `CHANGELOG.md`.

---

## 3) Output source was wrong (repo commits vs GitHub Changelog)

### Symptom
- Generated content came from repository commit history, not GitHub official changelog posts.

### Root Cause
- Initial implementation used repository git history.

### Fix
- Use GitHub Changelog RSS as single source of truth.
- Filter to last week entries only.

### Verification
- Output items match posts on https://github.blog/changelog/ for the target week.

---

## 4) Copilot CLI not installed

### Symptom
- `copilot` command unavailable or only a placeholder stub.

### Fix
1. Install CLI in workflow/local environment.
2. Ensure executable path is available in `PATH`.

### Verification
- `copilot --help` works.

---

## 5) Copilot CLI installed but not authenticated

### Symptom
- Copilot command returns auth errors or asks for login.

### Fix
1. Run login flow:
   - `copilot auth login`
2. Complete device code authorization in browser.

### Verification
- `copilot --prompt "test"` returns model output.

---

## 6) GitHub Actions token setup confusion

### Symptom
- Unclear where to set token for workflow.

### Correct Location
- GitHub repository -> Settings -> Secrets and variables -> Actions -> New repository secret.

### Required Secret
- `COPILOT_GITHUB_TOKEN`

### Optional/Fallback Secret
- `GITHUB_MODELS_TOKEN`

### Verification
- Workflow logs show provider initialized and no token-missing error.

---

## 7) Output format drift (English mixed in / non-fixed structure)

### Symptom
- Output not strictly Japanese or section layout changed.

### Root Cause
- Prompt constraints were too weak or prompt path not passed.

### Fix
1. Keep format in template file:
   - `prompts/changelog_weekly_ja.md`
2. Always pass template parameter in script/workflow.
3. Add strict instructions:
   - Japanese only
   - Output body only
   - No tool-use text

### Verification
- Generated `CHANGELOG.md` matches fixed template sections.

## 8) Copilot CLI install step fails in GitHub Actions (Exit 22 / 404)

### Symptom
- Step "Install Copilot CLI" fails with `curl: (22) The requested URL returned error: 404`.

### Root Cause
- The install script URL `https://raw.githubusercontent.com/github/copilot-cli/main/scripts/install.sh` does not exist.
- `copilot-cli` is a local tool and cannot be used reliably inside GitHub Actions runners.

### Fix
1. Remove the "Install Copilot CLI" step from the workflow entirely.
2. Change the default `ai_provider` to `github` (uses GitHub Models API — no binary needed).
3. Workflow env: use `COPILOT_GITHUB_TOKEN` as fallback when `GITHUB_MODELS_TOKEN` is not set:
   ```yaml
   GITHUB_MODELS_TOKEN: ${{ secrets.GITHUB_MODELS_TOKEN || secrets.COPILOT_GITHUB_TOKEN }}
   ```
4. Script: read `COPILOT_GITHUB_TOKEN` as fallback in Python:
   ```python
   ai_token = os.environ.get("GITHUB_MODELS_TOKEN") or os.environ.get("COPILOT_GITHUB_TOKEN")
   ```

### Summary: Provider by Environment

| Environment     | Use provider |
|----------------|--------------|
| GitHub Actions | `github`     |
| Local terminal | `copilot-cli` or `github` |

### Verification
- Workflow step "Generate GitHub Changelog weekly summary" runs without error.
- `CHANGELOG.md` contains Japanese AI summary.

### Also Fix: max_tokens too low
- `max_tokens: 200` truncates the summary output.
- Fix: change to `max_tokens: 2000` in `generate_github_changelog.py`.

---

## Quick Runbook

1. Local test:
   - `python3 scripts/generate_github_changelog.py --output CHANGELOG.md --days 7 --use-ai --ai-provider copilot-cli --prompt-template prompts/changelog_weekly_ja.md`
2. Commit and push:
   - `git add -A`
   - `git commit -m "docs: add troubleshooting manual for changelog workflow"`
   - `git push -u origin github-actions-changelog`
3. GitHub Actions manual run:
   - `use_ai=true`
   - `ai_provider=copilot-cli`

## Fast Checklist Before Each Run

- On correct branch: `github-actions-changelog`
- Secret exists: `COPILOT_GITHUB_TOKEN`
- Prompt template exists: `prompts/changelog_weekly_ja.md`
- Script exists: `scripts/generate_github_changelog.py`
- Output target: `CHANGELOG.md`

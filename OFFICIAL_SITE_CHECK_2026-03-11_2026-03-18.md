# GitHub Changelog 公式ページ照合レポート

説明
この文書は、GitHub 公式 Changelog の Actions / Copilot フィルター結果と、このリポジトリで生成した `CHANGELOG.md` を照合し、漏れがあるかを確認した結果をまとめたものです。

対象期間：2026/03/11～2026/03/18
確認対象ページ：https://github.blog/changelog/?label=actions%2Ccopilot&opened-months=3
確認日時：2026/03/17

## 結論

- 公式ページ上で確認できた対象記事は 8 件
- 現在の `CHANGELOG.md` に含まれている記事は 6 件
- 差分は 2 件
- 差分 2 件は、現在スクリプトが参照している RSS フィード `https://github.blog/changelog/feed/` に含まれていないことを確認済み
- そのため、現状の実装では公式一覧ページには出ているが RSS には出ていない記事を拾えない

## 1. 公式ページで確認できた記事

### Action

1. 2026-03-13
   Self-hosted runner minimum version enforcement paused
   https://github.blog/changelog/2026-03-13-self-hosted-runner-minimum-version-enforcement-paused

2. 2026-03-12
   Actions OIDC tokens now support repository custom properties
   https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties

### Copilot

1. 2026-03-13
   Optionally skip approval for Copilot coding agent Actions workflows
   https://github.blog/changelog/2026-03-13-optionally-skip-approval-for-copilot-coding-agent-actions-workflows

2. 2026-03-13
   Updates to GitHub Copilot for students
   https://github.blog/changelog/2026-03-13-updates-to-github-copilot-for-students

3. 2026-03-12
   Copilot auto model selection is generally available in JetBrains IDEs
   https://github.blog/changelog/2026-03-12-copilot-auto-model-selection-is-generally-available-in-jetbrains-ides

4. 2026-03-11
   Request Copilot code review from GitHub CLI
   https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli

5. 2026-03-11
   Major agentic capabilities improvements in GitHub Copilot for JetBrains IDEs
   https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides

6. 2026-03-11
   Explore a repository using Copilot on the web
   https://github.blog/changelog/2026-03-11-explore-a-repository-using-copilot-on-the-web

## 2. 現在の CHANGELOG.md に含まれている記事

### Action

1. 2026-03-13
   Self-hosted runner minimum version enforcement paused
   https://github.blog/changelog/2026-03-13-self-hosted-runner-minimum-version-enforcement-paused

2. 2026-03-12
   Actions OIDC tokens now support repository custom properties
   https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties

### Copilot

1. 2026-03-13
   Optionally skip approval for Copilot coding agent Actions workflows
   https://github.blog/changelog/2026-03-13-optionally-skip-approval-for-copilot-coding-agent-actions-workflows

2. 2026-03-13
   Updates to GitHub Copilot for students
   https://github.blog/changelog/2026-03-13-updates-to-github-copilot-for-students

3. 2026-03-12
   Copilot auto model selection is generally available in JetBrains IDEs
   https://github.blog/changelog/2026-03-12-copilot-auto-model-selection-is-generally-available-in-jetbrains-ides

4. 2026-03-11
   Request Copilot code review from GitHub CLI
   https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli

## 3. 漏れている記事

### 漏れ 1

- 日付：2026-03-11
- タイトル：Major agentic capabilities improvements in GitHub Copilot for JetBrains IDEs
- URL：https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides
- 状態：公式ページには存在するが、現在の `CHANGELOG.md` には未反映

### 漏れ 2

- 日付：2026-03-11
- タイトル：Explore a repository using Copilot on the web
- URL：https://github.blog/changelog/2026-03-11-explore-a-repository-using-copilot-on-the-web
- 状態：公式ページには存在するが、現在の `CHANGELOG.md` には未反映

## 4. 原因切り分け

今回の確認では、漏れている 2 件について以下を確認した。

- 公式のフィルター済み一覧ページには掲載されている
- 現在のスクリプトが取得元として使っている RSS フィードには文字列として含まれていない

確認対象 RSS:

- https://github.blog/changelog/feed/

このことから、今回の漏れはテンプレートの整形漏れではなく、データソース差分による可能性が高い。

## 5. 影響

- 現在の実装は RSS ベースであるため、公式一覧ページと完全一致しない場合がある
- 特に、公式サイトのラベル一覧には見えるが RSS に出ていない記事は自動収集できない
- そのため、顧客提出前に公式ページと照合する工程を入れた方が安全

## 6. 推奨対応

### 対応案 A

RSS ベースの生成はそのまま維持し、提出前に公式ページとの照合レポートを別途作る。

### 対応案 B

収集元を RSS だけでなく、公式一覧ページの HTML も補助ソースとして使う。

### 対応案 C

対象期間の最終チェックとして、以下のページを毎回目視または自動照合する。

- https://github.blog/changelog/?label=actions%2Ccopilot&opened-months=3

## 7. 今回の判定

今回の 2026/03/11～2026/03/18 の範囲では、現在の `CHANGELOG.md` は 2 件不足している。

不足件数：2

不足記事:

- Major agentic capabilities improvements in GitHub Copilot for JetBrains IDEs
- Explore a repository using Copilot on the web

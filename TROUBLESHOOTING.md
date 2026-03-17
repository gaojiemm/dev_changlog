# Changelog Workflow 実行手順・環境設定・トラブルシューティング

このファイルは、このリポジトリを別の環境でも再現できるようにするための手順書です。
macOS、Linux、GitHub Actions を前提に、セットアップ手順、実行コマンド、AI の有効化確認、よくある失敗の対処をまとめています。

## 1. このリポジトリでやっていること

- GitHub Changelog の RSS を取得する
- 指定期間の投稿だけを抽出する
- `Action` と `Copilot` に関係する更新を日本語で整形する
- 出力結果を `CHANGELOG.md` に書き出す

使用スクリプト:

- `scripts/generate_github_changelog.py`

出力フォーマット定義:

- `prompts/changelog_weekly_ja.md`

主なデータソース:

- `https://github.blog/changelog/feed/`

## 2. 前提条件

最低限必要なものは以下です。

- Python 3
- Git
- インターネット接続
- AI を使う場合は以下のいずれか
  - GitHub Copilot CLI
  - GitHub Models 用トークン

推奨環境:

- macOS
- Linux
- Windows の場合は WSL2 上での実行を推奨

Python 追加ライブラリは不要です。標準ライブラリのみで動作します。

## 3. 新しい環境で最初にやること

### 3.1 リポジトリを取得

```bash
git clone <YOUR_REPOSITORY_URL>
cd changelog-workflow
```

### 3.2 Python の確認

```bash
python3 --version
```

期待結果:

- `Python 3.x` が表示される

### 3.3 スクリプト単体で動くか確認

まずは AI なしで確認します。

```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --output CHANGELOG.md
```

期待結果:

- `CHANGELOG.md` が生成される
- AI が無効でも、期間集計つきのフォールバック出力は生成される

## 4. AI を使ってローカル実行する方法

ローカルでは、以下の 2 パターンがあります。

### 4.1 方法 A: GitHub Copilot CLI を使う

この方法は、ローカル端末で一番使いやすい方法です。

#### インストール確認

```bash
copilot --version
```

期待結果:

- バージョン番号が表示される

表示されない場合は GitHub Copilot CLI をインストールしてください。

#### PATH の設定

Copilot CLI が `~/.local/bin/copilot` に入る場合があります。

zsh の場合:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

bash の場合:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

Linux bash の場合も基本的には同じです。

反映確認:

```bash
command -v copilot
copilot --version
```

#### 認証確認

最小確認コマンド:

```bash
copilot --prompt "OK だけ出力してください" --silent
```

期待結果:

- `OK` のような応答が返る

#### 実行コマンド

```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --use-github-ai \
  --ai-provider copilot-cli \
  --copilot-cli-command "copilot --silent" \
  --prompt-template prompts/changelog_weekly_ja.md \
  --output CHANGELOG.md
```

### 4.2 方法 B: GitHub Models を使う

Copilot CLI を使わず、トークンで GitHub Models を直接呼ぶ方法です。

#### トークン設定

zsh:

```bash
export GITHUB_MODELS_TOKEN=YOUR_TOKEN
```

bash:

```bash
export GITHUB_MODELS_TOKEN=YOUR_TOKEN
```

永続化したい場合は、`~/.zprofile` または `~/.bash_profile` に追記してください。

#### 実行コマンド

```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --use-github-ai \
  --ai-provider github \
  --ai-model openai/gpt-4.1-mini \
  --prompt-template prompts/changelog_weekly_ja.md \
  --output CHANGELOG.md
```

### 4.3 AI が有効か確認する方法

以下のどちらかなら AI 出力に成功しています。

- `CHANGELOG.md` に `Action:` と `Copilot:` が本文として出ている
- `AI要約を生成できませんでした` という文言が出ていない

確認例:

```bash
grep -n "AI要約を生成できませんでした\|^Action:\|^Copilot:" CHANGELOG.md
```

## 5. GitHub Actions で実行する方法

このリポジトリには以下のワークフローがあります。

- `.github/workflows/generate-changelog.yml`

### 5.1 実行方法

GitHub 上で以下を開きます。

- `Actions` → `Generate Changelog` → `Run workflow`

入力値:

- `since`: 開始日 `YYYY-MM-DD`
- `until`: 終了日 `YYYY-MM-DD`
- `use_ai`: `true` または `false`
- `ai_provider`: `github` / `copilot-cli` / `local`
- `ai_model`: 例 `openai/gpt-4.1-mini`

### 5.2 GitHub Actions で推奨する設定

GitHub Actions では `github` プロバイダを推奨します。

推奨理由:

- GitHub Models API をそのまま利用できる
- CLI バイナリ依存を避けられる
- ランナー上の認証トラブルを減らせる

推奨入力:

- `use_ai=true`
- `ai_provider=github`
- `ai_model=openai/gpt-4.1-mini`

### 5.3 Secrets の設定

リポジトリの以下に設定します。

- `Settings` → `Secrets and variables` → `Actions`

設定候補:

- `GITHUB_MODELS_TOKEN`
- `COPILOT_GITHUB_TOKEN`

ワークフローでは `GITHUB_MODELS_TOKEN` を優先し、未設定時は `COPILOT_GITHUB_TOKEN` を代わりに使います。

## 6. 実行例

### 6.1 AI なし

```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --output CHANGELOG.md
```

### 6.2 Copilot CLI あり

```bash
source ~/.zprofile 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"

python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --use-github-ai \
  --ai-provider copilot-cli \
  --copilot-cli-command "copilot --silent" \
  --prompt-template prompts/changelog_weekly_ja.md \
  --output CHANGELOG.md
```

### 6.3 GitHub Models あり

```bash
export GITHUB_MODELS_TOKEN=YOUR_TOKEN

python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --use-github-ai \
  --ai-provider github \
  --ai-model openai/gpt-4.1-mini \
  --prompt-template prompts/changelog_weekly_ja.md \
  --output CHANGELOG.md
```

## 7. 別のシステムに移したときの確認チェックリスト

新しい macOS、Linux、WSL2 などに移した場合は、以下を順番に確認します。

### 7.1 共通

- `git clone` できた
- `python3 --version` が通る
- `scripts/generate_github_changelog.py` が存在する
- `prompts/changelog_weekly_ja.md` が存在する

### 7.2 Copilot CLI を使う場合

- `command -v copilot` が通る
- `copilot --version` が通る
- `copilot --prompt "OK だけ出力してください" --silent` が成功する
- `PATH` に `~/.local/bin` が入っている

### 7.3 GitHub Models を使う場合

- `echo $GITHUB_MODELS_TOKEN` が空ではない
- トークンに `models:read` 権限がある

### 7.4 出力確認

- `CHANGELOG.md` が生成される
- `Action:` と `Copilot:` が出力される
- `AI要約を生成できませんでした` が出ていない

## 8. よくある問題と対処

### 8.1 `copilot` コマンドが見つからない

症状:

- `command not found: copilot`
- `Cannot find GitHub Copilot CLI`

対処:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
command -v copilot
```

bash の場合:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
command -v copilot
```

### 8.2 Copilot CLI はあるが AI 出力に失敗する

症状:

- `CHANGELOG.md` に `AI要約を生成できませんでした` が出る

確認:

```bash
copilot --prompt "OK だけ出力してください" --silent
```

対処:

- Copilot CLI の認証状態を確認する
- 端末プロファイルを再読み込みする
- `--copilot-cli-command "copilot --silent"` を明示する

### 8.3 GitHub Actions で AI 生成に失敗する

症状:

- ワークフローが `token missing` で失敗する
- フォールバック文面が生成される

対処:

- `GITHUB_MODELS_TOKEN` を設定する
- 代替として `COPILOT_GITHUB_TOKEN` を設定する
- `ai_provider=github` を使う
- `ai_model=openai/gpt-4.1-mini` を使う

### 8.4 出力が英語混じりになる、または形式が崩れる

確認項目:

- `--prompt-template prompts/changelog_weekly_ja.md` を付けているか
- テンプレートファイルを別環境にコピーし忘れていないか

対処:

- 必ず `prompts/changelog_weekly_ja.md` を使う
- 形式を変えたい場合はテンプレートだけを編集する

### 8.5 対象期間の件数が想定より少ない

原因候補:

- 指定期間内の GitHub Changelog 投稿自体が少ない
- このテンプレートは `Action` と `Copilot` のみを対象にしている
- Security や Projects の投稿は意図的に除外される

確認方法:

```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --output CHANGELOG.md
```

AI なしで件数だけ確認し、対象の絞り込みが原因かを切り分けます。

## 9. 最低限これだけやれば動く手順

Copilot CLI を使う最短手順です。

```bash
git clone <YOUR_REPOSITORY_URL>
cd changelog-workflow

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile

copilot --version
copilot --prompt "OK だけ出力してください" --silent

python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --use-github-ai \
  --ai-provider copilot-cli \
  --copilot-cli-command "copilot --silent" \
  --prompt-template prompts/changelog_weekly_ja.md \
  --output CHANGELOG.md
```

## 10. 推奨運用

- ローカル端末: `copilot-cli`
- GitHub Actions: `github`
- 出力形式を変えたい場合: `prompts/changelog_weekly_ja.md` だけを編集する
- 実行結果を確認する場合: `CHANGELOG.md` を見る

## 11. 実行成功の最終確認

成功していれば以下を満たします。

- `CHANGELOG.md` が生成される
- `説明`、`対象期間`、`Action:`、`Copilot:` が出力される
- 日本語でまとまっている
- `AI要約を生成できませんでした` が含まれていない

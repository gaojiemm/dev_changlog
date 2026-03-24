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
- `ai_provider`: `copilot-cli` / `github` / `local`
- `ai_model`: 例 `openai/gpt-4.1-mini`（`github` プロバイダー使用時のみ）

### 5.2 GitHub Actions で推奨する設定

GitHub Actions では **`copilot-cli`** プロバイダを推奨します。

推奨理由:

- ローカルと同じ CLI で統一できる
- Fine-grained PAT は必要だが、一度設定すれば再利用可能
- Copilot の最新機能に対応しやすい
- 更新が簡単（npm update のみ）

推奨入力:

- `use_ai=true`
- `ai_provider=copilot-cli`
- `ai_model`: （指定不要）

### 5.3 Secrets の設定

#### 5.3.1 Fine-grained PAT の作成（推奨：Copilot CLI 用）

Copilot CLI を使う場合は、Fine-grained Personal Access Token (PAT) が必要です。

**重要**: デフォルトの `GITHUB_TOKEN` は **Copilot API へのアクセス権がありません**。必ず Fine-grained PAT を作成してください。

手順:

1. [GitHub PAT 作成ページ](https://github.com/settings/personal-access-tokens/new) を開く
2. **Token name** に `copilot-actions` などわかりやすい名前をつける
3. **Expiration** を適切に設定（90日など）
4. **Repository access** で対象リポジトリを選択
5. **Permissions** で以下の2つを設定:
   - `Copilot Requests` → **Read** ✅ （必須）
   - `Contents` → Read （任意、コードを読む場合）
6. **Generate token** をクリックしてトークンをコピー

⚠️ **注意**: Classic PAT（`ghp_` で始まるトークン）は使えません。必ず **Fine-grained PAT** を使ってください。

#### 5.3.2 リポジトリに Secrets を登録

作成したトークンをリポジトリの secrets に保存します:

1. リポジトリの **Settings** → **Secrets and variables** → **Actions** を開く
2. **New repository secret** をクリック
3. **Name**: `COPILOT_GITHUB_TOKEN`
4. **Secret**: コピーしたトークンを貼り付け
5. **Add secret** で保存

#### 5.3.3 GitHub Models トークンを使う場合

`github` プロバイダを使う場合は:

1. **Name**: `GITHUB_MODELS_TOKEN`
2. **Secret**: GitHub Models のトークンを貼り付け

設定後:

- Copilot CLI を使う場合: `COPILOT_GITHUB_TOKEN` が使われます
- GitHub Models を使う場合: `GITHUB_MODELS_TOKEN` が使われます

## 6. 実行例

### 6.1 Copilot CLI あり（推奨）

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

GitHub Actions では Fine-grained PAT を `COPILOT_GITHUB_TOKEN` に設定すると自動的に使われます。

### 6.2 GitHub Models を使う場合

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

### 6.3 AI なし

```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
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

対処（Copilot CLI 使用時）:

- `COPILOT_GITHUB_TOKEN` に Fine-grained PAT を設定する
- PAT に `Copilot Requests: Read` 権限があるか確認
- Classic PAT（`ghp_` で始まる）ではなく Fine-grained PAT を使う

対処（GitHub Models 使用時）:

- `GITHUB_MODELS_TOKEN` を設定する
- トークンに `models:read` 権限があるか確認
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

- ローカル端末: `copilot-cli`（ローカルコマンドとの統一）
- GitHub Actions: `copilot-cli`（同じ CLI で統一、Fine-grained PAT を設定）
- 出力形式を変えたい場合: `prompts/changelog_weekly_ja.md` だけを編集する
- 実行結果を確認する場合: `CHANGELOG.md` を見る

**GitHub Actions の設定**:
- Secrets: `COPILOT_GITHUB_TOKEN` に Fine-grained PAT を設定
- ワークフロー入力: `ai_provider=copilot-cli`

## 11. 実行成功の最終確認

成功していれば以下を満たします。

- `CHANGELOG.md` が生成される
- `説明`、`対象期間`、`Action:`、`Copilot:` が出力される
- 日本語でまとまっている
- `AI要約を生成できませんでした` が含まれていない

## 12. 生成結果の検証 (新機能)

### 12.1 概要

`scripts/verify_changelog.py` は、生成した `CHANGELOG.md` が GitHub 公式サイトのデータと一致しているかを検証するスクリプトです。

データソース:

- GitHub 公式 Changelog Sitemap XML
- ローカル `CHANGELOG.md`

### 12.2 基本的な使い方

```bash
python3 scripts/verify_changelog.py
```

### 12.3 実行例とオプション

#### 例 1: 基本的な検証

```bash
python3 scripts/verify_changelog.py
```

出力内容:

- 本地 CHANGELOG.md の条目一覧（分類付き）
- 公式 Sitemap から取得した条目一覧（分類付き）
- 不足している条目
- 多すぎる条目
- 統計情報（Action/Copilot/Other の個数）

#### 例 2: 特定期間を検証

```bash
python3 scripts/verify_changelog.py \
  --since 2026-03-18 \
  --until 2026-03-25
```

#### 例 3: 別の CHANGELOG ファイルを検証

```bash
python3 scripts/verify_changelog.py \
  --changelog other_changelog.md
```

#### 例 4: すべてのカテゴリを含めて表示

```bash
python3 scripts/verify_changelog.py --include-all
```

通常は `Action` と `Copilot` のみ対象ですが、この オプションで Security、Mobile などの行も表示します。

### 12.4 出力の見方

**色分け表示:**

- `✅ [Action ]` - Action に該当する条目
- `✅ [Copilot]` - Copilot に該当する条目
- `⚠️ [Other ]` - Action/Copilot 以外の条目

**統計情報:**

```
本地 CHANGELOG.md:
  - Action:  2
  - Copilot: 8
  - Other:   0
  - 合計:    10

官网 Sitemap:
  - Action:  3
  - Copilot: 8
  - Other:   4
  - 合計:    15
```

**対比分析:**

- `✅ 一致` - CHANGELOG と公式サイトの条目がすべて同じ
- `⚠️ 不一致` - 不足している条目がある

不足している場合の例:

```
❌ 本地缺少 5 个条目（官网有，本地没有）:
   ⚠️ [Other  ] 2026-03-23 - push-protection-exemptions-from-repository-settings
   ✅ [Action ] 2026-03-19 - hierarchy-view-in-github-projects-is-now-generally-available
   ...
```

### 12.5 使用シーン

**シーン 1: CHANGELOG 生成後の品質確認**

```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-18 \
  --until 2026-03-25 \
  --language ja \
  --output CHANGELOG.md

# 生成結果を検証
python3 scripts/verify_changelog.py
```

**シーン 2: 過去のデータを追跡**

CHANGELOG がカバーしているべき期間の条目が本当に全部含まれているか確認:

```bash
python3 scripts/verify_changelog.py \
  --since 2026-02-01 \
  --until 2026-02-28
```

**シーン 3: 定期実行の品質チェック**

毎週実行後に自動でこのスクリプトを呼び出し、不足がないかを確認する。

### 12.6 想定される出力パターン

**パターン A: 完全に一致**

```
整体状态: ✅ 一致

✅ 所有条目完全一致！
```

→ CHANGELOG が公式サイトと完全に一致している状態。最高です。

**パターン B: Action/Copilot 特化（推奨）**

```
整体状态: ⚠️ 不一致

❌ 本地缺少 5 个条目（官网有，本地没有）:
   ⚠️ [Other  ] 2026-03-23 - push-protection-exemptions-from-repository-settings
   ⚠️ [Other  ] 2026-03-20 - a-smoother-navigation-experience-in-github-mobile-for-android
   ...

⚠️  缺少的其他类别条目: 4 (非 Action/Copilot)
   这很正常，因为 CHANGELOG 只关注 Action 和 Copilot 相关的更新。
```

→ 正常です。このプロジェクトは Action と Copilot のみを対象としているため、他のカテゴリが不足するのは意図通りです。

**パターン C: Action/Copilot の欠落（注意）**

```
缺少的 Action/Copilot 条目: 1
  - Action:  1
  - Copilot: 0

👉 如需更新 CHANGELOG，请重新执行生成命令。
```

→ Action または Copilot 関連の条目が漏れている。再生成を検討してください。

### 12.7 トラブルシューティング

**問題: タイムアウト**

```
Error fetching https://github.blog/changelog-sitemap4.xml: ...
```

対処:

- ネットワーク接続を確認
- 数秒待てて再実行

**問題: CHANGELOG.md が見つからない**

```
❌ 文件不存在: CHANGELOG.md
```

対処:

```bash
# 正しいパスを指定
python3 scripts/verify_changelog.py --changelog /full/path/to/CHANGELOG.md
```

**問題: 日付範囲が自動抽出されない**

CHANGELOG.md に `対象期間：YYYY/MM/DD～YYYY/MM/DD` の形式がない場合、明示的に指定:

```bash
python3 scripts/verify_changelog.py \
  --since 2026-03-18 \
  --until 2026-03-25
```

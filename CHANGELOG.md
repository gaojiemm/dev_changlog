説明
この週は、GitHub Actionsでは認証連携とランナー運用に関する更新があり、GitHub Copilotではモデル提供、CLI・Web・JetBrains・coding agent 周辺の機能拡張が続きました。

対象期間：2026/03/11～2026/03/18

Action:

- タイトル： OIDCトークンでリポジトリのカスタムプロパティを利用可能に
- 内容
	- 認証連携
		- GitHub Actions の OIDC トークンが、リポジトリのカスタムプロパティに対応しました。
		- OIDC を使った外部連携時に、リポジトリ属性を認証情報に含められるようになりました。
		- リポジトリごとの属性を前提にした認可条件を組み込みやすくなりました。
		- 外部クラウドや認証基盤と連携する運用で、属性ベースの制御を行いやすくなります。
- 情報元： 🔗 https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties

- タイトル： 自己ホストランナーの最低バージョン強制を一時停止
- 内容
	- ランナー運用
		- 自己ホストランナーに対する最低バージョンの強制適用が一時停止されました。
		- 直近で最低バージョンへ合わせる前提が外れ、既存環境を維持しやすくなりました。
		- ランナー更新のタイミングを見直すための猶予が生まれました。
		- 運用負荷は一時的に下がりますが、継続的なバージョン管理自体は引き続き必要です。
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-self-hosted-runner-minimum-version-enforcement-paused

Copilot:

- タイトル： GPT-5.3 Codex を長期サポート対象として提供
- 内容
	- 変更点
		- GitHub Copilot で GPT-5.3 Codex が長期サポート対象になりました。
		- 継続利用を前提に選びやすいモデルとして位置付けられました。
		- モデル運用時に、安定利用を重視する選択肢が増えました。
	- 変更がない点
		- 他モデルの提供終了や置き換えについては、この告知では案内されていません。
		- Copilot の基本的な利用方法全体を変更する告知ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-gpt-5-3-codex-long-term-support-in-github-copilot

- タイトル： Copilot coding agent の検証ツールを設定可能に
- 内容
	- 変更点
		- Copilot coding agent 向けに、検証ツールを設定できるようになりました。
		- エージェントの検証工程で使うツールを運用に合わせて調整できます。
		- コーディングエージェント利用時の確認手順を構成しやすくなりました。
	- 変更がない点
		- coding agent 自体の提供終了や基本機能の廃止は案内されていません。
		- 他の Copilot 製品全体の仕様変更をまとめて行う告知ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools

- タイトル： GPT-5.4 mini を一般提供開始
- 内容
	- 変更点
		- GitHub Copilot で GPT-5.4 mini が一般提供になりました。
		- プレビュー段階ではなく、正式利用できるモデルとして扱われます。
		- Copilot で利用可能なモデルの選択肢が広がりました。
	- 変更がない点
		- 既存モデルの廃止や強制切替については、この告知では示されていません。
		- Copilot の基本操作や利用導線全体を変更する内容ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-17-gpt-5-4-mini-is-now-generally-available-for-github-copilot

- タイトル： 組織レベルの利用指標に Copilot CLI 活動を追加
- 内容
	- 変更点
		- Copilot の利用指標に、組織レベルの GitHub Copilot CLI 活動が含まれるようになりました。
		- 管理者が CLI 利用状況を組織単位で把握しやすくなりました。
		- 利用実績の可視化対象が広がりました。
	- 変更がない点
		- GitHub Copilot CLI 自体の利用方法変更を主題とする告知ではありません。
		- 既存の他指標の廃止については、この告知では案内されていません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-17-copilot-usage-metrics-now-includes-organization-level-github-copilot-cli-activity

- タイトル： semantic code search により coding agent を高速化
- 内容
	- 変更点
		- Copilot coding agent が semantic code search により、より速く動作するようになりました。
		- コード探索や理解に関わる処理性能の改善が示されています。
		- coding agent 利用時の作業効率向上が期待できます。
	- 変更がない点
		- 利用条件や料金体系の変更については、この告知では触れられていません。
		- coding agent 以外の Copilot 機能全体を変更する内容ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-17-copilot-coding-agent-works-faster-with-semantic-code-search

- タイトル： 学生向け GitHub Copilot の提供内容を更新
- 内容
	- 変更点
		- 学生向け GitHub Copilot に関する更新がリリースされました。
		- 変更対象が学生向け提供であることが明示されました。
		- 学生利用者向けの運用内容が最新化されました。
	- 変更がない点
		- 一般向け Copilot 全体の仕様変更を主題とする告知ではありません。
		- 他カテゴリ製品の変更は、この告知の対象ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-updates-to-github-copilot-for-students

- タイトル： coding agent の Actions ワークフローで承認スキップを任意設定化
- 内容
	- 変更点
		- Copilot coding agent の Actions ワークフローで、承認を任意でスキップできるようになりました。
		- ワークフロー承認の要否を設定で選べるようになりました。
		- 承認待ちを前提としない運用を組みやすくなりました。
	- 変更がない点
		- GitHub Actions 全体の承認仕様を一律変更する告知ではありません。
		- coding agent 自体の提供有無や基本利用方法の全面変更は案内されていません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-optionally-skip-approval-for-copilot-coding-agent-actions-workflows

- タイトル： JetBrains IDEs で自動モデル選択を一般提供開始
- 内容
	- 変更点
		- Copilot の自動モデル選択機能が JetBrains IDEs で一般提供になりました。
		- JetBrains 利用者が IDE 上で正式機能として自動選択を使えるようになりました。
		- モデル選択を手動で都度判断する負荷を下げやすくなりました。
	- 変更がない点
		- 手動でのモデル選択が廃止されるとは、この告知では示されていません。
		- JetBrains 以外の IDE 全般の変更をまとめて告知する内容ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-12-copilot-auto-model-selection-is-generally-available-in-jetbrains-ides

- タイトル： GitHub CLI から Copilot コードレビューを直接依頼可能に
- 内容
	- 変更点
		- GitHub CLI から Copilot のコードレビューを直接依頼できるようになりました。
		- ターミナル中心の開発フローに、レビュー依頼の導線が追加されました。
		- Web 画面を介さずに Copilot レビューを呼び出せるようになりました。
	- 変更がない点
		- 既存の他画面や他経路でのレビュー依頼が廃止されるとは案内されていません。
		- CLI 全体の基本操作体系を変更する告知ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli

- タイトル： JetBrains IDEs 向けのエージェント機能を大幅改善
- 内容
	- 変更点
		- GitHub Copilot for JetBrains IDEs の agentic capabilities が大きく改善されました。
		- 改善対象が JetBrains IDEs 向け機能であることが明示されました。
		- JetBrains 環境でのエージェント利用体験の強化が進みました。
	- 変更がない点
		- 他 IDE 全体の仕様変更を一括で行う告知ではありません。
		- JetBrains 向け Copilot の提供終了や縮小を示す内容ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides

- タイトル： Web 上の Copilot でリポジトリ探索が可能に
- 内容
	- 変更点
		- GitHub Copilot を使って、Web 上でリポジトリを探索できるようになりました。
		- ブラウザ上でリポジトリ理解を進めるための導線が追加されました。
		- Copilot の利用場面が Web での探索作業まで広がりました。
	- 変更がない点
		- ローカル開発環境や IDE での利用が不要になるという告知ではありません。
		- 他の Copilot 機能全般の置き換えや廃止は案内されていません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-explore-a-repository-using-copilot-on-the-web

説明
この週は、GitHub Actions では認証制御とランナー運用に関する更新があり、GitHub Copilot では承認設定、学生向け提供、CLI・Web・JetBrains IDEs での利用機能強化が進みました。

対象期間：2026/03/11～2026/03/18

Action:

- タイトル：セルフホストランナー最小バージョン強制の一時停止
- 内容
	- 運用変更
		- セルフホストランナーに対する最小バージョン強制の適用が一時停止されました。
		- 直近での強制アップデート対応は求められない状態になりました。
		- 現時点では、最小バージョン未満の環境に対する強制適用は停止中です。
		- ランナー管理者は、即時対応の負荷が下がる一方で、今後の再開案内に備えて継続的な更新管理が必要です。
- 情報元：🔗 https://github.blog/changelog/2026-03-13-self-hosted-runner-minimum-version-enforcement-paused

- タイトル：OIDC トークンでリポジトリのカスタムプロパティーを利用可能に
- 内容
	- 認証連携
		- GitHub Actions の OIDC トークンが、リポジトリのカスタムプロパティーに対応しました。
		- リポジトリ単位で定義した属性を、外部クラウドとの認証条件に反映しやすくなりました。
		- OIDC を使う認証・認可ポリシーの条件設定を、より細かく設計できるようになります。
		- クラウド接続時のアクセス制御を、リポジトリ属性に基づいて整理しやすくなる更新です。
- 情報元：🔗 https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties

Copilot:

- タイトル：Copilot コーディングエージェントの Actions ワークフローで承認省略を選択可能に
- 内容
	- 変更点
		- Copilot コーディングエージェントが実行する Actions ワークフローで、承認を省略する設定が選べるようになりました。
		- 承認必須にするかどうかを、運用方針に応じて切り替えられるようになりました。
		- 承認待ちを省く運用では、ワークフロー実行までの時間短縮が見込まれます。
	- 変更がない点
		- Copilot コーディングエージェントが Actions ワークフローを使う前提は変わりません。
		- 承認を必要とする運用を継続する選択肢も維持されます。
- 情報元：🔗 https://github.blog/changelog/2026-03-13-optionally-skip-approval-for-copilot-coding-agent-actions-workflows

- タイトル：学生向け GitHub Copilot の提供内容を更新
- 内容
	- 変更点
		- 学生向け GitHub Copilot に関する更新が公開されました。
		- 学生向け提供枠に関する案内内容が見直されました。
		- 学生利用者は、最新の提供条件や利用案内を確認する必要があります。
	- 変更がない点
		- 対象が学生向け GitHub Copilot である点は変わりません。
		- 学生向けプログラムとして GitHub Copilot を案内する枠組みは継続しています。
- 情報元：🔗 https://github.blog/changelog/2026-03-13-updates-to-github-copilot-for-students

- タイトル：JetBrains IDEs で自動モデル選択機能が一般提供に移行
- 内容
	- 変更点
		- JetBrains IDEs 向け GitHub Copilot の自動モデル選択機能が一般提供になりました。
		- 利用者が都度モデルを選ばなくても、適切なモデルを選択しやすくなりました。
		- JetBrains IDEs での Copilot 利用時に、モデル選択の運用負荷を下げられます。
	- 変更がない点
		- 対象環境が JetBrains IDEs 向け GitHub Copilot である点は変わりません。
		- Copilot を IDE 上で使う基本的な利用形態は維持されます。
- 情報元：🔗 https://github.blog/changelog/2026-03-12-copilot-auto-model-selection-is-generally-available-in-jetbrains-ides

- タイトル：GitHub CLI から Copilot のコードレビューを直接依頼可能に
- 内容
	- 変更点
		- GitHub CLI から Copilot にコードレビューを直接依頼できるようになりました。
		- ターミナル中心の開発フローから、そのままレビュー依頼を実行しやすくなりました。
		- CLI を使った開発や確認作業に、Copilot レビューを組み込みやすくなります。
	- 変更がない点
		- コードレビューの主体が Copilot である点は変わりません。
		- GitHub CLI を使う既存の開発運用に追加で利用できる形です。
- 情報元：🔗 https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli

- タイトル：JetBrains IDEs 向け Copilot のエージェント機能を強化
- 内容
	- 変更点
		- JetBrains IDEs 向け GitHub Copilot で、エージェント型の機能が大きく改善されました。
		- IDE 内での複数段階の支援や作業補助が強化されました。
		- JetBrains IDEs 利用者のコーディング支援体験を拡張する更新です。
	- 変更がない点
		- 対象が JetBrains IDEs 向け GitHub Copilot である点は変わりません。
		- 既存の IDE 連携型の Copilot 利用基盤は維持されます。
- 情報元：🔗 https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides

- タイトル：Web 上で Copilot を使ったリポジトリ探索が可能に
- 内容
	- 変更点
		- GitHub Copilot で、Web 上からリポジトリを探索できるようになりました。
		- ブラウザー上でリポジトリの内容理解を進めやすくなりました。
		- ローカル環境に入る前の確認や把握に Copilot を活用しやすくなります。
	- 変更がない点
		- 対象が Web 上の GitHub Copilot 利用である点は変わりません。
		- リポジトリ探索に Copilot を追加する更新であり、既存の閲覧方法自体がなくなるものではありません。
- 情報元：🔗 https://github.blog/changelog/2026-03-11-explore-a-repository-using-copilot-on-the-web

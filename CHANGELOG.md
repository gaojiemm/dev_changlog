説明
この週は GitHub Actions で OIDC とセルフホストランナー運用に関する更新があり、GitHub Copilot ではモデル提供、CLI・Web・JetBrains・coding agent の機能拡張が進んだ。

対象期間：2026/03/11～2026/03/18

Action:

- タイトル： セルフホストランナーの最低バージョン強制適用を一時停止
- 内容
	- ランナー運用
		- セルフホストランナーの最低バージョン要件の強制適用が一時停止された
		- 最低バージョンへの即時更新を前提にした対応を急がなくてよい状態になった
		- 強制適用の再開時期や再案内には引き続き注意が必要になる
		- 当面は既存ランナー運用を継続しやすくなる更新といえる
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-self-hosted-runner-minimum-version-enforcement-paused

- タイトル： Actions の OIDC トークンがリポジトリのカスタムプロパティに対応
- 内容
	- 認証連携
		- GitHub Actions の OIDC トークンでリポジトリのカスタムプロパティを扱えるようになった
		- 外部クラウドや認証基盤との連携時に参照できるリポジトリ属性が増えた
		- リポジトリ単位の属性を使った認可条件やポリシー設計を行いやすくなった
		- Actions と外部認証の連携をより細かく制御しやすくなる更新である
- 情報元： 🔗 https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties

Copilot:

- タイトル： Copilot coding agent で検証ツールの設定が可能に
- 内容
	- 変更点
		- Copilot coding agent 向けに検証ツールを設定できるようになった
		- エージェント実行時の検証方法を利用環境に合わせて調整しやすくなった
		- coding agent の作業結果を確認する運用を構成しやすくなった
	- 変更がない点
		- GitHub Copilot の coding agent 自体の提供は継続している
		- 他の Copilot 機能の廃止や料金変更には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools

- タイトル： Copilot で GPT-5.3 Codex の長期サポートを提供
- 内容
	- 変更点
		- GitHub Copilot で GPT-5.3 Codex が長期サポート対象になった
		- 継続利用を前提にモデルを選びやすくなった
		- 安定運用を重視する利用計画に組み込みやすくなった
	- 変更がない点
		- GitHub Copilot のモデル利用の枠組み自体は継続している
		- 他モデルの終了や価格改定には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-gpt-5-3-codex-long-term-support-in-github-copilot

- タイトル： Copilot coding agent のセマンティックコード検索を高速化
- 内容
	- 変更点
		- Copilot coding agent がセマンティックコード検索により高速化された
		- 意味ベースのコード検索を使った関連箇所の探索が強化された
		- リポジトリ理解や対象コードの特定をより速く進めやすくなった
	- 変更がない点
		- coding agent の基本的な利用対象と位置づけは継続している
		- 新たな料金や利用条件の変更には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-17-copilot-coding-agent-works-faster-with-semantic-code-search

- タイトル： 組織単位の Copilot 利用状況に CLI 活動が追加
- 内容
	- 変更点
		- Copilot 利用状況メトリクスに組織レベルの GitHub Copilot CLI 活動が追加された
		- CLI 利用分も組織単位で把握できるようになった
		- 利用状況の可視化範囲が広がり、運用状況を確認しやすくなった
	- 変更がない点
		- 既存の Copilot 利用状況把握の仕組みは継続している
		- 個別機能の動作変更や新料金には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-17-copilot-usage-metrics-now-includes-organization-level-github-copilot-cli-activity

- タイトル： Copilot で GPT-5.4 mini を一般提供
- 内容
	- 変更点
		- GitHub Copilot で GPT-5.4 mini が一般提供になった
		- プレビュー段階ではなく正式に利用できるモデルが増えた
		- 日常利用時のモデル選択肢が広がった
	- 変更がない点
		- GitHub Copilot の既存利用フローは継続している
		- 他モデルの終了や IDE 対応範囲の変更には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-17-gpt-5-4-mini-is-now-generally-available-for-github-copilot

- タイトル： Copilot coding agent の Actions ワークフロー承認を任意で省略可能に
- 内容
	- 変更点
		- Copilot coding agent に関連する Actions ワークフローで承認を任意で省略できるようになった
		- 承認手順を必須ではなく選択制で運用できるようになった
		- 条件に応じて実行開始までの待ち時間を減らしやすくなった
	- 変更がない点
		- 承認省略は任意設定であり一律の必須変更ではない
		- Copilot coding agent と Actions ワークフローの連携自体は継続している
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-optionally-skip-approval-for-copilot-coding-agent-actions-workflows

- タイトル： 学生向け GitHub Copilot の提供内容を更新
- 内容
	- 変更点
		- 学生向け GitHub Copilot に関する更新が提供された
		- 更新対象が学生向け利用者であることが明示された
		- 学生向けプランの提供内容が見直された
	- 変更がない点
		- 学生向け GitHub Copilot の提供枠組み自体は継続している
		- 一般向けプランの変更には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-updates-to-github-copilot-for-students

- タイトル： JetBrains IDE で Copilot の自動モデル選択を一般提供
- 内容
	- 変更点
		- JetBrains IDE で Copilot の自動モデル選択が一般提供になった
		- IDE 内でのモデル選択自動化を正式機能として利用できるようになった
		- JetBrains 利用時の設定負荷を下げやすくなった
	- 変更がない点
		- 対象が JetBrains IDE である点は変わっていない
		- 他 IDE の提供範囲変更には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-12-copilot-auto-model-selection-is-generally-available-in-jetbrains-ides

- タイトル： GitHub CLI から Copilot のコードレビューを直接依頼可能に
- 内容
	- 変更点
		- GitHub CLI から Copilot のコードレビューを直接依頼できるようになった
		- CLI 上でレビュー依頼の操作を完結できるようになった
		- ブラウザを介さないレビュー依頼の導線が追加された
	- 変更がない点
		- Copilot のコードレビュー機能自体は継続している
		- GitHub CLI 以外の依頼方法の廃止には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli

- タイトル： JetBrains IDE 向け Copilot のエージェント機能を大幅改善
- 内容
	- 変更点
		- JetBrains IDE 向け GitHub Copilot の agentic capabilities が大きく改善された
		- JetBrains 上でのエージェント型支援の機能強化が行われた
		- IDE 内での作業支援の幅と使い勝手の向上が進んだ
	- 変更がない点
		- 対象が JetBrains IDE である点は維持されている
		- 料金や利用資格の変更には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides

- タイトル： Web 上の Copilot でリポジトリ探索が可能に
- 内容
	- 変更点
		- Web 上の Copilot を使ってリポジトリを探索できるようになった
		- ブラウザからリポジトリ内容を Copilot とともに確認する導線が追加された
		- コードベース理解の初動を Web でも進めやすくなった
	- 変更がない点
		- GitHub Copilot の Web 利用基盤は継続している
		- ローカル IDE や CLI の機能廃止には触れていない
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-explore-a-repository-using-copilot-on-the-web

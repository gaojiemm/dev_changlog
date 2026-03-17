説明
この週は、GitHub Actions では OIDC クレーム拡張とセルフホストランナー運用方針の一時変更があり、GitHub Copilot では承認フロー、学生向けプラン、JetBrains・CLI・Web での利用体験が更新された。

対象期間：2026/03/11～2026/03/18

Action:

- タイトル： OIDC トークンでリポジトリのカスタムプロパティをクレームとして利用可能に
- 内容
	- OIDC クレーム拡張
		- GitHub Actions の OIDC トークンで、リポジトリのカスタムプロパティをクレームとして扱えるようになった。
		- リポジトリ、組織、エンタープライズの設定から、OIDC トークンのクレームを構成できる設定ページが公開プレビューで提供された。
		- クレームにプロパティを追加する設定を、画面上で管理しやすくなった。
		- 外部クラウドや認証先との連携で、リポジトリ属性に基づく制御を行いやすくなる。
- 情報元： 🔗 https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties

- タイトル： セルフホストランナー最小バージョン要件の適用が一時停止
- 内容
	- ランナー運用
		- 2026年3月16日から予定されていた、セルフホストランナー v2.329.0 以上の最小バージョン要件の適用が一時停止された。
		- 一時停止期間中は、v2.329.0 未満のランナーでも登録と設定を継続できる。
		- 直近で予定されていた強制適用は見送られ、既存運用をすぐに変更する必要はなくなった。
		- ランナー更新の猶予が確保された一方で、将来の適用再開に備えた更新計画は引き続き必要となる。
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-self-hosted-runner-minimum-version-enforcement-paused

Copilot:

- タイトル： Copilot コーディングエージェントの Actions ワークフロー承認を任意で省略可能に
- 内容
	- 変更点
		- Copilot コーディングエージェントがプルリクエストを作成した場合や変更を push した場合の Actions ワークフロー承認を、任意で省略できるようになった。
		- オープンソースプロジェクトで Copilot が外部コントリビューター相当として扱われるケースに対し、運用の選択肢が追加された。
		- 人手による承認待ちを減らせるため、Copilot を使った変更提案から実行までの流れを短縮しやすくなった。
	- 変更がない点
		- 承認を必要とする既存の安全側の運用は、設定を変えない限り維持できる。
		- Copilot が作成したプルリクエストや変更が Actions と連動する基本的な仕組み自体は変わらない。
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-optionally-skip-approval-for-copilot-coding-agent-actions-workflows

- タイトル： 学生向け Copilot プランが新プランへ移行
- 内容
	- 変更点
		- GitHub Education 特典を持つ学生は、新しい GitHub Copilot Student プランへ移行した。
		- この移行に伴い、利用可能なモデル構成が更新された。
		- 学生向けに AI ネイティブな学習ツールへの継続投資を前提とした、長期的な提供形態へ見直された。
	- 変更がない点
		- GitHub Education を通じて学生向けに Copilot を提供する方針は維持される。
		- 学生向けに最適化した Copilot 体験を提供する方向性自体は継続される。
- 情報元： 🔗 https://github.blog/changelog/2026-03-13-updates-to-github-copilot-for-students

- タイトル： JetBrains IDE で自動モデル選択が一般提供に移行
- 内容
	- 変更点
		- GitHub Copilot の自動モデル選択機能が、JetBrains IDE 向けに一般提供となった。
		- 対象は全 Copilot プランで、利用者の代わりにモデルの可用性や性能に応じて選択される。
		- JetBrains 環境でのモデル選択の手間を減らし、利用状況に応じた使い分けがしやすくなった。
	- 変更がない点
		- JetBrains IDE で Copilot を利用する基本的な開発体験はそのまま維持される。
		- 各 Copilot プランの枠組み自体は変わらず、その上で自動選択機能が使えるようになった。
- 情報元： 🔗 https://github.blog/changelog/2026-03-12-copilot-auto-model-selection-is-generally-available-in-jetbrains-ides

- タイトル： GitHub CLI から Copilot にコードレビューを依頼可能に
- 内容
	- 変更点
		- `gh pr edit` と `gh pr create` から、GitHub Copilot をレビュアーとして直接指定できるようになった。
		- 既存のプルリクエスト編集時と新規作成時の両方で、ターミナルからレビュー依頼を完結できる。
		- ブラウザへ切り替えずに Copilot レビューを依頼できるため、CLI 中心の開発フローに組み込みやすくなった。
	- 変更がない点
		- プルリクエストの作成や編集を GitHub CLI で行う基本操作は変わらない。
		- Copilot をレビューに活用する運用でも、GitHub 上のプルリクエスト管理の枠組みは維持される。
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli

- タイトル： JetBrains IDE 向けのエージェント機能が大幅に改善
- 内容
	- 変更点
		- GitHub Copilot for JetBrains IDEs のエージェント機能に大幅な改善が入った。
		- JetBrains 環境での Copilot 活用において、エージェント型の支援体験が強化された。
		- IDE 上での支援精度や操作の流れの改善が見込まれる更新として位置付けられている。
	- 変更がない点
		- JetBrains IDE 向け Copilot の提供自体は継続される。
		- JetBrains 上で Copilot を利用する基本的な導入先や利用形態は維持される。
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides

- タイトル： Web 上の Copilot でリポジトリ探索が可能に
- 内容
	- 変更点
		- GitHub Copilot を使って、Web 上でリポジトリを探索できるようになった。
		- ブラウザ上でリポジトリ内容の把握や確認を進める導線が追加された。
		- ローカル環境や IDE に依存せず、Web からコードベース理解を始めやすくなった。
	- 変更がない点
		- GitHub の Web 体験の中で Copilot を利用する流れは維持される。
		- リポジトリそのものの管理方法や GitHub 上の基本的な閲覧機能は変わらない。
- 情報元： 🔗 https://github.blog/changelog/2026-03-11-explore-a-repository-using-copilot-on-the-web

説明
この週は、GitHub Actions で運用設定と ARC 機能が拡充され、Copilot では対応モデル、管理可視化、コーディングエージェントの運用性が継続的に強化された。

対象期間：2026/03/18～2026/03/25

Action:

- タイトル： GitHub Actions の 2026年3月後半アップデート
- 内容
	- ワークフロー運用改善
		- スケジュール実行でタイムゾーンを指定できるようになった
		- 自動デプロイを伴わない環境の利用に対応した
		- 細かな運用上の不便を解消する改善が含まれている
		- 定期実行や環境管理の柔軟性が高まり、実運用での設定負荷を下げやすくなった
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates

- タイトル： Actions Runner Controller 0.14.0 の一般提供開始
- 内容
	- ARC 機能拡張
		- runner scale sets で複数ラベルの利用に対応した
		- actions/scaleset ライブラリクライアントへ移行した
		- リソースのカスタマイズ設定と listener pod のスケジューリング改善が追加された
		- セルフホストランナーの拡張性と運用調整のしやすさが向上した
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0

Copilot:

- タイトル： Gemini 3.1 Pro が主要 IDE 向けにプレビュー提供開始
- 内容
	- 変更点
		- Gemini 3.1 Pro が JetBrains IDEs、Xcode、Eclipse で利用可能になった
		- 提供形態はパブリックプレビューである
		- Copilot Enterprise、Copilot Business、Copilot Pro、Copilot Pro+ が対象となる
	- 変更がない点
		- 対象として案内されている Copilot の各プラン区分はそのまま維持されている
		- GitHub Copilot の提供枠内で追加モデルとして扱われている点は変わらない
- 情報元： 🔗 https://github.blog/changelog/2026-03-23-gemini-3-1-pro-is-now-available-in-jetbrains-ides-xcode-and-eclipse

- タイトル： Copilot 利用状況メトリクスで実際の使用モデルを確認可能に
- 内容
	- 変更点
		- 自動モデル選択を有効にした場合でも、利用状況メトリクスで実際のモデル名を確認できるようになった
		- これまで汎用的な「Auto」表記だった活動が実モデル名に解決表示される
		- 管理者がチームのモデル利用状況をより正確に把握できるようになった
	- 変更がない点
		- 自動モデル選択の利用自体は継続できる
		- 管理者向けの利用状況把握というメトリクスの役割は維持されている
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-copilot-usage-metrics-now-resolve-auto-model-selection-to-actual-models

- タイトル： Copilot コーディングエージェントのコミット追跡性を強化
- 内容
	- 変更点
		- Copilot コーディングエージェントが作成した各コミットをセッションログにたどれるようになった
		- コミット作成者は Copilot として記録される
		- タスクを依頼した人は共同作成者として記録され、生成元の把握がしやすくなった
	- 変更がない点
		- コーディングエージェントがバックグラウンドで作業する仕組み自体は変わらない
		- 人がレビューする運用前提は維持されている
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs

- タイトル： Raycast から Copilot コーディングエージェントのログをライブ監視可能に
- 内容
	- 変更点
		- Raycast 上で Copilot コーディングエージェントのログをライブで確認できるようになった
		- バックグラウンド実行中の状況確認がしやすくなった
		- Raycast 利用者にとって作業導線の中で確認しやすい連携が追加された
	- 変更がない点
		- Copilot コーディングエージェントがバックグラウンドで動作する点は変わらない
		- ログ確認の対象がエージェントのセッションである点は維持されている
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-monitor-copilot-coding-agent-logs-live-in-raycast

- タイトル： Copilot コーディングエージェントのセッション可視性を向上
- 内容
	- 変更点
		- タスクを委任した後の Copilot コーディングエージェントのセッションログを確認しやすくなった
		- エージェントが処理中に何を行ったかを把握できる
		- レビュー前に作業内容を確認するための透明性が高まった
	- 変更がない点
		- タスク委任後にエージェントがバックグラウンドで作業する流れは維持されている
		- 作業後にレビューを求める運用は変わらない
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-more-visibility-into-copilot-coding-agent-sessions

- タイトル： Copilot コーディングエージェントの作業開始を高速化
- 内容
	- 変更点
		- Copilot コーディングエージェントの作業開始速度が 50% 改善された
		- タスク委任から実作業着手までの待ち時間が短縮された
		- 背景処理を使う開発フローの応答性が向上した
	- 変更がない点
		- 対象は Copilot コーディングエージェントである点は変わらない
		- 機能追加ではなく既存エージェントの性能改善である
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-copilot-coding-agent-now-starts-work-50-faster

- タイトル： Copilot コーディングエージェントの検証ツール設定に対応
- 内容
	- 変更点
		- Copilot コーディングエージェント向けに検証ツールを設定できるようになった
		- エージェント実行時の検証手段を利用者側で定義しやすくなった
		- コード変更後の確認フローを運用に合わせて整えやすくなった
	- 変更がない点
		- 対象機能は Copilot コーディングエージェントのままである
		- エージェントを用いたコード作業の基本的な利用形態は維持されている
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools

- タイトル： GPT-5.3 Codex が GitHub Copilot で長期サポート化
- 内容
	- 変更点
		- GPT-5.3 Codex が GitHub Copilot で長期サポート対象になった
		- 利用モデルの継続性を重視した選択肢として扱いやすくなった
		- モデル運用の安定性を求める利用者向けの位置付けが明確になった
	- 変更がない点
		- 対象は引き続き GitHub Copilot 内のモデル提供である
		- GPT-5.3 Codex 自体が Copilot で利用できる前提は維持されている
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-gpt-5-3-codex-long-term-support-in-github-copilot

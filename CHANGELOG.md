説明
この週は、Action ではワークフロー運用性と ARC の拡張性に関する更新があり、Copilot では対応モデルの拡大、利用状況の可視化、コーディングエージェントの追跡性と起動速度の改善が進みました。

対象期間：2026/03/18～2026/03/25

Action:

- タイトル： GitHub Actions の 3 月後半運用改善
- 内容
	- ワークフロー運用改善
		- スケジュール実行のワークフローでタイムゾーン指定に対応しました。
		- 環境機能について、自動デプロイを伴わない使い方が可能になりました。
		- 細かな運用上の不便さの解消を中心とした更新です。
		- 定期実行や環境管理の柔軟性が上がり、既存運用の調整がしやすくなります。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates

- タイトル： Actions Runner Controller 0.14.0 の一般提供開始
- 内容
	- ARC 機能拡張
		- Runner Scale Sets でマルチラベルに対応しました。
		- クライアント実装が `actions/scaleset` ライブラリ利用へ切り替わりました。
		- リソース設定のカスタマイズ項目が追加され、listener Pod のスケジューリングも改善されました。
		- 大規模運用時の割り当て条件や実行基盤の調整がしやすくなります。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0

Copilot:

- タイトル： Gemini 3.1 Pro が複数 IDE でプレビュー提供開始
- 内容
	- 変更点
		- Gemini 3.1 Pro が JetBrains IDE、Xcode、Eclipse で利用可能になりました。
		- 公開プレビューとして提供されています。
		- Copilot Enterprise、Copilot Business、Copilot Pro、Copilot Pro+ が対象です。
	- 変更がない点
		- Copilot の既存プラン区分は維持されています。
		- 提供形態は正式版ではなくプレビューのままです。
- 情報元： 🔗 https://github.blog/changelog/2026-03-23-gemini-3-1-pro-is-now-available-in-jetbrains-ides-xcode-and-eclipse

- タイトル： 利用状況メトリクスで実際のモデル名を表示
- 内容
	- 変更点
		- 自動モデル選択を有効にした場合の利用状況表示が改善されました。
		- これまで汎用的な「Auto」と表示されていた利用分が、実際のモデル名に解決されるようになりました。
		- 管理者がチーム内で使われているモデルを正確に把握できるようになりました。
	- 変更がない点
		- 自動モデル選択そのものの利用方法は継続されます。
		- 利用状況を管理者が確認する仕組み自体は維持されています。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-copilot-usage-metrics-now-resolve-auto-model-selection-to-actual-models

- タイトル： コーディングエージェントのコミット追跡性を強化
- 内容
	- 変更点
		- Copilot coding agent によるコミットは、作成者が Copilot として記録されます。
		- タスクを依頼した人は共同作成者として記録されます。
		- コミットから対応するセッションログを追跡しやすくなりました。
	- 変更がない点
		- 背景でタスクを実行してレビューを求める利用形態は継続されます。
		- コーディングエージェントを使った作業委任の基本フローは維持されています。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs

- タイトル： Raycast でコーディングエージェントのログをライブ監視可能に
- 内容
	- 変更点
		- Raycast から Copilot coding agent のログをリアルタイムで確認できるようになりました。
		- エージェントの進行状況を IDE 外から追いやすくなりました。
		- macOS と Windows で使われる Raycast 連携により、確認手段が増えました。
	- 変更がない点
		- ログ確認の対象は Copilot coding agent のセッションです。
		- コーディングエージェント自体の実行方式は継続されています。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-monitor-copilot-coding-agent-logs-live-in-raycast

- タイトル： コーディングエージェントのセッション可視性を向上
- 内容
	- 変更点
		- タスクを委任した後の Copilot coding agent の動きを、セッションログで確認できるようになりました。
		- バックグラウンド実行中に何を行ったかを把握しやすくなりました。
		- レビュー前に実施内容を確認するための透明性が高まりました。
	- 変更がない点
		- タスク委任後にレビュー依頼を受ける流れは継続されます。
		- エージェントがバックグラウンドで作業する利用形態は維持されています。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-more-visibility-into-copilot-coding-agent-sessions

- タイトル： コーディングエージェントの作業開始を高速化
- 内容
	- 変更点
		- Copilot coding agent の起動最適化が行われました。
		- 作業開始までの時間が 50% 短縮されました。
		- タスク委任後の待ち時間が減り、着手までが速くなりました。
	- 変更がない点
		- 対象は Copilot coding agent の起動部分です。
		- エージェントの基本的な利用フローは継続されます。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-copilot-coding-agent-now-starts-work-50-faster

- タイトル： GPT-5.3 Codex の長期サポート提供
- 内容
	- 変更点
		- GitHub Copilot で GPT-5.3 Codex の長期サポート版が提供されました。
		- 継続利用を前提としたモデル選択肢が追加されました。
		- 長期運用を重視する利用者向けの選択肢が明確になりました。
	- 変更がない点
		- GitHub Copilot の既存利用形態は維持されています。
		- モデル提供の枠組み自体は継続されています。
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-gpt-5-3-codex-long-term-support-in-github-copilot

- タイトル： コーディングエージェントの検証ツール設定に対応
- 内容
	- 変更点
		- Copilot coding agent で検証ツールを設定できるようになりました。
		- エージェント作業後の検証方法を運用に合わせて調整しやすくなりました。
		- タスク実行時の確認手順を構成しやすくなりました。
	- 変更がない点
		- 機能追加の対象は Copilot coding agent です。
		- エージェントにタスクを委任する基本フローは継続されます。
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools

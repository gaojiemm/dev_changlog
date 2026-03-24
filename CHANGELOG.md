説明
この週は GitHub Actions で定期実行とセルフホスト運用の改善が進み、Copilot では対応IDEの拡大に加えて、利用状況の可視化、コーディングエージェントの追跡性、ログ確認、起動速度が強化された。

対象期間：2026/03/18～2026/03/24

Action:

- タイトル： 定期実行と環境利用の細かな運用改善
- 内容
	- ワークフロー運用改善
		- スケジュール実行のワークフローでタイムゾーン指定に対応した。
		- 自動デプロイを伴わない形でも environment を利用できるようになった。
		- 既存運用で不便だった細かな点がまとめて改善された。
		- 定期実行の設定精度と environment 活用の自由度が上がり、運用時の調整負荷を下げやすくなった。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates

- タイトル： Actions Runner Controller 0.14.0 の一般提供開始
- 内容
	- ARC 0.14.0 の主な更新
		- runner scale sets で複数ラベルの利用に対応した。
		- クライアント実装が `actions/scaleset` ライブラリへ切り替えられた。
		- リソースのカスタマイズ設定が追加され、listener pod のスケジューリングも改善された。
		- セルフホスト runner の拡張性と配置効率が高まり、大規模運用時の調整がしやすくなった。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0

Copilot:

- タイトル： JetBrains、Xcode、Eclipse で Gemini 3.1 Pro を試用可能に拡大
- 内容
	- 変更点
		- Gemini 3.1 Pro が JetBrains IDE、Xcode、Eclipse で利用可能になった。
		- 提供形態は公開プレビューとして案内された。
		- 対象は Copilot Enterprise、Copilot Business、Copilot Pro、Copilot Pro+ の利用者である。
	- 変更がない点
		- Copilot の提供対象は既存の契約プラン区分に沿っている。
		- 今回の案内は利用可能なIDEの拡大が中心で、記事要約上は料金や契約条件の変更は示されていない。
- 情報元： 🔗 https://github.blog/changelog/2026-03-23-gemini-3-1-pro-is-now-available-in-jetbrains-ides-xcode-and-eclipse

- タイトル： 自動モデル選択時の利用実績が実モデル名で確認可能に改善
- 内容
	- 変更点
		- Copilot usage metrics で、自動モデル選択時の利用実績が実際のモデル名に解決表示されるようになった。
		- 従来の汎用的な「Auto」表記ではなく、実際に使われたモデルを確認できる。
		- 管理者がチームのモデル利用状況を、より完全かつ正確に把握しやすくなった。
	- 変更がない点
		- 自動モデル選択の利用前提自体は維持される。
		- 利用状況の確認主体が管理者である点は変わらない。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-copilot-usage-metrics-now-resolve-auto-model-selection-to-actual-models

- タイトル： コーディングエージェントのコミット追跡性を強化
- 内容
	- 変更点
		- Copilot coding agent が作成した各コミットは、Copilot 名義で記録されるよう整理された。
		- タスクを依頼した人は共同作成者として記録される。
		- コミットから該当セッションログを追跡しやすくなり、生成経緯の確認性が上がった。
	- 変更がない点
		- 対象はクラウドベースの Copilot coding agent のコミットである。
		- 人がタスクを依頼する運用前提は維持される。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs

- タイトル： Raycast からコーディングエージェントのログをライブ監視可能に
- 内容
	- 変更点
		- Copilot coding agent のログを Raycast からライブで監視できるようになった。
		- ログ確認の導線が Raycast に広がり、エージェントの進行状況を追いやすくなった。
		- 利用環境として、Raycast が macOS と Windows 向けのランチャーであることが案内されている。
	- 変更がない点
		- 監視対象は Copilot coding agent のセッションログである。
		- Raycast はアプリ起動やファイル検索などを行える既存のランチャーとして位置付けられている。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-monitor-copilot-coding-agent-logs-live-in-raycast

- タイトル： コーディングエージェントのセッション内容を確認しやすく改善
- 内容
	- 変更点
		- Copilot coding agent に委任したタスクのセッションログを閲覧できるようになった。
		- バックグラウンドで何を実施したかを後から確認できる。
		- レビュー時に作業過程を把握しやすくなり、確認作業の透明性が高まった。
	- 変更がない点
		- タスク委任後にエージェントがバックグラウンドで作業する流れは維持される。
		- 作業後にレビューを求める運用は変わらない。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-more-visibility-into-copilot-coding-agent-sessions

- タイトル： コーディングエージェントの作業開始速度を改善
- 内容
	- 変更点
		- Copilot coding agent の最初の作業開始が 50% 速くなった。
		- エージェントの起動処理が最適化された。
		- タスク着手までの待ち時間が短くなり、依頼開始直後の応答性が改善した。
	- 変更がない点
		- 対象機能は Copilot coding agent である。
		- 今回の案内は作業開始速度の改善が中心で、記事要約上は機能範囲そのものの変更は示されていない。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-copilot-coding-agent-now-starts-work-50-faster

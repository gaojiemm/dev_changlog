説明
この週は GitHub Actions の運用改善に加え、Copilot ではコーディングエージェントの可視化・起動速度・検証設定・利用モデルの拡充が進みました。

対象期間：[2026/03/18]～[2026/03/25]

Action:

- タイトル： GitHub Actions の定期実行と環境利用に関する細かな改善
- 内容
	- ワークフロー運用改善
		- スケジュール実行ワークフローでタイムゾーン指定に対応しました。
		- 自動デプロイを伴わない形でも environment を利用できるようになりました。
		- 月内更新として、運用上の細かな使い勝手の課題解消が進められました。
		- 定期実行の設定精度と environment 活用の柔軟性が上がり、運用設計がしやすくなります。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates

- タイトル： Actions Runner Controller 0.14.0 の一般提供開始
- 内容
	- ARC 機能拡張
		- runner scale sets で複数ラベルを扱えるようになりました。
		- クライアント実装が actions/scaleset ライブラリ利用に切り替わりました。
		- リソース設定のカスタマイズ性が追加され、listener pod のスケジューリングも改善されました。
		- セルフホスト運用の柔軟性とスケーラビリティが向上し、大規模運用に適した更新です。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0

Copilot:

- タイトル： Gemini 3.1 Pro が JetBrains・Xcode・Eclipse で利用可能に
- 内容
	- 変更点
		- Gemini 3.1 Pro が JetBrains IDE、Xcode、Eclipse で利用可能になりました。
		- 提供形態はパブリックプレビューです。
		- 対象は Copilot Enterprise、Copilot Business、Copilot Pro、Copilot Pro+ です。
	- 変更がない点
		- Copilot の既存プラン体系の中で提供される構成は維持されています。
		- 正式提供ではなく、プレビュー段階での提供である点は変わりません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-23-gemini-3-1-pro-is-now-available-in-jetbrains-ides-xcode-and-eclipse

- タイトル： 利用状況メトリクスで自動選択モデルの実モデル名を表示
- 内容
	- 変更点
		- 自動モデル選択を有効化している場合でも、利用状況メトリクス上で実際に使われたモデル名を確認できるようになりました。
		- 従来の汎用的な「Auto」表示が、実モデル名ベースの表示に置き換わりました。
		- 管理者がチーム内のモデル利用状況をより正確に把握できるようになりました。
	- 変更がない点
		- 自動モデル選択そのものの利用方式は維持されています。
		- 利用状況メトリクスを管理用途で確認する基本的な位置付けは変わりません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-copilot-usage-metrics-now-resolve-auto-model-selection-to-actual-models

- タイトル： コーディングエージェントのコミットをセッションログまで追跡可能に
- 内容
	- 変更点
		- Copilot coding agent が作成した各コミットは Copilot 名義で記録されるようになりました。
		- タスクを指示した人は co-author として記録されます。
		- どのコミットがエージェント生成か、誰が開始した作業かを追跡しやすくなりました。
	- 変更がない点
		- Copilot coding agent がバックグラウンドで作業する前提は維持されています。
		- 人によるレビューを前提とした運用の流れ自体は変わりません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-trace-any-copilot-coding-agent-commit-to-its-session-logs

- タイトル： Raycast からコーディングエージェントのログをリアルタイム監視可能に
- 内容
	- 変更点
		- Raycast 上で Copilot coding agent のログをライブで確認できるようになりました。
		- エージェント実行状況の確認導線が Raycast に広がりました。
		- ログ確認を既存の作業環境に寄せて行いやすくなりました。
	- 変更がない点
		- コーディングエージェントのログという確認対象自体は維持されています。
		- Raycast はログ閲覧手段の追加であり、エージェントの基本動作そのものを置き換えるものではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-20-monitor-copilot-coding-agent-logs-live-in-raycast

- タイトル： コーディングエージェントのセッション可視性を強化
- 内容
	- 変更点
		- タスク委任後の Copilot coding agent のセッションログを確認できるようになりました。
		- バックグラウンド実行中に何を行ったかを把握しやすくなりました。
		- レビュー前にエージェントの作業内容を確認する透明性が高まりました。
	- 変更がない点
		- タスクを委任し、完了後にレビューする基本フローは維持されています。
		- エージェントがバックグラウンドで作業する方式自体は変わりません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-more-visibility-into-copilot-coding-agent-sessions

- タイトル： コーディングエージェントの作業開始を高速化
- 内容
	- 変更点
		- Copilot coding agent の作業開始が 50% 高速化されました。
		- タスク投入から実際の作業開始までの待ち時間が短縮されました。
		- バックグラウンド実行の立ち上がりが改善され、応答性が上がりました。
	- 変更がない点
		- コーディングエージェントを使った委任型の作業方式は維持されています。
		- 作業後に結果を確認する利用形態そのものは変わりません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-19-copilot-coding-agent-now-starts-work-50-faster

- タイトル： GPT-5.3 Codex の長期サポートを Copilot で提供
- 内容
	- 変更点
		- GitHub Copilot で GPT-5.3 Codex の長期サポート提供が始まりました。
		- 継続利用を前提にした安定的なモデル選択肢が追加されました。
		- モデル更新頻度の影響を抑えたい利用者に向く位置付けの更新です。
	- 変更がない点
		- 提供先は GitHub Copilot の利用文脈の中にとどまります。
		- 今回の主眼はモデル提供期間の整理であり、他機能の大幅変更を示す更新ではありません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-gpt-5-3-codex-long-term-support-in-github-copilot

- タイトル： コーディングエージェントの検証ツール設定に対応
- 内容
	- 変更点
		- Copilot coding agent で利用する検証ツールを設定できるようになりました。
		- 生成変更に対して、確認に使うツール類を運用に合わせて定義しやすくなりました。
		- チームの検証手順に沿ったエージェント活用を進めやすくなりました。
	- 変更がない点
		- Copilot coding agent を用いた開発支援の枠組み自体は維持されています。
		- 今回の更新は検証設定の追加が中心であり、エージェントの基本的な役割は変わりません。
- 情報元： 🔗 https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools

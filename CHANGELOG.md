# GitHub Changelog 週間要約

## 対象期間
- 2026-03-05 〜 2026-03-11 (JST)

## 今週の要点
- GPT-5.4 が GitHub Copilot に正式提供開始、エージェント型コーディング能力が強化された
- Copilot と Figma の連携が拡張され、デザインとコードの双方向ワークフローが実現
- Dependabot が pre-commit フックの依存関係自動更新に対応
- CodeQL 2.24.3 リリース、Java 26 サポートおよびコードスキャン精度が向上
- GitHub Projects の階層ビュー改善と、Jira 連携による Copilot コーディングエージェントがパブリックプレビュー開始

## 注目アップデート
### 1. Copilot のモデル・エージェント機能強化
- 概要: GPT-5.4 の正式提供開始、VS Code 向け Copilot の 2 月リリースにより長時間・複雑なタスクへの対応が向上した。プルリクエストコメントでの使用モデル選択も可能になった。
- 影響: Copilot を日常的に使う開発者全般。特に複数ステップにわたる作業やコードレビュー支援の品質が向上する。
- 関連項目:
	- GPT-5.4 の正式提供
	- VS Code 向け Copilot v1.110（2 月リリース）
	- プルリクエストコメントでのモデル指定機能

### 2. Figma と Copilot の双方向連携
- 概要: VS Code から Figma MCP サーバーへ接続し、デザインコンテキストをコードに取り込むだけでなく、生成した UI を Figma の編集可能なフレームとして書き戻せるようになった。
- 影響: デザインとコードを行き来するフロントエンド開発者・デザイナー。Figma → コード → Figma のサイクルが一つの環境で完結する。
- 関連項目:
	- VS Code での Figma MCP サーバー接続
	- Copilot CLI への展開（近日予定）

### 3. セキュリティスキャン機能の更新
- 概要: CodeQL 2.24.3 で Java 26 サポートが追加されスキャン精度が改善。シークレットスキャンの検出パターンも 3 月分が更新された。
- 影響: Java を使うプロジェクトや、シークレット漏洩リスクを管理するセキュリティ担当者に直接関係する。
- 関連項目:
	- CodeQL 2.24.3 リリース
	- シークレットスキャンパターン更新（2026 年 3 月）

## カテゴリ別サマリー
- Copilot: GPT-5.4 正式提供、VS Code v1.110 リリース、Figma 双方向連携、プルリクエストでのモデル選択、エンタープライズ向けセッションフィルター追加
- Security: CodeQL 2.24.3（Java 26 対応・精度向上）、シークレットスキャンパターン更新
- Projects / Collaboration: GitHub Projects の階層ビュー改善・イシューフォームへのファイルアップロード対応、Jira 向け Copilot コーディングエージェントがパブリックプレビュー開始
- Other: Dependabot が pre-commit フックの依存関係自動更新に対応

## 監視メモ
- Figma MCP 連携の Copilot CLI 対応は「近日予定」とされており、リリース時期を追うとよい
- Jira 向け Copilot コーディングエージェントはパブリックプレビュー段階のため、正式提供への移行と機能拡張に注意
- GPT-5.4 のロールアウト状況（段階的展開の完了タイミング）を継続確認
- Dependabot の pre-commit サポートは新規エコシステム対応であり、他ツールへの拡張動向も注目

## 参考URL
- https://github.blog/changelog/2026-03-05-gpt-5-4-is-generally-available-in-github-copilot
- https://github.blog/changelog/2026-03-06-figma-mcp-server-can-now-generate-design-layers-from-vs-code
- https://github.blog/changelog/2026-03-10-codeql-2-24-3-adds-java-26-support-and-other-improvements
- https://github.blog/changelog/2026-03-10-dependabot-now-supports-pre-commit-hooks
- https://github.blog/changelog/2026-03-05-github-copilot-coding-agent-for-jira-is-now-in-public-preview
- https://github.blog/changelog/2026-03-06-github-copilot-in-visual-studio-code-v1-110-february-release

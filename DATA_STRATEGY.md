# データ取得の3層戦略

## 問題
RSS フィードは最近のエントリーのみを保持（約 10-30 件）し、古い期間のデータはロールアウトされるため、履歴データをクエリできません。

## 解決方法：3層の順序ロード

```
クエリリクエスト（日付範囲）
  ↓
第1層: RSS フィード（高速、最新）
  → 0 件～N 件のデータ（時間経過に依存）
  ↓
第2層: ローカルキャッシュ (cache.json)
  → 履歴データを高速に補充
  ↓
第3層: 公式ウェブページスクレイピング (GitHub Changelog ウェブ)
  → 完全取得、キャッシュを自動更新
  ↓
最終備選: KNOWN_MISSING_ENTRIES（ハードコード）
  → 上位レイヤーすべてが失敗した場合のみ使用
```

## ワークフロー

### 1. RSS 取得（最速）
```python
entries = parse_feed(fetch_feed(FEED_URL))
# 通常、最新の 10-20 件を返す
```

### 2. キャッシュ補充（秒級）
```python
cache = load_cache()  # cache.json を読み込み
cached = get_cached_entries(since, until)
entries.extend(cached)  # 履歴データを補充
```

### 3. ウェブページスクレイピング（オプション）
データがまだ不足している場合（< 5 件）：
```python
web_entries = fetch_from_official_page(since, until)
entries.extend(web_entries)
save_cache(cache)  # キャッシュを自動更新、次回使用時に使用
```

### 4. 備選（極端な場合）
```python
entries = add_known_missing_entries(entries)  # ハードコードリスト
```

## ファイル説明

### `cache.json` - キャッシュファイル
```json
{
  "metadata": {
    "last_updated": "2026-03-22T00:00:00Z"
  },
  "entries": {
    "2026-03-11_2026-03-18": [
      { "date": "2026-03-11", "title": "...", "link": "...", ... }
    ]
  }
}
```

**特徴**:
- 日付範囲で整理（キー = "開始日_終了日"）
- 新しくスクレイピングしたウェブデータを自動保存
- 実行成功後も保持、手動メンテナンスは不要

### `scripts/generate_github_changelog.py` - メインスクリプト
**新規関数**:
- `load_cache()` - キャッシュを読み込み
- `save_cache()` - キャッシュを保存
- `get_cached_entries()` - キャッシュから特定の日付範囲のデータを取得
- `fetch_from_official_page()` - 公式ウェブページをスクレイピング
- `check_and_fill_missing_entries()` - 3層戦略を実行

## 使用例

### 最近1週間をクエリ（通常ケース、RSS を使用）
```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-16 \
  --until 2026-03-22 \
  --language ja \
  --use-github-ai \
  --ai-provider copilot-cli \
  --output CHANGELOG.md
```
**予期される出力**: 
```
[data] RSS provided 10 entries
```

### 過去のある週をクエリ（キャッシュから自動復元）
```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --output CHANGELOG.md
```
**予期される出力**:
```
[data] RSS provided 0 entries
[data] Cache has 13 entries
```

### 新しい期間をクエリ（ウェブから自動取得およびキャッシュ）
```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-02-15 \
  --until 2026-02-21 \
  --language ja \
  --output CHANGELOG.md
```
**予期される出力**:
```
[data] RSS provided 0 entries
[data] Fetching from official page...
[data] Official page provided 8 entries
```
同じ範囲への後続クエリ：
```
[data] RSS provided 0 entries
[data] Cache has 8 entries
```

## メリット

| 問題 | 旧方法 | 新方法 |
|------|--------|--------|
| RSS 期限切れデータ | ❌ クエリ不可 | ✅ キャッシュが自動補充 |
| 手動メンテナンス | ⚠️ KNOWN_MISSING_ENTRIES が必要 | ✅ キャッシュを自動更新 |
| クエリ速度 | ~ | ✅ キャッシュは秒級レスポンス |
| データ完全性 | ⚠️ 常に不完全 | ✅ ウェブスクレイピングが完全性を保証 |
| メンテナンスコスト | ⚠️ 高い | ✅ 極めて低い |

## 制限事項と今後の改善

1. **現在**: ウェブスクレイピングは正規表現のみ（シンプルだが信頼性がある）
2. **将来**: BeautifulSoup に切り替え、より複雑な HTML パースが可能
3. **現在**: キャッシュキーは "開始_終了"、固定範囲
4. **将来**: タイムスタンプ範囲に変更、クロスレンジクエリをサポート可能

## デバッグ

実行ログを確認：
```bash
python3 scripts/generate_github_changelog.py ... 2>&1 | grep "\[data\]"
```

キャッシュをクリアして再開始：
```bash
rm cache.json
```

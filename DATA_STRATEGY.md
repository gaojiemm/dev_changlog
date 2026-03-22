# 数据获取三层策略

## 问题
RSS 源只保留最近的条目（约 10-30 条），较早期间的数据会轮转掉，导致无法查询历史数据。

## 解决方案：三层顺序加载

```
查询请求 (日期范围)
  ↓
第1层: RSS 源（快速，最新）
  → 0 条～N 条数据（取决于时间推移）
  ↓
第2层: 本地缓存 (cache.json)
  → 快速补充历史数据
  ↓
第3层: 官方网页爬取 (GitHub Changelog 网页)
  → 完整获取，自动更新缓存
  ↓
最后备选: KNOWN_MISSING_ENTRIES（硬编码）
  → 仅当上层都失败时使用
```

## 工作流程

### 1. RSS 获取（最快）
```python
entries = parse_feed(fetch_feed(FEED_URL))
# 通常返回最近 10-20 条
```

### 2. 缓存补充（秒级）
```python
cache = load_cache()  # 读取 cache.json
cached = get_cached_entries(since, until)
entries.extend(cached)  # 补充历史数据
```

### 3. 网页爬取（可选）
如果数据仍然不足（< 5 条），则：
```python
web_entries = fetch_from_official_page(since, until)
entries.extend(web_entries)
save_cache(cache)  # 自动更新缓存，下次使用
```

### 4. 备选（极端情况）
```python
entries = add_known_missing_entries(entries)  # 硬编码列表
```

## 文件说明

### `cache.json` - 缓存文件
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

**特点**:
- 按日期范围组织（键 = "开始日期_结束日期"）
- 自动保存新抓取的网页数据
- 跨执行保留，无需手动维护

### `scripts/generate_github_changelog.py` - 主脚本
**新增函数**:
- `load_cache()` - 读取缓存
- `save_cache()` - 保存缓存
- `get_cached_entries()` - 从缓存获取特定日期范围的数据
- `fetch_from_official_page()` - 爬取官方网页
- `check_and_fill_missing_entries()` - 执行三层策略

## 使用示例

### 查询最近一周（正常情况，使用 RSS）
```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-16 \
  --until 2026-03-22 \
  --language ja \
  --use-github-ai \
  --ai-provider copilot-cli \
  --output CHANGELOG.md
```
**预期输出**: 
```
[data] RSS provided 10 entries
```

### 查询过去的某个周（自动从缓存恢复）
```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-03-11 \
  --until 2026-03-18 \
  --language ja \
  --output CHANGELOG.md
```
**预期输出**:
```
[data] RSS provided 0 entries
[data] Cache has 13 entries
```

### 查询全新期间（自动从网页获取并缓存）
```bash
python3 scripts/generate_github_changelog.py \
  --since 2026-02-15 \
  --until 2026-02-21 \
  --language ja \
  --output CHANGELOG.md
```
**预期输出**:
```
[data] RSS provided 0 entries
[data] Fetching from official page...
[data] Official page provided 8 entries
```
后续查询同一范围时：
```
[data] RSS provided 0 entries
[data] Cache has 8 entries
```

## 优势

| 问题 | 旧方案 | 新方案 |
|------|--------|--------|
| RSS 过期数据 | ❌ 无法查询 | ✅ 缓存自动补充 |
| 手动维护 | ⚠️ 需手编 KNOWN_MISSING_ENTRIES | ✅ 自动更新缓存 |
| 查询速度 | ~ | ✅ 缓存秒级响应 |
| 数据完整性 | ⚠️ 总是不完整 | ✅ 网页爬取保证完整 |
| 维护成本 | ⚠️ 高 | ✅ 极低 |

## 局限和未来改进

1. **当前**: 网页爬取仅用正则（简单但可靠）
2. **未来**: 可切换到 BeautifulSoup 做更复杂的 HTML 解析
3. **当前**: 缓存 key 为 "开始_结束"，固定范围
4. **未来**: 可改为时间戳范围，支持跨范围查询

## 调试

查看执行日志：
```bash
python3 scripts/generate_github_changelog.py ... 2>&1 | grep "\[data\]"
```

清除缓存重新开始：
```bash
rm cache.json
```

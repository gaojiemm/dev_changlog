#!/usr/bin/env python3
"""
CHANGELOG.md と GitHub 公式データの一致性を検証する

使用方法:
    python3 scripts/verify_changelog.py                          # 現在の CHANGELOG.md を検証
    python3 scripts/verify_changelog.py --since 2026-03-18 --until 2026-03-25    # 対象期間を指定して検証
    python3 scripts/verify_changelog.py --include-all            # Action/Copilot 以外も含めて検証
"""

import urllib.request
import re
import sys
from datetime import datetime
from pathlib import Path

def extract_from_changelog(changelog_path):
    """ローカルの CHANGELOG.md から条目を抽出する"""
    entries = []
    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 対象期間を抽出
        date_match = re.search(r'対象期間：(\d{4})/(\d{2})/(\d{2})～(\d{4})/(\d{2})/(\d{2})', content)
        if date_match:
            since = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            until = f"{date_match.group(4)}-{date_match.group(5)}-{date_match.group(6)}"
        else:
            since = until = None
        
        # 記事 URL を抽出
        matches = re.findall(
            r'https://github\.blog/changelog/(\d{4}-\d{2}-\d{2})-([^\s<"\']+)',
            content
        )
        entries = sorted(set(matches), reverse=True)
        
        return entries, since, until
    except FileNotFoundError:
        print(f"❌ ファイルが存在しません: {changelog_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)

def fetch_from_sitemaps(since=None, until=None):
    """公式 Sitemap から条目を取得する"""
    official_entries = []
    
    print("⏳ 公式 Sitemap からデータを取得しています...", file=sys.stderr)
    
    for sitemap_num in [4, '', 3, 2]:
        url = f"https://github.blog/changelog-sitemap{sitemap_num}.xml"
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                xml = r.read().decode('utf-8')
            
            matches = re.findall(
                r'https://github\.blog/changelog/(\d{4}-\d{2}-\d{2})-([^\s<"\'\\]+)',
                xml
            )
            
            for date_str, slug in matches:
                if since and until:
                    if not (since <= date_str <= until):
                        continue
                official_entries.append((date_str, slug))
        except Exception as e:
            print(f"⚠️ {url} の取得に失敗しました", file=sys.stderr)
            continue
    
    return sorted(set(official_entries), reverse=True)

def get_label_category(slug):
    """slug から分類を判定する"""
    action_keywords = {'action', 'actions', 'runner', 'workflow', 'oidc', 'reusable', 'artifact', 'arc'}
    copilot_keywords = {'copilot', 'gpt', 'gemini'}

    slug_lower = slug.lower()
    tokens = set(slug_lower.split('-'))

    if tokens & action_keywords:
        return 'Action'
    elif tokens & copilot_keywords or 'copilot' in slug_lower:
        return 'Copilot'
    else:
        return 'Other'


def filter_target_entries(entries, include_all=False):
    """検証範囲に応じて条目を絞り込む。既定では Action/Copilot のみ。"""
    if include_all:
        return entries
    return [entry for entry in entries if get_label_category(entry[1]) in ['Action', 'Copilot']]

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CHANGELOG.md と GitHub 公式データの一致性を検証します。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
    例:
  python3 scripts/verify_changelog.py
  python3 scripts/verify_changelog.py --since 2026-03-18 --until 2026-03-25
  python3 scripts/verify_changelog.py --include-all
        '''
    )
    
    parser.add_argument(
        '--changelog',
        default='CHANGELOG.md',
        help='CHANGELOG ファイルのパスです (既定: CHANGELOG.md)'
    )
    parser.add_argument('--since', help='検証対象の開始日です (YYYY-MM-DD)')
    parser.add_argument('--until', help='検証対象の終了日です (YYYY-MM-DD)')
    parser.add_argument(
        '--include-all',
        action='store_true',
        help='Action/Copilot 以外のカテゴリも含めて検証します'
    )
    
    args = parser.parse_args()
    
    # ローカル CHANGELOG を読み込む
    changelog_path = Path(args.changelog)
    if not changelog_path.is_absolute():
        changelog_path = Path.cwd() / changelog_path
    
    local_entries, local_since, local_until = extract_from_changelog(changelog_path)
    
    # 日付未指定時は CHANGELOG 記載の期間を使う
    check_since = args.since or local_since
    check_until = args.until or local_until
    
    # 公式データを取得する
    official_entries = fetch_from_sitemaps(check_since, check_until)
    
    print("\n" + "=" * 70)
    print("📊 CHANGELOG 一致性検証レポート")
    print("=" * 70 + "\n")
    
    print(f"📅 検証期間: {check_since} ~ {check_until}\n")
    
    # ローカル条目
    print(f"📋 ローカル CHANGELOG.md: {len(local_entries)} 件")
    if args.include_all:
        for date, slug in local_entries:
            print(f"   {date} - {slug}")
    else:
        for date, slug in local_entries:
            category = get_label_category(slug)
            marker = '✅' if category in ['Action', 'Copilot'] else '⚠️'
            print(f"   {marker} [{category:7}] {date} - {slug}")
    print()
    
    # 公式条目
    print(f"🌐 公式 Sitemap: {len(official_entries)} 件")
    if args.include_all:
        for date, slug in official_entries:
            print(f"   {date} - {slug}")
    else:
        for date, slug in official_entries:
            category = get_label_category(slug)
            marker = '✅' if category in ['Action', 'Copilot'] else '⚠️'
            print(f"   {marker} [{category:7}] {date} - {slug}")
    print()
    
    # 差分比較
    print("=" * 70)
    print("📋 差分比較")
    print("=" * 70 + "\n")
    
    comparison_local_entries = filter_target_entries(local_entries, args.include_all)
    comparison_official_entries = filter_target_entries(official_entries, args.include_all)

    local_set = set(comparison_local_entries)
    official_set = set(comparison_official_entries)
    
    missing = official_set - local_set
    extra = local_set - official_set
    
    status = "✅ 一致"
    if missing or extra:
        status = "⚠️ 不一致"
    
    print(f"判定: {status}\n")
    
    if missing:
        print(f"❌ ローカルに不足している条目: {len(missing)} 件")
        for date, slug in sorted(missing, reverse=True):
            category = get_label_category(slug)
            is_target = "✅" if category in ['Action', 'Copilot'] else "⚠️"
            print(f"   {is_target} [{category:7}] {date} - {slug}")
        print()
    
    if extra:
        print(f"❌ ローカルのみに存在する条目: {len(extra)} 件")
        for date, slug in sorted(extra, reverse=True):
            category = get_label_category(slug)
            print(f"   [{category:7}] {date} - {slug}")
        print()
    
    if not missing and not extra:
        print("✅ すべての対象条目が一致しました。\n")
    
    # 件数集計
    print("=" * 70)
    print("📈 集計")
    print("=" * 70 + "\n")
    
    local_action = sum(1 for _, slug in local_entries if get_label_category(slug) == 'Action')
    local_copilot = sum(1 for _, slug in local_entries if get_label_category(slug) == 'Copilot')
    local_other = len(local_entries) - local_action - local_copilot
    
    official_action = sum(1 for _, slug in official_entries if get_label_category(slug) == 'Action')
    official_copilot = sum(1 for _, slug in official_entries if get_label_category(slug) == 'Copilot')
    official_other = len(official_entries) - official_action - official_copilot
    
    print(f"ローカル CHANGELOG.md:")
    print(f"  - Action:  {local_action}")
    print(f"  - Copilot: {local_copilot}")
    print(f"  - Other:   {local_other}")
    print(f"  - 合計:    {len(local_entries)}\n")
    
    print(f"公式 Sitemap:")
    print(f"  - Action:  {official_action}")
    print(f"  - Copilot: {official_copilot}")
    print(f"  - Other:   {official_other}")
    print(f"  - 合計:    {len(official_entries)}\n")
    
    # 案内
    if missing and not args.include_all:
        print("=" * 70)
        print("💡 補足")
        print("=" * 70 + "\n")
        
        missing_action = [s for d, s in missing if get_label_category(s) == 'Action']
        missing_copilot = [s for d, s in missing if get_label_category(s) == 'Copilot']
        missing_other = len(missing) - len(missing_action) - len(missing_copilot)
        
        if missing_action or missing_copilot:
            action_count = len(missing_action)
            copilot_count = len(missing_copilot)
            print(f"不足している Action/Copilot 条目: {action_count + copilot_count}")
            print(f"  - Action:  {action_count}")
            print(f"  - Copilot: {copilot_count}\n")
            print("👉 CHANGELOG を更新する場合は再生成を実行してください。\n")
        
        if missing_other:
            print(f"⚠️  対象外カテゴリの不足条目: {missing_other} 件")
            print("   これは正常です。CHANGELOG は Action と Copilot のみを対象にしています。\n")
    
    # 終了コード
    return 0 if (not missing and not extra) else 1

if __name__ == '__main__':
    sys.exit(main())

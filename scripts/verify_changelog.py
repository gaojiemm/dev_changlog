#!/usr/bin/env python3
"""
验证 CHANGELOG.md 与 GitHub 官网数据一致性

使用方法:
  python3 scripts/verify_changelog.py                          # 验证当前 CHANGELOG.md
  python3 scripts/verify_changelog.py --since 2026-03-18 --until 2026-03-25    # 指定日期范围
  python3 scripts/verify_changelog.py --include-all            # 包含所有类别（不仅仅 Action/Copilot）
"""

import urllib.request
import re
import sys
from datetime import datetime
from pathlib import Path

def extract_from_changelog(changelog_path):
    """从本地 CHANGELOG.md 提取条目"""
    entries = []
    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取日期范围
        date_match = re.search(r'対象期間：(\d{4})/(\d{2})/(\d{2})～(\d{4})/(\d{2})/(\d{2})', content)
        if date_match:
            since = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            until = f"{date_match.group(4)}-{date_match.group(5)}-{date_match.group(6)}"
        else:
            since = until = None
        
        # 提取所有 URL
        matches = re.findall(
            r'https://github\.blog/changelog/(\d{4}-\d{2}-\d{2})-([^\s<"\']+)',
            content
        )
        entries = sorted(set(matches), reverse=True)
        
        return entries, since, until
    except FileNotFoundError:
        print(f"❌ 文件不存在: {changelog_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 读取文件出错: {e}")
        sys.exit(1)

def fetch_from_sitemaps(since=None, until=None):
    """从官网 Sitemap 获取条目"""
    official_entries = []
    
    print("⏳ 正在从官网 Sitemap 获取数据...", file=sys.stderr)
    
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
            print(f"⚠️ 获取 {url} 失败", file=sys.stderr)
            continue
    
    return sorted(set(official_entries), reverse=True)

def get_label_category(slug):
    """根据条目的 slug 判断分类"""
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
    """按验证范围过滤条目，默认仅保留 Action/Copilot"""
    if include_all:
        return entries
    return [entry for entry in entries if get_label_category(entry[1]) in ['Action', 'Copilot']]

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='验证 CHANGELOG.md 与 GitHub 官网数据一致性',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python3 scripts/verify_changelog.py
  python3 scripts/verify_changelog.py --since 2026-03-18 --until 2026-03-25
  python3 scripts/verify_changelog.py --include-all
        '''
    )
    
    parser.add_argument('--changelog', default='CHANGELOG.md',
                       help='CHANGELOG 文件路径 (默认: CHANGELOG.md)')
    parser.add_argument('--since', help='检查的开始日期 (YYYY-MM-DD)')
    parser.add_argument('--until', help='检查的结束日期 (YYYY-MM-DD)')
    parser.add_argument('--include-all', action='store_true',
                       help='包含所有类别（不仅仅 Action/Copilot）')
    
    args = parser.parse_args()
    
    # 读取本地 CHANGELOG
    changelog_path = Path(args.changelog)
    if not changelog_path.is_absolute():
        changelog_path = Path.cwd() / changelog_path
    
    local_entries, local_since, local_until = extract_from_changelog(changelog_path)
    
    # 如果没有指定日期，使用 CHANGELOG 中的日期
    check_since = args.since or local_since
    check_until = args.until or local_until
    
    # 从官网获取数据
    official_entries = fetch_from_sitemaps(check_since, check_until)
    
    print("\n" + "=" * 70)
    print("📊 CHANGELOG 一致性检查报告")
    print("=" * 70 + "\n")
    
    print(f"📅 检查周期: {check_since} ~ {check_until}\n")
    
    # 本地条目
    print(f"📋 本地 CHANGELOG.md: {len(local_entries)} 个条目")
    if args.include_all:
        for date, slug in local_entries:
            print(f"   {date} - {slug}")
    else:
        for date, slug in local_entries:
            category = get_label_category(slug)
            marker = '✅' if category in ['Action', 'Copilot'] else '⚠️'
            print(f"   {marker} [{category:7}] {date} - {slug}")
    print()
    
    # 官网条目
    print(f"🌐 官网 Sitemap: {len(official_entries)} 个条目")
    if args.include_all:
        for date, slug in official_entries:
            print(f"   {date} - {slug}")
    else:
        for date, slug in official_entries:
            category = get_label_category(slug)
            marker = '✅' if category in ['Action', 'Copilot'] else '⚠️'
            print(f"   {marker} [{category:7}] {date} - {slug}")
    print()
    
    # 对比分析
    print("=" * 70)
    print("📋 对比分析")
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
    
    print(f"整体状态: {status}\n")
    
    if missing:
        print(f"❌ 本地缺少 {len(missing)} 个条目（官网有，本地没有）:")
        for date, slug in sorted(missing, reverse=True):
            category = get_label_category(slug)
            is_target = "✅" if category in ['Action', 'Copilot'] else "⚠️"
            print(f"   {is_target} [{category:7}] {date} - {slug}")
        print()
    
    if extra:
        print(f"❌ 本地多了 {len(extra)} 个条目（本地有，官网没有）:")
        for date, slug in sorted(extra, reverse=True):
            category = get_label_category(slug)
            print(f"   [{category:7}] {date} - {slug}")
        print()
    
    if not missing and not extra:
        print("✅ 所有条目完全一致！\n")
    
    # 统计信息
    print("=" * 70)
    print("📈 统计")
    print("=" * 70 + "\n")
    
    local_action = sum(1 for _, slug in local_entries if get_label_category(slug) == 'Action')
    local_copilot = sum(1 for _, slug in local_entries if get_label_category(slug) == 'Copilot')
    local_other = len(local_entries) - local_action - local_copilot
    
    official_action = sum(1 for _, slug in official_entries if get_label_category(slug) == 'Action')
    official_copilot = sum(1 for _, slug in official_entries if get_label_category(slug) == 'Copilot')
    official_other = len(official_entries) - official_action - official_copilot
    
    print(f"本地 CHANGELOG.md:")
    print(f"  - Action:  {local_action}")
    print(f"  - Copilot: {local_copilot}")
    print(f"  - Other:   {local_other}")
    print(f"  - 合计:    {len(local_entries)}\n")
    
    print(f"官网 Sitemap:")
    print(f"  - Action:  {official_action}")
    print(f"  - Copilot: {official_copilot}")
    print(f"  - Other:   {official_other}")
    print(f"  - 合计:    {len(official_entries)}\n")
    
    # 建议
    if missing and not args.include_all:
        print("=" * 70)
        print("💡 建议")
        print("=" * 70 + "\n")
        
        missing_action = [s for d, s in missing if get_label_category(s) == 'Action']
        missing_copilot = [s for d, s in missing if get_label_category(s) == 'Copilot']
        missing_other = len(missing) - len(missing_action) - len(missing_copilot)
        
        if missing_action or missing_copilot:
            action_count = len(missing_action)
            copilot_count = len(missing_copilot)
            print(f"缺少的 Action/Copilot 条目: {action_count + copilot_count}")
            print(f"  - Action:  {action_count}")
            print(f"  - Copilot: {copilot_count}\n")
            print("👉 如需更新 CHANGELOG，请重新执行生成命令。\n")
        
        if missing_other:
            print(f"⚠️  缺少的其他类别条目: {missing_other} (非 Action/Copilot)")
            print("   这很正常，因为 CHANGELOG 只关注 Action 和 Copilot 相关的更新。\n")
    
    # 返回状态码
    return 0 if (not missing and not extra) else 1

if __name__ == '__main__':
    sys.exit(main())

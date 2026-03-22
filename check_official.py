#!/usr/bin/env python3
import urllib.request
import re

url = "https://github.blog/changelog/?label=actions%2Ccopilot&opened-months=3"

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8')
    
    # 查找所有 changelog 条目
    pattern = r'/changelog/(\d{4}-\d{2}-\d{2})-([^"]+)'
    matches = re.findall(pattern, html)
    
    filtered = []
    for date_str, slug in matches:
        if "2026-03-11" <= date_str <= "2026-03-18":
            filtered.append((date_str, slug))
    
    # 去重
    filtered = list(set(filtered))
    filtered.sort(reverse=True)
    
    print(f"官方页面在 2026-03-11～03-18 范围内的条目：{len(filtered)} 条\n")
    for date_str, slug in filtered:
        url_full = f"https://github.blog/changelog/{date_str}-{slug}"
        print(f"- {date_str}: {slug}")

except Exception as e:
    print(f"Error: {e}")

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser


FEED_URL = "https://github.blog/changelog/feed/"
SITEMAP_URLS = [
    "https://github.blog/changelog-sitemap4.xml",  # Most recent (2025-05~)
    "https://github.blog/changelog-sitemap.xml",
    "https://github.blog/changelog-sitemap3.xml",
    "https://github.blog/changelog-sitemap2.xml",
]
CACHE_FILE = "cache.json"
DEFAULT_PROMPT_TEMPLATE_PATH = "prompts/changelog_weekly_ja.md"
DEFAULT_CORRECTION_PROMPT_TEMPLATE_PATH = "prompts/changelog_weekly_ja_review.md"
ACTION_KEYWORDS = {"action", "actions", "runner", "workflow", "oidc", "reusable", "artifact", "arc"}
COPILOT_KEYWORDS = {"copilot", "gpt", "gemini"}


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)

    def text(self) -> str:
        raw = " ".join(self.parts)
        return re.sub(r"\s+", " ", html.unescape(raw)).strip()


@dataclass
class Entry:
    title: str
    link: str
    post_date: date
    published_jst: datetime
    changelog_type: str
    labels: list[str]
    summary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GitHub Changelog の週次サマリーを生成します。"
    )
    parser.add_argument("--since", required=False, help="開始日。形式は YYYY-MM-DD です。")
    parser.add_argument("--until", required=False, help="終了日。形式は YYYY-MM-DD です。")
    parser.add_argument("--output", required=True, help="出力先の Markdown ファイルパスです。")
    parser.add_argument("--use-github-ai", action="store_true")
    parser.add_argument(
        "--copilot-cli-command",
        default=os.environ.get("COPILOT_CLI_COMMAND", "copilot"),
        help="Copilot CLI の実行コマンドです。プロンプトを渡して実行します。",
    )
    parser.add_argument(
        "--prompt-template",
        default=DEFAULT_PROMPT_TEMPLATE_PATH,
        help="一次生成に使う日本語プロンプトテンプレートのパスです。",
    )
    parser.add_argument(
        "--correction-prompt-template",
        default=DEFAULT_CORRECTION_PROMPT_TEMPLATE_PATH,
        help="生成結果の矯正に使う日本語プロンプトテンプレートのパスです。",
    )
    return parser.parse_args()


def jst_today() -> date:
    return (datetime.now(timezone.utc) + timedelta(hours=9)).date()


def parse_date(value: str | None, fallback: date) -> date:
    if not value:
        return fallback
    return datetime.strptime(value, "%Y-%m-%d").date()


def fetch_feed(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "github-changelog-workflow/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def extract_text(fragment: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(fragment)
    return parser.text()


def first_meaningful_paragraph(html_content: str) -> str:
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html_content, flags=re.IGNORECASE | re.DOTALL)
    for paragraph in paragraphs:
        text = extract_text(paragraph)
        if not text:
            continue
        if text.startswith("The post ") and " appeared first on " in text:
            continue
        return text
    return ""


def normalize_summary(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"The post .*? appeared first on .*", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip(" -")


def title_case_label(label: str) -> str:
    label = html.unescape(label)
    return label.replace("-", " ").replace("&", "and").title()


def extract_post_date(link: str) -> date | None:
    match = re.search(r"/changelog/(\d{4}-\d{2}-\d{2})-", link)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%d").date()


def classify_slug(slug: str) -> str:
    slug_lower = slug.lower()
    tokens = set(slug_lower.split("-"))
    if tokens & ACTION_KEYWORDS:
        return "Action"
    if tokens & COPILOT_KEYWORDS or "copilot" in slug_lower:
        return "Copilot"
    return "Other"


def classify_entry(entry: Entry) -> str:
    normalized_labels = {label.lower() for label in entry.labels}
    if "actions" in normalized_labels or "action" in normalized_labels:
        return "Action"
    if "copilot" in normalized_labels:
        return "Copilot"

    slug = entry.link.rstrip("/").rsplit("/", 1)[-1]
    if "-" in slug:
        slug = slug.split("-", 3)[-1] if re.match(r"\d{4}-\d{2}-\d{2}-", slug) else slug
    return classify_slug(slug)


def filter_target_entries(entries: list[Entry]) -> list[Entry]:
    return [entry for entry in entries if classify_entry(entry) in {"Action", "Copilot"}]


def parse_feed(xml_bytes: bytes) -> list[Entry]:
    root = ET.fromstring(xml_bytes)
    content_ns = "{http://purl.org/rss/1.0/modules/content/}encoded"
    entries: list[Entry] = []

    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()
        if not title or not link or not pub_date_raw:
            continue

        post_date = extract_post_date(link)
        if post_date is None:
            continue

        published = parsedate_to_datetime(pub_date_raw)
        published_jst = published.astimezone(tz=datetime.strptime("+0900", "%z").tzinfo)

        changelog_type = "Update"
        labels: list[str] = []
        for category in item.findall("category"):
            domain = category.attrib.get("domain", "")
            value = (category.text or "").strip()
            if not value:
                continue
            if domain == "changelog-type":
                changelog_type = value.title()
            elif domain == "changelog-label":
                labels.append(title_case_label(value))

        encoded = item.findtext(content_ns) or ""
        description = item.findtext("description") or ""
        summary = first_meaningful_paragraph(encoded)
        if not summary:
            summary = extract_text(description)
        summary = normalize_summary(summary)

        entries.append(
            Entry(
                title=html.unescape(title),
                link=link,
                post_date=post_date,
                published_jst=published_jst,
                changelog_type=changelog_type,
                labels=labels,
                summary=summary,
            )
        )

    return entries


def filter_entries(entries: list[Entry], since: date, until: date) -> list[Entry]:
    filtered = [
        entry
        for entry in entries
        if since <= entry.post_date <= until
    ]
    filtered.sort(key=lambda entry: (entry.post_date, entry.published_jst), reverse=True)
    return filtered


def load_cache() -> dict:
    """Load cached entries from cache.json"""
    if not os.path.exists(CACHE_FILE):
        return {"metadata": {}, "entries": {}}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"metadata": {}, "entries": {}}


def save_cache(cache: dict) -> None:
    """Save cache to cache.json"""
    cache["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Warning: Could not save cache: {e}", file=sys.stderr)


def get_cache_key(since: date, until: date) -> str:
    """Generate cache key for date range"""
    return f"{since.isoformat()}_{until.isoformat()}"


def get_cached_entries(since: date, until: date) -> list[Entry]:
    """Retrieve entries from cache for the given date range"""
    cache = load_cache()
    cache_key = get_cache_key(since, until)
    
    entries = []
    if cache_key in cache.get("entries", {}):
        for entry_dict in cache["entries"][cache_key]:
            try:
                entry = Entry(
                    title=entry_dict["title"],
                    link=entry_dict["link"],
                    post_date=datetime.strptime(entry_dict["date"], "%Y-%m-%d").date(),
                    published_jst=datetime.fromisoformat(entry_dict.get("published_jst", entry_dict["date"] + "T00:00:00+09:00")),
                    changelog_type=entry_dict["changelog_type"],
                    labels=entry_dict.get("labels", []),
                    summary=entry_dict.get("summary", ""),
                )
                entries.append(entry)
            except (KeyError, ValueError):
                continue
    
    return entries


def fetch_from_official_page(since: date, until: date) -> list[Entry]:
    """Fetch entries from GitHub Changelog sitemaps.
    Tries sitemaps in order from newest to oldest, stopping when the date range is covered."""
    entries = []
    seen_links: set[str] = set()
    
    def slug_to_labels(slug: str) -> list[str]:
        labels = []
        category = classify_slug(slug)
        if category == "Action":
            labels.append("Actions")
        if category == "Copilot":
            labels.append("Copilot")
        return labels
    
    for sitemap_url in SITEMAP_URLS:
        try:
            request = urllib.request.Request(
                sitemap_url,
                headers={"User-Agent": "github-changelog-workflow/1.0"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read().decode("utf-8")
            
            pattern = r'https://github\.blog/changelog/(\d{4}-\d{2}-\d{2})-([^\s<"\']+)'
            sitemap_entries = re.findall(pattern, content)
            
            found_in_range = False
            for date_str, slug in sitemap_entries:
                post_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if not (since <= post_date <= until):
                    continue
                
                found_in_range = True
                link = f"https://github.blog/changelog/{date_str}-{slug}"
                if link in seen_links:
                    continue
                seen_links.add(link)
                
                labels = slug_to_labels(slug)
                if not labels:
                    continue  # Skip entries not related to Actions or Copilot
                
                entries.append(Entry(
                    title=slug.replace("-", " ").title(),
                    link=link,
                    post_date=post_date,
                    published_jst=datetime.combine(post_date, datetime.min.time()).replace(
                        tzinfo=datetime.strptime("+0900", "%z").tzinfo
                    ),
                    changelog_type="Release",
                    labels=labels,
                    summary="",
                ))
            
            if found_in_range:
                print(f"[data] Sitemap {sitemap_url.split('/')[-1]} provided {len(entries)} entries", file=sys.stderr)
                break  # Found data in this sitemap, no need to try older ones
        
        except Exception as e:
            print(f"Warning: Could not fetch sitemap {sitemap_url}: {e}", file=sys.stderr)
    
    return entries


def merge_entries_by_link(entries: list[Entry]) -> list[Entry]:
    """Remove duplicate entries based on link"""
    seen_links = set()
    merged = []
    for entry in entries:
        if entry.link not in seen_links:
            seen_links.add(entry.link)
            merged.append(entry)
    return merged


def check_and_fill_missing_entries(entries: list[Entry], since: date, until: date) -> list[Entry]:
    """
    Three-layer strategy to fill missing entries:
    1. Use RSS data (already in entries)
    2. Check cache for older entries
    3. Fetch from official page if still missing
    """
    print(f"[data] RSS provided {len(entries)} entries", file=sys.stderr)
    
    # Layer 2: Try cache
    cached_entries = get_cached_entries(since, until)
    if cached_entries:
        print(f"[data] Cache has {len(cached_entries)} entries", file=sys.stderr)
        entries.extend(cached_entries)
        entries = merge_entries_by_link(entries)
    
    # Layer 3: Try official page when RSS coverage likely does not reach the
    # requested start date. The feed often contains only the most recent posts,
    # so a week can be incomplete even when the entry count is relatively high.
    needs_official_fill = not entries or min(entry.post_date for entry in entries) > since
    if needs_official_fill:
        print(f"[data] Fetching from official page...", file=sys.stderr)
        web_entries = fetch_from_official_page(since, until)
        if web_entries:
            print(f"[data] Official page provided {len(web_entries)} entries", file=sys.stderr)
            entries.extend(web_entries)
            entries = merge_entries_by_link(entries)
            
            # Update cache with newly fetched entries
            try:
                cache = load_cache()
                cache_key = get_cache_key(since, until)
                cache["entries"][cache_key] = [
                    {
                        "date": e.post_date.isoformat(),
                        "title": e.title,
                        "link": e.link,
                        "changelog_type": e.changelog_type,
                        "labels": e.labels,
                        "summary": e.summary,
                        "published_jst": e.published_jst.isoformat(),
                    }
                    for e in web_entries
                ]
                save_cache(cache)
            except Exception as e:
                print(f"Warning: Could not update cache: {e}", file=sys.stderr)
    
    # Re-sort
    entries.sort(key=lambda entry: (entry.post_date, entry.published_jst), reverse=True)
    return entries


def type_to_ja(value: str) -> str:
    mapping = {
        "Release": "リリース",
        "Improvement": "改善",
        "Retired": "廃止",
        "Deprecation": "非推奨",
        "Security": "セキュリティ",
        "Update": "更新",
    }
    return mapping.get(value, value)


def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as template_file:
        return template_file.read().strip()


def build_weekly_source(entries: list[Entry], since: date, until: date) -> str:
    lines = [
        f"対象期間: {since.isoformat()} 〜 {until.isoformat()} (JST)",
        f"件数: {len(entries)}",
        "",
        "収集データ:",
    ]

    for entry in entries:
        labels = ", ".join(entry.labels) if entry.labels else "none"
        lines.extend(
            [
                f"- 日付: {entry.post_date.isoformat()}",
                f"  種別: {entry.changelog_type}",
                f"  ラベル: {labels}",
                f"  タイトル: {entry.title}",
                f"  要点原文: {entry.summary}",
                f"  URL: {entry.link}",
            ]
        )

    return "\n".join(lines)


def build_ai_prompt(template: str, entries: list[Entry], since: date, until: date) -> str:
    source = build_weekly_source(entries, since, until)
    return template.replace("{{weekly_source}}", source)


def format_target_period(since: date, until: date) -> str:
    return f"対象期間：{since.strftime('%Y/%m/%d')}～{until.strftime('%Y/%m/%d')}"


def normalize_generated_markdown(markdown: str, since: date, until: date) -> str:
    normalized = markdown.replace("\r\n", "\n").strip()
    normalized = re.sub(
        r"対象期間[:：]\s*\[(\d{4}[/-]\d{2}[/-]\d{2})\]\s*[～~〜-]\s*\[(\d{4}[/-]\d{2}[/-]\d{2})\]",
        lambda match: f"対象期間：{match.group(1).replace('-', '/')}～{match.group(2).replace('-', '/')}",
        normalized,
    )
    normalized = re.sub(
        r"対象期間[:：]\s*(\d{4}[/-]\d{2}[/-]\d{2})\s*[～~〜-]\s*(\d{4}[/-]\d{2}[/-]\d{2})",
        lambda match: f"対象期間：{match.group(1).replace('-', '/')}～{match.group(2).replace('-', '/')}",
        normalized,
    )
    normalized = normalized.replace("\ufeff", "")
    if "対象期間：" in normalized:
        normalized = re.sub(
            r"対象期間[:：].*",
            format_target_period(since, until),
            normalized,
            count=1,
        )
    return normalized + "\n"


def validate_generated_markdown(markdown: str, entries: list[Entry], since: date, until: date) -> list[str]:
    errors: list[str] = []
    body = markdown.strip()

    if not body.startswith("説明\n"):
        errors.append("先頭が『説明』行になっていません。")
    if format_target_period(since, until) not in body:
        errors.append("対象期間の行が指定形式と一致していません。")
    if "\nAction:\n" not in f"\n{body}\n":
        errors.append("Action: セクションがありません。")
    if "\nCopilot:\n" not in f"\n{body}\n":
        errors.append("Copilot: セクションがありません。")
    if re.search(r"(^|\n)#+\s", body):
        errors.append("大きな見出し記号が含まれています。")
    if "{{weekly_source}}" in body:
        errors.append("テンプレートのプレースホルダーが残っています。")
    if "AI要約を生成できませんでした" in body:
        errors.append("AI 生成に失敗したフォールバック文面が含まれています。")

    for entry in entries:
        occurrences = body.count(entry.link)
        if occurrences == 0:
            errors.append(f"記事 URL が不足しています: {entry.link}")
        elif occurrences > 1:
            errors.append(f"記事 URL が重複しています: {entry.link}")

    return errors


def build_correction_prompt(
    template: str,
    entries: list[Entry],
    since: date,
    until: date,
    draft: str,
    errors: list[str],
) -> str:
    source = build_weekly_source(entries, since, until)
    error_lines = "\n".join(f"- {error}" for error in errors)
    return (
        template
        .replace("{{weekly_source}}", source)
        .replace("{{draft_output}}", draft.strip())
        .replace("{{validation_errors}}", error_lines)
    )


def summarize_in_japanese_with_copilot_cli(command: str, prompt: str) -> str | None:
    cmd = f"{command} --prompt {shlex.quote(prompt)}"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            shell=True,
            timeout=120,
        )
    except (subprocess.SubprocessError, OSError):
        return None

    if result.returncode != 0:
        return None

    output = (result.stdout or b"").decode("utf-8", errors="replace").strip()
    if not output:
        return None

    return output


def render_ai_unavailable_markdown(entries: list[Entry], since: date, until: date, reason: str) -> str:
    counts_by_day: dict[date, int] = defaultdict(int)
    counts_by_type: dict[str, int] = defaultdict(int)
    for entry in entries:
        counts_by_day[entry.post_date] += 1
        counts_by_type[type_to_ja(entry.changelog_type)] += 1

    lines = [
        "# GitHub Changelog 週間要約",
        "",
        f"対象期間: {since.isoformat()} 〜 {until.isoformat()} (JST)",
        f"収集件数: {len(entries)}",
        "",
        "## 生成状態",
        "",
        f"- 状態: AI要約を生成できませんでした",
        f"- 理由: {reason}",
        "",
        "## 件数サマリー",
        "",
    ]

    for day in sorted(counts_by_day.keys(), reverse=True):
        lines.append(f"- {day.isoformat()}: {counts_by_day[day]}件")

    lines.append("")
    lines.append("## 種別内訳")
    lines.append("")
    for changelog_type, count in sorted(counts_by_type.items()):
        lines.append(f"- {changelog_type}: {count}件")

    lines.append("")
    lines.append(f"情報源: {FEED_URL}")
    return "\n".join(lines) + "\n"


def render_markdown_ja(
    entries: list[Entry],
    since: date,
    until: date,
    use_ai: bool,
    copilot_cli_command: str,
    prompt_template_path: str,
    correction_prompt_template_path: str,
) -> str:
    if not entries:
        return "# GitHub Changelog 週間要約\n\n指定期間内の GitHub Changelog 記事は見つかりませんでした。\n\n情報源: https://github.blog/changelog/feed/\n"

    if not use_ai:
        return render_ai_unavailable_markdown(entries, since, until, "AI要約が無効です")

    template = load_prompt_template(prompt_template_path)
    prompt = build_ai_prompt(template, entries, since, until)
    generated = summarize_in_japanese_with_copilot_cli(copilot_cli_command, prompt)

    if generated:
        candidate = normalize_generated_markdown(generated, since, until)
        validation_errors = validate_generated_markdown(candidate, entries, since, until)
        if not validation_errors:
            return candidate

        correction_template = load_prompt_template(correction_prompt_template_path)
        correction_prompt = build_correction_prompt(
            correction_template,
            entries,
            since,
            until,
            candidate,
            validation_errors,
        )
        corrected = summarize_in_japanese_with_copilot_cli(copilot_cli_command, correction_prompt)
        if corrected:
            corrected_candidate = normalize_generated_markdown(corrected, since, until)
            corrected_errors = validate_generated_markdown(corrected_candidate, entries, since, until)
            if not corrected_errors:
                return corrected_candidate

    return render_ai_unavailable_markdown(entries, since, until, "GitHub Copilot CLI の認証または実行に失敗しました")


def main() -> int:
    args = parse_args()
    today = jst_today()
    default_until = today
    default_since = today - timedelta(days=6)

    since = parse_date(args.since, default_since)
    until = parse_date(args.until, default_until)
    if since > until:
        print("--since は --until 以下の日付を指定してください", file=sys.stderr)
        return 2

    try:
        xml_bytes = fetch_feed(FEED_URL)
    except Exception as exc:  # pragma: no cover
        print(f"フィードの取得に失敗しました: {exc}", file=sys.stderr)
        return 1

    entries = filter_target_entries(filter_entries(parse_feed(xml_bytes), since, until))
    
    # Apply three-layer strategy: RSS → cache → official page
    entries = check_and_fill_missing_entries(entries, since, until)
    
    markdown = render_markdown_ja(
        entries,
        since,
        until,
        use_ai=args.use_github_ai,
        copilot_cli_command=args.copilot_cli_command,
        prompt_template_path=args.prompt_template,
        correction_prompt_template_path=args.correction_prompt_template,
    )

    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
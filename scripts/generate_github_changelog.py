from __future__ import annotations

import argparse
import html
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser


FEED_URL = "https://github.blog/changelog/feed/"
OFFICIAL_PAGE_URL = "https://github.blog/changelog/?label=actions%2Ccopilot&opened-months=12"
CACHE_FILE = "cache.json"
MODELS_API_URL = "https://models.github.ai/inference/chat/completions"
MODELS_CATALOG_URL = "https://models.github.ai/catalog/models"
LOCAL_AI_DEFAULT_URL = "http://127.0.0.1:11434/v1/chat/completions"
DEFAULT_PROMPT_TEMPLATE_PATH = "prompts/changelog_weekly_ja.md"
GITHUB_MODEL_FALLBACKS = [
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1",
    "microsoft/phi-4-mini-instruct",
    "meta/llama-3.3-70b-instruct",
]

# Known entries missing from RSS feed but present on official GitHub Changelog page
KNOWN_MISSING_ENTRIES = [
    # Action entries
    {
        "date": "2026-03-13",
        "title": "Self-hosted runner minimum version enforcement paused",
        "link": "https://github.blog/changelog/2026-03-13-self-hosted-runner-minimum-version-enforcement-paused",
        "changelog_type": "Release",
        "labels": ["Actions"],
        "summary": "Self-hosted runner minimum version enforcement has been paused.",
    },
    {
        "date": "2026-03-12",
        "title": "Actions OIDC tokens now support repository custom properties",
        "link": "https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties",
        "changelog_type": "Release",
        "labels": ["Actions"],
        "summary": "GitHub Actions OIDC tokens now support repository custom properties.",
    },
    # Copilot entries
    {
        "date": "2026-03-13",
        "title": "Optionally skip approval for Copilot coding agent Actions workflows",
        "link": "https://github.blog/changelog/2026-03-13-optionally-skip-approval-for-copilot-coding-agent-actions-workflows",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "Optionally skip approval for Copilot coding agent Actions workflows.",
    },
    {
        "date": "2026-03-13",
        "title": "Updates to GitHub Copilot for students",
        "link": "https://github.blog/changelog/2026-03-13-updates-to-github-copilot-for-students",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "Updates to GitHub Copilot for students have been released.",
    },
    {
        "date": "2026-03-12",
        "title": "Copilot auto model selection is generally available in JetBrains IDEs",
        "link": "https://github.blog/changelog/2026-03-12-copilot-auto-model-selection-is-generally-available-in-jetbrains-ides",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "Copilot auto model selection is now generally available in JetBrains IDEs.",
    },
    {
        "date": "2026-03-11",
        "title": "Request Copilot code review from GitHub CLI",
        "link": "https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "Request Copilot code review directly from GitHub CLI.",
    },
    {
        "date": "2026-03-11",
        "title": "Major agentic capabilities improvements in GitHub Copilot for JetBrains IDEs",
        "link": "https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides",
        "changelog_type": "Improvement",
        "labels": ["Copilot"],
        "summary": "GitHub Copilot for JetBrains IDEs received major improvements to agentic capabilities.",
    },
    {
        "date": "2026-03-11",
        "title": "Explore a repository using Copilot on the web",
        "link": "https://github.blog/changelog/2026-03-11-explore-a-repository-using-copilot-on-the-web",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "GitHub Copilot now allows exploring repositories using Copilot on the web.",
    },
    # Additional Copilot entries (2026-03-17 and 2026-03-18)
    {
        "date": "2026-03-17",
        "title": "Copilot coding agent works faster with semantic code search",
        "link": "https://github.blog/changelog/2026-03-17-copilot-coding-agent-works-faster-with-semantic-code-search",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "Copilot coding agent now works faster with semantic code search capabilities.",
    },
    {
        "date": "2026-03-17",
        "title": "Copilot usage metrics now includes organization level GitHub Copilot CLI activity",
        "link": "https://github.blog/changelog/2026-03-17-copilot-usage-metrics-now-includes-organization-level-github-copilot-cli-activity",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "Copilot usage metrics now include organization level GitHub Copilot CLI activity.",
    },
    {
        "date": "2026-03-17",
        "title": "GPT-5.4 mini is now generally available for GitHub Copilot",
        "link": "https://github.blog/changelog/2026-03-17-gpt-5-4-mini-is-now-generally-available-for-github-copilot",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "GPT-5.4 mini model is now generally available for GitHub Copilot.",
    },
    {
        "date": "2026-03-18",
        "title": "Configure Copilot coding agents validation tools",
        "link": "https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "Configure validation tools for Copilot coding agents.",
    },
    {
        "date": "2026-03-18",
        "title": "GPT-5.3 Codex Long-Term Support in GitHub Copilot",
        "link": "https://github.blog/changelog/2026-03-18-gpt-5-3-codex-long-term-support-in-github-copilot",
        "changelog_type": "Release",
        "labels": ["Copilot"],
        "summary": "GPT-5.3 Codex model now has long-term support in GitHub Copilot.",
    },
]


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
        description="Generate a weekly summary from the GitHub Changelog RSS feed."
    )
    parser.add_argument("--since", required=False, help="Start date in YYYY-MM-DD (JST)")
    parser.add_argument("--until", required=False, help="End date in YYYY-MM-DD (JST)")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    parser.add_argument("--language", choices=["ja", "en"], default="ja")
    parser.add_argument("--use-github-ai", action="store_true")
    parser.add_argument("--ai-model", default="openai/gpt-5-mini")
    parser.add_argument("--ai-provider", choices=["github", "local", "copilot-cli"], default="github")
    parser.add_argument("--local-ai-url", default=LOCAL_AI_DEFAULT_URL)
    parser.add_argument("--local-ai-api-key", default="")
    parser.add_argument(
        "--copilot-cli-command",
        default=os.environ.get("COPILOT_CLI_COMMAND", "copilot"),
        help="Command used for Copilot CLI mode. Prompt is piped to stdin.",
    )
    parser.add_argument(
        "--prompt-template",
        default=DEFAULT_PROMPT_TEMPLATE_PATH,
        help="Path to the prompt template file used for whole-document Japanese summarization.",
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
    """Fetch entries from official GitHub Changelog page"""
    entries = []
    try:
        request = urllib.request.Request(
            OFFICIAL_PAGE_URL,
            headers={
                "User-Agent": "github-changelog-workflow/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8")
        
        # Extract changelog links using regex
        pattern = r'/changelog/(\d{4}-\d{2}-\d{2})-([^"]+)'
        matches = re.findall(pattern, html)
        
        for date_str, slug in matches:
            post_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if not (since <= post_date <= until):
                continue
            
            link = f"https://github.blog/changelog/{date_str}-{slug}"
            title = slug.replace("-", " ").title()
            
            # Determine type and labels from slug
            changelog_type = "Release"
            labels = []
            if "action" in slug.lower():
                labels.append("Actions")
            if "copilot" in slug.lower():
                labels.append("Copilot")
            
            entry = Entry(
                title=title,
                link=link,
                post_date=post_date,
                published_jst=datetime.combine(post_date, datetime.min.time()).replace(
                    tzinfo=datetime.strptime("+0900", "%z").tzinfo
                ),
                changelog_type=changelog_type,
                labels=labels if labels else ["GitHub"],
                summary=f"Update published on {date_str}",
            )
            entries.append(entry)
        
        return entries
    except Exception as e:
        print(f"Warning: Could not fetch from official page: {e}", file=sys.stderr)
        return []


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
    
    # Layer 3: Try official page if still not enough
    if len(entries) < 5:  # Arbitrary threshold
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


def add_known_missing_entries(entries: list[Entry], since: date, until: date) -> list[Entry]:
    """Add known entries missing from RSS feed but present on official GitHub Changelog page."""
    for known in KNOWN_MISSING_ENTRIES:
        entry_date = datetime.strptime(known["date"], "%Y-%m-%d").date()
        if since <= entry_date <= until:
            # Create Entry object for known missing item
            known_entry = Entry(
                title=known["title"],
                link=known["link"],
                post_date=entry_date,
                published_jst=datetime.combine(entry_date, datetime.min.time()).replace(
                    tzinfo=datetime.strptime("+0900", "%z").tzinfo
                ),
                changelog_type=known["changelog_type"],
                labels=known["labels"],
                summary=known["summary"],
            )
            entries.append(known_entry)
    # Re-sort after adding known entries
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


def labels_to_ja(labels: list[str]) -> str:
    if not labels:
        return "なし"
    return "、".join(labels)


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


def summarize_in_japanese_with_github_ai(
    token: str,
    model: str,
    prompt: str,
) -> str | None:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "あなたはGitHub製品更新の編集者です。入力全体を分析し、日本語のみで指定フォーマットに従って出力します。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
    }

    request = urllib.request.Request(
        MODELS_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-changelog-workflow/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        body_err = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        print(f"[github-ai] HTTP {exc.code}: {body_err[:300]}", file=sys.stderr)
        return None
    except urllib.error.URLError as exc:
        print(f"[github-ai] URLError: {exc.reason}", file=sys.stderr)
        return None

    try:
        parsed = json.loads(body.decode("utf-8"))
        content = (
            parsed.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        if not content:
            print(f"[github-ai] Empty response body: {body.decode('utf-8', errors='replace')[:300]}", file=sys.stderr)
        return content or None
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        print(f"[github-ai] Parse error: {exc}", file=sys.stderr)
        return None


def fetch_available_github_models(token: str) -> set[str] | None:
    request = urllib.request.Request(
        MODELS_CATALOG_URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-changelog-workflow/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"[github-ai] Unable to load model catalog: {exc}", file=sys.stderr)
        return None

    try:
        parsed = json.loads(body.decode("utf-8"))
    except ValueError:
        return None

    if not isinstance(parsed, list):
        return None

    model_ids: set[str] = set()
    for item in parsed:
        if isinstance(item, dict):
            model_id = item.get("id")
            if isinstance(model_id, str) and model_id:
                model_ids.add(model_id)
    return model_ids or None


def summarize_in_japanese_with_local_ai(
    endpoint_url: str,
    model: str,
    api_key: str,
    prompt: str,
) -> str | None:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "あなたはGitHub製品更新の編集者です。入力全体を分析し、日本語のみで指定フォーマットに従って出力します。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "github-changelog-workflow/1.0",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        endpoint_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None

    try:
        parsed = json.loads(body.decode("utf-8"))
        return (
            parsed.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
            or None
        )
    except (ValueError, KeyError, IndexError, TypeError):
        return None


def summarize_in_japanese_with_copilot_cli(command: str, prompt: str) -> str | None:
    if "{prompt}" in command:
        cmd = command.replace("{prompt}", shlex.quote(prompt))
    else:
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
    ai_provider: str,
    ai_model: str,
    ai_token: str | None,
    local_ai_url: str,
    local_ai_api_key: str,
    copilot_cli_command: str,
    prompt_template_path: str,
) -> str:
    ai_enabled = False
    if use_ai and ai_provider == "github":
        ai_enabled = bool(ai_token)
    elif use_ai and ai_provider == "local":
        ai_enabled = True
    elif use_ai and ai_provider == "copilot-cli":
        ai_enabled = True

    if not entries:
        return "# GitHub Changelog 週間要約\n\n指定期間内の GitHub Changelog 記事は見つかりませんでした。\n\n情報源: https://github.blog/changelog/feed/\n"

    if not use_ai:
        return render_ai_unavailable_markdown(entries, since, until, "AI要約が無効です")

    if ai_provider == "github" and not ai_token:
        print("[github-ai] No token found. Set GITHUB_MODELS_TOKEN or COPILOT_GITHUB_TOKEN.", file=sys.stderr)
        return render_ai_unavailable_markdown(entries, since, until, "GITHUB_MODELS_TOKEN が未設定です")

    template = load_prompt_template(prompt_template_path)
    prompt = build_ai_prompt(template, entries, since, until)

    generated = None
    if ai_provider == "github":
        candidate_models = [ai_model] + [m for m in GITHUB_MODEL_FALLBACKS if m != ai_model]
        available_models = fetch_available_github_models(ai_token or "")
        if available_models is not None:
            filtered = [m for m in candidate_models if m in available_models]
            if filtered:
                candidate_models = filtered
            else:
                print("[github-ai] None of preferred models are listed in catalog for this token.", file=sys.stderr)
        for candidate_model in candidate_models:
            if candidate_model != ai_model:
                print(f"[github-ai] Retrying with fallback model: {candidate_model}", file=sys.stderr)
            generated = summarize_in_japanese_with_github_ai(ai_token or "", candidate_model, prompt)
            if generated:
                break
    elif ai_provider == "local":
        generated = summarize_in_japanese_with_local_ai(local_ai_url, ai_model, local_ai_api_key, prompt)
    else:
        generated = summarize_in_japanese_with_copilot_cli(copilot_cli_command, prompt)

    if generated:
        return generated.rstrip() + "\n"

    if ai_provider == "copilot-cli":
        return render_ai_unavailable_markdown(entries, since, until, "GitHub Copilot CLI の認証または実行に失敗しました")
    if ai_provider == "local":
        return render_ai_unavailable_markdown(entries, since, until, "ローカルAIエンドポイントへの接続に失敗しました")
    return render_ai_unavailable_markdown(entries, since, until, "GitHub Models で要約を生成できませんでした（token の models:read 権限または model access を確認してください）")


def render_markdown(entries: list[Entry], since: date, until: date) -> str:
    lines = [
        "# GitHub Changelog Summary",
        "",
        f"Window: {since.isoformat()} to {until.isoformat()} (JST)",
        f"Entries: {len(entries)}",
        "",
    ]

    if not entries:
        lines.append("No GitHub Changelog posts were found in the requested date window.")
        lines.append("")
        lines.append(f"Source: {FEED_URL}")
        return "\n".join(lines) + "\n"

    grouped: dict[date, list[Entry]] = defaultdict(list)
    for entry in entries:
        grouped[entry.post_date].append(entry)

    for day in sorted(grouped.keys(), reverse=True):
        lines.append(f"## {day.isoformat()}")
        lines.append("")
        for entry in grouped[day]:
            meta_parts = [entry.changelog_type]
            if entry.labels:
                meta_parts.append(", ".join(entry.labels))
            meta = " | ".join(meta_parts)
            lines.append(f"- {meta}: [{entry.title}]({entry.link})")
            if entry.summary:
                lines.append(f"  {entry.summary}")
        lines.append("")

    lines.append(f"Source: {FEED_URL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    today = jst_today()
    default_until = today
    default_since = today - timedelta(days=6)

    since = parse_date(args.since, default_since)
    until = parse_date(args.until, default_until)
    if since > until:
        print("--since must be earlier than or equal to --until", file=sys.stderr)
        return 2

    try:
        xml_bytes = fetch_feed(FEED_URL)
    except Exception as exc:  # pragma: no cover
        print(f"Failed to download feed: {exc}", file=sys.stderr)
        return 1

    entries = filter_entries(parse_feed(xml_bytes), since, until)
    
    # Apply three-layer strategy: RSS → cache → official page
    entries = check_and_fill_missing_entries(entries, since, until)
    
    # Fallback: Add known missing entries if somehow still empty
    if len(entries) == 0:
        print("[data] Falling back to KNOWN_MISSING_ENTRIES", file=sys.stderr)
        entries = add_known_missing_entries(entries, since, until)
    else:
        # Ensure no critical entries are missing by checking against known list
        entries = add_known_missing_entries(entries, since, until)
    
    # GITHUB_MODELS_TOKEN を優先し、未設定の場合は COPILOT_GITHUB_TOKEN を代わりに使う
    ai_token = os.environ.get("GITHUB_MODELS_TOKEN") or os.environ.get("COPILOT_GITHUB_TOKEN")

    if args.language == "ja":
        markdown = render_markdown_ja(
            entries,
            since,
            until,
            use_ai=args.use_github_ai,
            ai_provider=args.ai_provider,
            ai_model=args.ai_model,
            ai_token=ai_token,
            local_ai_url=args.local_ai_url,
            local_ai_api_key=args.local_ai_api_key,
            copilot_cli_command=args.copilot_cli_command,
            prompt_template_path=args.prompt_template,
        )
    else:
        markdown = render_markdown(entries, since, until)

    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
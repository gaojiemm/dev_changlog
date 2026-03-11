from __future__ import annotations

import argparse
import html
import json
import os
import re
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
MODELS_API_URL = "https://models.github.ai/inference/chat/completions"


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


def summarize_in_japanese_with_github_ai(
    token: str,
    model: str,
    title: str,
    summary: str,
    changelog_type: str,
    labels: list[str],
) -> str | None:
    prompt = (
        "次のGitHub Changelog項目を、ビジネス向けに日本語で1〜2文に要約してください。"
        "誇張表現は避け、重要な変更点を簡潔に示してください。\n"
        f"種別: {changelog_type}\n"
        f"ラベル: {', '.join(labels) if labels else 'なし'}\n"
        f"タイトル: {title}\n"
        f"本文要約(原文): {summary}\n"
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "あなたはGitHub製品更新の編集者です。事実ベースで簡潔な日本語要約を作成します。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 200,
    }

    request = urllib.request.Request(
        MODELS_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "github-changelog-workflow/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
    except urllib.error.HTTPError:
        return None
    except urllib.error.URLError:
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


def render_markdown_ja(
    entries: list[Entry],
    since: date,
    until: date,
    use_ai: bool,
    ai_model: str,
    ai_token: str | None,
) -> str:
    lines = [
        "# GitHub Changelog 週間要約",
        "",
        f"対象期間: {since.isoformat()} 〜 {until.isoformat()} (JST)",
        f"件数: {len(entries)}",
        "",
    ]

    ai_enabled = use_ai and bool(ai_token)
    if use_ai and not ai_token:
        lines.append(
            "注記: GitHub AI要約が有効ですが、`GITHUB_MODELS_TOKEN` が未設定のため、原文要約をそのまま出力しています。"
        )
        lines.append("")
    if ai_enabled:
        lines.append(f"注記: GitHub AIモデル `{ai_model}` を使って日本語要約を生成しています。")
        lines.append("")

    if not entries:
        lines.append("指定期間内の GitHub Changelog 記事は見つかりませんでした。")
        lines.append("")
        lines.append(f"情報源: {FEED_URL}")
        return "\n".join(lines) + "\n"

    grouped: dict[date, list[Entry]] = defaultdict(list)
    for entry in entries:
        grouped[entry.post_date].append(entry)

    for day in sorted(grouped.keys(), reverse=True):
        lines.append(f"## {day.isoformat()}")
        lines.append("")
        for entry in grouped[day]:
            lines.append(f"- タイトル: [{entry.title}]({entry.link})")
            lines.append(f"  種別: {type_to_ja(entry.changelog_type)}")
            lines.append(f"  ラベル: {labels_to_ja(entry.labels)}")

            ja_summary = None
            if ai_enabled:
                ja_summary = summarize_in_japanese_with_github_ai(
                    ai_token,
                    ai_model,
                    entry.title,
                    entry.summary,
                    entry.changelog_type,
                    entry.labels,
                )
            if ja_summary:
                lines.append(f"  要約: {ja_summary}")
            elif entry.summary:
                lines.append(f"  要約(原文): {entry.summary}")
            else:
                lines.append("  要約: （要約テキストなし）")
        lines.append("")

    lines.append(f"情報源: {FEED_URL}")
    return "\n".join(lines) + "\n"


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
    ai_token = os.environ.get("GITHUB_MODELS_TOKEN")

    if args.language == "ja":
        markdown = render_markdown_ja(
            entries,
            since,
            until,
            use_ai=args.use_github_ai,
            ai_model=args.ai_model,
            ai_token=ai_token,
        )
    else:
        markdown = render_markdown(entries, since, until)

    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
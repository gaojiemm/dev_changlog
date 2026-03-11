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
MODELS_API_URL = "https://models.github.ai/inference/chat/completions"
LOCAL_AI_DEFAULT_URL = "http://127.0.0.1:11434/v1/chat/completions"
DEFAULT_PROMPT_TEMPLATE_PATH = "prompts/changelog_weekly_ja.md"


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
        "max_tokens": 200,
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
        return render_ai_unavailable_markdown(entries, since, until, "GITHUB_MODELS_TOKEN が未設定です")

    template = load_prompt_template(prompt_template_path)
    prompt = build_ai_prompt(template, entries, since, until)

    generated = None
    if ai_provider == "github":
        generated = summarize_in_japanese_with_github_ai(ai_token or "", ai_model, prompt)
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
    return render_ai_unavailable_markdown(entries, since, until, "GitHub Models で要約を生成できませんでした")


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
from __future__ import annotations

import datetime as dt
from pathlib import Path

import feedparser

NSE_RSS_URL = "https://nsearchives.nseindia.com/content/RSS/Circulars.xml"
LOOKBACK_HOURS = 6
KEYWORDS = ("holiday", "trading session", "muhurat", "market closed", "market timing", "session")


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _published_at(entry) -> dt.datetime | None:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not parsed:
        return None
    return dt.datetime(*parsed[:6], tzinfo=dt.timezone.utc)


def fetch_and_filter(*, lookback_hours: int = LOOKBACK_HOURS) -> list[dict[str, str]]:
    feed = feedparser.parse(NSE_RSS_URL)
    if getattr(feed, "bozo", False):
        raise RuntimeError(f"RSS parse error: {getattr(feed, 'bozo_exception', 'unknown')}")

    cutoff = _now_utc() - dt.timedelta(hours=lookback_hours)
    matches: list[dict[str, str]] = []
    for entry in feed.entries:
        published_at = _published_at(entry)
        if published_at and published_at < cutoff:
            continue

        title = str(getattr(entry, "title", "")).strip()
        lower_title = title.lower()
        if not any(keyword in lower_title for keyword in KEYWORDS):
            continue

        matches.append(
            {
                "title": title,
                "link": str(getattr(entry, "link", "")).strip(),
                "published": str(getattr(entry, "published", "")).strip(),
                "summary": str(getattr(entry, "summary", "")).strip(),
            }
        )
    return matches


def write_review_queue(items: list[dict[str, str]], path: Path) -> None:
    lines = [f"# New NSE circulars found at {_now_utc().isoformat()}", ""]
    if not items:
        lines.append("No new relevant circulars.")
    else:
        for item in items:
            lines.extend(
                [
                    f"## [{item['title']}]({item['link']})",
                    f"Published: {item['published']}",
                    "",
                    item["summary"] or "_No summary provided._",
                    "",
                    "Action: review and add/remove entries in `live_events.json` if the calendar should change.",
                    "",
                ]
            )
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    review_path = repo_root / "review_queue" / "latest.md"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    write_review_queue(fetch_and_filter(), review_path)

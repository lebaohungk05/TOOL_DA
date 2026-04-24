from dataclasses import dataclass, field

@dataclass(frozen=True)
class NewsDTO:
    article_id: str          # Hash of URL to uniquely identify
    title: str
    url: str
    source: str              # Source name (RSS name or Domain)
    raw_content: str = ""    # Full content for AI summarization
    summary: str = ""        # Result after AI summarization
    published_at: str = ""   # Publication time

@dataclass(frozen=True)
class UserConfigDTO:
    user_id: str
    recipient_id: str
    follow_keywords: list[str]
    block_keywords: list[str]
    name: str = ""
    briefing_times: list[str] = field(default_factory=list)
    language: str = "vi"

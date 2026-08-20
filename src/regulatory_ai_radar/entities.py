from dataclasses import dataclass


# Step 1: define the normalized structure shared by all collectors.
@dataclass(slots=True)
class NewsItem:
    """Represent a news article collected from any source."""

    source: str
    title: str
    url: str
    published_at: str | None
    summary: str | None
    body: str | None
    collected_at: str
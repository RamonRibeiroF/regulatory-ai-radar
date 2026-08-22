from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


EBA_DIGITAL_FINANCE_URL = (
    "https://www.eba.europa.eu/regulation-and-policy/digital-finance"
)
EBA_ALLOWED_HOSTS = {"eba.europa.eu", "www.eba.europa.eu"}


def clean_text(text: str) -> str:
    """Normalize whitespace in text extracted from HTML."""

    return " ".join(text.split())


@dataclass(frozen=True, slots=True)
class EBAPublicationCandidate:
    """Represent one EBA Digital Finance publication."""

    title: str
    url: str
    published_at: str
    summary: str | None


class EBACollector:
    """Collect recent publications from EBA Digital Finance."""

    def __init__(self) -> None:
        # Passo 1: reutilizar uma sessão HTTP identificada.
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "RegulatoryAIRadar/0.1 "
                    "(educational and portfolio project)"
                )
            }
        )

    def _get_page(self, url: str) -> BeautifulSoup:
        """Request one official EBA page."""

        response = self.session.get(url, timeout=(10, 30))
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _normalize_url(self, href: str) -> str | None:
        """Accept only canonical EBA publication URLs."""

        url = urljoin(EBA_DIGITAL_FINANCE_URL, href)
        parsed = urlparse(url)

        if (
            parsed.scheme != "https"
            or parsed.netloc.lower() not in EBA_ALLOWED_HOSTS
            or not parsed.path.startswith("/publications-and-media/")
        ):
            return None

        return parsed._replace(query="", fragment="").geturl()

    def _parse_date(self, text: str) -> str | None:
        """Convert the English EBA date to ISO format."""

        try:
            return datetime.strptime(
                clean_text(text), "%d %B %Y"
            ).date().isoformat()
        except ValueError:
            return None

    def _extract_candidates(
        self, soup: BeautifulSoup
    ) -> list[EBAPublicationCandidate]:
        """Extract, deduplicate, and sort Digital Finance cards."""

        candidates_by_url: dict[str, EBAPublicationCandidate] = {}

        # Passo 2: ler somente os cartões temáticos da página oficial.
        for card in soup.select("article.teaser"):
            title_node = card.select_one(".teaser__title")
            date_node = card.select_one(".teaser__metadata")
            summary_node = card.select_one(".field--name-description")
            links = [
                anchor
                for anchor in card.select("a[href]")
                if "/publications-and-media/" in anchor.get("href", "")
            ]

            if title_node is None or date_node is None or not links:
                continue

            url = self._normalize_url(links[-1].get("href", ""))
            published_at = self._parse_date(
                date_node.get_text(" ", strip=True)
            )
            title = clean_text(title_node.get_text(" ", strip=True))
            summary = (
                clean_text(summary_node.get_text(" ", strip=True))
                if summary_node is not None
                else None
            )

            if url is None or published_at is None or not title:
                continue

            candidates_by_url[url] = EBAPublicationCandidate(
                title=title,
                url=url,
                published_at=published_at,
                summary=summary or None,
            )

        candidates = list(candidates_by_url.values())
        candidates.sort(key=lambda item: item.published_at, reverse=True)
        return candidates

    def _extract_body(self, soup: BeautifulSoup) -> str | None:
        """Extract meaningful paragraphs from an EBA publication."""

        paragraphs: list[str] = []
        seen: set[str] = set()

        # Passo 3: preservar apenas blocos informativos da publicação.
        for node in soup.select("article p"):
            paragraph = clean_text(node.get_text(" ", strip=True))
            if len(paragraph) < 30 or paragraph in seen:
                continue
            seen.add(paragraph)
            paragraphs.append(paragraph)

        return "\n\n".join(paragraphs) if paragraphs else None

    def collect(self, limit: int = 5) -> list[NewsItem]:
        """Collect the latest EBA Digital Finance publications."""

        if limit <= 0:
            return []

        listing = self._get_page(EBA_DIGITAL_FINANCE_URL)
        candidates = self._extract_candidates(listing)[:limit]
        collected_at = datetime.now(timezone.utc).isoformat()
        news_items: list[NewsItem] = []

        # Passo 4: enriquecer cada cartão com o texto da página oficial.
        for candidate in candidates:
            page = self._get_page(candidate.url)
            body = self._extract_body(page)
            news_items.append(
                NewsItem(
                    source="EBA",
                    title=candidate.title,
                    url=candidate.url,
                    published_at=candidate.published_at,
                    summary=candidate.summary,
                    body=body,
                    collected_at=collected_at,
                )
            )

        return news_items

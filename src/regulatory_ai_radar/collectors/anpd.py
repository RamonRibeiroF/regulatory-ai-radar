from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import sleep
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


ANPD_NEWS_URL = "https://www.gov.br/anpd/pt-br/assuntos/noticias"

ANPD_NEWS_API_URL = (
    "https://www.gov.br/anpd/++api++/pt-br/assuntos/"
    "noticias/@querystring-search"
)

ANPD_NEWS_PATH = "/anpd/pt-br/assuntos/noticias/"

BRASILIA_TIMEZONE = timezone(timedelta(hours=-3))

PUBLISHED_PATTERN = re.compile(
    r"Publicado em\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})"
)


@dataclass(slots=True)
class NewsItem:
    """Represent a news article collected from a regulatory source."""

    source: str
    title: str
    url: str
    published_at: str | None
    summary: str | None
    body: str | None
    collected_at: str


def clean_text(text: str) -> str:
    """Remove unnecessary spaces and line breaks."""

    return " ".join(text.split())


class ANPDCollector:
    """Collect news articles published by the ANPD."""

    def __init__(self) -> None:
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "RegulatoryAIRadar/0.1 "
                    "(educational and portfolio project)"
                )
            }
        )

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Download a page and return its parsed HTML."""

        response = self.session.get(
            url,
            timeout=(10, 30),
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser",
        )

    def _extract_article_links(
        self,
        limit: int,
    ) -> list[tuple[str, str]]:
        """Retrieve article titles and URLs from the ANPD API."""

        # Step 1: define the query used by the ANPD news page.
        query = {
            "b_size": limit,
            "limit": 10_000_000_000,
            "query": [
                {
                    "i": "portal_type",
                    "o": (
                        "plone.app.querystring.operation."
                        "selection.any"
                    ),
                    "v": ["News Item"],
                },
                {
                    "i": "path",
                    "o": (
                        "plone.app.querystring.operation."
                        "string.relativePath"
                    ),
                    "v": "",
                },
            ],
            "sort_on": "effective",
            "sort_order": "descending",
            "sort_order_boolean": True,
        }

        # Step 2: request the latest articles from the official API.
        response = self.session.post(
            ANPD_NEWS_API_URL,
            json=query,
            headers={"Accept": "application/json"},
            timeout=(10, 30),
        )

        response.raise_for_status()

        data = response.json()

        articles: list[tuple[str, str]] = []
        seen_urls: set[str] = set()

        # Step 3: validate and normalize the returned articles.
        for item in data.get("items", []):
            title = clean_text(
                str(item.get("title", ""))
            )

            url = str(item.get("@id", ""))

            if len(title) < 15 or not url:
                continue

            parsed_url = urlparse(url)

            if parsed_url.netloc != "www.gov.br":
                continue

            if not parsed_url.path.startswith(ANPD_NEWS_PATH):
                continue

            normalized_url = (
                f"{parsed_url.scheme}://"
                f"{parsed_url.netloc}"
                f"{parsed_url.path.rstrip('/')}"
            )

            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)

            articles.append(
                (
                    title,
                    normalized_url,
                )
            )

            if len(articles) >= limit:
                break

        return articles

    def _extract_article(
        self,
        fallback_title: str,
        url: str,
    ) -> NewsItem:
        """Extract structured data from an individual article."""

        # Step 4: download and parse the individual article.
        soup = self._get_soup(url)

        page_title = soup.find("h1")

        if page_title:
            title = clean_text(
                page_title.get_text(
                    " ",
                    strip=True,
                )
            )
        else:
            title = fallback_title

        # Step 5: extract the article summary.
        description_meta = soup.find(
            "meta",
            attrs={"name": "description"},
        )

        if description_meta is None:
            description_meta = soup.find(
                "meta",
                attrs={"property": "og:description"},
            )

        summary = None

        if description_meta:
            content = description_meta.get("content")

            if content:
                summary = clean_text(str(content))

        # Step 6: locate and standardize the publication date.
        entire_page_text = clean_text(
            soup.get_text(
                " ",
                strip=True,
            )
        )

        published_at = None

        published_match = PUBLISHED_PATTERN.search(
            entire_page_text
        )

        if published_match:
            date_text = published_match.group(1)
            time_text = published_match.group(2)

            publication_datetime = datetime.strptime(
                f"{date_text} {time_text}",
                "%d/%m/%Y %H:%M",
            )

            publication_datetime = publication_datetime.replace(
                tzinfo=BRASILIA_TIMEZONE
            )

            published_at = publication_datetime.isoformat()

        # Step 7: extract the main article content.
        content_area = soup.select_one(
            "#content-core"
        )

        if content_area is None:
            content_area = soup.find("main")

        body = None

        if content_area:
            paragraphs: list[str] = []

            for paragraph in content_area.find_all("p"):
                paragraph_text = clean_text(
                    paragraph.get_text(
                        " ",
                        strip=True,
                    )
                )

                if len(paragraph_text) >= 40:
                    paragraphs.append(
                        paragraph_text
                    )

            if paragraphs:
                body = "\n\n".join(paragraphs)

        collected_at = datetime.now(
            timezone.utc
        ).isoformat()

        # Step 8: return the standardized news article.
        return NewsItem(
            source="ANPD",
            title=title,
            url=url,
            published_at=published_at,
            summary=summary,
            body=body,
            collected_at=collected_at,
        )

    def collect(
        self,
        limit: int = 5,
    ) -> list[NewsItem]:
        """Run the complete ANPD collection process."""

        # Step 9: retrieve the latest article links.
        try:
            article_links = self._extract_article_links(
                limit=limit
            )
        except requests.RequestException as error:
            print(
                f"Error fetching the ANPD news list: {error}"
            )

            return []

        news_items: list[NewsItem] = []

        # Step 10: collect each article individually.
        for title, url in article_links:
            try:
                item = self._extract_article(
                    fallback_title=title,
                    url=url,
                )

                news_items.append(item)

            except requests.RequestException as error:
                print(
                    f"Error collecting {url}: {error}"
                )

            sleep(0.4)

        return news_items
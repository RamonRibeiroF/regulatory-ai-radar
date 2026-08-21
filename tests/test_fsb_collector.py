from __future__ import annotations

import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from regulatory_ai_radar.collectors.fsb import (
    FSBCollector,
    FSBPublicationCandidate,
)
from regulatory_ai_radar.entities import NewsItem


class FSBCollectorTests(unittest.TestCase):
    """Validate the Financial Stability Board collector rules."""

    def setUp(self) -> None:
        self.collector = FSBCollector()

    def _build_listing_page(
        self,
        cards: list[tuple[str, str, str, str]],
    ) -> BeautifulSoup:
        """Create a local FSB financial innovation listing."""

        card_html = ""

        for (
            title,
            publication_url,
            publication_date,
            summary,
        ) in cards:
            card_html += f"""
                <div
                    class="
                        post-excerpt
                        post-excerpt-default
                    "
                >
                    <div class="post-heading">
                        <div class="post-title">
                            <h3>
                                <a href="{publication_url}">
                                    {title}
                                </a>
                            </h3>
                        </div>
                        <div class="post-date">
                            <span>
                                {publication_date}
                            </span>
                        </div>
                    </div>
                    <div class="post-content">
                        <span class="media-excerpt">
                            {summary}
                        </span>
                    </div>
                </div>
            """

        return BeautifulSoup(
            (
                "<html><body><main>"
                f"{card_html}"
                "</main></body></html>"
            ),
            "html.parser",
        )

    def test_candidates_are_sorted_newest_first(
        self,
    ) -> None:
        listing_page = self._build_listing_page(
            [
                (
                    "Older FSB publication",
                    (
                        "https://www.fsb.org/2026/06/"
                        "older-publication/"
                    ),
                    "01 June 2026",
                    "Older financial innovation summary.",
                ),
                (
                    "Newest FSB publication",
                    (
                        "https://www.fsb.org/2026/08/"
                        "newest-publication/"
                    ),
                    "06 August 2026",
                    "Newest financial innovation summary.",
                ),
                (
                    "Middle FSB publication",
                    (
                        "https://www.fsb.org/2026/07/"
                        "middle-publication/"
                    ),
                    "07 July 2026",
                    "Middle financial innovation summary.",
                ),
            ]
        )

        candidates = self.collector._extract_candidates(
            listing_page
        )

        self.assertEqual(len(candidates), 3)
        self.assertEqual(
            candidates[0].title,
            "Newest FSB publication",
        )
        self.assertEqual(
            candidates[1].title,
            "Middle FSB publication",
        )
        self.assertEqual(
            candidates[2].title,
            "Older FSB publication",
        )

    def test_duplicate_cards_are_removed(
        self,
    ) -> None:
        publication_url = (
            "https://www.fsb.org/2026/08/"
            "repeated-publication/"
        )

        listing_page = self._build_listing_page(
            [
                (
                    "Repeated FSB publication",
                    publication_url,
                    "06 August 2026",
                    "Repeated summary.",
                ),
                (
                    "Repeated FSB publication",
                    publication_url,
                    "06 August 2026",
                    "Repeated summary.",
                ),
            ]
        )

        candidates = self.collector._extract_candidates(
            listing_page
        )

        self.assertEqual(len(candidates), 1)

    def test_external_urls_are_rejected(
        self,
    ) -> None:
        result = self.collector._normalize_url(
            "https://example.com/2026/08/external/"
        )

        self.assertIsNone(result)

    def test_article_content_is_normalized(
        self,
    ) -> None:
        candidate = FSBPublicationCandidate(
            title="Listing title",
            url=(
                "https://www.fsb.org/2026/08/"
                "official-publication/"
            ),
            published_at="2026-08-06",
            summary=(
                "Official summary about artificial "
                "intelligence in finance."
            ),
        )

        article_page = BeautifulSoup(
            """
            <html>
                <body>
                    <main>
                        <article>
                            <h1>
                                Official FSB AI publication
                            </h1>
                            <section class="post-content">
                                <p>
                                    This publication explains
                                    artificial intelligence risks
                                    for financial institutions.
                                </p>
                                <ul>
                                    <li>
                                        Financial institutions must
                                        maintain effective AI
                                        governance and controls.
                                    </li>
                                </ul>
                            </section>
                        </article>
                    </main>
                </body>
            </html>
            """,
            "html.parser",
        )

        with patch.object(
            self.collector,
            "_get_page",
            return_value=article_page,
        ):
            result = self.collector._extract_article(
                candidate
            )

        self.assertIsNotNone(result)

        if result is None:
            self.fail(
                "A valid FSB publication was not normalized."
            )

        self.assertEqual(result.source, "FSB")
        self.assertEqual(
            result.title,
            "Official FSB AI publication",
        )
        self.assertEqual(
            result.published_at,
            "2026-08-06",
        )
        self.assertEqual(result.summary, candidate.summary)
        self.assertIn(
            "artificial intelligence risks",
            result.body or "",
        )
        self.assertIn(
            "AI governance and controls",
            result.body or "",
        )
        self.assertEqual(result.url, candidate.url)

    def test_collection_stops_at_requested_limit(
        self,
    ) -> None:
        listing_page = self._build_listing_page(
            [
                (
                    "First FSB publication",
                    (
                        "https://www.fsb.org/2026/08/"
                        "first-publication/"
                    ),
                    "06 August 2026",
                    "First summary.",
                ),
                (
                    "Second FSB publication",
                    (
                        "https://www.fsb.org/2026/07/"
                        "second-publication/"
                    ),
                    "07 July 2026",
                    "Second summary.",
                ),
                (
                    "Third FSB publication",
                    (
                        "https://www.fsb.org/2026/06/"
                        "third-publication/"
                    ),
                    "10 June 2026",
                    "Third summary.",
                ),
            ]
        )

        def build_news_item(
            candidate: FSBPublicationCandidate,
        ) -> NewsItem:
            return NewsItem(
                source="FSB",
                title=candidate.title,
                url=candidate.url,
                published_at=candidate.published_at,
                summary=candidate.summary,
                body="Local body.",
                collected_at="2026-08-21T10:00:00+00:00",
            )

        with (
            patch.object(
                self.collector,
                "_get_page",
                return_value=listing_page,
            ),
            patch.object(
                self.collector,
                "_extract_article",
                side_effect=build_news_item,
            ) as mocked_extraction,
        ):
            result = self.collector.collect(limit=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0].title,
            "First FSB publication",
        )
        self.assertEqual(
            result[1].title,
            "Second FSB publication",
        )
        self.assertEqual(
            mocked_extraction.call_count,
            2,
        )

    def test_non_positive_limit_avoids_requests(
        self,
    ) -> None:
        with patch.object(
            self.collector,
            "_get_page",
        ) as mocked_request:
            result = self.collector.collect(limit=0)

        self.assertEqual(result, [])
        mocked_request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
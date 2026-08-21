from __future__ import annotations

import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from regulatory_ai_radar.collectors.eu_ai_office import (
    EUNewsCandidate,
    EUAIOfficeCollector,
)
from regulatory_ai_radar.entities import NewsItem


class EUAIOfficeCollectorTests(unittest.TestCase):
    """Validate the European AI Office collector rules."""

    def setUp(self) -> None:
        # Step 1: create a fresh collector for every test.
        self.collector = EUAIOfficeCollector()

    def _build_listing_page(
        self,
        cards: list[tuple[str, str, str]],
    ) -> BeautifulSoup:
        """Create a local European Commission listing page."""

        card_html = ""

        for title, relative_url, publication_date in cards:
            card_html += f"""
                <article class="ecl-content-item">
                    <ul>
                        <li
                            class="
                                ecl-content-block__primary-meta-item
                            "
                        >
                            Press release
                        </li>
                        <li
                            class="
                                ecl-content-block__primary-meta-item
                            "
                        >
                            {publication_date}
                        </li>
                    </ul>
                    <a
                        data-ecl-title-link
                        href="{relative_url}"
                    >
                        {title}
                    </a>
                </article>
            """

        return BeautifulSoup(
            f"<html><body>{card_html}</body></html>",
            "html.parser",
        )

    def test_candidates_are_sorted_newest_first(
        self,
    ) -> None:
        # Step 2: create publication cards in an incorrect order.
        listing_page = self._build_listing_page(
            [
                (
                    "Older publication",
                    "/en/news/older-publication",
                    "01 June 2026",
                ),
                (
                    "Newest publication",
                    "/en/news/newest-publication",
                    "03 August 2026",
                ),
                (
                    "Middle publication",
                    "/en/news/middle-publication",
                    "15 July 2026",
                ),
            ]
        )

        candidates = self.collector._extract_candidates(
            listing_page
        )

        # Step 3: confirm descending publication-date ordering.
        self.assertEqual(
            len(candidates),
            3,
        )
        self.assertEqual(
            candidates[0].title,
            "Newest publication",
        )
        self.assertEqual(
            candidates[1].title,
            "Middle publication",
        )
        self.assertEqual(
            candidates[2].title,
            "Older publication",
        )

    def test_duplicate_cards_are_removed(
        self,
    ) -> None:
        listing_page = self._build_listing_page(
            [
                (
                    "Repeated publication",
                    "/en/news/repeated-publication",
                    "01 August 2026",
                ),
                (
                    "Repeated publication",
                    "/en/news/repeated-publication",
                    "01 August 2026",
                ),
            ]
        )

        # Step 4: remove repeated cards through the official URL.
        candidates = self.collector._extract_candidates(
            listing_page
        )

        self.assertEqual(
            len(candidates),
            1,
        )

    def test_external_urls_are_rejected(
        self,
    ) -> None:
        # Step 5: reject links outside the official EU domain.
        result = self.collector._normalize_url(
            "https://example.com/en/news/external"
        )

        self.assertIsNone(
            result
        )

    def test_article_content_is_normalized(
        self,
    ) -> None:
        candidate = EUNewsCandidate(
            title="Listing title",
            url=(
                "https://digital-strategy.ec.europa.eu/"
                "en/news/official-publication"
            ),
            published_at="2026-08-03",
        )

        article_page = BeautifulSoup(
            """
            <html>
                <body>
                    <h1>
                        Official European AI publication
                    </h1>
                    <p
                        class="
                            ecl-page-header-standardised__description
                        "
                    >
                        Official summary about European AI regulation.
                    </p>
                    <div class="cnt-main-body">
                        <p>
                            This paragraph explains the new regulatory
                            obligations for artificial intelligence.
                        </p>
                        <ul>
                            <li>
                                Providers must follow the official
                                European transparency requirements.
                            </li>
                        </ul>
                    </div>
                </body>
            </html>
            """,
            "html.parser",
        )

        # Step 6: simulate the official detail page locally.
        with patch.object(
            self.collector,
            "_get_page",
            return_value=article_page,
        ):
            result = self.collector._extract_article(
                candidate
            )

        self.assertIsNotNone(
            result
        )

        if result is None:
            self.fail(
                "A valid European publication was not normalized."
            )

        # Step 7: validate the shared NewsItem fields.
        self.assertEqual(
            result.source,
            "EU_AI_OFFICE",
        )
        self.assertEqual(
            result.title,
            "Official European AI publication",
        )
        self.assertEqual(
            result.published_at,
            "2026-08-03",
        )
        self.assertEqual(
            result.summary,
            (
                "Official summary about European "
                "AI regulation."
            ),
        )
        self.assertIn(
            "regulatory obligations",
            result.body or "",
        )
        self.assertIn(
            "transparency requirements",
            result.body or "",
        )
        self.assertEqual(
            result.url,
            candidate.url,
        )

    def test_collection_stops_at_requested_limit(
        self,
    ) -> None:
        listing_page = self._build_listing_page(
            [
                (
                    "First publication",
                    "/en/news/first-publication",
                    "03 August 2026",
                ),
                (
                    "Second publication",
                    "/en/news/second-publication",
                    "02 August 2026",
                ),
                (
                    "Third publication",
                    "/en/news/third-publication",
                    "01 August 2026",
                ),
            ]
        )

        def build_news_item(
            candidate: EUNewsCandidate,
        ) -> NewsItem:
            return NewsItem(
                source="EU_AI_OFFICE",
                title=candidate.title,
                url=candidate.url,
                published_at=candidate.published_at,
                summary="Local summary.",
                body="Local body.",
                collected_at="2026-08-21T10:00:00+00:00",
            )

        # Step 8: simulate listing and detail processing locally.
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
            result = self.collector.collect(
                limit=2
            )

        self.assertEqual(
            len(result),
            2,
        )
        self.assertEqual(
            result[0].title,
            "First publication",
        )
        self.assertEqual(
            result[1].title,
            "Second publication",
        )
        self.assertEqual(
            mocked_extraction.call_count,
            2,
        )

    def test_non_positive_limit_avoids_requests(
        self,
    ) -> None:
        # Step 9: confirm that an empty request uses no network call.
        with patch.object(
            self.collector,
            "_get_page",
        ) as mocked_request:
            result = self.collector.collect(
                limit=0
            )

        self.assertEqual(
            result,
            [],
        )
        mocked_request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
from __future__ import annotations

import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from regulatory_ai_radar.collectors.bis import (
    BISCollector,
    BISPublicationCandidate,
)
from regulatory_ai_radar.entities import NewsItem


class BISCollectorTests(unittest.TestCase):
    """Validate the BIS Innovation Hub collector rules."""

    def setUp(self) -> None:
        # Step 1: create a fresh collector for every test.
        self.collector = BISCollector()

    def _build_payload(
        self,
        publications: list[
            tuple[str, str, str]
        ],
    ) -> dict[str, object]:
        """Create a local response matching the official BIS API."""

        publication_list: dict[
            str,
            dict[str, str],
        ] = {}

        for index, (
            path,
            title,
            publication_date,
        ) in enumerate(
            publications,
            start=1,
        ):
            publication_list[
                f"publication-{index}"
            ] = {
                "path": path,
                "short_title": title,
                "publication_start_date": (
                    publication_date
                ),
            }

        return {
            "list": publication_list,
            "document_date_type": None,
        }

    def test_candidates_are_sorted_newest_first(
        self,
    ) -> None:
        # Step 2: verify explicit newest-to-oldest ordering.
        payload = self._build_payload(
            [
                (
                    "/publ/othp108",
                    "Older BIS publication",
                    "2026-01-29",
                ),
                (
                    "/publ/othp112",
                    "Newest BIS publication",
                    "2026-07-08",
                ),
                (
                    "/publ/othp110",
                    "Middle BIS publication",
                    "2026-05-27",
                ),
            ]
        )

        candidates = self.collector._extract_candidates(
            payload
        )

        self.assertEqual(len(candidates), 3)
        self.assertEqual(
            candidates[0].title,
            "Newest BIS publication",
        )
        self.assertEqual(
            candidates[1].title,
            "Middle BIS publication",
        )
        self.assertEqual(
            candidates[2].title,
            "Older BIS publication",
        )

    def test_duplicate_publications_are_removed(
        self,
    ) -> None:
        # Step 3: verify deduplication through canonical URLs.
        payload = {
            "list": {
                "first-result": {
                    "path": "/publ/othp112",
                    "short_title": (
                        "Repeated BIS publication"
                    ),
                    "publication_start_date": (
                        "2026-07-08"
                    ),
                },
                "second-result": {
                    "path": "/publ/othp112",
                    "short_title": (
                        "Repeated BIS publication"
                    ),
                    "publication_start_date": (
                        "2026-07-08"
                    ),
                },
            }
        }

        candidates = self.collector._extract_candidates(
            payload
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0].url,
            "https://www.bis.org/publ/othp112.htm",
        )

    def test_invalid_publication_paths_are_rejected(
        self,
    ) -> None:
        # Step 4: reject paths outside the official publication format.
        external_result = (
            self.collector._build_publication_url(
                "https://example.com/publication"
            )
        )

        press_result = (
            self.collector._build_publication_url(
                "/press/p260708"
            )
        )

        traversal_result = (
            self.collector._build_publication_url(
                "/publ/../private"
            )
        )

        self.assertIsNone(external_result)
        self.assertIsNone(press_result)
        self.assertIsNone(traversal_result)

    def test_publication_content_is_normalized(
        self,
    ) -> None:
        # Step 5: validate title, summary, body, date, and source.
        candidate = BISPublicationCandidate(
            title="Listing title",
            path="/publ/othp112",
            url=(
                "https://www.bis.org/"
                "publ/othp112.htm"
            ),
            published_at="2026-07-08",
        )

        publication_page = BeautifulSoup(
            """
            <html>
                <head>
                    <meta
                        name="description"
                        content="
                            Official summary about artificial
                            intelligence and financial supervision.
                        "
                    >
                </head>
                <body>
                    <main>
                        <h1>
                            Official BIS Innovation Hub publication
                        </h1>
                        <div id="cmsContent">
                            <p>
                                This publication explains how
                                artificial intelligence can support
                                financial authorities and central
                                banks.
                            </p>
                            <ul>
                                <li>
                                    Institutions must maintain
                                    effective governance and model
                                    risk controls.
                                </li>
                            </ul>
                        </div>
                    </main>
                </body>
            </html>
            """,
            "html.parser",
        )

        with patch.object(
            self.collector,
            "_get_page",
            return_value=publication_page,
        ):
            result = (
                self.collector._extract_publication(
                    candidate
                )
            )

        self.assertIsNotNone(result)

        if result is None:
            self.fail(
                "A valid BIS publication was not normalized."
            )

        self.assertEqual(result.source, "BIS")
        self.assertEqual(
            result.title,
            "Official BIS Innovation Hub publication",
        )
        self.assertEqual(
            result.published_at,
            "2026-07-08",
        )
        self.assertIn(
            "artificial intelligence",
            result.summary or "",
        )
        self.assertIn(
            "financial authorities",
            result.body or "",
        )
        self.assertIn(
            "model risk controls",
            result.body or "",
        )
        self.assertEqual(
            result.url,
            candidate.url,
        )

    def test_collection_stops_at_requested_limit(
        self,
    ) -> None:
        # Step 6: verify that extra detail pages are not requested.
        payload = self._build_payload(
            [
                (
                    "/publ/othp112",
                    "First BIS publication",
                    "2026-07-08",
                ),
                (
                    "/publ/othp111",
                    "Second BIS publication",
                    "2026-05-29",
                ),
                (
                    "/publ/othp110",
                    "Third BIS publication",
                    "2026-05-27",
                ),
            ]
        )

        def build_news_item(
            candidate: BISPublicationCandidate,
        ) -> NewsItem:
            return NewsItem(
                source="BIS",
                title=candidate.title,
                url=candidate.url,
                published_at=candidate.published_at,
                summary="Local BIS summary.",
                body="Local BIS publication body.",
                collected_at=(
                    "2026-08-21T10:00:00+00:00"
                ),
            )

        with (
            patch.object(
                self.collector,
                "_get_json",
                return_value=payload,
            ),
            patch.object(
                self.collector,
                "_extract_publication",
                side_effect=build_news_item,
            ) as mocked_extraction,
        ):
            result = self.collector.collect(
                limit=2
            )

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0].title,
            "First BIS publication",
        )
        self.assertEqual(
            result[1].title,
            "Second BIS publication",
        )
        self.assertEqual(
            mocked_extraction.call_count,
            2,
        )

    def test_non_positive_limit_avoids_requests(
        self,
    ) -> None:
        # Step 7: avoid network requests when no items are requested.
        with patch.object(
            self.collector,
            "_get_json",
        ) as mocked_request:
            result = self.collector.collect(
                limit=0
            )

        self.assertEqual(result, [])
        mocked_request.assert_not_called()


if __name__ == "__main__":
    # Step 8: allow this test file to run directly.
    unittest.main()
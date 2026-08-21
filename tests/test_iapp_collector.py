from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from regulatory_ai_radar.collectors.iapp import (
    IAPPCollector,
    IAPP_INITIAL_RESULTS_PREFIX,
)


class IAPPCollectorTests(unittest.TestCase):
    """Validate the official IAPP news collector rules."""

    def setUp(self) -> None:
        # Step 1: create a fresh collector for every test.
        self.collector = IAPPCollector()

    def _build_hit(
        self,
        *,
        title: str,
        publication_date: str,
        url: str,
        member_gated: bool = False,
        summary: str = "Official IAPP article summary.",
        body: str = "Official public article body about privacy.",
    ) -> dict[str, object]:
        """Create one local result matching the IAPP structure."""

        return {
            "article_details": {
                "headline": title,
                "date": publication_date,
            },
            "url": url,
            "entry_summary": summary,
            "member_gated": member_gated,
            "article_body": [
                {
                    "rte": {
                        "rich_text_editor": (
                            f"<p>{body}</p>"
                        ),
                    }
                }
            ],
        }

    def _build_payload(
        self,
        hits: list[dict[str, object]],
    ) -> dict[str, object]:
        """Create the local structured search payload."""

        return {
            "all_article_date_desc": {
                "results": [
                    {
                        "hits": hits,
                    }
                ]
            }
        }

    def test_structured_payload_is_extracted(
        self,
    ) -> None:
        # Step 2: decode the public server-rendered search results.
        payload = self._build_payload(
            [
                self._build_hit(
                    title="IAPP privacy update",
                    publication_date="2026-08-21",
                    url="/news/a/iapp-privacy-update",
                )
            ]
        )

        page = BeautifulSoup(
            (
                "<html><body><script>"
                f"{IAPP_INITIAL_RESULTS_PREFIX}"
                f"{json.dumps(payload)};"
                "</script></body></html>"
            ),
            "html.parser",
        )

        result = self.collector._extract_initial_payload(
            page
        )

        self.assertEqual(result, payload)

    def test_candidates_are_sorted_newest_first(
        self,
    ) -> None:
        # Step 3: verify explicit newest-to-oldest ordering.
        payload = self._build_payload(
            [
                self._build_hit(
                    title="Older IAPP article",
                    publication_date="2026-08-19",
                    url="/news/a/older-iapp-article",
                ),
                self._build_hit(
                    title="Newest IAPP article",
                    publication_date="2026-08-21",
                    url="/news/a/newest-iapp-article",
                ),
                self._build_hit(
                    title="Middle IAPP article",
                    publication_date="2026-08-20",
                    url="/news/a/middle-iapp-article",
                ),
            ]
        )

        candidates = self.collector._extract_candidates(
            payload
        )

        self.assertEqual(
            [candidate.title for candidate in candidates],
            [
                "Newest IAPP article",
                "Middle IAPP article",
                "Older IAPP article",
            ],
        )

    def test_duplicate_urls_are_removed(
        self,
    ) -> None:
        # Step 4: remove repeated results through canonical URLs.
        repeated_hit = self._build_hit(
            title="Repeated IAPP article",
            publication_date="2026-08-21",
            url="/news/a/repeated-iapp-article",
        )

        candidates = self.collector._extract_candidates(
            self._build_payload(
                [repeated_hit, repeated_hit]
            )
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0].url,
            (
                "https://iapp.org/news/a/"
                "repeated-iapp-article"
            ),
        )

    def test_invalid_or_external_urls_are_rejected(
        self,
    ) -> None:
        # Step 5: accept only official HTTPS article paths.
        self.assertIsNone(
            self.collector._normalize_url(
                "https://example.com/news/a/external"
            )
        )
        self.assertIsNone(
            self.collector._normalize_url(
                "https://iapp.org/about"
            )
        )
        self.assertIsNone(
            self.collector._normalize_url(
                "http://iapp.org/news/a/insecure"
            )
        )

    def test_public_article_body_is_normalized(
        self,
    ) -> None:
        # Step 6: retain normalized body text from public articles.
        payload = self._build_payload(
            [
                self._build_hit(
                    title="Public IAPP article",
                    publication_date="2026-08-21",
                    url="/news/a/public-iapp-article",
                    body=(
                        "Public guidance about privacy, data "
                        "protection, and artificial intelligence."
                    ),
                )
            ]
        )

        candidate = self.collector._extract_candidates(
            payload
        )[0]

        self.assertFalse(candidate.is_member_gated)
        self.assertIn(
            "data protection",
            candidate.body or "",
        )

    def test_member_gated_body_is_not_stored(
        self,
    ) -> None:
        # Step 7: preserve metadata without protected body content.
        payload = self._build_payload(
            [
                self._build_hit(
                    title="Member-only IAPP article",
                    publication_date="2026-08-21",
                    url="/news/a/member-only-iapp-article",
                    member_gated=True,
                    body="Protected member-only article content.",
                )
            ]
        )

        candidate = self.collector._extract_candidates(
            payload
        )[0]

        self.assertTrue(candidate.is_member_gated)
        self.assertIsNone(candidate.body)
        self.assertEqual(
            candidate.summary,
            "Official IAPP article summary.",
        )

    def test_collection_respects_requested_limit(
        self,
    ) -> None:
        # Step 8: select only the requested most recent articles.
        payload = self._build_payload(
            [
                self._build_hit(
                    title="First IAPP article",
                    publication_date="2026-08-21",
                    url="/news/a/first-iapp-article",
                ),
                self._build_hit(
                    title="Second IAPP article",
                    publication_date="2026-08-20",
                    url="/news/a/second-iapp-article",
                ),
                self._build_hit(
                    title="Third IAPP article",
                    publication_date="2026-08-19",
                    url="/news/a/third-iapp-article",
                ),
            ]
        )

        page = BeautifulSoup("<html></html>", "html.parser")

        with (
            patch.object(
                self.collector,
                "_get_page",
                return_value=page,
            ),
            patch.object(
                self.collector,
                "_extract_initial_payload",
                return_value=payload,
            ),
        ):
            result = self.collector.collect(limit=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "First IAPP article")
        self.assertEqual(result[1].title, "Second IAPP article")
        self.assertTrue(
            all(item.source == "IAPP" for item in result)
        )

    def test_non_positive_limit_avoids_requests(
        self,
    ) -> None:
        # Step 9: avoid network requests when no items are requested.
        with patch.object(
            self.collector,
            "_get_page",
        ) as mocked_request:
            result = self.collector.collect(limit=0)

        self.assertEqual(result, [])
        mocked_request.assert_not_called()


if __name__ == "__main__":
    # Step 10: allow this test file to run directly.
    unittest.main()

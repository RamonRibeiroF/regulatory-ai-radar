from __future__ import annotations

import unittest
from unittest.mock import patch

from regulatory_ai_radar.collectors.oecd_ai import (
    OECDAICollector,
    OECD_AI_API_URL,
)


class OECDAICollectorTests(unittest.TestCase):
    """Validate the official OECD.AI publication collector."""

    def setUp(self) -> None:
        # Step 1: create a fresh collector for every test.
        self.collector = OECDAICollector()

    def _build_item(
        self,
        *,
        title: str,
        slug: str,
        publication_date: str,
        summary: str = "Official OECD.AI publication summary.",
        body: str = "Official OECD.AI publication body.",
    ) -> dict[str, object]:
        """Create one local record matching the official API."""

        return {
            "id": 1,
            "date": publication_date,
            "slug": slug,
            "title": {
                "rendered": title,
            },
            "excerpt": {
                "rendered": f"<p>{summary}</p>",
            },
            "content": {
                "rendered": f"<p>{body}</p>",
            },
        }

    def test_candidates_are_sorted_newest_first(
        self,
    ) -> None:
        # Step 2: verify explicit newest-to-oldest ordering.
        payload = [
            self._build_item(
                title="Older OECD.AI publication",
                slug="older-oecd-ai-publication",
                publication_date="2026-02-01T09:00:00",
            ),
            self._build_item(
                title="Newest OECD.AI publication",
                slug="newest-oecd-ai-publication",
                publication_date="2026-07-08T13:26:41",
            ),
            self._build_item(
                title="Middle OECD.AI publication",
                slug="middle-oecd-ai-publication",
                publication_date="2026-05-10T10:00:00",
            ),
        ]

        candidates = self.collector._extract_candidates(
            payload
        )

        self.assertEqual(
            [candidate.title for candidate in candidates],
            [
                "Newest OECD.AI publication",
                "Middle OECD.AI publication",
                "Older OECD.AI publication",
            ],
        )

    def test_duplicate_publications_are_removed(
        self,
    ) -> None:
        # Step 3: remove repeated records through canonical URLs.
        repeated_item = self._build_item(
            title="Repeated OECD.AI publication",
            slug="repeated-oecd-ai-publication",
            publication_date="2026-07-08T13:26:41",
        )

        candidates = self.collector._extract_candidates(
            [repeated_item, repeated_item]
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0].url,
            (
                "https://oecd.ai/en/ai-publications/"
                "repeated-oecd-ai-publication"
            ),
        )

    def test_invalid_slugs_are_rejected(
        self,
    ) -> None:
        # Step 4: reject paths and characters outside the slug format.
        self.assertIsNone(
            self.collector._build_publication_url(
                "../private"
            )
        )
        self.assertIsNone(
            self.collector._build_publication_url(
                "https://example.com/publication"
            )
        )
        self.assertIsNone(
            self.collector._build_publication_url(
                "invalid_slug"
            )
        )

    def test_publication_content_is_normalized(
        self,
    ) -> None:
        # Step 5: normalize entities and meaningful HTML blocks.
        payload = [
            self._build_item(
                title="AI governance &amp; public policy",
                slug="ai-governance-public-policy",
                publication_date="2026-07-08T13:26:41",
                summary=(
                    "OECD.AI guidance for trustworthy &amp; "
                    "human-centred artificial intelligence."
                ),
                body=(
                    "Governments should establish transparent "
                    "AI governance and accountability controls."
                ),
            )
        ]

        candidate = self.collector._extract_candidates(
            payload
        )[0]

        self.assertEqual(
            candidate.title,
            "AI governance & public policy",
        )
        self.assertIn(
            "trustworthy & human-centred",
            candidate.summary or "",
        )
        self.assertIn(
            "accountability controls",
            candidate.body or "",
        )
        self.assertEqual(
            candidate.published_at,
            "2026-07-08",
        )

    def test_missing_excerpt_uses_body_summary(
        self,
    ) -> None:
        # Step 6: use the first body paragraph when no excerpt exists.
        item = self._build_item(
            title="OECD.AI policy report",
            slug="oecd-ai-policy-report",
            publication_date="2026-07-08T13:26:41",
            body=(
                "This first paragraph provides the official "
                "publication summary."
            ),
        )
        item["excerpt"] = {
            "rendered": "",
        }

        candidate = self.collector._extract_candidates(
            [item]
        )[0]

        self.assertEqual(
            candidate.summary,
            (
                "This first paragraph provides the official "
                "publication summary."
            ),
        )

    def test_collection_uses_ordered_api_and_limit(
        self,
    ) -> None:
        # Step 7: verify official endpoint parameters and result limit.
        payload = [
            self._build_item(
                title="First OECD.AI publication",
                slug="first-oecd-ai-publication",
                publication_date="2026-07-08T13:26:41",
            ),
            self._build_item(
                title="Second OECD.AI publication",
                slug="second-oecd-ai-publication",
                publication_date="2026-02-19T07:28:23",
            ),
            self._build_item(
                title="Third OECD.AI publication",
                slug="third-oecd-ai-publication",
                publication_date="2026-02-17T08:40:49",
            ),
        ]

        with patch.object(
            self.collector,
            "_get_json",
            return_value=payload,
        ) as mocked_request:
            result = self.collector.collect(limit=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0].title,
            "First OECD.AI publication",
        )
        self.assertEqual(
            result[1].title,
            "Second OECD.AI publication",
        )
        self.assertTrue(
            all(item.source == "OECD_AI" for item in result)
        )

        request_url = mocked_request.call_args.args[0]
        request_params = mocked_request.call_args.kwargs["params"]

        self.assertEqual(request_url, OECD_AI_API_URL)
        self.assertEqual(request_params["orderby"], "date")
        self.assertEqual(request_params["order"], "desc")
        self.assertEqual(request_params["per_page"], 10)

    def test_non_positive_limit_avoids_requests(
        self,
    ) -> None:
        # Step 8: avoid network requests when no items are requested.
        with patch.object(
            self.collector,
            "_get_json",
        ) as mocked_request:
            result = self.collector.collect(limit=0)

        self.assertEqual(result, [])
        mocked_request.assert_not_called()


if __name__ == "__main__":
    # Step 9: allow this test file to run directly.
    unittest.main()

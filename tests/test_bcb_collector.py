import unittest
from unittest.mock import patch
from xml.etree import ElementTree

from regulatory_ai_radar.collectors.bcb import BCBCollector


ATOM_FEED = """
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>RSS - Feeds do BC</title>

    <entry>
        <id>external-entry</id>
        <title>External article that must be rejected</title>
        <updated>2026-08-20T12:00:00-03:00</updated>
        <link
            rel="alternate"
            href="https://example.com/external-article"
        />
        <content type="html">
            &lt;div&gt;
                This external content must not be collected.
            &lt;/div&gt;
        </content>
    </entry>

    <entry>
        <id>newest-entry</id>
        <title>Newest BCB regulatory article</title>
        <updated>2026-08-19T12:00:00-03:00</updated>
        <link
            rel="alternate"
            href="https://www.bcb.gov.br/detalhenoticia/3/noticia?source=test#section"
        />
        <content type="html">
            &lt;div&gt;
                This is the summary of the newest regulatory article.
            &lt;/div&gt;
            &lt;div&gt;
                This is an additional paragraph with regulatory details.
            &lt;/div&gt;
        </content>
    </entry>

    <entry>
        <id>oldest-entry</id>
        <title>Oldest BCB regulatory article</title>
        <updated>2026-08-10T12:00:00-03:00</updated>
        <link
            rel="alternate"
            href="https://www.bcb.gov.br/detalhenoticia/1/noticia"
        />
        <content type="html">
            &lt;div&gt;
                This is the content of the oldest regulatory article.
            &lt;/div&gt;
        </content>
    </entry>

    <entry>
        <id>middle-entry</id>
        <title>Middle BCB regulatory article</title>
        <updated>2026-08-15T12:00:00-03:00</updated>
        <link
            rel="alternate"
            href="https://www.bcb.gov.br/detalhenoticia/2/noticia"
        />
        <content type="html">
            &lt;div&gt;
                This is the content of the middle regulatory article.
            &lt;/div&gt;
        </content>
    </entry>
</feed>
"""


def create_test_feed() -> ElementTree.Element:
    """Create an Atom feed used by the collector tests."""

    return ElementTree.fromstring(
        ATOM_FEED
    )


class BCBCollectorTests(unittest.TestCase):
    """Test the Central Bank of Brazil news collector."""

    def setUp(self) -> None:
        # Step 1: create a fresh collector before each test.
        self.collector = BCBCollector()

    def test_collect_returns_latest_articles_first(self) -> None:
        # Step 2: replace the internet request with a local Atom feed.
        with patch.object(
            self.collector,
            "_get_feed",
            return_value=create_test_feed(),
        ) as mocked_get_feed:
            news_items = self.collector.collect(
                limit=2,
                year=2026,
            )

        # Step 3: verify the requested year and article limit.
        mocked_get_feed.assert_called_once_with(
            year=2026
        )

        self.assertEqual(
            len(news_items),
            2,
        )

        # Step 4: verify explicit newest-to-oldest ordering.
        self.assertEqual(
            [
                item.title
                for item in news_items
            ],
            [
                "Newest BCB regulatory article",
                "Middle BCB regulatory article",
            ],
        )

    def test_collect_normalizes_article_information(self) -> None:
        # Step 5: collect one normalized article from the local feed.
        with patch.object(
            self.collector,
            "_get_feed",
            return_value=create_test_feed(),
        ):
            news_item = self.collector.collect(
                limit=1,
                year=2026,
            )[0]

        # Step 6: verify the shared news structure.
        self.assertEqual(
            news_item.source,
            "BCB",
        )

        self.assertEqual(
            news_item.title,
            "Newest BCB regulatory article",
        )

        self.assertEqual(
            news_item.url,
            (
                "https://www.bcb.gov.br/"
                "detalhenoticia/3/noticia"
            ),
        )

        self.assertEqual(
            news_item.published_at,
            "2026-08-19T12:00:00-03:00",
        )

        self.assertEqual(
            news_item.summary,
            (
                "This is the summary of the newest "
                "regulatory article."
            ),
        )

        self.assertIn(
            "additional paragraph",
            news_item.body or "",
        )

    def test_collect_rejects_external_urls(self) -> None:
        # Step 7: collect every valid entry from the local feed.
        with patch.object(
            self.collector,
            "_get_feed",
            return_value=create_test_feed(),
        ):
            news_items = self.collector.collect(
                limit=10,
                year=2026,
            )

        # Step 8: verify that only official BCB URLs are accepted.
        self.assertEqual(
            len(news_items),
            3,
        )

        self.assertTrue(
            all(
                item.url.startswith(
                    "https://www.bcb.gov.br/"
                )
                for item in news_items
            )
        )

    def test_non_positive_limit_does_not_request_feed(self) -> None:
        # Step 9: monitor the feed request method.
        with patch.object(
            self.collector,
            "_get_feed",
        ) as mocked_get_feed:
            news_items = self.collector.collect(
                limit=0
            )

        # Step 10: verify the early return without internet access.
        self.assertEqual(
            news_items,
            [],
        )

        mocked_get_feed.assert_not_called()


# Run the tests only when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
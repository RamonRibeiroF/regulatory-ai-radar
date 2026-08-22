from __future__ import annotations

import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from regulatory_ai_radar.collectors.eba import EBACollector


class EBACollectorTests(unittest.TestCase):
    """Validate the EBA Digital Finance collector."""

    def setUp(self) -> None:
        self.collector = EBACollector()

    def _listing(self) -> BeautifulSoup:
        return BeautifulSoup(
            """
            <article class="teaser">
              <div class="teaser__metadata">1 February 2025</div>
              <h4 class="teaser__title">New digital finance report</h4>
              <div class="field--name-description">Recent EBA evidence.</div>
              <a href="/publications-and-media/press-releases/new-report">View press release</a>
            </article>
            <article class="teaser">
              <div class="teaser__metadata">14 October 2025</div>
              <h4 class="teaser__title">Newest digital finance report</h4>
              <div class="field--name-description">Newest EBA evidence.</div>
              <a href="/publications-and-media/press-releases/newest-report">View press release</a>
            </article>
            """,
            "html.parser",
        )

    def test_candidates_are_sorted_newest_first(self) -> None:
        # Passo 1: comprovar a ordenação decrescente por data.
        candidates = self.collector._extract_candidates(self._listing())
        self.assertEqual(
            [candidate.published_at for candidate in candidates],
            ["2025-10-14", "2025-02-01"],
        )

    def test_external_urls_are_rejected(self) -> None:
        # Passo 2: impedir que links externos entrem no coletor.
        self.assertIsNone(
            self.collector._normalize_url("https://example.com/report")
        )

    def test_collection_respects_limit(self) -> None:
        # Passo 3: limitar a saída e preservar a fonte normalizada.
        article = BeautifulSoup(
            "<article><p>Official paragraph with enough regulatory content.</p></article>",
            "html.parser",
        )
        with patch.object(
            self.collector,
            "_get_page",
            side_effect=[self._listing(), article],
        ):
            result = self.collector.collect(limit=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].source, "EBA")
        self.assertEqual(result[0].published_at, "2025-10-14")

    def test_non_positive_limit_avoids_requests(self) -> None:
        # Passo 4: não acessar a rede quando o limite for inválido.
        with patch.object(self.collector, "_get_page") as request:
            self.assertEqual(self.collector.collect(limit=0), [])
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()

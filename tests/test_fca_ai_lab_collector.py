from __future__ import annotations

import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from regulatory_ai_radar.collectors.fca_ai_lab import FCAAiLabCollector


class FCAAiLabCollectorTests(unittest.TestCase):
    """Validate the FCA artificial intelligence collector."""

    def setUp(self) -> None:
        self.collector = FCAAiLabCollector()

    def _search_page(self) -> BeautifulSoup:
        return BeautifulSoup(
            """
            <li class="search-item">
              <h3><a class="search-item__clickthrough" href="https://www.fca.org.uk/news/older-ai">Older AI report</a></h3>
              <div class="search-item__meta"><p class="meta-item type">News</p><p class="published-date">Published: 01/02/2026</p></div>
              <div class="search-item__body">Artificial intelligence governance.</div>
            </li>
            <li class="search-item">
              <h3><a class="search-item__clickthrough" href="https://www.fca.org.uk/news/newer-ai">Newer AI report</a></h3>
              <div class="search-item__meta"><p class="meta-item type">News</p><p class="published-date">Published: 10/07/2026</p></div>
              <div class="search-item__body">Machine learning supervision.</div>
            </li>
            <li class="search-item">
              <h3><a class="search-item__clickthrough" href="https://www.fca.org.uk/news/warnings/fake-ai">Fake AI firm</a></h3>
              <div class="search-item__meta"><p class="meta-item type">Warnings</p><p class="published-date">Published: 20/07/2026</p></div>
              <div class="search-item__body">Artificial intelligence warning.</div>
            </li>
            """,
            "html.parser",
        )

    def test_candidates_are_sorted_and_warnings_removed(self) -> None:
        # Passo 1: ordenar resultados e excluir alertas comerciais.
        candidates = self.collector._extract_candidates(
            [self._search_page()]
        )
        self.assertEqual(
            [candidate.title for candidate in candidates],
            ["Newer AI report", "Older AI report"],
        )

    def test_external_urls_are_rejected(self) -> None:
        # Passo 2: impedir que links externos entrem no coletor.
        self.assertIsNone(
            self.collector._normalize_url("https://example.com/ai")
        )

    def test_collection_respects_limit(self) -> None:
        # Passo 3: limitar a saída e preservar a fonte normalizada.
        article = BeautifulSoup(
            '<div role="main"><article><p>Official FCA paragraph with sufficient content.</p></article></div>',
            "html.parser",
        )
        with patch.object(
            self.collector,
            "_get_page",
            side_effect=[self._search_page(), article],
        ):
            result = self.collector.collect(limit=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].source, "FCA_AI_LAB")
        self.assertEqual(result[0].published_at, "2026-07-10")

    def test_non_positive_limit_avoids_requests(self) -> None:
        # Passo 4: não acessar a rede quando o limite for inválido.
        with patch.object(self.collector, "_get_page") as request:
            self.assertEqual(self.collector.collect(limit=0), [])
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()

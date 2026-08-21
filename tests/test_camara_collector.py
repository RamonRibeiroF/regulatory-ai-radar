from __future__ import annotations

import unittest
from unittest.mock import patch

from regulatory_ai_radar.collectors.camara import (
    SEARCH_TERMS,
    CamaraCollector,
)


class CamaraCollectorTests(unittest.TestCase):
    """Validate the Chamber of Deputies collector rules."""

    def setUp(self) -> None:
        # Step 1: create a fresh collector for every test.
        self.collector = CamaraCollector()

    def _build_proposition(
        self,
        proposition_id: int,
        publication_date: str,
        number: int,
        summary: str,
        proposition_type: str = "PL",
        year: int = 2026,
    ) -> dict[str, object]:
        """Create a local proposition fixture."""

        return {
            "id": proposition_id,
            "uri": (
                "https://dadosabertos.camara.leg.br/"
                f"api/v2/proposicoes/{proposition_id}"
            ),
            "siglaTipo": proposition_type,
            "codTipo": 139,
            "numero": number,
            "ano": year,
            "ementa": summary,
            "dataApresentacao": publication_date,
        }

    def test_latest_propositions_are_returned_first(
        self,
    ) -> None:
        # Step 2: provide propositions in an incorrect order.
        propositions = [
            self._build_proposition(
                proposition_id=100,
                publication_date="2026-06-01T10:00",
                number=100,
                summary="Older proposition.",
            ),
            self._build_proposition(
                proposition_id=300,
                publication_date="2026-08-01T10:00",
                number=300,
                summary="Newest proposition.",
            ),
            self._build_proposition(
                proposition_id=200,
                publication_date="2026-07-01T10:00",
                number=200,
                summary="Middle proposition.",
            ),
        ]

        with patch.object(
            self.collector,
            "_get_propositions",
            return_value=propositions,
        ):
            result = self.collector.collect(
                limit=2
            )

        # Step 3: confirm descending date ordering and the limit.
        self.assertEqual(
            len(result),
            2,
        )
        self.assertIn(
            "idProposicao=300",
            result[0].url,
        )
        self.assertIn(
            "idProposicao=200",
            result[1].url,
        )

    def test_proposition_is_normalized(
        self,
    ) -> None:
        proposition = self._build_proposition(
            proposition_id=4881,
            publication_date="2026-08-04T15:58",
            number=4881,
            summary=(
                "  Regulates artificial intelligence "
                "in consumer relations.  "
            ),
        )

        # Step 4: normalize one local API proposition.
        result = self.collector._normalize_proposition(
            proposition
        )

        self.assertIsNotNone(result)

        if result is None:
            self.fail(
                "A valid proposition was not normalized."
            )

        # Step 5: validate the shared NewsItem fields.
        self.assertEqual(
            result.source,
            "CAMARA",
        )
        self.assertEqual(
            result.title,
            (
                "PL 4881/2026: Regulates artificial "
                "intelligence in consumer relations."
            ),
        )
        self.assertEqual(
            result.published_at,
            "2026-08-04T15:58",
        )
        self.assertEqual(
            result.summary,
            (
                "Regulates artificial intelligence "
                "in consumer relations."
            ),
        )
        self.assertEqual(
            result.url,
            (
                "https://www.camara.leg.br/"
                "proposicoesWeb/fichadetramitacao"
                "?idProposicao=4881"
            ),
        )
        self.assertIsNone(
            result.body
        )

    def test_duplicate_search_results_are_removed(
        self,
    ) -> None:
        propositions = [
            self._build_proposition(
                proposition_id=500,
                publication_date="2026-08-10T09:00",
                number=500,
                summary="First unique proposition.",
            ),
            self._build_proposition(
                proposition_id=600,
                publication_date="2026-08-11T09:00",
                number=600,
                summary="Second unique proposition.",
            ),
        ]

        # Step 6: simulate the same results for every keyword.
        with patch.object(
            self.collector,
            "_get_propositions",
            return_value=propositions,
        ) as mocked_request:
            result = self.collector.collect(
                limit=5
            )

        # Step 7: confirm that repeated IDs appear only once.
        self.assertEqual(
            len(result),
            2,
        )
        self.assertEqual(
            mocked_request.call_count,
            len(SEARCH_TERMS),
        )

    def test_non_positive_limit_avoids_requests(
        self,
    ) -> None:
        # Step 8: confirm that an empty request uses no network call.
        with patch.object(
            self.collector,
            "_get_propositions",
        ) as mocked_request:
            result = self.collector.collect(
                limit=0
            )

        self.assertEqual(
            result,
            [],
        )
        mocked_request.assert_not_called()

    def test_invalid_lookback_period_is_rejected(
        self,
    ) -> None:
        # Step 9: reject an invalid collection period.
        with patch.object(
            self.collector,
            "_get_propositions",
        ) as mocked_request:
            with self.assertRaises(
                ValueError
            ):
                self.collector.collect(
                    limit=5,
                    lookback_days=0,
                )

        mocked_request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
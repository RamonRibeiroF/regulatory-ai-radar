import unittest

from regulatory_ai_radar.analysis import RelevanceAnalyzer


class RelevanceAnalyzerTests(unittest.TestCase):
    """Test the deterministic regulatory relevance rules."""

    def setUp(self) -> None:
        # Step 1: create a fresh analyzer before each test.
        self.analyzer = RelevanceAnalyzer()

    def test_relevant_title_returns_medium_score(self) -> None:
        # Step 2: analyze a title with three regulatory topics.
        result = self.analyzer.analyze(
            title=(
                "ANPD publica metodologia de testagem do "
                "Sandbox Regulatório em IA e Proteção de Dados"
            )
        )

        # Step 3: verify the exact and explainable result.
        self.assertEqual(
            result.score,
            42,
        )
        self.assertEqual(
            result.level,
            "medium",
        )
        self.assertTrue(
            result.is_relevant
        )
        self.assertEqual(
            result.matched_keywords,
            (
                "sandbox regulatório",
                "proteção de dados",
                "ia",
            ),
        )

    def test_unrelated_title_returns_low_score(self) -> None:
        # Step 4: analyze content without configured keywords.
        result = self.analyzer.analyze(
            title=(
                "Institution publishes its annual activity report"
            )
        )

        # Step 5: verify that unrelated content is not relevant.
        self.assertEqual(
            result.score,
            0,
        )
        self.assertEqual(
            result.level,
            "low",
        )
        self.assertFalse(
            result.is_relevant
        )
        self.assertEqual(
            result.matched_keywords,
            (),
        )

    def test_article_body_contributes_to_score(self) -> None:
        # Step 6: analyze a generic title with relevant body content.
        result = self.analyzer.analyze(
            title="ANPD promotes a new institutional event",
            body=(
                "The event discusses inteligência artificial "
                "and LGPD."
            ),
        )

        # Step 7: verify that relevant body content is considered.
        self.assertEqual(
            result.score,
            32,
        )
        self.assertEqual(
            result.level,
            "medium",
        )
        self.assertTrue(
            result.is_relevant
        )

    def test_matching_is_case_and_accent_insensitive(self) -> None:
        # Step 8: analyze an uppercase title without accents.
        result = self.analyzer.analyze(
            title="PROTECAO DE DADOS"
        )

        # Step 9: verify normalization and title bonus.
        self.assertEqual(
            result.score,
            15,
        )
        self.assertIn(
            "proteção de dados",
            result.matched_keywords,
        )

    def test_score_is_limited_to_one_hundred(self) -> None:
        # Step 10: analyze content containing many relevant topics.
        result = self.analyzer.analyze(
            title=(
                "Inteligência Artificial, AI Act, IA generativa, "
                "governança de IA, LGPD, proteção de dados, "
                "sandbox regulatório e risco de modelo"
            )
        )

        # Step 11: verify the maximum score and high relevance level.
        self.assertEqual(
            result.score,
            100,
        )
        self.assertEqual(
            result.level,
            "high",
        )
        self.assertTrue(
            result.is_relevant
        )


# Run the tests only when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
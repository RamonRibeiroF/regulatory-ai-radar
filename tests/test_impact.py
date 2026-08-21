from __future__ import annotations

import unittest

from regulatory_ai_radar.analysis.impact import (
    ClassificadorImpactoRegulatorio,
)


class TestesClassificadorImpacto(unittest.TestCase):
    """Valida dimensões, limites e explicação do impacto local."""

    def setUp(self) -> None:
        self.classificador = ClassificadorImpactoRegulatorio()

    def test_resultado_soma_as_quatro_dimensoes(self) -> None:
        resultado = self.classificador.classificar(
            titulo="AI regulation for financial institutions",
            resumo="New requirements begin enforcement.",
            categorias=("ai_governance",),
        )

        soma = (
            resultado.forca_regulatoria
            + resultado.aplicabilidade_financeira
            + resultado.governanca_tecnologica
            + resultado.urgencia_operacional
        )
        self.assertEqual(resultado.pontuacao_impacto, soma)
        self.assertLessEqual(resultado.pontuacao_impacto, 100)

    def test_dimensoes_respeitam_limites(self) -> None:
        resultado = self.classificador.classificar(
            titulo=(
                "Lei regulation resolution rules requirement enforcement "
                "financial institution central bank payment credit fraud "
                "virtual asset AML consumer"
            ),
            categorias=(
                "ai_regulation",
                "ai_governance",
                "data_protection",
            ),
        )

        self.assertEqual(resultado.forca_regulatoria, 30)
        self.assertEqual(resultado.aplicabilidade_financeira, 30)
        self.assertEqual(resultado.governanca_tecnologica, 25)
        self.assertLessEqual(resultado.urgencia_operacional, 15)

    def test_fronteiras_dos_niveis(self) -> None:
        casos = (
            (0, "baixo"),
            (19, "baixo"),
            (20, "moderado"),
            (39, "moderado"),
            (40, "alto"),
            (59, "alto"),
            (60, "muito_alto"),
            (79, "muito_alto"),
            (80, "critico"),
            (100, "critico"),
        )

        for pontuacao, nivel in casos:
            with self.subTest(pontuacao=pontuacao):
                self.assertEqual(
                    self.classificador._definir_nivel(pontuacao),
                    nivel,
                )

    def test_justificativa_expoe_as_parcelas(self) -> None:
        resultado = self.classificador.classificar(
            titulo="Consulta sobre proteção de dados",
            categorias=("data_protection",),
        )

        self.assertIn("força regulatória", resultado.justificativa)
        self.assertIn("aplicabilidade financeira", resultado.justificativa)
        self.assertIn("governança tecnológica", resultado.justificativa)
        self.assertIn("urgência operacional", resultado.justificativa)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from regulatory_ai_radar.analysis.local_classifier import (
    ClassificadorLocalDeterministico,
)


class TestesClassificadorLocal(unittest.TestCase):
    """Valida todas as fronteiras da escala local de estrelas."""

    def setUp(self) -> None:
        self.classificador = ClassificadorLocalDeterministico()

    def test_fronteiras_das_cinco_faixas(self) -> None:
        casos = (
            (0, 1), (19, 1), (20, 2), (39, 2), (40, 3),
            (59, 3), (60, 4), (79, 4), (80, 5), (100, 5),
        )

        for pontuacao, estrelas_esperadas in casos:
            with self.subTest(pontuacao=pontuacao):
                resultado = self.classificador.classificar(
                    pontuacao=pontuacao
                )
                self.assertEqual(
                    resultado.avaliacao_estrelas,
                    estrelas_esperadas,
                )
                self.assertEqual(
                    resultado.evidencia_percentual,
                    pontuacao,
                )

    def test_resultado_registra_evidencias_objetivas(self) -> None:
        resultado = self.classificador.classificar(
            pontuacao=45,
            palavras_chave=("ia", "governança"),
            categorias=("inteligência artificial",),
        )

        self.assertEqual(resultado.avaliacao_estrelas, 3)
        self.assertIn("45/100", resultado.justificativa)
        self.assertIn("2 palavra(s)-chave", resultado.justificativa)
        self.assertEqual(
            resultado.categorias,
            ("inteligência artificial",),
        )

    def test_rejeita_pontuacao_fora_da_escala(self) -> None:
        for pontuacao in (-1, 101):
            with self.subTest(pontuacao=pontuacao):
                with self.assertRaisesRegex(ValueError, "pontuacao"):
                    self.classificador.classificar(pontuacao=pontuacao)


if __name__ == "__main__":
    unittest.main()

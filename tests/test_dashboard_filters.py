from __future__ import annotations

import unittest
from datetime import date, datetime, timezone

from dashboard.app import filter_articles
from regulatory_ai_radar.database.dashboard_repository import DashboardArticle


class TestesFiltrosDashboard(unittest.TestCase):
    """Valida o filtro inclusivo por período de publicação."""

    @staticmethod
    def criar_artigo(
        identificador: int,
        data_publicacao: datetime | None,
    ) -> DashboardArticle:
        # Passo 1: cria um artigo determinístico para isolar o filtro de datas.
        return DashboardArticle(
            id=identificador,
            source="FONTE_TESTE",
            title=f"Notícia {identificador}",
            url=f"https://example.com/{identificador}",
            published_at=data_publicacao,
            summary="Resumo",
            score=50,
            level="medium",
            is_relevant=True,
            matched_keywords=(),
            local_rating=3,
            local_evidence=50,
            local_justification="Evidência local.",
            impact_score=40,
            impact_level="alto",
            impact_justification="Impacto local.",
        )

    def filtrar(
        self,
        artigos: list[DashboardArticle],
        data_inicial: date,
        data_final: date,
    ) -> list[DashboardArticle]:
        # Passo 2: mantém os demais filtros abertos para testar somente a data.
        return filter_articles(
            articles=artigos,
            selected_sources=["FONTE_TESTE"],
            selected_levels=["medium"],
            minimum_score=0,
            minimum_impact=0,
            data_inicial=data_inicial,
            data_final=data_final,
            relevant_only=False,
            search_query="",
        )

    def test_mantem_datas_nos_limites_inclusivos(self) -> None:
        artigos = [
            self.criar_artigo(
                1,
                datetime(2026, 8, 10, tzinfo=timezone.utc),
            ),
            self.criar_artigo(
                2,
                datetime(2026, 8, 20, tzinfo=timezone.utc),
            ),
        ]

        resultado = self.filtrar(
            artigos,
            date(2026, 8, 10),
            date(2026, 8, 20),
        )

        self.assertEqual([artigo.id for artigo in resultado], [2, 1])

    def test_remove_datas_fora_do_periodo_e_ausentes(self) -> None:
        artigos = [
            self.criar_artigo(
                1,
                datetime(2026, 8, 9, tzinfo=timezone.utc),
            ),
            self.criar_artigo(
                2,
                datetime(2026, 8, 15, tzinfo=timezone.utc),
            ),
            self.criar_artigo(3, None),
        ]

        resultado = self.filtrar(
            artigos,
            date(2026, 8, 10),
            date(2026, 8, 20),
        )

        self.assertEqual([artigo.id for artigo in resultado], [2])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from regulatory_ai_radar.database.base import Base
from regulatory_ai_radar.database.dashboard_repository import (
    DashboardRepository,
)
from regulatory_ai_radar.database.models import (
    ArticleFeedback,
    NewsArticle,
)


class RepositorioDashboardTestes(unittest.TestCase):
    """Testa os dados de feedback disponibilizados ao dashboard."""

    def setUp(self) -> None:
        # Passo 1: cria um banco SQLite isolado em memória.
        self.motor = create_engine(
            "sqlite://",
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.motor)

        fabrica_sessoes = sessionmaker(
            bind=self.motor,
            autoflush=False,
            expire_on_commit=False,
        )
        self.sessao: Session = fabrica_sessoes()
        self.repositorio = DashboardRepository(self.sessao)

    def tearDown(self) -> None:
        # Passo 2: libera todos os recursos isolados.
        self.sessao.close()
        Base.metadata.drop_all(bind=self.motor)
        self.motor.dispose()

    def criar_noticia(self, sufixo: str) -> NewsArticle:
        """Cria uma notícia determinística para a consulta do dashboard."""

        noticia = NewsArticle(
            source="FONTE_TESTE",
            title=f"Notícia regulatória {sufixo}",
            url=f"https://example.com/dashboard-{sufixo}",
            published_at=datetime(2026, 8, 21, tzinfo=timezone.utc),
            summary="Resumo regulatório.",
            body="Conteúdo regulatório.",
            collected_at=datetime(2026, 8, 21, tzinfo=timezone.utc),
        )
        self.sessao.add(noticia)
        self.sessao.commit()
        return noticia

    def test_retorna_estrelas_e_observacao_da_noticia_avaliada(self) -> None:
        # Passo 3: associa uma avaliação humana à notícia.
        noticia = self.criar_noticia("avaliada")
        self.sessao.add(
            ArticleFeedback(
                article_id=noticia.id,
                human_rating=5,
                notes="Prioridade regulatória elevada.",
            )
        )
        self.sessao.commit()

        artigos = self.repositorio.list_articles()

        self.assertEqual(len(artigos), 1)
        self.assertEqual(artigos[0].human_rating, 5)
        self.assertEqual(
            artigos[0].feedback_notes,
            "Prioridade regulatória elevada.",
        )

    def test_mantem_noticia_sem_avaliacao_na_consulta(self) -> None:
        # Passo 4: consulta uma notícia que ainda não recebeu feedback.
        self.criar_noticia("sem-avaliacao")

        artigos = self.repositorio.list_articles()

        self.assertEqual(len(artigos), 1)
        self.assertIsNone(artigos[0].human_rating)
        self.assertIsNone(artigos[0].feedback_notes)


if __name__ == "__main__":
    unittest.main()

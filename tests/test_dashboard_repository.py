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
    ClassificacaoLocalArtigo,
    ImpactoRegulatorioArtigo,
    NewsArticle,
)


class RepositorioDashboardTestes(unittest.TestCase):
    """Testa a classificação local disponibilizada ao dashboard."""

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

    def test_retorna_classificacao_local(self) -> None:
        # Passo 3: associa uma classificação local à notícia.
        noticia = self.criar_noticia("avaliada")
        self.sessao.add(
            ClassificacaoLocalArtigo(
                artigo_id=noticia.id,
                avaliacao_estrelas=5,
                confianca_percentual=70,
                justificativa="Pontuação determinística 70/100.",
                categorias=["inteligência artificial"],
                nome_modelo="classificador-local-deterministico",
                versao_criterios="1.0",
            )
        )
        self.sessao.commit()

        artigos = self.repositorio.list_articles()

        self.assertEqual(len(artigos), 1)
        self.assertEqual(artigos[0].local_rating, 5)
        self.assertEqual(artigos[0].local_evidence, 70)
        self.assertIn("70/100", artigos[0].local_justification)

    def test_mantem_noticia_sem_classificacao_na_consulta(self) -> None:
        # Passo 4: consulta uma notícia sem classificação local.
        self.criar_noticia("sem-avaliacao")

        artigos = self.repositorio.list_articles()

        self.assertEqual(len(artigos), 1)
        self.assertIsNone(artigos[0].local_rating)
        self.assertIsNone(artigos[0].local_evidence)

    def test_retorna_impacto_regulatorio(self) -> None:
        # Passo 5: associa um impacto local auditável à notícia.
        noticia = self.criar_noticia("com-impacto")
        self.sessao.add(
            ImpactoRegulatorioArtigo(
                artigo_id=noticia.id,
                pontuacao_impacto=64,
                nivel_impacto="muito_alto",
                forca_regulatoria=24,
                aplicabilidade_financeira=20,
                governanca_tecnologica=14,
                urgencia_operacional=6,
                evidencias=["forca_regulatoria: regulation"],
                justificativa="Impacto 64/100 (muito_alto).",
                nome_modelo="classificador-impacto-regulatorio-local",
                versao_criterios="1.0",
            )
        )
        self.sessao.commit()

        artigo = self.repositorio.list_articles()[0]

        self.assertEqual(artigo.impact_score, 64)
        self.assertEqual(artigo.impact_level, "muito_alto")
        self.assertIn("64/100", artigo.impact_justification)


if __name__ == "__main__":
    unittest.main()

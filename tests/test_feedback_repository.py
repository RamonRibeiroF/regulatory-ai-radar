from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from regulatory_ai_radar.database.base import Base
from regulatory_ai_radar.database.feedback_repository import (
    ArticleFeedbackRepository,
)
from regulatory_ai_radar.database.models import NewsArticle


class RepositorioFeedbackArtigoTestes(unittest.TestCase):
    """Testa o repositório de avaliações humanas sem alterar o banco real."""

    def setUp(self) -> None:
        # Passo 1: cria um SQLite isolado em memória para cada teste.
        self.motor = create_engine(
            "sqlite://",
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.motor)

        # Passo 2: abre uma sessão e cadastra uma notícia válida.
        fabrica_sessoes = sessionmaker(
            bind=self.motor,
            autoflush=False,
            expire_on_commit=False,
        )
        self.sessao: Session = fabrica_sessoes()
        self.repositorio = ArticleFeedbackRepository(self.sessao)

        noticia = NewsArticle(
            source="FONTE_TESTE",
            title="Regulação de inteligência artificial",
            url="https://example.com/noticia-feedback",
            published_at=datetime(2026, 8, 21, tzinfo=timezone.utc),
            summary="Resumo regulatório para teste.",
            body="Conteúdo regulatório para teste.",
            collected_at=datetime(2026, 8, 21, tzinfo=timezone.utc),
        )
        self.sessao.add(noticia)
        self.sessao.commit()
        self.id_noticia = noticia.id

    def tearDown(self) -> None:
        # Passo 3: libera integralmente os recursos isolados.
        self.sessao.close()
        Base.metadata.drop_all(bind=self.motor)
        self.motor.dispose()

    def test_salva_e_consulta_feedback(self) -> None:
        # Passo 4: cria a primeira avaliação humana da notícia.
        feedback_salvo = self.repositorio.save(
            article_id=self.id_noticia,
            human_rating=5,
            notes="Muito relevante para governança.",
        )
        feedback_consultado = self.repositorio.get_by_article_id(
            self.id_noticia
        )

        self.assertEqual(feedback_salvo.human_rating, 5)
        self.assertIsNotNone(feedback_consultado)
        self.assertEqual(feedback_consultado.human_rating, 5)
        self.assertEqual(
            feedback_consultado.notes,
            "Muito relevante para governança.",
        )

    def test_atualiza_feedback_sem_criar_duplicidade(self) -> None:
        # Passo 5: salva duas avaliações para a mesma notícia.
        feedback_inicial = self.repositorio.save(
            article_id=self.id_noticia,
            human_rating=2,
            notes="Avaliação inicial.",
        )
        feedback_atualizado = self.repositorio.save(
            article_id=self.id_noticia,
            human_rating=4,
            notes="Avaliação revisada.",
        )

        self.assertEqual(feedback_inicial.article_id, self.id_noticia)
        self.assertEqual(feedback_atualizado.human_rating, 4)
        self.assertEqual(feedback_atualizado.notes, "Avaliação revisada.")
        self.assertEqual(self.repositorio.count(), 1)

    def test_normaliza_observacao_opcional(self) -> None:
        # Passo 6: remove espaços repetidos e converte texto vazio em nulo.
        feedback_com_texto = self.repositorio.save(
            article_id=self.id_noticia,
            human_rating=3,
            notes="  Texto   com\n espaços repetidos.  ",
        )
        self.assertEqual(
            feedback_com_texto.notes,
            "Texto com espaços repetidos.",
        )

        feedback_sem_texto = self.repositorio.save(
            article_id=self.id_noticia,
            human_rating=3,
            notes="   ",
        )
        self.assertIsNone(feedback_sem_texto.notes)

    def test_rejeita_avaliacoes_fora_do_intervalo(self) -> None:
        # Passo 7: confirma os limites inferior e superior permitidos.
        for avaliacao_invalida in (0, 6):
            with self.subTest(avaliacao_invalida=avaliacao_invalida):
                with self.assertRaisesRegex(
                    ValueError,
                    "between 1 and 5",
                ):
                    self.repositorio.save(
                        article_id=self.id_noticia,
                        human_rating=avaliacao_invalida,
                    )

        self.assertEqual(self.repositorio.count(), 0)

    def test_conta_apenas_artigos_avaliados(self) -> None:
        # Passo 8: confirma zero antes e um depois da primeira avaliação.
        self.assertEqual(self.repositorio.count(), 0)

        self.repositorio.save(
            article_id=self.id_noticia,
            human_rating=1,
        )

        self.assertEqual(self.repositorio.count(), 1)


if __name__ == "__main__":
    unittest.main()

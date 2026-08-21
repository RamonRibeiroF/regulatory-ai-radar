from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from regulatory_ai_radar.analysis.local_classifier import (
    ClassificadorLocalDeterministico,
)
from regulatory_ai_radar.database.base import Base
from regulatory_ai_radar.database.local_classification_repository import (
    RepositorioClassificacaoLocal,
)
from regulatory_ai_radar.database.models import NewsArticle


class TestesRepositorioClassificacaoLocal(unittest.TestCase):
    """Valida persistência local sem duplicar a notícia."""

    def setUp(self) -> None:
        self.motor = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.motor)
        self.sessao = Session(self.motor)
        self.repositorio = RepositorioClassificacaoLocal(self.sessao)
        self.classificador = ClassificadorLocalDeterministico()

        noticia = NewsArticle(
            source="TESTE",
            title="Notícia regulatória",
            url="https://example.com/classificacao-local",
            collected_at=datetime.now(timezone.utc),
        )
        self.sessao.add(noticia)
        self.sessao.commit()
        self.artigo_id = noticia.id

    def tearDown(self) -> None:
        self.sessao.close()
        self.motor.dispose()

    def test_cria_e_atualiza_sem_duplicidade(self) -> None:
        primeiro, criado = self.repositorio.salvar(
            artigo_id=self.artigo_id,
            resultado=self.classificador.classificar(pontuacao=30),
            nome_modelo=self.classificador.nome_modelo,
            versao_criterios=self.classificador.versao_criterios,
        )
        segundo, criado_novamente = self.repositorio.salvar(
            artigo_id=self.artigo_id,
            resultado=self.classificador.classificar(pontuacao=60),
            nome_modelo=self.classificador.nome_modelo,
            versao_criterios=self.classificador.versao_criterios,
        )

        self.assertTrue(criado)
        self.assertFalse(criado_novamente)
        self.assertEqual(primeiro.avaliacao_estrelas, 3)
        self.assertEqual(segundo.avaliacao_estrelas, 5)
        self.assertEqual(self.repositorio.contar(), 1)


if __name__ == "__main__":
    unittest.main()

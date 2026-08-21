from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from regulatory_ai_radar.analysis.local_classifier import (
    ResultadoClassificacaoLocal,
)
from regulatory_ai_radar.database.models import ClassificacaoLocalArtigo


@dataclass(frozen=True, slots=True)
class RegistroClassificacaoLocal:
    """Representa a classificação local retornada pelo repositório."""

    artigo_id: int
    avaliacao_estrelas: int
    evidencia_percentual: int
    justificativa: str
    categorias: tuple[str, ...]
    nome_modelo: str
    versao_criterios: str
    criado_em: datetime
    atualizado_em: datetime


class RepositorioClassificacaoLocal:
    """Cria ou atualiza uma classificação local por notícia."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def obter_por_artigo(
        self,
        artigo_id: int,
    ) -> RegistroClassificacaoLocal | None:
        """Retorna a classificação local atual da notícia."""

        classificacao = self.sessao.scalar(
            select(ClassificacaoLocalArtigo).where(
                ClassificacaoLocalArtigo.artigo_id == artigo_id
            )
        )
        if classificacao is None:
            return None
        return self._converter(classificacao)

    def salvar(
        self,
        *,
        artigo_id: int,
        resultado: ResultadoClassificacaoLocal,
        nome_modelo: str,
        versao_criterios: str,
    ) -> tuple[RegistroClassificacaoLocal, bool]:
        """Persiste o resultado e informa se um registro foi criado."""

        nome_modelo = self._normalizar(nome_modelo, "nome_modelo")
        versao_criterios = self._normalizar(
            versao_criterios,
            "versao_criterios",
        )

        try:
            classificacao = self.sessao.scalar(
                select(ClassificacaoLocalArtigo).where(
                    ClassificacaoLocalArtigo.artigo_id == artigo_id
                )
            )
            criado = classificacao is None

            if classificacao is None:
                classificacao = ClassificacaoLocalArtigo(
                    artigo_id=artigo_id,
                    avaliacao_estrelas=resultado.avaliacao_estrelas,
                    confianca_percentual=resultado.evidencia_percentual,
                    justificativa=resultado.justificativa,
                    categorias=list(resultado.categorias),
                    nome_modelo=nome_modelo,
                    versao_criterios=versao_criterios,
                )
                self.sessao.add(classificacao)
            else:
                classificacao.avaliacao_estrelas = resultado.avaliacao_estrelas
                classificacao.confianca_percentual = (
                    resultado.evidencia_percentual
                )
                classificacao.justificativa = resultado.justificativa
                classificacao.categorias = list(resultado.categorias)
                classificacao.nome_modelo = nome_modelo
                classificacao.versao_criterios = versao_criterios
                classificacao.atualizado_em = datetime.now(timezone.utc)

            self.sessao.commit()
            self.sessao.refresh(classificacao)
        except Exception:
            self.sessao.rollback()
            raise

        return self._converter(classificacao), criado

    def contar(self) -> int:
        """Conta as classificações locais atuais."""

        return self.sessao.scalar(
            select(func.count(ClassificacaoLocalArtigo.id))
        ) or 0

    @staticmethod
    def _normalizar(valor: str, nome: str) -> str:
        valor = " ".join(valor.split())
        if not valor:
            raise ValueError(f"{nome} não pode ficar vazio.")
        return valor

    @staticmethod
    def _converter(
        classificacao: ClassificacaoLocalArtigo,
    ) -> RegistroClassificacaoLocal:
        return RegistroClassificacaoLocal(
            artigo_id=classificacao.artigo_id,
            avaliacao_estrelas=classificacao.avaliacao_estrelas,
            evidencia_percentual=classificacao.confianca_percentual,
            justificativa=classificacao.justificativa,
            categorias=tuple(classificacao.categorias),
            nome_modelo=classificacao.nome_modelo,
            versao_criterios=classificacao.versao_criterios,
            criado_em=classificacao.criado_em,
            atualizado_em=classificacao.atualizado_em,
        )

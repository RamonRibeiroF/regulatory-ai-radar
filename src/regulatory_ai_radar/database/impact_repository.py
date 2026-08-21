from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from regulatory_ai_radar.analysis.impact import ResultadoImpactoRegulatorio
from regulatory_ai_radar.database.models import ImpactoRegulatorioArtigo


class RepositorioImpactoRegulatorio:
    """Cria ou atualiza um impacto regulatório por notícia."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def salvar(
        self,
        *,
        artigo_id: int,
        resultado: ResultadoImpactoRegulatorio,
        nome_modelo: str,
        versao_criterios: str,
    ) -> bool:
        """Persiste o resultado e informa se o registro foi criado."""

        try:
            impacto = self.sessao.scalar(
                select(ImpactoRegulatorioArtigo).where(
                    ImpactoRegulatorioArtigo.artigo_id == artigo_id
                )
            )
            criado = impacto is None
            valores = {
                "pontuacao_impacto": resultado.pontuacao_impacto,
                "nivel_impacto": resultado.nivel_impacto,
                "forca_regulatoria": resultado.forca_regulatoria,
                "aplicabilidade_financeira": (
                    resultado.aplicabilidade_financeira
                ),
                "governanca_tecnologica": resultado.governanca_tecnologica,
                "urgencia_operacional": resultado.urgencia_operacional,
                "evidencias": list(resultado.evidencias),
                "justificativa": resultado.justificativa,
                "nome_modelo": nome_modelo,
                "versao_criterios": versao_criterios,
            }

            if impacto is None:
                impacto = ImpactoRegulatorioArtigo(
                    artigo_id=artigo_id,
                    **valores,
                )
                self.sessao.add(impacto)
            else:
                for campo, valor in valores.items():
                    setattr(impacto, campo, valor)
                impacto.atualizado_em = datetime.now(timezone.utc)

            self.sessao.commit()
        except Exception:
            self.sessao.rollback()
            raise

        return criado

    def contar(self) -> int:
        """Conta os impactos persistidos."""

        return self.sessao.scalar(
            select(func.count(ImpactoRegulatorioArtigo.id))
        ) or 0

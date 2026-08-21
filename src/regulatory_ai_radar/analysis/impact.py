from __future__ import annotations

from dataclasses import dataclass

from regulatory_ai_radar.analysis.relevance import (
    contains_keyword,
    normalize_text,
)


@dataclass(frozen=True, slots=True)
class ResultadoImpactoRegulatorio:
    """Representa uma avaliação local e auditável de impacto."""

    pontuacao_impacto: int
    nivel_impacto: str
    forca_regulatoria: int
    aplicabilidade_financeira: int
    governanca_tecnologica: int
    urgencia_operacional: int
    evidencias: tuple[str, ...]
    justificativa: str


class ClassificadorImpactoRegulatorio:
    """Avalia impacto regulatório sem rede, API ou aleatoriedade."""

    nome_modelo = "classificador-impacto-regulatorio-local"
    versao_criterios = "1.0"

    _regras_forca = (
        ("lei", 10),
        ("law", 10),
        ("regulamento", 10),
        ("regulation", 10),
        ("resolucao", 12),
        ("resolution", 12),
        ("regra", 8),
        ("rules", 8),
        ("requirement", 12),
        ("requisito", 12),
        ("obrigacao", 12),
        ("enforcement", 14),
        ("enforcing", 14),
        ("supervision", 10),
        ("supervisao", 10),
        ("consultation", 6),
        ("consulta", 6),
        ("report", 4),
        ("relatorio", 4),
    )
    _regras_financeiras = (
        ("financial institution", 18),
        ("instituicao financeira", 18),
        ("central bank", 12),
        ("banco central", 12),
        ("bank", 6),
        ("banco", 6),
        ("payment", 10),
        ("pagamento", 10),
        ("credit", 10),
        ("credito", 10),
        ("fraud", 10),
        ("fraude", 10),
        ("virtual asset", 12),
        ("ativo virtual", 12),
        ("aml", 12),
        ("money laundering", 12),
        ("lavagem de dinheiro", 12),
        ("consumer", 8),
        ("consumidor", 8),
    )
    _pesos_categorias = {
        "ai_regulation": 16,
        "ai_governance": 14,
        "model_risk": 14,
        "automated_decisions": 14,
        "data_protection": 12,
        "biometrics": 10,
        "algorithms": 8,
        "generative_ai": 8,
        "regulatory_innovation": 6,
        "artificial_intelligence": 4,
    }
    _regras_urgencia = (
        ("enforcement", 14),
        ("enforcing", 14),
        ("determina", 12),
        ("determines", 12),
        ("suspende", 12),
        ("suspend", 12),
        ("proibe", 12),
        ("prohibit", 12),
        ("effective", 10),
        ("entra em vigor", 10),
        ("deadline", 10),
        ("prazo", 10),
        ("mandatory", 10),
        ("obrigatorio", 10),
        ("begins", 6),
        ("begin", 6),
    )

    @staticmethod
    def _pontuar_regras(
        texto: str,
        regras: tuple[tuple[str, int], ...],
        limite: int,
        dimensao: str,
    ) -> tuple[int, tuple[str, ...]]:
        correspondencias = tuple(
            (termo, peso)
            for termo, peso in regras
            if contains_keyword(texto, termo)
        )
        pontos = min(limite, sum(peso for _, peso in correspondencias))
        evidencias = tuple(
            f"{dimensao}: {termo}"
            for termo, _ in correspondencias
        )
        return pontos, evidencias

    @staticmethod
    def _definir_nivel(pontuacao: int) -> str:
        if pontuacao >= 80:
            return "critico"
        if pontuacao >= 60:
            return "muito_alto"
        if pontuacao >= 40:
            return "alto"
        if pontuacao >= 20:
            return "moderado"
        return "baixo"

    def classificar(
        self,
        *,
        titulo: str,
        resumo: str | None = None,
        corpo: str | None = None,
        categorias: tuple[str, ...] = (),
    ) -> ResultadoImpactoRegulatorio:
        """Calcula as quatro dimensões e explica o resultado."""

        # Passo 1: reúne e normaliza apenas o conteúdo disponível.
        texto = normalize_text(
            " ".join(filter(None, (titulo, resumo, corpo)))
        )

        # Passo 2: limita cada dimensão à parcela definida da escala.
        forca, evidencias_forca = self._pontuar_regras(
            texto,
            self._regras_forca,
            30,
            "forca_regulatoria",
        )
        financeiro, evidencias_financeiras = self._pontuar_regras(
            texto,
            self._regras_financeiras,
            30,
            "aplicabilidade_financeira",
        )
        governanca = min(
            25,
            sum(
                self._pesos_categorias.get(categoria, 0)
                for categoria in categorias
            ),
        )
        evidencias_governanca = tuple(
            f"governanca_tecnologica: {categoria}"
            for categoria in categorias
            if categoria in self._pesos_categorias
        )
        urgencia, evidencias_urgencia = self._pontuar_regras(
            texto,
            self._regras_urgencia,
            15,
            "urgencia_operacional",
        )

        # Passo 3: soma as parcelas e registra sua composição.
        pontuacao = forca + financeiro + governanca + urgencia
        nivel = self._definir_nivel(pontuacao)
        evidencias = (
            evidencias_forca
            + evidencias_financeiras
            + evidencias_governanca
            + evidencias_urgencia
        )
        justificativa = (
            f"Impacto {pontuacao}/100 ({nivel}): força regulatória "
            f"{forca}/30, aplicabilidade financeira {financeiro}/30, "
            f"governança tecnológica {governanca}/25 e urgência "
            f"operacional {urgencia}/15."
        )

        return ResultadoImpactoRegulatorio(
            pontuacao_impacto=pontuacao,
            nivel_impacto=nivel,
            forca_regulatoria=forca,
            aplicabilidade_financeira=financeiro,
            governanca_tecnologica=governanca,
            urgencia_operacional=urgencia,
            evidencias=evidencias,
            justificativa=justificativa,
        )

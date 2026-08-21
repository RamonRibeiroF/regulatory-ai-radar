from __future__ import annotations

from sqlalchemy import select

from regulatory_ai_radar.analysis.local_classifier import (
    ClassificadorLocalDeterministico,
)
from regulatory_ai_radar.database.local_classification_repository import (
    RepositorioClassificacaoLocal,
)
from regulatory_ai_radar.database.models import ArticleAnalysis
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


def main() -> None:
    """Recalcula e persiste as estrelas de todas as análises."""

    # Passo 1: garante que a tabela de classificação esteja disponível.
    initialize_database()

    with SessionFactory() as sessao:
        analises = list(
            sessao.scalars(
                select(ArticleAnalysis).order_by(ArticleAnalysis.article_id)
            ).all()
        )
        classificador = ClassificadorLocalDeterministico()
        repositorio = RepositorioClassificacaoLocal(sessao)
        criadas = 0
        atualizadas = 0

        # Passo 2: converte cada pontuação existente em estrelas auditáveis.
        for analise in analises:
            resultado = classificador.classificar(
                pontuacao=analise.score,
                palavras_chave=tuple(analise.matched_keywords),
                categorias=tuple(analise.matched_categories),
            )
            _, criada = repositorio.salvar(
                artigo_id=analise.article_id,
                resultado=resultado,
                nome_modelo=classificador.nome_modelo,
                versao_criterios=classificador.versao_criterios,
            )
            criadas += int(criada)
            atualizadas += int(not criada)

        # Passo 3: apresenta somente contagens obtidas do SQLite real.
        print("REGULATORY AI RADAR")
        print("Local classification summary:")
        print(f"- Analyzed records: {len(analises)}")
        print(f"- Classifications created: {criadas}")
        print(f"- Classifications updated: {atualizadas}")
        print(f"- Total stored: {repositorio.contar()}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from sqlalchemy import select

from regulatory_ai_radar.analysis.impact import (
    ClassificadorImpactoRegulatorio,
)
from regulatory_ai_radar.database.impact_repository import (
    RepositorioImpactoRegulatorio,
)
from regulatory_ai_radar.database.models import ArticleAnalysis, NewsArticle
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


def main() -> None:
    """Recalcula e persiste o impacto de todas as notícias analisadas."""

    # Passo 1: cria somente a tabela ausente, preservando os dados atuais.
    initialize_database()

    with SessionFactory() as sessao:
        registros = sessao.execute(
            select(NewsArticle, ArticleAnalysis)
            .join(ArticleAnalysis, ArticleAnalysis.article_id == NewsArticle.id)
            .order_by(NewsArticle.id)
        ).all()
        classificador = ClassificadorImpactoRegulatorio()
        repositorio = RepositorioImpactoRegulatorio(sessao)
        criados = 0
        atualizados = 0

        # Passo 2: classifica o impacto com conteúdo e categorias existentes.
        for artigo, analise in registros:
            resultado = classificador.classificar(
                titulo=artigo.title,
                resumo=artigo.summary,
                corpo=artigo.body,
                categorias=tuple(analise.matched_categories),
            )
            criado = repositorio.salvar(
                artigo_id=artigo.id,
                resultado=resultado,
                nome_modelo=classificador.nome_modelo,
                versao_criterios=classificador.versao_criterios,
            )
            criados += int(criado)
            atualizados += int(not criado)

        # Passo 3: exibe apenas contagens lidas da execução real.
        print("REGULATORY AI RADAR")
        print("Impact classification summary:")
        print(f"- Analyzed records: {len(registros)}")
        print(f"- Impacts created: {criados}")
        print(f"- Impacts updated: {atualizados}")
        print(f"- Total stored: {repositorio.contar()}")


if __name__ == "__main__":
    main()

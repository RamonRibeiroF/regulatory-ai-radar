from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from regulatory_ai_radar.database.models import (
    ArticleAnalysis,
    ClassificacaoLocalArtigo,
    ImpactoRegulatorioArtigo,
    NewsArticle,
    PipelineRun,
    PipelineSourceRun,
)


@dataclass(frozen=True, slots=True)
class DashboardArticle:
    """Represent article data prepared for the dashboard."""

    id: int
    source: str
    title: str
    url: str
    published_at: datetime | None
    summary: str | None
    score: int | None
    level: str
    is_relevant: bool
    matched_keywords: tuple[str, ...]
    local_rating: int | None
    local_evidence: int | None
    local_justification: str | None
    impact_score: int | None
    impact_level: str
    impact_justification: str | None


@dataclass(frozen=True, slots=True)
class DashboardPipelineRun:
    """Represent the latest complete pipeline execution."""

    id: int
    status: str
    started_at: datetime
    finished_at: datetime | None
    total_collected: int
    total_inserted: int
    total_skipped: int
    total_analyzed: int
    error_count: int


@dataclass(frozen=True, slots=True)
class DashboardSourceRun:
    """Represent the latest pipeline result for one source."""

    source: str
    status: str
    finished_at: datetime
    duration_seconds: float
    collected_count: int
    inserted_count: int
    skipped_count: int
    error_message: str | None


class DashboardRepository:
    """Provide read-only data for the dashboard."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def list_articles(self) -> list[DashboardArticle]:
        """Return articles and their current relevance analysis."""

        # Passo 1: combina notícias, análises e classificações locais.
        statement = (
            select(
                NewsArticle,
                ArticleAnalysis,
                ClassificacaoLocalArtigo,
                ImpactoRegulatorioArtigo,
            )
            .outerjoin(
                ArticleAnalysis,
                ArticleAnalysis.article_id
                == NewsArticle.id,
            )
            .outerjoin(
                ClassificacaoLocalArtigo,
                ClassificacaoLocalArtigo.artigo_id
                == NewsArticle.id,
            )
            .outerjoin(
                ImpactoRegulatorioArtigo,
                ImpactoRegulatorioArtigo.artigo_id == NewsArticle.id,
            )
            .order_by(
                NewsArticle.id
            )
        )

        rows = self.session.execute(
            statement
        ).all()

        dashboard_articles: list[DashboardArticle] = []

        # Passo 2: converte as linhas em dados estáveis do dashboard.
        for article, analysis, classificacao_local, impacto in rows:
            dashboard_article = DashboardArticle(
                id=article.id,
                source=article.source,
                title=article.title,
                url=article.url,
                published_at=article.published_at,
                summary=article.summary,
                score=(
                    analysis.score
                    if analysis
                    else None
                ),
                level=(
                    analysis.level
                    if analysis
                    else "not_analyzed"
                ),
                is_relevant=(
                    analysis.is_relevant
                    if analysis
                    else False
                ),
                matched_keywords=(
                    tuple(
                        analysis.matched_keywords
                    )
                    if analysis
                    else ()
                ),
                local_rating=(
                    classificacao_local.avaliacao_estrelas
                    if classificacao_local
                    else None
                ),
                local_evidence=(
                    classificacao_local.confianca_percentual
                    if classificacao_local
                    else None
                ),
                local_justification=(
                    classificacao_local.justificativa
                    if classificacao_local
                    else None
                ),
                impact_score=(
                    impacto.pontuacao_impacto
                    if impacto
                    else None
                ),
                impact_level=(
                    impacto.nivel_impacto
                    if impacto
                    else "not_analyzed"
                ),
                impact_justification=(
                    impacto.justificativa
                    if impacto
                    else None
                ),
            )

            dashboard_articles.append(
                dashboard_article
            )

        # Passo 3: retorna os dados sem expor objetos do SQLAlchemy.
        return dashboard_articles

    def get_latest_pipeline_run(
        self,
    ) -> DashboardPipelineRun | None:
        """Return the most recent complete pipeline execution."""

        # Step 4: locate the latest main pipeline record.
        pipeline_run = self.session.scalar(
            select(PipelineRun)
            .order_by(
                PipelineRun.id.desc()
            )
            .limit(1)
        )

        if pipeline_run is None:
            return None

        # Step 5: convert the ORM record into dashboard data.
        return DashboardPipelineRun(
            id=pipeline_run.id,
            status=pipeline_run.status,
            started_at=pipeline_run.started_at,
            finished_at=pipeline_run.finished_at,
            total_collected=pipeline_run.total_collected,
            total_inserted=pipeline_run.total_inserted,
            total_skipped=pipeline_run.total_skipped,
            total_analyzed=pipeline_run.total_analyzed,
            error_count=pipeline_run.error_count,
        )

    def list_latest_source_runs(
        self,
    ) -> list[DashboardSourceRun]:
        """Return the latest execution result for every source."""

        # Step 6: identify the newest record for each source.
        latest_source_ids = (
            select(
                PipelineSourceRun.source,
                func.max(
                    PipelineSourceRun.id
                ).label("latest_id"),
            )
            .group_by(
                PipelineSourceRun.source
            )
            .subquery()
        )

        # Step 7: retrieve the complete latest source records.
        statement = (
            select(PipelineSourceRun)
            .join(
                latest_source_ids,
                PipelineSourceRun.id
                == latest_source_ids.c.latest_id,
            )
            .order_by(
                PipelineSourceRun.source
            )
        )

        source_runs = self.session.scalars(
            statement
        ).all()

        # Step 8: return source data without exposing ORM objects.
        return [
            DashboardSourceRun(
                source=source_run.source,
                status=source_run.status,
                finished_at=source_run.finished_at,
                duration_seconds=source_run.duration_seconds,
                collected_count=source_run.collected_count,
                inserted_count=source_run.inserted_count,
                skipped_count=source_run.skipped_count,
                error_message=source_run.error_message,
            )
            for source_run in source_runs
        ]

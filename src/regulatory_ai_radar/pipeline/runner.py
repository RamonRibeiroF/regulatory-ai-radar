from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from regulatory_ai_radar.analysis import RelevanceAnalyzer
from regulatory_ai_radar.analysis.local_classifier import (
    ClassificadorLocalDeterministico,
)
from regulatory_ai_radar.collectors.anpd import ANPDCollector
from regulatory_ai_radar.collectors.bcb import BCBCollector
from regulatory_ai_radar.collectors.bis import BISCollector
from regulatory_ai_radar.collectors.camara import CamaraCollector
from regulatory_ai_radar.collectors.eu_ai_office import (
    EUAIOfficeCollector,
)
from regulatory_ai_radar.collectors.fsb import FSBCollector
from regulatory_ai_radar.collectors.iapp import IAPPCollector
from regulatory_ai_radar.collectors.oecd_ai import OECDAICollector
from regulatory_ai_radar.database.analysis_repository import (
    ArticleAnalysisRepository,
)
from regulatory_ai_radar.database.models import (
    ArticleAnalysis,
    ClassificacaoLocalArtigo,
    NewsArticle,
)
from regulatory_ai_radar.database.local_classification_repository import (
    RepositorioClassificacaoLocal,
)
from regulatory_ai_radar.database.pipeline_repository import (
    PipelineRepository,
    PipelineTotals,
)
from regulatory_ai_radar.database.repository import NewsRepository
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)
from regulatory_ai_radar.entities import NewsItem


@dataclass(frozen=True, slots=True)
class CollectorDefinition:
    """Define one regulatory source executed by the pipeline."""

    source: str
    collect: Callable[[int], list[NewsItem]]


@dataclass(frozen=True, slots=True)
class PipelineExecutionResult:
    """Represent the final result returned by the pipeline."""

    pipeline_run_id: int
    status: str
    successful_sources: int
    failed_sources: int
    totals: PipelineTotals


# Step 1: register all official regulatory data sources.
DEFAULT_COLLECTORS: tuple[CollectorDefinition, ...] = (
    CollectorDefinition(
        source="ANPD",
        collect=lambda limit: ANPDCollector().collect(
            limit=limit,
        ),
    ),
    CollectorDefinition(
        source="BCB",
        collect=lambda limit: BCBCollector().collect(
            limit=limit,
        ),
    ),
    CollectorDefinition(
        source="CAMARA",
        collect=lambda limit: CamaraCollector().collect(
            limit=limit,
            lookback_days=90,
        ),
    ),
    CollectorDefinition(
        source="EU_AI_OFFICE",
        collect=lambda limit: EUAIOfficeCollector().collect(
            limit=limit,
        ),
    ),
    CollectorDefinition(
        source="FSB",
        collect=lambda limit: FSBCollector().collect(
            limit=limit,
        ),
    ),
    CollectorDefinition(
        source="BIS",
        collect=lambda limit: BISCollector().collect(
            limit=limit,
        ),
    ),
    CollectorDefinition(
        source="IAPP",
        collect=lambda limit: IAPPCollector().collect(
            limit=limit,
        ),
    ),
    CollectorDefinition(
        source="OECD_AI",
        collect=lambda limit: OECDAICollector().collect(
            limit=limit,
        ),
    ),
)


class PipelineRunner:
    """Coordinate collection, persistence, analysis, and monitoring."""

    def __init__(
        self,
        collectors: Sequence[CollectorDefinition] = DEFAULT_COLLECTORS,
        session_factory: Callable[[], Session] = SessionFactory,
        database_initializer: Callable[[], None] = initialize_database,
    ) -> None:
        # Step 2: store configurable pipeline dependencies.
        self.collectors = tuple(collectors)
        self.session_factory = session_factory
        self.database_initializer = database_initializer

    def run(
        self,
        *,
        limit_per_source: int = 5,
    ) -> PipelineExecutionResult:
        """Execute every configured source and analyze new records."""

        if limit_per_source < 1:
            raise ValueError(
                "limit_per_source must be greater than zero."
            )

        # Step 3: ensure that all database tables are available.
        self.database_initializer()

        # Step 4: create the main pipeline execution record.
        with self.session_factory() as session:
            pipeline_repository = PipelineRepository(session)
            pipeline_run = pipeline_repository.start_pipeline()
            pipeline_run_id = pipeline_run.id

        total_collected = 0
        total_inserted = 0
        total_skipped = 0
        total_analyzed = 0
        analyses_created = 0
        analyses_updated = 0
        error_messages: list[str] = []
        failed_sources = 0

        # Step 5: execute every source independently.
        for collector_definition in self.collectors:
            source_started_at = datetime.now(timezone.utc)
            source_status = "success"
            source_error: str | None = None
            collected_count = 0
            inserted_count = 0
            skipped_count = 0

            try:
                # Step 6: collect the most recent source records.
                news_items = collector_definition.collect(
                    limit_per_source
                )
                collected_count = len(news_items)

                # Step 7: persist new records and skip duplicate URLs.
                with self.session_factory() as session:
                    news_repository = NewsRepository(session)
                    save_result = news_repository.save_many(
                        news_items
                    )

                inserted_count = save_result.inserted
                skipped_count = save_result.skipped

                total_collected += collected_count
                total_inserted += inserted_count
                total_skipped += skipped_count

            except Exception as exception:
                # Step 8: isolate a source failure from the other sources.
                source_status = "failed"
                source_error = str(exception)
                failed_sources += 1
                error_messages.append(
                    f"{collector_definition.source}: "
                    f"{source_error}"
                )

            source_finished_at = datetime.now(timezone.utc)

            # Step 9: record the individual source execution.
            with self.session_factory() as session:
                pipeline_repository = PipelineRepository(session)
                pipeline_repository.record_source_run(
                    pipeline_run_id=pipeline_run_id,
                    source=collector_definition.source,
                    status=source_status,
                    started_at=source_started_at,
                    finished_at=source_finished_at,
                    collected_count=collected_count,
                    inserted_count=inserted_count,
                    skipped_count=skipped_count,
                    error_message=source_error,
                )

        # Step 10: locate articles that do not have an analysis yet.
        try:
            with self.session_factory() as session:
                statement = (
                    select(NewsArticle)
                    .outerjoin(
                        ArticleAnalysis,
                        ArticleAnalysis.article_id
                        == NewsArticle.id,
                    )
                    .where(
                        ArticleAnalysis.id.is_(None)
                    )
                    .order_by(NewsArticle.id)
                )

                pending_articles = list(
                    session.scalars(statement).all()
                )

                # Step 11: calculate relevance for every new article.
                analyzer = RelevanceAnalyzer()
                analysis_items = []

                for article in pending_articles:
                    relevance_result = analyzer.analyze(
                        title=article.title,
                        summary=article.summary,
                        body=article.body,
                    )

                    analysis_items.append(
                        (
                            article.id,
                            relevance_result,
                        )
                    )

                # Step 12: persist the newly calculated analyses.
                analysis_repository = ArticleAnalysisRepository(
                    session
                )
                analysis_save_result = (
                    analysis_repository.save_many(
                        analysis_items
                    )
                )

                total_analyzed = len(pending_articles)
                analyses_created = (
                    analysis_save_result.created
                )
                analyses_updated = (
                    analysis_save_result.updated
                )

        except Exception as exception:
            # Step 13: preserve collection results if analysis fails.
            error_messages.append(
                f"ANALYSIS: {exception}"
            )

        # Passo 14: classifica localmente análises ainda sem estrelas.
        try:
            with self.session_factory() as session:
                classificacoes_pendentes = session.execute(
                    select(ArticleAnalysis)
                    .outerjoin(
                        ClassificacaoLocalArtigo,
                        ClassificacaoLocalArtigo.artigo_id
                        == ArticleAnalysis.article_id,
                    )
                    .where(ClassificacaoLocalArtigo.id.is_(None))
                    .order_by(ArticleAnalysis.article_id)
                ).scalars().all()

                classificador_local = ClassificadorLocalDeterministico()
                repositorio_local = RepositorioClassificacaoLocal(session)

                for analise in classificacoes_pendentes:
                    resultado_local = classificador_local.classificar(
                        pontuacao=analise.score,
                        palavras_chave=tuple(analise.matched_keywords),
                        categorias=tuple(analise.matched_categories),
                    )
                    repositorio_local.salvar(
                        artigo_id=analise.article_id,
                        resultado=resultado_local,
                        nome_modelo=classificador_local.nome_modelo,
                        versao_criterios=(
                            classificador_local.versao_criterios
                        ),
                    )

        except Exception as exception:
            error_messages.append(f"LOCAL_CLASSIFICATION: {exception}")

        error_count = len(error_messages)
        successful_sources = (
            len(self.collectors) - failed_sources
        )

        # Step 15: determine the final pipeline status.
        if error_count == 0:
            pipeline_status = "success"
        elif successful_sources == 0:
            pipeline_status = "failed"
        else:
            pipeline_status = "partial"

        totals = PipelineTotals(
            total_collected=total_collected,
            total_inserted=total_inserted,
            total_skipped=total_skipped,
            total_analyzed=total_analyzed,
            analyses_created=analyses_created,
            analyses_updated=analyses_updated,
            error_count=error_count,
        )

        combined_error_message = (
            "\n".join(error_messages)
            if error_messages
            else None
        )

        # Step 16: finish and persist the main pipeline execution.
        with self.session_factory() as session:
            pipeline_repository = PipelineRepository(session)
            pipeline_repository.finish_pipeline(
                pipeline_run_id=pipeline_run_id,
                status=pipeline_status,
                totals=totals,
                error_message=combined_error_message,
            )

        # Step 17: return a structured execution summary.
        return PipelineExecutionResult(
            pipeline_run_id=pipeline_run_id,
            status=pipeline_status,
            successful_sources=successful_sources,
            failed_sources=failed_sources,
            totals=totals,
        )

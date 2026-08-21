from __future__ import annotations

import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from regulatory_ai_radar.database.base import Base
from regulatory_ai_radar.database.models import (
    ArticleAnalysis,
    PipelineRun,
    PipelineSourceRun,
)
from regulatory_ai_radar.entities import NewsItem
from regulatory_ai_radar.pipeline import (
    CollectorDefinition,
    PipelineRunner,
)


class PipelineRunnerTests(unittest.TestCase):
    """Test the automated pipeline without external network requests."""

    def setUp(self) -> None:
        # Step 1: create an isolated in-memory SQLite database.
        self.engine = create_engine(
            "sqlite://",
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
        )

        # Step 2: create every project table in the test database.
        Base.metadata.create_all(
            bind=self.engine,
        )

        # Step 3: configure isolated sessions for each test.
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def tearDown(self) -> None:
        # Step 4: release the isolated database resources.
        Base.metadata.drop_all(
            bind=self.engine,
        )
        self.engine.dispose()

    @staticmethod
    def make_news_item(
        *,
        source: str = "TEST_SOURCE",
        url: str = "https://example.com/article-1",
    ) -> NewsItem:
        """Create a normalized article for pipeline tests."""

        # Step 5: return a deterministic regulatory article.
        return NewsItem(
            source=source,
            title=(
                "Artificial intelligence governance "
                "and data protection"
            ),
            url=url,
            published_at="2026-08-21T12:00:00+00:00",
            summary=(
                "New regulatory requirements for responsible AI."
            ),
            body=(
                "The publication discusses AI governance, "
                "privacy, and data protection."
            ),
            collected_at="2026-08-21T12:30:00+00:00",
        )

    def create_runner(
        self,
        collectors: tuple[CollectorDefinition, ...],
    ) -> PipelineRunner:
        """Create a pipeline connected to the isolated database."""

        # Step 6: inject simulated collectors and test sessions.
        return PipelineRunner(
            collectors=collectors,
            session_factory=self.session_factory,
            database_initializer=lambda: None,
        )

    def test_pipeline_collects_persists_and_analyzes(self) -> None:
        # Step 7: configure one successful simulated collector.
        collector = CollectorDefinition(
            source="TEST_SOURCE",
            collect=lambda limit: [
                self.make_news_item()
            ][:limit],
        )

        runner = self.create_runner(
            (
                collector,
            )
        )

        # Step 8: execute the complete isolated pipeline.
        result = runner.run(
            limit_per_source=5,
        )

        # Step 9: verify the returned execution totals.
        self.assertEqual(
            result.status,
            "success",
        )
        self.assertEqual(
            result.successful_sources,
            1,
        )
        self.assertEqual(
            result.failed_sources,
            0,
        )
        self.assertEqual(
            result.totals.total_collected,
            1,
        )
        self.assertEqual(
            result.totals.total_inserted,
            1,
        )
        self.assertEqual(
            result.totals.total_analyzed,
            1,
        )
        self.assertEqual(
            result.totals.analyses_created,
            1,
        )

        # Step 10: verify the persisted execution records.
        with self.session_factory() as session:
            pipeline_run = session.scalar(
                select(PipelineRun)
            )
            source_run = session.scalar(
                select(PipelineSourceRun)
            )
            analysis = session.scalar(
                select(ArticleAnalysis)
            )

        self.assertIsNotNone(pipeline_run)
        self.assertEqual(
            pipeline_run.status,
            "success",
        )
        self.assertIsNotNone(source_run)
        self.assertEqual(
            source_run.status,
            "success",
        )
        self.assertIsNotNone(analysis)

    def test_pipeline_skips_duplicate_articles(self) -> None:
        # Step 11: configure a collector that always returns one URL.
        collector = CollectorDefinition(
            source="TEST_SOURCE",
            collect=lambda limit: [
                self.make_news_item()
            ][:limit],
        )

        runner = self.create_runner(
            (
                collector,
            )
        )

        # Step 12: execute the same pipeline twice.
        first_result = runner.run(
            limit_per_source=5,
        )
        second_result = runner.run(
            limit_per_source=5,
        )

        # Step 13: verify duplicate prevention and analysis reuse.
        self.assertEqual(
            first_result.totals.total_inserted,
            1,
        )
        self.assertEqual(
            second_result.totals.total_inserted,
            0,
        )
        self.assertEqual(
            second_result.totals.total_skipped,
            1,
        )
        self.assertEqual(
            second_result.totals.total_analyzed,
            0,
        )

    def test_pipeline_isolates_source_failure(self) -> None:
        # Step 14: define one collector that raises an error.
        def failing_collector(
            limit: int,
        ) -> list[NewsItem]:
            del limit
            raise RuntimeError(
                "Simulated source failure"
            )

        successful_collector = CollectorDefinition(
            source="SUCCESS_SOURCE",
            collect=lambda limit: [
                self.make_news_item(
                    source="SUCCESS_SOURCE",
                )
            ][:limit],
        )

        failed_collector = CollectorDefinition(
            source="FAILED_SOURCE",
            collect=failing_collector,
        )

        runner = self.create_runner(
            (
                successful_collector,
                failed_collector,
            )
        )

        # Step 15: execute both simulated sources.
        result = runner.run(
            limit_per_source=5,
        )

        # Step 16: verify that one failure does not stop the pipeline.
        self.assertEqual(
            result.status,
            "partial",
        )
        self.assertEqual(
            result.successful_sources,
            1,
        )
        self.assertEqual(
            result.failed_sources,
            1,
        )
        self.assertEqual(
            result.totals.total_inserted,
            1,
        )
        self.assertEqual(
            result.totals.error_count,
            1,
        )

        # Step 17: verify both source statuses in the database.
        with self.session_factory() as session:
            source_runs = session.scalars(
                select(PipelineSourceRun).order_by(
                    PipelineSourceRun.id
                )
            ).all()

        self.assertEqual(
            len(source_runs),
            2,
        )
        self.assertEqual(
            source_runs[0].status,
            "success",
        )
        self.assertEqual(
            source_runs[1].status,
            "failed",
        )
        self.assertIn(
            "Simulated source failure",
            source_runs[1].error_message,
        )


# Run the tests only when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
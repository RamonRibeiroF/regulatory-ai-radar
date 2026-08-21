from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from regulatory_ai_radar.database.models import (
    PipelineRun,
    PipelineSourceRun,
)


@dataclass(frozen=True, slots=True)
class PipelineTotals:
    """Represent the final counters of a pipeline execution."""

    total_collected: int
    total_inserted: int
    total_skipped: int
    total_analyzed: int
    analyses_created: int
    analyses_updated: int
    error_count: int


class PipelineRepository:
    """Provide database operations for pipeline monitoring."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        # Step 1: store the active database session.
        self.session = session

    def start_pipeline(self) -> PipelineRun:
        """Create a new pipeline execution with running status."""

        try:
            # Step 2: create the main pipeline execution record.
            pipeline_run = PipelineRun(
                status="running",
            )

            self.session.add(pipeline_run)
            self.session.commit()
            self.session.refresh(pipeline_run)

        except Exception:
            # Step 3: undo the transaction if it cannot be saved.
            self.session.rollback()
            raise

        return pipeline_run

    def record_source_run(
        self,
        *,
        pipeline_run_id: int,
        source: str,
        status: str,
        started_at: datetime,
        finished_at: datetime,
        collected_count: int = 0,
        inserted_count: int = 0,
        skipped_count: int = 0,
        error_message: str | None = None,
    ) -> PipelineSourceRun:
        """Store the execution result of one regulatory source."""

        # Step 4: calculate how long the source execution took.
        duration_seconds = max(
            (finished_at - started_at).total_seconds(),
            0.0,
        )

        try:
            # Step 5: create the individual source execution record.
            source_run = PipelineSourceRun(
                pipeline_run_id=pipeline_run_id,
                source=source,
                status=status,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration_seconds,
                collected_count=collected_count,
                inserted_count=inserted_count,
                skipped_count=skipped_count,
                error_message=error_message,
            )

            self.session.add(source_run)
            self.session.commit()
            self.session.refresh(source_run)

        except Exception:
            # Step 6: undo the transaction if the source result fails.
            self.session.rollback()
            raise

        return source_run

    def finish_pipeline(
        self,
        *,
        pipeline_run_id: int,
        status: str,
        totals: PipelineTotals,
        error_message: str | None = None,
    ) -> PipelineRun:
        """Finish a pipeline execution and store its final totals."""

        try:
            # Step 7: locate the pipeline execution being completed.
            pipeline_run = self.session.get(
                PipelineRun,
                pipeline_run_id,
            )

            if pipeline_run is None:
                raise ValueError(
                    f"Pipeline run {pipeline_run_id} was not found."
                )

            # Step 8: update the execution status and final timestamp.
            pipeline_run.status = status
            pipeline_run.finished_at = datetime.now(timezone.utc)

            # Step 9: store collection and analysis totals.
            pipeline_run.total_collected = totals.total_collected
            pipeline_run.total_inserted = totals.total_inserted
            pipeline_run.total_skipped = totals.total_skipped
            pipeline_run.total_analyzed = totals.total_analyzed
            pipeline_run.analyses_created = totals.analyses_created
            pipeline_run.analyses_updated = totals.analyses_updated
            pipeline_run.error_count = totals.error_count
            pipeline_run.error_message = error_message

            # Step 10: save the completed pipeline execution.
            self.session.commit()
            self.session.refresh(pipeline_run)

        except Exception:
            # Step 11: undo all changes if completion fails.
            self.session.rollback()
            raise

        return pipeline_run
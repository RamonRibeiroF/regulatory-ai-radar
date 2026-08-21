from __future__ import annotations

import argparse

from regulatory_ai_radar.pipeline import PipelineRunner


def parse_arguments() -> argparse.Namespace:
    """Read command-line options for the pipeline."""

    # Step 1: create the command-line argument parser.
    parser = argparse.ArgumentParser(
        description=(
            "Collect, persist, and analyze regulatory publications "
            "from all configured sources."
        )
    )

    # Step 2: allow the collection limit to be customized.
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help=(
            "Maximum number of recent publications collected "
            "from each source. Default: 5."
        ),
    )

    return parser.parse_args()


def main() -> None:
    """Execute the complete Regulatory AI Radar pipeline."""

    # Step 3: read the execution options.
    arguments = parse_arguments()

    print("=" * 70)
    print("REGULATORY AI RADAR")
    print("Automated regulatory data pipeline")
    print("=" * 70)
    print(
        "\nExecuting all configured regulatory sources..."
    )

    # Step 4: create and execute the pipeline coordinator.
    runner = PipelineRunner()
    result = runner.run(
        limit_per_source=arguments.limit,
    )

    # Step 5: display the final execution status.
    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Pipeline run ID: {result.pipeline_run_id}")
    print(f"Status: {result.status}")
    print(
        f"Successful sources: {result.successful_sources}"
    )
    print(f"Failed sources: {result.failed_sources}")

    # Step 6: display collection and persistence totals.
    print("\nCollection summary:")
    print(
        f"- Collected: {result.totals.total_collected}"
    )
    print(
        f"- Inserted: {result.totals.total_inserted}"
    )
    print(
        f"- Skipped as duplicates: "
        f"{result.totals.total_skipped}"
    )

    # Step 7: display automatic analysis totals.
    print("\nAnalysis summary:")
    print(
        f"- Analyzed: {result.totals.total_analyzed}"
    )
    print(
        f"- Analyses created: "
        f"{result.totals.analyses_created}"
    )
    print(
        f"- Analyses updated: "
        f"{result.totals.analyses_updated}"
    )
    print(f"- Errors: {result.totals.error_count}")
    print("=" * 70)


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()
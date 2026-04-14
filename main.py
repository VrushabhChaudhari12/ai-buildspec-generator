"""
Main entry point for the AI BuildSpec Generator.
Supports CLI arguments to select scenarios and export JSON results.
"""
import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from mock_requests import get_request, get_context
from generator import generate_buildspec
from output_writer import save_buildspec

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

ALL_SCENARIOS = ["nodejs_ecr", "python_lambda", "java_eks", "react_s3"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI BuildSpec Generator — produce production-ready AWS CodeBuild buildspec.yml files"
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=ALL_SCENARIOS,
        choices=ALL_SCENARIOS,
        help="Scenarios to generate (default: all)",
    )
    parser.add_argument(
        "--output-json",
        metavar="FILE",
        help="Write results summary to a JSON file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenarios = args.scenarios

    log.info("AI BUILDSPEC & PIPELINE GENERATOR")
    log.info("Running %d scenario(s): %s", len(scenarios), scenarios)

    results = []

    for scenario in scenarios:
        log.info("--- Scenario: %s ---", scenario)

        request_text = get_request(scenario)
        context = get_context(scenario)

        log.info("Developer request: %s", request_text)

        try:
            buildspec = generate_buildspec(request_text, context)
            output_path = save_buildspec(scenario, buildspec)
            log.info("Saved buildspec to: %s", output_path)
            results.append({"scenario": scenario, "status": "success", "output": output_path})
        except Exception as exc:
            log.error("Failed to generate buildspec for '%s': %s", scenario, exc)
            results.append({"scenario": scenario, "status": "error", "error": str(exc)})

    # Summary
    success_count = sum(1 for r in results if r["status"] == "success")
    log.info("Completed: %d/%d succeeded", success_count, len(results))

    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(results, f, indent=2)
        log.info("Results written to %s", args.output_json)


if __name__ == "__main__":
    main()

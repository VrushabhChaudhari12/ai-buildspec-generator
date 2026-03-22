"""
Main entry point for the AI BuildSpec Generator.
Runs all four scenarios and generates buildspec files.
"""

import os
import sys

# Add the current directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mock_requests import get_request, get_context
from generator import generate_buildspec
from output_writer import save_buildspec


# List of scenarios to run
SCENARIOS = ["nodejs_ecr", "python_lambda", "java_eks", "react_s3"]


def main():
    """
    Run all four scenarios and generate buildspec files.
    """
    print("\n" + "=" * 70)
    print("AI BUILSPEC & PIPELINE GENERATOR")
    print("=" * 70 + "\n")

    for scenario in SCENARIOS:
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario}")
        print(f"{'='*70}\n")

        # Get the plain-English request
        request_text = get_request(scenario)
        print(f"Developer Request:\n{request_text}\n")

        # Get the context
        context = get_context(scenario)
        print(f"Project Context: {context}\n")

        print("-" * 70)
        print("Generating buildspec...")
        print("-" * 70)

        try:
            # Generate the buildspec
            yaml_content = generate_buildspec(request_text, context)

            # Save the buildspec
            save_buildspec(yaml_content, scenario)

            # Print the generated YAML to console
            print("\nGenerated YAML:")
            print("-" * 70)
            print(yaml_content)
            print("-" * 70)

        except Exception as e:
            print(f"\nERROR: Failed to generate buildspec for {scenario}")
            print(f"Error details: {e}\n")
            continue

        # Print separator between scenarios
        print("\n" + "=" * 70)
        print("SCENARIO COMPLETED")
        print("=" * 70 + "\n")

    print("\n" + "=" * 70)
    print("ALL SCENARIOS COMPLETED")
    print("=" * 70)
    print(f"\nGenerated buildspec files:")
    for scenario in SCENARIOS:
        filepath = os.path.join(os.getcwd(), f"buildspec_{scenario}.yml")
        print(f"  - {filepath}")
    print()


if __name__ == "__main__":
    main()
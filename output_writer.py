"""
Output writer for saving generated buildspec files.
"""

import os
import yaml


def save_buildspec(yaml_content: str, scenario_name: str) -> None:
    """
    Save the generated buildspec to a file and print a formatted summary.

    Args:
        yaml_content: The generated YAML buildspec content
        scenario_name: The name of the scenario (e.g., 'nodejs_ecr', 'python_lambda')
    """
    # Save to buildspec_{scenario_name}.yml in current directory
    filename = f"buildspec_{scenario_name}.yml"
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    # Parse the YAML to extract info for summary
    parsed = yaml.safe_load(yaml_content)

    # Detect runtime from env variables or phases
    runtime = "unknown"
    if parsed and 'env' in parsed and 'variables' in parsed['env']:
        runtime = parsed['env'].get('variables', {}).get('runtime', 'not specified')

    # Count phases generated
    phases_count = 0
    if parsed and 'phases' in parsed:
        phases_count = len(parsed['phases'])

    # Print formatted summary
    print("=" * 60)
    print("BUILDSPEC FILE SAVED SUCCESSFULLY")
    print("=" * 60)
    print(f"Scenario Name:    {scenario_name}")
    print(f"Detected Runtime: {runtime}")
    print(f"Phases Generated: {phases_count}")
    print(f"File Location:    {filepath}")
    print("=" * 60)
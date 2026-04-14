"""
Main generator logic for buildspec generation.
Uses OpenAI library pointing to Ollama (or any OpenAI-compatible endpoint).
"""
import logging
import time
import yaml
from openai import OpenAI

import config
from prompts import SYSTEM_PROMPT, build_prompt

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def generate_buildspec(request_text: str, context: dict) -> str:
    """
    Generate a buildspec.yml from a plain-English request using an LLM.

    Args:
        request_text: The plain-English request description
        context: Dictionary with project context

    Returns:
        The generated YAML buildspec content as a string
    """
    user_message = build_prompt(request_text, context)

    client = OpenAI(
        base_url=config.BASE_URL,
        api_key=config.API_KEY,
        timeout=config.TIMEOUT_SECONDS,
    )

    previous_outputs: list[str] = []
    retry_count = 0

    while retry_count < config.MAX_RETRIES:
        try:
            log.info("Calling LLM (attempt %d/%d)", retry_count + 1, config.MAX_RETRIES)
            response = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
            )

            generated_content = response.choices[0].message.content.strip()

            # Strip markdown fences if present
            if generated_content.startswith("```yaml"):
                generated_content = generated_content[7:]
            elif generated_content.startswith("```"):
                generated_content = generated_content[3:]
            if generated_content.endswith("```"):
                generated_content = generated_content[:-3]
            generated_content = generated_content.strip()

            # Validate: must start with version: 0.2
            if not generated_content.startswith(config.TERMINATION_CONDITION):
                log.warning(
                    "Output does not start with '%s'. Retrying...",
                    config.TERMINATION_CONDITION,
                )
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            # Validate YAML
            try:
                yaml.safe_load(generated_content)
                log.info("YAML validation passed")
            except yaml.YAMLError as exc:
                log.warning("YAML validation failed: %s. Retrying...", exc)
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            # Loop detection
            if generated_content in previous_outputs:
                log.warning("Loop detected: identical output repeated. Retrying...")
                previous_outputs.clear()
                retry_count += 1
                time.sleep(2 ** retry_count)
                continue

            previous_outputs.append(generated_content)
            if len(previous_outputs) >= config.LOOP_DETECTION_THRESHOLD:
                log.warning("Loop detection threshold reached. Using last output.")
                break

            log.info("Buildspec generated successfully")
            return generated_content

        except Exception as exc:
            log.error("Error during generation: %s", exc)
            retry_count += 1
            if retry_count >= config.MAX_RETRIES:
                raise RuntimeError(f"Failed after {config.MAX_RETRIES} retries: {exc}") from exc
            wait_time = 2 ** retry_count
            log.info("Retrying in %d seconds...", wait_time)
            time.sleep(wait_time)

    raise RuntimeError(
        f"Failed to generate valid buildspec after {config.MAX_RETRIES} retries"
    )


def validate_buildspec(yaml_content: str) -> bool:
    """
    Validate that the generated YAML is parseable and has version: 0.2.

    Args:
        yaml_content: The YAML content to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = yaml.safe_load(yaml_content)
        if parsed and isinstance(parsed, dict):
            return parsed.get("version") == "0.2"
    except yaml.YAMLError:
        pass
    return False

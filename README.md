# AI BuildSpec & Pipeline Generator

> **Plain-English → production-ready AWS CodeBuild `buildspec.yml` in seconds.** Eliminates the hours developers spend writing, debugging, and iterating on pipeline config by delegating YAML generation to an LLM with strict schema validation, retry logic, and loop detection.

---

## The Problem This Solves

Writing AWS CodeBuild buildspecs is repetitive, error-prone boilerplate. A Node.js ECR pipeline needs ECR login, `docker build`, `docker push`, Snyk scan, Slack webhook — developers copy-paste from docs and spend 30–60 minutes getting YAML indentation and CLI flags right. This tool reduces that to a one-liner.

```
# Before: 45 minutes of YAML wrangling
# After:
python main.py --scenarios nodejs_ecr python_lambda
```

---

## What Gets Generated

Four real-world pipeline scenarios, each producing a complete multi-phase buildspec:

| Scenario | Stack | Phases | Integrations |
|----------|-------|--------|----------------------------|
| `nodejs_ecr` | Node.js 20 + Docker | install, pre_build, build, post_build | ECR, Jest, Snyk, Slack |
| `python_lambda` | Python 3.12 | install, pre_build, build, post_build | S3 ZIP upload, SNS, pytest |
| `java_eks` | Java 17 + Maven | install, pre_build, build, post_build | ECR, EKS deploy, JUnit |
| `react_s3` | React + Node | install, pre_build, build, post_build | S3 sync, CloudFront invalidation |

Each buildspec includes:
- **`pre_build`**: Snyk security scan (`snyk test --json > snyk-results.json || true`)
- **`build`**: Compile, test, Docker build/push or artifact packaging
- **`post_build`**: Slack/SNS notification with build number and status
- **Environment variables**: `$AWS_DEFAULT_REGION`, `$AWS_ACCOUNT_ID`, `$SLACK_WEBHOOK_URL`

---

## Architecture

```
Developer request (plain English)
        |
        v
  prompts.py  ──────────────────────────────────┐
  (system prompt + context builder)             |
        |                                        |
        v                                        |
  generator.py  (LLM call via OpenAI client)    |
        |                                        |
        +─── validate: starts with "version: 0.2"|
        +─── validate: YAML parseable           |
        +─── loop detection (3 identical = stop) |
        +─── exponential backoff on failure      |
        |                                        |
        v                                        |
  output_writer.py  ────────────────────────────┘
  (save buildspec.yml to output/)
        |
        v
  output/<scenario>/buildspec.yml
```

---

## Engineering Quality

| Feature | Implementation |
|---------|---------------|
| Config management | `config.py` — all settings via env vars with typed defaults |
| Structured logging | Python `logging` module — level, timestamp, module name |
| Input validation | Schema check: `version: 0.2` + `yaml.safe_load()` |
| Retry logic | Exponential backoff (2^n seconds), max 3 retries |
| Loop detection | Tracks repeated outputs, breaks after threshold |
| CLI interface | `argparse` — `--scenarios`, `--output-json` |
| Error isolation | Per-scenario try/except, continues on individual failures |
| LLM-agnostic | OpenAI-compatible client — swap Ollama for GPT-4/Claude via env vars |

---

## Quick Start

### 1. Install Ollama + model
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3.2
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the generator
```bash
# All four scenarios
python main.py

# Specific scenarios
python main.py --scenarios nodejs_ecr python_lambda

# Export results summary
python main.py --output-json results.json
```

### Optional environment variables
```bash
export BASE_URL=http://localhost:11434/v1
export MODEL=llama3.2
export LOG_LEVEL=DEBUG
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

---

## Project Structure

```
ai-buildspec-generator/
├── main.py             # CLI entry point — argparse, orchestration
├── generator.py        # LLM call, YAML validation, retry + loop detection
├── prompts.py          # System prompt + context-aware user message builder
├── config.py           # Centralized config with env var overrides
├── mock_requests.py    # Simulated developer requests for 4 scenarios
├── output_writer.py    # Save buildspec.yml to output directory
├── requirements.txt    # openai, pyyaml
└── docs/               # GitHub Pages — interactive visualizer
```

---

## Why This Matters (Resume Context)

This project demonstrates end-to-end DevOps AI automation for a real pain point:
- **Prompt engineering discipline**: system prompt constrains format to valid YAML — no markdown, no explanations, just `version: 0.2` output
- **Production safety patterns**: validation gates, retry with backoff, loop detection — same patterns used in production LLM pipelines
- **Real CI/CD knowledge**: generated buildspecs use actual AWS CLI commands, ECR login syntax, EKS `kubectl` deployment, S3 artifact upload
- **Tool is LLM-agnostic**: swap Ollama → OpenAI GPT-4 or Anthropic Claude by changing two env vars — demonstrates portable AI integration design
- **Interactive demo**: GitHub Pages visualizer at `/docs` for non-technical stakeholders

# AI BuildSpec & Pipeline Generator

An AI-powered generator that takes plain-English descriptions of what needs to be built and returns production-ready AWS CodeBuild buildspec.yml files.

## Overview

This project uses a local LLM (Ollama with llama3.2) to generate AWS CodeBuild BuildSpec files from simple developer requests. The generated BuildSpecs include:

- **Snyk Security Scanning**: Automated security vulnerability scanning in the pre_build phase
- **ECR Push**: Docker image building and pushing to Amazon ECR
- **Slack Notifications**: Real-time build status notifications via Slack webhooks
- **SNS Notifications**: Build status notifications via Amazon SNS
- **Full CI/CD Pipeline**: Complete install, pre_build, build, and post_build phases

## Supported Scenarios

1. **Node.js + ECR**: Node.js 20 app with Jest tests, Docker image pushed to ECR, Slack notifications
2. **Python Lambda**: Python 3.12 Lambda function with pytest, packaged as ZIP, uploaded to S3, SNS notifications
3. **Java + EKS**: Java 17 Maven app with JUnit tests, Docker image pushed to ECR, deployed to EKS
4. **React + S3**: React app with ESLint and Jest tests, production bundle synced to S3, CloudFront cache invalidation

## Stack

- **Language**: Python 3.10+
- **LLM**: Ollama (localhost:11434) with llama3.2 model
- **Dependencies**: openai, pyyaml

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running with the llama3.2 model:

```bash
ollama serve
# In another terminal:
ollama pull llama3.2
```

## Usage

Run the generator for all four scenarios:

```bash
py main.py
```

This will:
1. Process each of the four developer scenarios
2. Generate production-ready buildspec.yml files
3. Save them as `buildspec_{scenario}.yml` in the current directory
4. Print the generated YAML to the console

## Output

The tool generates buildspec files for each scenario:

- `buildspec_nodejs_ecr.yml`
- `buildspec_python_lambda.yml`
- `buildspec_java_eks.yml`
- `buildspec_react_s3.yml`

## Example

Input (Developer Request):
```
"I need a Node.js 20 app built, unit tests run with Jest, Docker image built and pushed to ECR, Slack notification on success or failure"
```

Output (Generated BuildSpec):
```yaml
version: 0.2

env:
  variables:
    AWS_DEFAULT_REGION: "us-east-1"
    AWS_ACCOUNT_ID: "123456789012"

phases:
  install:
    commands:
      - npm install -g npm@latest
      - npm install

  pre_build:
    commands:
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - snyk test --json > snyk-results.json || true

  build:
    commands:
      - npm test

  post_build:
    commands:
      - docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/nodejs-app:latest .
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/nodejs-app:latest
      - |
        curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Build $CODEBUILD_BUILD_NUMBER $CODEBUILD_BUILD_STATUS in $AWS_DEFAULT_REGION"}' \
        $SLACK_WEBHOOK_URL

artifacts:
  files:
    - '**/*'
  name: build-output

cache:
  paths:
    - /root/.npm/**/*
```

## Features

- **Four-Layer Termination Safety**:
  1. Checks output starts with "version: 0.2"
  2. Maximum 3 retries with exponential backoff
  3. 90-second timeout per request
  4. Loop detection to break on repeated outputs

- **YAML Validation**: All generated BuildSpecs are validated using Python's yaml.safe_load before being saved

- **Production-Ready**: Includes real AWS CLI commands, environment variables, security scanning, and notifications

## License

MIT
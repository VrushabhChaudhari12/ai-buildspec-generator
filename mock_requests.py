"""
Mock developer requests for buildspec generation.
Each request is a plain-English description of what needs to be built.
"""

# Dictionary of scenario requests
REQUESTS = {
    "nodejs_ecr": "I need a Node.js 20 app built, unit tests run with Jest, Docker image built and pushed to ECR, Slack notification on success or failure",
    "python_lambda": "Python 3.12 Lambda function, run pytest, package as zip, upload to S3 bucket called my-lambda-artifacts, send SNS notification",
    "java_eks": "Java 17 Maven app, run JUnit tests, build Docker image, push to ECR, deploy to EKS cluster called prod-cluster using kubectl",
    "react_s3": "React app using Node 20, run ESLint, run Jest tests, build production bundle, sync to S3 bucket my-frontend-bucket, invalidate CloudFront cache"
}

# Context dictionary for each scenario
CONTEXT = {
    "nodejs_ecr": {
        "project_name": "nodejs-app",
        "runtime": "nodejs:20",
        "aws_region": "us-east-1",
        "account_id": "123456789012",
        "ecr_repo": "nodejs-app-repo",
        "slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    },
    "python_lambda": {
        "project_name": "python-lambda",
        "runtime": "python:3.12",
        "aws_region": "us-east-1",
        "account_id": "123456789012",
        "s3_bucket": "my-lambda-artifacts",
        "sns_topic": "lambda-deployments"
    },
    "java_eks": {
        "project_name": "java-app",
        "runtime": "java:17",
        "aws_region": "us-east-1",
        "account_id": "123456789012",
        "ecr_repo": "java-app-repo",
        "eks_cluster": "prod-cluster"
    },
    "react_s3": {
        "project_name": "react-frontend",
        "runtime": "nodejs:20",
        "aws_region": "us-east-1",
        "account_id": "123456789012",
        "s3_bucket": "my-frontend-bucket",
        "cloudfront_distribution": "E1234567890ABC"
    }
}


def get_request(scenario: str) -> str:
    """
    Get the plain-English request description for a given scenario.

    Args:
        scenario: The scenario name (e.g., 'nodejs_ecr', 'python_lambda')

    Returns:
        The plain-English request description as a string
    """
    return REQUESTS.get(scenario, "")


def get_context(scenario: str) -> dict:
    """
    Get the context dictionary for a given scenario.

    Args:
        scenario: The scenario name

    Returns:
        Dictionary containing project context (project_name, runtime, aws_region, account_id, etc.)
    """
    return CONTEXT.get(scenario, {})
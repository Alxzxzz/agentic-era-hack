# Infra-Vision Agent

## Project Overview

Infra-Vision Agent is a specialized AI agent designed for infrastructure cost optimization and analysis on the Google Cloud Platform (GCP). Built on Google's Agent Development Kit (ADK), it utilizes a ReAct (Reasoning and Acting) agent pattern to provide a natural language interface for complex cloud management tasks.

This agent allows users to:

*   Analyze their GCP resources and associated costs.
*   Receive official cost-saving recommendations from Google Cloud.
*   Generate architectural diagrams of their infrastructure.

## Features

*   **Natural Language Interaction:**  Communicate with the agent in plain English to perform complex analysis.
*   **Comprehensive Infrastructure Analysis:** Get a detailed summary of your GCP resources, including VMs, Cloud SQL, GKE, Storage, and more.
*   **Cost Breakdown:**  Receive an estimated monthly cost for each identified resource.
*   **Official GCP Recommendations:**  Access cost, security, performance, and reliability recommendations from the Google Cloud Recommender API.
*   **Infrastructure Visualization:** Generate architectural diagrams of your infrastructure using Gemini's image generation capabilities.

## Architecture

The agent's architecture is centered around a core `root_agent` that orchestrates a set of tools to interact with GCP services.

*   **Agent:** `root_agent` (an instance of ADK's `Agent`)
*   **AI Model:** `gemini-2.5-flash`

### Architectural Design

The agent employs a ReAct (Reason-Act) pattern through the ADK, which is a form of chain-of-thought reasoning. The architecture is modular and well-defined for its purpose. It is designed to be a single, specialized agent and does not implement more complex patterns like multi-agent systems.

### Tool Integration & Function Calling

The agent effectively selects and utilizes a set of four distinct tools to interact with GCP APIs and Gemini for image generation:

*   `set_project_id`: Sets the GCP project ID for analysis.
*   `analyze_infrastructure`: Analyzes resources using the Google Cloud Asset Inventory.
*   `get_google_cloud_recommendations`: Fetches recommendations from the Google Cloud Recommender API.
*   `generate_infrastructure_image`: Creates a visual diagram of the infrastructure.

### Task Decomposition & Planning

The current version of the agent responds to direct requests with a specific tool. It does not yet implement complex multi-step planning for a single high-level goal.

## Implementation & Production Readiness

### Effective Use of GCP & Starter Pack

This project is a canonical example of the `agent-starter-pack`. It utilizes `uv` for package management, a `Makefile` for common commands, and the recommended folder structure. It leverages Vertex AI for the agent and key GCP services like Asset Inventory and Recommender.

### Code Quality

The code is modularized into services like `infrastructure_analyzer` and `recommender_service`. It uses type hints and includes basic error handling for GCP client initialization.

### CI/CD & Observability

The repository contains configuration files for a complete CI/CD pipeline using Google Cloud Build (`.cloudbuild/`) and infrastructure deployment with Terraform (`deployment/`).

## Problem, Solution & UX

### Problem-Solution Fit

The agent solves a clear and valuable real-world problem: the complexity of analyzing and optimizing GCP infrastructure costs. The solution is practical and provides high value for DevOps and FinOps teams.

### User Experience

The interaction with the agent is conversational and direct. The `Makefile` simplifies the process of launching a local playground (`make playground`) for a smooth user experience.

## Innovation

The application of an AI agent for cloud infrastructure management (CloudOps) is an innovative field with significant market potential to simplify complex operations.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following tools installed and configured:

*   [uv](https://docs.astral.sh/uv/getting-started/installation/): Python package manager
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install): For interacting with GCP services
*   [Terraform](https://developer.hashicorp.com/terraform/downloads): For infrastructure deployment
*   [make](https://www.gnu.org/software/make/): Build automation tool

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/Alxzxzz/agentic-era-hack.git
    cd agentic-era-hack
    ```

2.  Install the required dependencies:

    ```bash
    make install
    ```

## Usage

### Local Playground

To test the agent locally in an interactive web interface, run:

```bash
make playground
```

This will start a Streamlit application where you can chat with your agent.

### Available Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch the Streamlit interface for testing the agent locally and remotely.                  |
| `make backend`       | Deploy the agent to Agent Engine.                                                           |
| `make test`          | Run unit and integration tests.                                                             |
| `make lint`          | Run code quality checks (codespell, ruff, mypy).                                            |
| `make setup-dev-env` | Set up the development environment resources using Terraform.                               |
| `uv run jupyter lab` | Launch Jupyter notebook.                                                                    |

## Deployment

This project is configured for automated deployment to Google Cloud using a CI/CD pipeline.

### CI/CD Pipeline

The CI/CD pipeline is managed by Google Cloud Build and is defined in the `.cloudbuild/` directory. The pipeline is triggered by pushes and pull requests to the `main` branch of the GitHub repository.

*   **Pull Requests:** The `pr_checks.yaml` pipeline runs tests to validate changes.
*   **Push to `main`:** The `staging.yaml` pipeline deploys the agent to the staging environment.
*   **Production Deployment:** The `deploy-to-prod.yaml` pipeline deploys the agent to the production environment after manual approval.

### Staging Environment

The staging environment is automatically deployed to when changes are pushed to the `main` branch. This environment is intended for testing and validation before deploying to production.

### Production Environment

The production environment is deployed to after manual approval in the Cloud Build console. The production agent is accessible via a public URL.

**Production Endpoint URL:**

`https://us-central1-aiplatform.googleapis.com/v1beta1/projects/1038271134031/locations/us-central1/reasoningEngines/8568208242235146240:streamQuery`

To interact with the production agent, you can use `curl` with an access token:

```bash
curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/1038271134031/locations/us-central1/reasoningEngines/8568208242235146240:streamQuery" \
-d '{ "message": "analyze my infrastructure" }'
```

## Monitoring and Observability

The project is configured with the following observability features:

*   **Cloud Logging:** All logs from the agent and the CI/CD pipeline are sent to Cloud Logging.
*   **Cloud Trace:** The application uses OpenTelemetry to send traces to Cloud Trace for performance monitoring.
*   **BigQuery:** Logs are sinked to BigQuery for long-term storage and analysis.
*   **Looker Studio:** A [Looker Studio dashboard template](https://lookerstudio.google.com/reporting/46b38b-4e44-bd37-701ef4307418/page/tEnnC) is available for visualizing events logged in BigQuery.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

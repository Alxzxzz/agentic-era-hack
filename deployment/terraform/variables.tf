# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

variable "prod_project_id" {
  type        = string
  description = "The GCP project ID for the production environment."
}

variable "staging_project_id" {
  type        = string
  description = "The GCP project ID for the staging environment."
}

variable "cicd_runner_project_id" {
  type        = string
  description = "The GCP project ID where CI/CD resources like Cloud Build triggers will be created."
}

variable "dev_project_id" {
  type        = string
  description = "The GCP project ID for the development environment."
  default     = null
}

variable "region" {
  type        = string
  description = "The primary GCP region for deploying resources."
}

variable "repository_owner" {
  type        = string
  description = "The owner of the GitHub repository (user or organization)."
}

variable "repository_name" {
  type        = string
  description = "The name of the GitHub repository."
}

variable "project_name" {
  type        = string
  description = "The base name for the agent project, used for naming resources."
  default     = "infra-vision-agent"
}

variable "iap" {
  type        = bool
  description = "Flag to enable Identity-Aware Proxy for the UI."
  default     = false
}

variable "data_ingestion" {
  type        = bool
  description = "Flag to include data ingestion pipelines."
  default     = false
}

# Variables added to fix errors
variable "create_repository" {
  type        = bool
  description = "Whether to create the GitHub repository."
  default     = true
}

variable "github_pat_secret_id" {
  type        = string
  description = "The Secret Manager secret ID for the GitHub PAT."
  default     = ""
}

variable "cicd_roles" {
  type        = list(string)
  description = "A list of IAM roles for the CI/CD service account on the CI/CD project."
  default     = []
}

variable "cicd_sa_deployment_required_roles" {
  type        = list(string)
  description = "A list of IAM roles required by the CI/CD service account on the deployment projects."
  default     = []
}

variable "app_sa_roles" {
  type        = list(string)
  description = "A list of IAM roles for the application's service account."
  default     = []
}

variable "telemetry_logs_filter" {
  type        = string
  description = "The filter for telemetry logs."
  default     = ""
}

variable "feedback_logs_filter" {
  type        = string
  description = "The filter for feedback logs."
  default     = ""
}

variable "github_app_installation_id" {
  type        = string
  description = "The installation ID for the GitHub App."
  default     = null
}

variable "create_cb_connection" {
  type        = bool
  description = "Whether to create the Cloud Build connection to GitHub."
  default     = true
}

variable "host_connection_name" {
  type        = string
  description = "The name for the Cloud Build host connection."
  default     = "github-connection"
}

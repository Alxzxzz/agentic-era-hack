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

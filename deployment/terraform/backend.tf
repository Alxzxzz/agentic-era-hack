terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-02-73852aeb6acb-terraform-state"
    prefix = "infra-vision-agent/prod"
  }
}

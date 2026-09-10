terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Ativar APIs necessárias
resource "google_project_service" "run_api" {
  project = var.project_id
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry_api" {
  project = var.project_id
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "vertex_api" {
  project = var.project_id
  service = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

# 2. Storage Bucket (Documentos Não Estruturados)
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "docs_bucket" {
  name                        = "autolub-docs-${var.project_id}-${random_id.bucket_suffix.hex}"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}

# 3. BigQuery (Data Warehouse Analítico)
resource "google_bigquery_dataset" "analytics_dataset" {
  dataset_id                  = "autolub_analytics"
  friendly_name               = "AutoLub Analytics"
  description                 = "Dataset Real para análises do Grupo AutoLub"
  location                    = var.region
  delete_contents_on_destroy  = true
}

resource "google_bigquery_table" "fact_vendas" {
  dataset_id = google_bigquery_dataset.analytics_dataset.dataset_id
  table_id   = "fact_vendas_consolidadas"
  
  schema = <<EOF
  [
    {"name": "mes_ano", "type": "STRING", "mode": "NULLABLE"},
    {"name": "trimestre", "type": "STRING", "mode": "NULLABLE"},
    {"name": "regiao", "type": "STRING", "mode": "NULLABLE"},
    {"name": "categoria_produto", "type": "STRING", "mode": "NULLABLE"},
    {"name": "volume_litros", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "faturamento_total", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "margem_media", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "qtd_pedidos", "type": "INTEGER", "mode": "NULLABLE"}
  ]
  EOF
  deletion_protection = false
}

# 4. Artifact Registry
resource "google_artifact_registry_repository" "repo" {
  provider      = google
  location      = var.region
  repository_id = "autolub-repo"
  description   = "Docker repository for AutoLub Demo"
  format        = "DOCKER"
  depends_on    = [google_project_service.artifactregistry_api]
}

# 5. Cloud Run Service (App ADK)
resource "google_cloud_run_v2_service" "default" {
  name     = "autolub-enterprise-agent"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/autolub-agent:latest"
      
      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
      }
      
      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }
      env {
        name  = "GCS_BUCKET_NAME"
        value = google_storage_bucket.docs_bucket.name
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
    }
  }

  depends_on = [google_project_service.run_api, null_resource.docker_build]
}

# 6. Build da Imagem
resource "null_resource" "docker_build" {
  triggers = {
    always_run = "${timestamp()}"
  }
  provisioner "local-exec" {
    command = "gcloud builds submit .. --tag ${var.region}-docker.pkg.dev/${var.project_id}/autolub-repo/autolub-agent:latest --project ${var.project_id}"
  }
  depends_on = [google_artifact_registry_repository.repo]
}

# 7. Acesso Público
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.default.location
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# OUTPUTS (Para uso no script de população de dados)
output "cloud_run_url" {
  value = google_cloud_run_v2_service.default.uri
}

output "gcs_bucket" {
  value = google_storage_bucket.docs_bucket.name
}

output "bq_dataset" {
  value = google_bigquery_dataset.analytics_dataset.dataset_id
}

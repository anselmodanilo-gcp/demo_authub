#!/bin/bash
set -e

PROJECT_ID="cool-ship-415013"
REGION="southamerica-east1"  # Região sugerida no contexto anterior para o cliente (pode mudar se necessário)
APP_NAME="autolub-enterprise-agent"

echo "============================================================"
echo "🚀 INICIANDO DEPLOY NO GOOGLE CLOUD RUN"
echo "Projeto: $PROJECT_ID | Região: $REGION"
echo "============================================================"

# Configurar o projeto no Gcloud
gcloud config set project $PROJECT_ID

# (Opcional) Ativar as APIs necessárias, caso não estejam
echo "🔧 Verificando APIs necessárias (Run, Artifact Registry, Vertex AI)..."
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    --project=$PROJECT_ID

echo "📦 Fazendo o build e deploy direto via Cloud Run from Source..."
# O Cloud Run agora suporta build from source direto sem precisar buildar o docker localmente primeiro!
gcloud run deploy $APP_NAME \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars=PYTHONUNBUFFERED=1 \
    --memory 2Gi \
    --cpu 1

echo "============================================================"
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "O seu Agent Platform com ADK já está disponível na URL informada acima."
echo "============================================================"

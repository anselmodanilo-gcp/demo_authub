import json
import os
from google.cloud import storage

DATA_DIR = "/home/anselmodanilo/dev/gruporevise_demo/autolub_enterprise_demo/data"

def query_jira_tickets(ticket_id: str = None) -> str:
    """Ferramenta para buscar chamados no Jira (Simulação JSON)."""
    jira_path = os.path.join(DATA_DIR, "jira", "tickets.json")
    try:
        with open(jira_path, "r", encoding="utf-8") as f:
            tickets = json.load(f)
        
        if ticket_id:
            filtered = [t for t in tickets if ticket_id in t.get("ticket_id", "") or ticket_id in t.get("descricao", "")]
            return json.dumps(filtered, ensure_ascii=False)
        return json.dumps(tickets, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

def search_unstructured_docs(query: str) -> str:
    """Ferramenta para buscar em documentos do Drive (Contratos PDF/TXT armazenados no Google Cloud Storage real)."""
    try:
        bucket_name = os.environ.get("GCS_BUCKET_NAME")
        if not bucket_name:
            return json.dumps({"error": "A variável de ambiente GCS_BUCKET_NAME não está configurada."})
            
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        results = []
        
        for blob in bucket.list_blobs():
            content = blob.download_as_text(encoding="utf-8")
            if query.lower() in content.lower():
                results.append({
                    "arquivo": blob.name,
                    "trecho": content[:500] + "..." # Limitando o trecho para contexto do LLM
                })
                
        if not results:
             return json.dumps({"msg": "Nenhum documento encontrado com este termo."})
             
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

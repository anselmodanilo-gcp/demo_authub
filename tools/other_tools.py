import json
import os

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
    """Ferramenta para buscar em documentos do Drive (Contratos PDF/TXT)."""
    docs_dir = os.path.join(DATA_DIR, "docs")
    results = []
    try:
        for filename in os.listdir(docs_dir):
            file_path = os.path.join(docs_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        # Simple extraction
                        results.append({
                            "arquivo": filename,
                            "trecho": content[:500] + "..." # retornando um pedaço
                        })
        if not results:
             return json.dumps({"msg": "Nenhum documento encontrado."})
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

"""Servidor local (ADK Mock) para testes do AutoLub Co-Pilot."""
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import json
import time

from tools.erp_tool import query_erp_operational
from tools.other_tools import query_jira_tickets, search_unstructured_docs

app = FastAPI(title="Assistente AutoLub - Local ADK Server", version="1.0.0")

class AgentPromptRequest(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "ONLINE", "framework": "Google-ADK", "demo": "AutoLub Enterprise"}

@app.post("/agent/evaluate")
def evaluate(req: AgentPromptRequest):
    start = time.time()
    prompt = req.prompt.lower()
    traces, tools_run = [], []
    response_text = ""

    # Router heurístico simulando a LLM do Agent Platform
    if any(k in prompt for k in ["venda", "faturado", "cliente", "desconto", "pedido", "9874"]):
        traces.append("Roteamento ADK: Consulta analítica de faturamento (Cloud SQL/BigQuery).")
        query = "SELECT * FROM pedidos p JOIN itens_pedido i ON p.id = i.pedido_id WHERE p.id = 9874" if "9874" in prompt else "SELECT p.id, c.razao_social, p.valor_total, p.status, p.data_emissao FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.data_emissao DESC LIMIT 5"
        res = query_erp_operational(query)
        tools_run.append({"tool": "erp_sql_query", "data": json.loads(res)})
        response_text = "Consultei o banco de dados ERP transacional com base na sua solicitação."

    if any(k in prompt for k in ["contrato", "dólar", "reajuste", "petroquímica", "sla", "logística"]):
        traces.append("Roteamento ADK: Auditoria semântica de contratos (Drive/GCS).")
        search_query = "dólar" if "dólar" in prompt else "logística"
        res = search_unstructured_docs(search_query)
        tools_run.append({"tool": "drive_search_tool", "data": json.loads(res)})
        response_text += " " + "Realizei também o RAG (Retrieval) na base de contratos e SLAs."

    if any(k in prompt for k in ["jira", "entrega", "incidente", "chamado", "desvio"]):
        traces.append("Roteamento ADK: Investigação de ocorrências operacionais (Jira Extensions).")
        res = query_jira_tickets("9874" if "9874" in prompt else None)
        tools_run.append({"tool": "ticket_ops_tool", "data": json.loads(res)})
        response_text += " " + "Consultei a API do Jira e encontrei tickets associados."

    if not response_text:
        response_text = "Sou o Agente AutoLub e estou conectado ao ERP, Drive e Jira. Como posso ajudar?"

    return {
        "status": "SUCCESS",
        "latency_sec": round(time.time() - start, 3),
        "text_response": response_text.strip(),
        "reasoning_traces": traces,
        "tools_executed": tools_run,
        "governance": {
            "grounding_audit": "PASSED",
            "zero_training_compliance": True
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

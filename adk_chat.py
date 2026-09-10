import asyncio
import os
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from tools.erp_tool import query_erp_operational
from tools.other_tools import query_jira_tickets
from tools.bq_tool import query_bigquery_analytics

# Conector do Gemini App (Vertex AI Search Engine)
vertex_search_tool = VertexAiSearchTool(
    search_engine_id="projects/cool-ship-415013/locations/global/collections/default_collection/engines/demo_autohub_app",
    bypass_multi_tools_limit=True
)

# Configuração do Agente com o Agent Development Kit (ADK)
copilot_agent = Agent(
    name="Assistente_AutoLub",
    model="gemini-2.5-flash", # Modelo fundacional (recomendado para tool calling)
    instruction="""Você é o assistente executivo de inteligência do Grupo AutoLub.
Sua função é auxiliar a diretoria e times operacionais.
Regras de Resposta:
1. Sempre tente usar as ferramentas fornecidas para responder à pergunta do usuário, caso tenha relação com Vendas, ERP, Contratos, SLAs, Jira ou Logística.
2. Ao reportar dados financeiros ou volumes, referencie o identificador do pedido/NF.
3. Ao auditar contratos, utilize a ferramenta de busca nativa do Vertex AI Search (conectada ao seu app). Cite expressamente o trecho e o nome do documento.
4. Mantenha um tom executivo, preciso e objetivo.
""",
    tools=[query_erp_operational, query_jira_tickets, vertex_search_tool, query_bigquery_analytics]
)

async def main():
    print("=" * 60)
    print("☁️ Inicializando Google ADK (Agent Development Kit)...")
    print("=" * 60)
    
    # O Runner é o motor de execução do ADK que gerencia memória e orquestração
    runner = Runner(
        app_name="autolub_enterprise_demo", 
        agent=copilot_agent, 
        session_service=InMemorySessionService(), 
        auto_create_session=True
    )
    
    user_id = "diretoria_user"
    session_id = "sessao_demo_01"
    
    print("💬 Assistente AutoLub online (via ADK). Digite 'sair' para encerrar.")
    print("   * DICA: É necessário estar autenticado no GCP (gcloud auth application-default login)")
    print("           ou exportar a variável GEMINI_API_KEY no seu terminal.\n")
    
    while True:
        try:
            user_input = input("Você: ")
            if not user_input.strip():
                continue
            if user_input.lower() in ['sair', 'exit', 'quit']:
                break
                
            msg = Content(parts=[Part.from_text(text=user_input)])
            
            print("\n🤖 Assistente: ", end="", flush=True)
            
            # Execução assíncrona do ADK (suporta multi-turn e tool-calling nativo)
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=msg):
                
                # Exibe chamadas de função ocorrendo em background (Opcional para demonstração)
                if getattr(event, 'get_function_calls', lambda: [])():
                    for call in event.get_function_calls():
                        print(f"\n   [Tool Calling ADK] ⚙️ Acionando ferramenta: {call.name}...")
                
                # Exibe o texto final gerado pelo modelo
                if getattr(event, 'is_final_response', False) and getattr(event, 'message', None) and event.message.parts:
                    for part in event.message.parts:
                        if getattr(part, 'text', None):
                            print(part.text, end="", flush=True)
                            
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n\n[!] Erro de API ou Execução ADK: {e}")
            print("[!] Verifique suas credenciais de acesso ao Gemini / Vertex AI.\n")

if __name__ == "__main__":
    asyncio.run(main())

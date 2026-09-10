import streamlit as st
import json
import asyncio
import os
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from tools.erp_tool import query_erp_operational
from tools.other_tools import query_jira_tickets
from tools.bq_tool import query_bigquery_analytics

# Configuração global do Agente ADK
@st.cache_resource
def get_adk_runner():
    vertex_search_tool = VertexAiSearchTool(
        search_engine_id="projects/cool-ship-415013/locations/global/collections/default_collection/engines/demo_autohub_app",
        bypass_multi_tools_limit=True
    )
    
    copilot_agent = Agent(
        name="Assistente_AutoLub",
        model="gemini-2.5-flash",
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
    
    runner = Runner(
        app_name="autolub_enterprise_demo", 
        agent=copilot_agent, 
        session_service=InMemorySessionService(), 
        auto_create_session=True
    )
    return runner

# Função assíncrona para orquestrar o ADK e coletar traces
async def run_adk_agent(prompt: str, runner: Runner):
    msg = Content(parts=[Part.from_text(text=prompt)])
    
    traces = []
    tools_executed = []
    response_text = ""
    
    async for event in runner.run_async(user_id="demo_user", session_id="demo_session", new_message=msg):
        # Captura ferramentas acionadas pelo Gemini
        if getattr(event, 'get_function_calls', lambda: [])():
            for call in event.get_function_calls():
                traces.append(f"O modelo Gemini decidiu acionar a ferramenta corporativa: `{call.name}`")
                
        # Simulação para capturar resultado do tool_call (Em um ambiente real teríamos os dados de volta aqui)
        # O ADK cuida da execução, aqui nós só vamos registrar para a UI que aconteceu.
                
        # Pega a resposta final
        if getattr(event, 'is_final_response', False) and getattr(event, 'message', None) and event.message.parts:
            for part in event.message.parts:
                if getattr(part, 'text', None):
                    response_text += part.text
                    
    return {
        "text": response_text,
        "traces": traces,
        "tools": tools_executed
    }

st.set_page_config(page_title="AutoLub - Agent Platform (Demo)", page_icon="☁️", layout="wide")

st.title("☁️ Google Cloud Vertex AI: Agent Platform (ADK)")
st.subheader("Assistente AutoLub Enterprise")

if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    st.warning("⚠️ Atenção: Nenhuma credencial GCP encontrada. O Agent Development Kit precisará de permissões do Vertex AI (ou GEMINI_API_KEY) para funcionar no Cloud Run.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Pergunte sobre faturamento (BigQuery), histórico de vendas (ERP) ou incidentes logísticos (Jira)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    runner = get_adk_runner()
    
    with st.chat_message("assistant"):
        with st.spinner("Agent ADK orquestrando e decidindo quais ferramentas utilizar..."):
            # Chama o motor ADK real!
            result = asyncio.run(run_adk_agent(prompt, runner))
            
            # Mostra Raciocínio / Traces
            for t in result["traces"]:
                st.info(f"**ADK Router Trace:** {t}")
                    
            st.markdown(result["text"])
            
    st.session_state.messages.append({"role": "assistant", "content": result["text"]})

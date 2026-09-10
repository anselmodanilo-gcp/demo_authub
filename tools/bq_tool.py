import json
import os
from google.cloud import bigquery

def query_bigquery_analytics(sql_query: str) -> str:
    """Ferramenta para consultar o Data Warehouse Analítico no BigQuery Real.
    Utilize APENAS para relatórios massivos, agregações, volumetria por trimestre, e análise de margens.
    NÃO utilize para buscar pedidos individuais.
    A tabela disponível é: autolub_analytics.fact_vendas_consolidadas
    Colunas: mes_ano, trimestre, regiao, categoria_produto, volume_litros, faturamento_total, margem_media, qtd_pedidos
    Exemplo de trimestre: '2026-Q1', '2026-Q2', '2026-Q3'
    """
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "cool-ship-415013")
        client = bigquery.Client(project=project_id)
        
        # Como o agente escreve a query, ele pode não colocar o project id ou dataset correto.
        # Mas vamos confiar que o modelo entende 'autolub_analytics.fact_vendas_consolidadas' da docstring.
        query_job = client.query(sql_query)
        results = [dict(row) for row in query_job]
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

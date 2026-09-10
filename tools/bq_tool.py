import sqlite3
import json
import os

DATA_DIR = "/home/anselmodanilo/dev/gruporevise_demo/autolub_enterprise_demo/data"

def query_bigquery_analytics(sql_query: str) -> str:
    """Ferramenta para consultar o Data Warehouse Analítico (Simulação BigQuery).
    Utilize APENAS para relatórios massivos, agregações, volumetria por trimestre, e análise de margens.
    NÃO utilize para buscar pedidos individuais.
    Tabela disponível:
    - fact_vendas_consolidadas (mes_ano, trimestre, regiao, categoria_produto, volume_litros, faturamento_total, margem_media, qtd_pedidos)
    Exemplo de trimestre: '2026-Q1', '2026-Q2', '2026-Q3'
    """
    db_path = os.path.join(DATA_DIR, "bigquery", "analytics_dw.db")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

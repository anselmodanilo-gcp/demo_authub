import sqlite3
import json
import os

DATA_DIR = "/home/anselmodanilo/dev/gruporevise_demo/autolub_enterprise_demo/data"

def query_erp_operational(sql_query: str) -> str:
    """Ferramenta para consultar o ERP (Simulação SQL Server com SQLite).
    Sempre utilize as seguintes tabelas e colunas (o ID do pedido fica na tabela pedidos, coluna id):
    - clientes (id, razao_social, cnpj, tier, regiao)
    - produtos (id, nome, categoria, preco_base)
    - vendedores (id, nome, regiao)
    - pedidos (id, cliente_id, vendedor_id, data_emissao, status, valor_total)
    - itens_pedido (id, pedido_id, produto_id, quantidade, preco_unitario, desconto)
    """
    db_path = os.path.join(DATA_DIR, "erp", "erp_producao.db")
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

import sqlite3
import random
import os
from datetime import datetime, timedelta

DATA_DIR = "/home/anselmodanilo/dev/gruporevise_demo/autolub_enterprise_demo/data"

def create_bq_mock():
    # Simula um data warehouse (BigQuery) consolidado via CDC
    os.makedirs(os.path.join(DATA_DIR, "bigquery"), exist_ok=True)
    db_path = os.path.join(DATA_DIR, "bigquery", "analytics_dw.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabela fato desnormalizada comum em DW
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS fact_vendas_consolidadas (
        mes_ano TEXT,
        trimestre TEXT,
        regiao TEXT,
        categoria_produto TEXT,
        volume_litros REAL,
        faturamento_total REAL,
        margem_media REAL,
        qtd_pedidos INTEGER
    );
    """)

    # Gerar dados agregados analíticos
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste"]
    categorias = ["Sintético", "Mineral", "Graxas", "Aditivos"]
    meses = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
    
    dados = []
    for mes in meses:
        tri = f"2026-Q{(int(mes.split('-')[1])-1)//3 + 1}"
        for regiao in regioes:
            for cat in categorias:
                vol = random.uniform(1000, 50000)
                fat = vol * random.uniform(15, 45)
                margem = random.uniform(8.0, 35.0) # Margem percentual
                qtd = random.randint(5, 50)
                
                # Simulando a anomalia (baixa margem) no Sudeste para Sintéticos no Q3
                if regiao == "Sudeste" and cat == "Sintético" and tri == "2026-Q3":
                    margem = random.uniform(2.0, 9.0) # Margem espremida
                    vol *= 1.5 # Volume alto, margem baixa
                
                dados.append((mes, tri, regiao, cat, vol, fat, margem, qtd))

    cursor.executemany("INSERT INTO fact_vendas_consolidadas VALUES (?, ?, ?, ?, ?, ?, ?, ?)", dados)
    conn.commit()
    conn.close()
    print(f"Data Warehouse Mock (BigQuery) criado em {db_path}")

if __name__ == "__main__":
    create_bq_mock()

import os
import sqlite3
import subprocess
import json
from google.cloud import bigquery, storage

DATA_DIR = "/home/anselmodanilo/dev/gruporevise_demo/autolub_enterprise_demo/data"

def populate():
    print("="*60)
    print("🚀 Iniciando Upload dos dados Locais para o Google Cloud Real")
    print("="*60)
    
    try:
        print("1. Obtendo saídas (outputs) do Terraform...")
        out = subprocess.check_output(["terraform", "output", "-json"], cwd="terraform")
        tf_outs = json.loads(out)
        bucket_name = tf_outs["gcs_bucket"]["value"]
        dataset_id = tf_outs["bq_dataset"]["value"]
        project_id = "cool-ship-415013"
        print(f"   -> Bucket alvo: {bucket_name}")
        print(f"   -> Dataset alvo: {dataset_id}")
    except Exception as e:
        print("Erro ao ler saídas do terraform. Você já rodou 'terraform apply'?")
        print(e)
        return

    # 2. Migração para o BigQuery Real
    print("\n2. Migrando Data Warehouse do SQLite para o BigQuery...")
    bq_client = bigquery.Client(project=project_id)
    db_path = os.path.join(DATA_DIR, "bigquery", "analytics_dw.db")
    
    if not os.path.exists(db_path):
        print("   -> Banco SQLite analítico não encontrado. Pule a execução se não o criou.")
    else:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM fact_vendas_consolidadas").fetchall()
        
        table_ref = f"{project_id}.{dataset_id}.fact_vendas_consolidadas"
        
        # Limpar tabela (Trunca para não duplicar se rodar duas vezes)
        try:
            bq_client.query(f"TRUNCATE TABLE `{table_ref}`").result()
        except Exception:
            pass # Ignora se a tabela estiver vazia na primeira vez
            
        errors = bq_client.insert_rows_json(table_ref, [dict(r) for r in rows])
        if errors:
            print(f"   [!] Erro ao inserir no BigQuery: {errors}")
        else:
            print(f"   -> {len(rows)} linhas inseridas com sucesso na tabela {table_ref}!")

    # 3. Migração para o Google Cloud Storage Real
    print("\n3. Fazendo upload dos Contratos para o Google Cloud Storage...")
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    docs_dir = os.path.join(DATA_DIR, "docs")
    
    for filename in os.listdir(docs_dir):
        file_path = os.path.join(docs_dir, filename)
        if os.path.isfile(file_path):
            blob = bucket.blob(filename)
            blob.upload_from_filename(file_path)
            print(f"   -> {filename} carregado para gs://{bucket_name}/{filename}")
            
    print("\n============================================================")
    print("✅ MIGRAÇÃO DOS DADOS MOCKADOS PARA O GCP CONCLUÍDA!")
    print("O Agente ADK no Cloud Run agora fará consultas diretamente no BigQuery e no Cloud Storage.")
    print("============================================================")

if __name__ == "__main__":
    populate()

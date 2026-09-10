import sqlite3
import random
import json
import os
from datetime import datetime, timedelta

DATA_DIR = "/home/anselmodanilo/dev/gruporevise_demo/autolub_enterprise_demo/data"

def create_erp_db():
    db_path = os.path.join(DATA_DIR, "erp", "erp_producao.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Criar tabelas
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY,
        razao_social TEXT,
        cnpj TEXT,
        tier TEXT,
        regiao TEXT
    );
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        categoria TEXT,
        preco_base REAL
    );
    CREATE TABLE IF NOT EXISTS vendedores (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        regiao TEXT
    );
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        vendedor_id INTEGER,
        data_emissao TEXT,
        status TEXT,
        valor_total REAL,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(vendedor_id) REFERENCES vendedores(id)
    );
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL,
        desconto REAL,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    );
    """)

    # Inserir Dados Falsos
    clientes = [
        (101, "Transportadora Rápido Sudeste Ltda", "11.111.111/0001-11", "Tier 1", "Sudeste"),
        (102, "Viação Norte Sul S.A", "22.222.222/0001-22", "Tier 2", "Sul"),
        (103, "Auto Peças Central", "33.333.333/0001-33", "Tier 3", "Nordeste"),
        (104, "Logística Brasil Express", "44.444.444/0001-44", "Tier 1", "Centro-Oeste")
    ]
    cursor.executemany("INSERT OR IGNORE INTO clientes VALUES (?, ?, ?, ?, ?)", clientes)

    produtos = [
        (201, "AutoLub Synth Ultra 5W30 (Tambor 200L)", "Sintético", 28.00),
        (202, "AutoLub Mineral Plus 20W50 (Galão 5L)", "Mineral", 15.00),
        (203, "Graxa LubriMax Complexa", "Graxas", 45.00),
        (204, "Aditivo MotorMax Clean", "Aditivos", 12.50)
    ]
    cursor.executemany("INSERT OR IGNORE INTO produtos VALUES (?, ?, ?, ?)", produtos)

    vendedores = [
        (1, "Carlos Silva", "Sudeste"),
        (2, "Mariana Costa", "Sul"),
        (3, "João Mendes", "Nordeste")
    ]
    cursor.executemany("INSERT OR IGNORE INTO vendedores VALUES (?, ?, ?)", vendedores)

    # Gerar pedidos históricos
    start_date = datetime(2026, 1, 1)
    for _ in range(150):
        c_id = random.choice(clientes)[0]
        v_id = random.choice(vendedores)[0]
        p_date = start_date + timedelta(days=random.randint(0, 250))
        status = random.choice(["FATURADO", "PENDENTE_AUDITORIA", "CANCELADO", "ENTREGUE"])
        
        cursor.execute("INSERT INTO pedidos (cliente_id, vendedor_id, data_emissao, status, valor_total) VALUES (?, ?, ?, ?, ?)",
                       (c_id, v_id, p_date.strftime("%Y-%m-%d"), status, 0))
        pedido_id = cursor.lastrowid
        
        valor_total = 0
        for _ in range(random.randint(1, 3)):
            prod = random.choice(produtos)
            qtd = random.randint(10, 500)
            desconto = round(random.uniform(0, 0.15), 2) # Até 15% de desconto
            if prod[2] == 'Sintético' and random.random() < 0.1:
                desconto = round(random.uniform(0.30, 0.45), 2) # Anomalia de desconto
                status = "PENDENTE_AUDITORIA"
            
            preco_final = prod[3] * (1 - desconto)
            valor_total += preco_final * qtd
            
            cursor.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario, desconto) VALUES (?, ?, ?, ?, ?)",
                           (pedido_id, prod[0], qtd, preco_final, desconto))
        
        cursor.execute("UPDATE pedidos SET valor_total = ?, status = ? WHERE id = ?", (valor_total, status, pedido_id))

    # Inserir pedido anômalo de exemplo (Invoice 9874)
    cursor.execute("INSERT INTO pedidos (id, cliente_id, vendedor_id, data_emissao, status, valor_total) VALUES (9874, 101, 1, '2026-09-02', 'PENDENTE_AUDITORIA', 367500.00)")
    cursor.execute("INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario, desconto) VALUES (9874, 201, 15000, 24.50, 0.4167)")

    conn.commit()
    conn.close()
    print(f"ERP Database criado em {db_path}")

def create_jira_mock():
    jira_path = os.path.join(DATA_DIR, "jira", "tickets.json")
    tickets = [
        {
            "ticket_id": "OPS-4592",
            "tipo": "Incidente",
            "status": "Em Andamento",
            "prioridade": "Alta",
            "criado_em": "2026-09-08T10:00:00Z",
            "descricao": "Atraso na entrega do pedido 9874 para Transportadora Rápido Sudeste. Caminhão retido na barreira fiscal.",
            "comentarios": [
                {"autor": "Logistica", "texto": "Aguardando liberação da SEFAZ."}
            ]
        },
        {
            "ticket_id": "OPS-4598",
            "tipo": "Qualidade",
            "status": "Aberto",
            "prioridade": "Crítica",
            "criado_em": "2026-09-09T14:30:00Z",
            "descricao": "Desvio de lote identificado no AutoLub Synth Ultra 5W30. Lote LUB-2609 apresenta viscosidade abaixo do padrão.",
            "comentarios": [
                {"autor": "Laboratório", "texto": "Amostra enviada para reanálise."}
            ]
        }
    ]
    with open(jira_path, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)
    print(f"Jira tickets criado em {jira_path}")

def create_contracts():
    doc1_path = os.path.join(DATA_DIR, "docs", "CTR-2025-BASEOIL-PETROQUIMICA.txt")
    doc2_path = os.path.join(DATA_DIR, "docs", "SLA-DISTRIBUICAO-LOGISTICA-2026.txt")
    
    with open(doc1_path, "w", encoding="utf-8") as f:
        f.write("CONTRATO DE FORNECIMENTO DE ÓLEO BÁSICO\n\n")
        f.write("Fornecedor: PetroQuímica Global S.A.\n")
        f.write("Comprador: AutoLub Brasil (Grupo)\n\n")
        f.write("CLÁUSULA QUARTA - DO PREÇO E REAJUSTE\n")
        f.write("4.1. O preço do litro do óleo básico será indexado ao barril de Brent.\n")
        f.write("4.2. Fica estabelecida a cláusula de reajuste cambial atrelada à variação do Dólar Americano (USD), a ser aplicada a cada 60 dias (sessenta dias) em caso de flutuação superior a 5%.\n\n")
        f.write("CLÁUSULA QUINTA - VIGÊNCIA\n")
        f.write("5.1. Este contrato tem validade até 31/12/2026.\n")

    with open(doc2_path, "w", encoding="utf-8") as f:
        f.write("ACORDO DE NÍVEL DE SERVIÇO (SLA) - LOGÍSTICA\n\n")
        f.write("Operador Logístico: LogBrasil Express\n\n")
        f.write("1. TEMPO DE ENTREGA (LEAD TIME)\n")
        f.write("1.1. Região Sudeste: 48 horas úteis.\n")
        f.write("1.2. Região Sul: 72 horas úteis.\n")
        f.write("1.3. Em caso de atraso superior a 24 horas do prazo estabelecido, incidirá multa de 2% sobre o valor do frete.\n")
    
    print(f"Documentos criados em {os.path.join(DATA_DIR, 'docs')}")

if __name__ == "__main__":
    create_erp_db()
    create_jira_mock()
    create_contracts()

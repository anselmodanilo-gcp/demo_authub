#!/bin/bash

# Acessa a pasta do projeto
cd /home/anselmodanilo/dev/gruporevise_demo/autolub_enterprise_demo

# Cria um ambiente virtual (se não existir)
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativa o ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instala as dependências
echo "Instalando dependências (isso pode levar alguns instantes na primeira vez)..."
pip install -r requirements.txt

# Executa o Streamlit
echo "Iniciando o AutoLub Enterprise Co-Pilot..."
streamlit run app.py

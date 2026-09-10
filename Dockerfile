# Use uma imagem Python oficial e leve
FROM python:3.11-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação e a pasta de dados mockados (bancos SQLite, TXTs, etc)
COPY . .

# Expõe as portas do FastAPI (8080) e do Streamlit (8501)
# O Cloud Run expõe por padrão a porta 8080, então vamos configurar o Streamlit para rodar nela se for a UI principal
EXPOSE 8080

# Comando para rodar o Streamlit na porta 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]

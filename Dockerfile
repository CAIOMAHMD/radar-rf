# Usa uma imagem oficial do Python leve
FROM python:3.10-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala ferramentas básicas do sistema para evitar erros de rede
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*
# Copia o arquivo de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo da sua pasta para dentro do container
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o Radar ao iniciar o container
ENTRYPOINT ["streamlit", "run", "interface.py", "--server.port=8501", "--server.address=0.0.0.0"]
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Atualiza o pip e instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements.txt primeiro (melhor para cache)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY analise_gps.py .

# Expõe a porta (Railway vai sobrescrever)
EXPOSE 8080

# Comando para rodar a aplicação
CMD ["python", "-u", "analise_gps.py"]

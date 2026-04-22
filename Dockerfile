FROM python:3.11-slim

WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY analise_gps.py .

# Railway define a porta automaticamente
ENV PORT=8080
EXPOSE 8080

# Executa a aplicação
CMD ["python", "analise_gps.py"]

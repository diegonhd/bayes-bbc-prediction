# ==============================================================================
# Estagio 1: Construtor (Builder)
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Instala ferramentas essenciais de compilacao se necessarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cria ambiente virtual dedicado para isolar os pacotes
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Estagio 2: Runtime Minimo e Seguro (Runner)
# ==============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Cria usuario sem privilegios administrativos (seguranca em producao)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copia o ambiente virtual completo do estagio builder
COPY --from=builder /opt/venv /opt/venv

# Garante que o ambiente virtual seja utilizado por padrao
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copia apenas os artefatos necessarios para a execucao
COPY app/ ./app
COPY models/ ./models

# Ajusta as permissoes para o usuario nao-root
RUN chown -R appuser:appgroup /app
USER appuser

# Exposicao da porta padrao da API
EXPOSE 8000

# Healthcheck para monitorar a saude da aplicacao em producao
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando padrao de inicializacao do servidor ASGI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

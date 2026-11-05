# ==========================================
# Dockerfile - devops-python-api
# ==========================================
FROM python:3.12-slim

# Evita geração de bytecode .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Diretório de trabalho na imagem
WORKDIR /app

# Criação de usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalação das dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cópia do código-fonte da aplicação
COPY . .

# Permissões apropriadas para o usuário não-root
RUN chown -R appuser:appuser /app
USER appuser

# Exposição da porta configurada
EXPOSE 5000

# Healthcheck do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Comando de inicialização usando Gunicorn (servidor WSGI de produção)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]

FROM python:3.12-alpine

# Instala dependências do sistema
RUN apk add --no-cache \
    build-base \
    libpq \
    linux-headers \
    libffi-dev \
    openssl-dev \
    curl

# Diretório de trabalho
WORKDIR /app

# Copia o restante da aplicação
COPY . .

# Instala as dependências do projeto
RUN pip install uv && \
    uv sync

# Copia o script de entrada e torna-o executável
COPY /entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Define variável de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]


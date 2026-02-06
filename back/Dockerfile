FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]

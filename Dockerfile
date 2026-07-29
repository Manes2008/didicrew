# MIT License
# Copyright (c) 2026 Manes2008/didicrew

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Docker CLI và Docker Compose phục vụ Docker-out-of-Docker
COPY --from=docker:latest /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker/compose:latest /usr/local/bin/docker-compose /usr/local/bin/docker-compose
RUN mkdir -p /usr/local/lib/docker/cli-plugins && \
    ln -s /usr/local/bin/docker-compose /usr/local/lib/docker/cli-plugins/docker-compose

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY policies ./policies

RUN uv pip install --system .

EXPOSE 8338

CMD ["python", "-m", "src.main"]

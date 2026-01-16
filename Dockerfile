FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY bin ./bin

RUN uv pip install --system .

EXPOSE 8338

CMD ["python", "-m", "src.main"]

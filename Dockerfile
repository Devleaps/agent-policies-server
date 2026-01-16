FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY bin ./bin

RUN uv pip install --system devleaps-agent-policies httpx bashlex
RUN uv pip install --system --no-deps .

EXPOSE 8338

CMD ["python", "-m", "src.main"]

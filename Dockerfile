FROM python:3.12-slim

ARG OPA_VERSION=1.12.3
ADD https://openpolicyagent.org/downloads/v${OPA_VERSION}/opa_linux_amd64_static /usr/local/bin/opa
RUN chmod +x /usr/local/bin/opa

RUN apt-get update && apt-get install -y --no-install-recommends \
    libatomic1 \
    git \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

# Install dependencies only (cached when pyproject.toml/uv.lock unchanged)
COPY pyproject.toml uv.lock ./
RUN uv export --no-hashes > requirements.txt && \
    uv pip install --system -r requirements.txt && \
    rm requirements.txt

# Copy source code and install local package without dependencies
COPY src ./src
COPY policies ./policies
RUN uv pip install --system --no-deps .

ARG GIT_SHA=unknown
ARG VERSION=unknown
ENV GIT_SHA=${GIT_SHA}
ENV VERSION=${VERSION}
ENV POLICY_SERVER_HOST=0.0.0.0

EXPOSE 8338

CMD ["python", "-m", "src.main"]

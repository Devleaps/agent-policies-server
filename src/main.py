#!/usr/bin/env python3
"""Run the OPA bundle server."""

import uvicorn

from src.config import settings
from src.server.server import app


def main():
    print(f"Starting bundle server on http://{settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()

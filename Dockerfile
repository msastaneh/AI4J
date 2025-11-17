# Multi-arch slim Python base
FROM python:3.12-slim

WORKDIR /app

# System deps (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
	curl \
    python3-dev \
    portaudio19-dev \
    bash \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Python runtime settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app 

RUN pip install --no-cache-dir \
    python-dotenv \
    requests \
    fastapi[standard] \
    pydantic \
	aiohttp \
	pandas \
	jira \
	ollama \
	langchain_ollama \
	langchain-community==0.3.0 \
	langchain==0.3.0 \
	atlassian-python-api
	
# Copy the agent code (Docker build context should be ./med-agent - the current directory should be outisde med-agent)
COPY . .

# Default port; override with -e PORT=8000 or similar
EXPOSE 8000

CMD ["uvicorn", "ai-jira:app", "--reload","--host", "0.0.0.0", "--port", "8000"]

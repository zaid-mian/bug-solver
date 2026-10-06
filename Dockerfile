FROM python:3.12-slim

# git CLI is required by the SubprocessGitManager adapter
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

# The agent under test lives in /target (mount it at runtime).
# Ollama is expected on the host: pass -e OLLAMA_HOST=host.docker.internal
# (or --network host on Linux).
ENTRYPOINT ["bugsolver"]
CMD ["--help"]

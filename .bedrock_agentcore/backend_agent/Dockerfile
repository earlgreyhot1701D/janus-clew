FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    AWS_REGION=us-east-1 \
    AWS_DEFAULT_REGION=us-east-1

# Copy requirements (build context is already backend/)
COPY requirements.txt requirements.txt

# Install dependencies
RUN uv pip install -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore

# Copy project files
COPY . .

# Set permissions
RUN chown -R bedrock_agentcore:bedrock_agentcore /app

USER bedrock_agentcore

EXPOSE 8000 8080

# Simple, direct CMD that works in ARM64
CMD ["python", "-m", "agent"]

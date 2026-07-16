FROM python:3.14.6-trixie

# Create normal (non-root) user
RUN groupadd -g 1000 moe \
    && useradd -u 1000 -g moe -m -s /bin/bash moe

# Explicitly set HOME and NVM_DIR to prevent Docker path confusion!
ENV HOME=/home/moe
ENV NVM_DIR=$HOME/.nvm

# Setup directories and ensure moe owns ALL of /home/moe
RUN mkdir -p /workspace \
    && chown -R moe:moe /workspace \
    && chown -R moe:moe /home/moe \
    && mkdir -p /workspace/frontend/node_modules /workspace/backend/.venv \
    && chown -R moe:moe /workspace/frontend/node_modules /workspace/backend/.venv

# Switch to moe user
USER moe

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install nvm, corepack and enable pnpm
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.5/install.sh | bash \
    && \. "$HOME/.nvm/nvm.sh" \
    && nvm install 26 \
    && npm install -g corepack \
    && corepack enable pnpm

CMD ["sleep", "infinity"]

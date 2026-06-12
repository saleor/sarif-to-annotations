FROM docker.io/python:3.14.6-slim-trixie@sha256:c79315c9ba2403aecb221fb9090486be9af43cdc2372959ca7ccf6b17ebe9912 AS deps

COPY \
  --from=ghcr.io/astral-sh/uv:0.11.8@sha256:3b7b60a81d3c57ef471703e5c83fd4aaa33abcd403596fb22ab07db85ae91347 \
  /uv /uvx /bin/

WORKDIR /app

ADD ./pyproject.toml ./README.md ./uv.lock /app/
ADD ./src/ ./src/

# Keeps the settings in env var as otherwise 'uv run' will
# try to reinstall the project
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=0 \
    UV_SYSTEM_PYTHON=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-editable

FROM docker.io/python:3.14.6-slim-trixie@sha256:c79315c9ba2403aecb221fb9090486be9af43cdc2372959ca7ccf6b17ebe9912 AS final 

WORKDIR /config

COPY --from=deps \
  /usr/local/bin/sarif-to-annotations \
  /usr/local/bin/

COPY --from=deps \
  /usr/local/lib/python3.14/site-packages/ \
  /usr/local/lib/python3.14/site-packages/

FROM final AS dev

ENTRYPOINT [ "/usr/local/bin/sarif-to-annotations" ]

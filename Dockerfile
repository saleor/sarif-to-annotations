FROM docker.io/python:3.14.5-slim-trixie@sha256:7a500125bc50693f2214e842a621440a1b1b9cbb2188f74ab045d29ed2ea5856 AS deps

COPY \
  --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a \
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

FROM docker.io/python:3.14.5-slim-trixie@sha256:7a500125bc50693f2214e842a621440a1b1b9cbb2188f74ab045d29ed2ea5856 AS final 

WORKDIR /config

COPY --from=deps \
  /usr/local/bin/sarif-to-annotations \
  /usr/local/bin/

COPY --from=deps \
  /usr/local/lib/python3.14/site-packages/ \
  /usr/local/lib/python3.14/site-packages/

FROM final AS dev

ENTRYPOINT [ "/usr/local/bin/sarif-to-annotations" ]

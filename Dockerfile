FROM docker.io/python:3.14.3-slim-trixie@sha256:fb83750094b46fd6b8adaa80f66e2302ecbe45d513f6cece637a841e1025b4ca AS deps

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

FROM docker.io/python:3.14.5-slim-trixie@sha256:af79f947dee1c929919b0488d20db7200d8737e00f68ee4abeef1fcf1fe05939 AS final 

WORKDIR /config

COPY --from=deps \
  /usr/local/bin/sarif-to-annotations \
  /usr/local/bin/

COPY --from=deps \
  /usr/local/lib/python3.14/site-packages/ \
  /usr/local/lib/python3.14/site-packages/

FROM final AS dev

ENTRYPOINT [ "/usr/local/bin/sarif-to-annotations" ]

FROM docker.io/python:3.15.0a8-slim-trixie@sha256:0818681082dee53faaa7c5376a18ee2c88f5bccd2191d4816dfeea8eb91bcf59 AS deps

COPY \
  --from=ghcr.io/astral-sh/uv:0.10.8@sha256:88234bc9e09c2b2f6d176a3daf411419eb0370d450a08129257410de9cfafd2a \
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

FROM docker.io/python:3.15.0a8-slim-trixie@sha256:0818681082dee53faaa7c5376a18ee2c88f5bccd2191d4816dfeea8eb91bcf59 AS final 

WORKDIR /config

COPY --from=deps \
  /usr/local/bin/sarif-to-annotations \
  /usr/local/bin/

COPY --from=deps \
  /usr/local/lib/python3.14/site-packages/ \
  /usr/local/lib/python3.14/site-packages/

FROM final AS dev

ENTRYPOINT [ "/usr/local/bin/sarif-to-annotations" ]

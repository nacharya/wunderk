FROM golang:1.24.2-bookworm AS builder

# Update and install only necessary packages, then clean up to reduce vulnerabilities
RUN apt-get update --allow-releaseinfo-change && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends bash git net-tools curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/build
COPY xdnext /app/build/xdnext
WORKDIR /app/build/xdnext
RUN go mod download
RUN go build -o /app/xdnext
RUN chmod +x /app/xdnext


FROM python:3.12.3-slim-bookworm

RUN apt-get update --allow-releaseinfo-change && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends bash net-tools curl procps && \
    apt-get purge -y gcc g++ build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN mkdir -p /app/data
RUN chmod 777 /app/data
WORKDIR /app

COPY --from=builder /app/xdnext /app/xdnext
COPY bootup.sh /app/bootup.sh
COPY main.sh /app/main.sh
COPY xdnext/xdnext.json /app/xdnext.json

# Revise
COPY .env /app/.env
RUN mkdir -p /root/.streamlit
COPY dotstreamlit/ /root/.streamlit/


COPY wui/ /app/wui/
WORKDIR /app
# set up the venv
RUN uv venv --python=python3.12 .venv
RUN . /app/.venv/bin/activate
RUN uv pip install --no-cache-dir -r /app/wui/requirements.txt

ENV PATH="/app/wui/.venv/bin:$PATH"
WORKDIR /app/wui
RUN uv sync --frozen --no-cache

# wunderk ports
EXPOSE 9701 9702

WORKDIR /app

CMD [ "/app/bootup.sh" ]

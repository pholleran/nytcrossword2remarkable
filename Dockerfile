FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ]; then \
        RMAPI_ARCH=arm64; \
    elif [ "$ARCH" = "x86_64" ]; then \
        RMAPI_ARCH=amd64; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    wget -O /tmp/rmapi.tar.gz https://github.com/ddvk/rmapi/releases/latest/download/rmapi-linux-${RMAPI_ARCH}.tar.gz && \
    tar -xzf /tmp/rmapi.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/rmapi && \
    rm /tmp/rmapi.tar.gz

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY . /usr/src/app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    mkdir -p /usr/src/app/output /usr/src/app/logs /home/runner/.config/rmapi && \
    chmod 755 /usr/src/app/output /usr/src/app/logs /home/runner/.config/rmapi

ENV APP_ROOT=/usr/src/app
ENV PYTHONPATH=/usr/src/app
ENV OUTPUT_DIR=/usr/src/app/output
ENV LOG_DIR=/usr/src/app/logs
ENV REMARKABLE_FOLDER="NYT Crosswords"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "/usr/src/app/main.py"]

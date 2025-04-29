# 多平台支持的 Dockerfile (Linux, macOS, Windows)
# 使用 BuildX 多架構構建支持 (x86, arm64)
FROM --platform=${BUILDPLATFORM} python:3.10-slim AS builder

# 設置工作目錄
WORKDIR /app

# 複製並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 多架構構建階段
FROM --platform=${TARGETPLATFORM} python:3.10-slim

# 设置环境变量，确保 Python 输出不被缓存
ENV PYTHONUNBUFFERED=1
# 设置时区为 UTC，確保跨平台時間一致性
ENV TZ=UTC

# 添加標籤信息
LABEL maintainer="Frank Chen <qwer4488999@gmail.com>"
LABEL org.opencontainers.image.title="File Indexer"
LABEL org.opencontainers.image.description="A file indexer that runs in Docker with multi-arch support"
LABEL org.opencontainers.image.source="https://github.com/haunchen/file_indexer"

# 安装额外的依赖以支持跨架构
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 複製已安裝的 Python 包
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 複製應用程序文件
COPY . .

# 創建掛載點，用於訪問主機文件系統
VOLUME ["/data"]

# 指定entrypoint腳本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

# 容器启动时运行索引器
CMD ["python", "indexer.py"]
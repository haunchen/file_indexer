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
# 设置时区为 UTC，确保跨平台时间一致性
ENV TZ=UTC

WORKDIR /app

# 複製已安裝的 Python 包
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 複製應用程序文件
COPY . .

# 默認配置，可以在構建或運行時覆蓋
# COPY config.json /app/config.json

# 容器启动时运行索引器
CMD ["python", "indexer.py"]
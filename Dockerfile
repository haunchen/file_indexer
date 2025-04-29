FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 默认配置，可以在构建或运行时覆盖
COPY config.json /app/config.json

# 容器启动时运行索引器
CMD ["python", "indexer.py"]
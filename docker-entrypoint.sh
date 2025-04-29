#!/bin/bash
set -e

# 確保配置文件存在
if [ ! -f /app/config.json ]; then
    echo "創建默認配置文件..."
    cat > /app/config.json << EOF
{
  "device_id": "docker-container",
  "scan_paths": ["/data"],
  "upload_url": "http://yourserver.com/upload",
  "exclude_dirs": [".git", "node_modules", "__pycache__"],
  "exclude_extensions": [".tmp", ".log", ".bak"]
}
EOF
    echo "請根據需要修改配置文件"
fi

# 如果傳入的第一個參數不是python，則執行該命令
if [ "$1" != "python" ]; then
    exec "$@"
    exit
fi

# 執行默認命令
exec python indexer.py "$@"
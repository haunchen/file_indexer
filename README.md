# 檔案索引器 (File Indexer)

![CI/CD Pipeline](https://github.com/haunchen/file_indexer/actions/workflows/ci-cd.yml/badge.svg)
[![codecov](https://codecov.io/gh/haunchen/file_indexer/branch/main/graph/badge.svg)](https://codecov.io/gh/haunchen/file_indexer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Hub](https://img.shields.io/docker/pulls/haunchen/file_indexer.svg)](https://hub.docker.com/r/haunchen/file_indexer)

這個應用程式能夠掃描指定的目錄，建立檔案索引，並將結果儲存在 SQLite 資料庫中。同時支援將索引上傳到遠端伺服器。

## 功能

- 📂 掃描指定目錄下的所有檔案
- 🗃️ 排除特定目錄和檔案類型
- 💾 將檔案索引保存到 SQLite 資料庫
- 🔄 支援將索引上傳到遠端伺服器
- 🔧 可配置的排除規則
- 🖥️ 跨平台支援 (Windows, macOS, Linux)
- 📁 支援掃描多個路徑
- 🔒 智能識別隱藏檔案和目錄
- 🐳 提供多架構 Docker 映像 (x86/amd64, ARM64)

## 安裝需求

```bash
pip install requests
```

## 使用方法

1. 首次運行程式會生成預設的 `config.json` 檔案
   ```bash
   python indexer.py
   ```

2. 依照需求編輯 `config.json` 配置檔
   ```json
   {
       "device_id": "您的電腦名稱",
       "scan_paths": [
           "/Users/your_username/Documents",
           "/Users/your_username/Downloads"
       ],
       "upload_url": "http://yourserver.com/upload",
       "exclude_dirs": [".git", "node_modules", "__pycache__"],
       "exclude_extensions": [".tmp", ".log"]
   }
   ```

3. 再次運行程式以執行檔案掃描與索引
   ```bash
   python indexer.py
   ```

## Docker 使用方法

您可以使用 Docker 容器運行此應用程式，無需安裝 Python 環境：

1. 拉取 Docker 鏡像（支援 x86/amd64 和 ARM64 架構）
   ```bash
   docker pull haunchen/file-indexer:latest
   ```
   
   Docker 會自動選擇適合您系統架構的映像檔。

2. 執行 Docker 容器（將本地目錄掛載到容器中以進行掃描）
   
   **在 Linux/macOS 系統上：**
   ```bash
   docker run -v /path/to/scan:/data -v $(pwd):/app/output haunchen/file-indexer
   ```
   
   **在 Windows 系統上 (PowerShell)：**
   ```powershell
   docker run -v ${PWD}\path\to\scan:/data -v ${PWD}:/app/output haunchen/file-indexer
   ```
   
   **在 Windows 系統上 (Command Prompt)：**
   ```cmd
   docker run -v %cd%\path\to\scan:/data -v %cd%:/app/output haunchen/file-indexer
   ```

3. 自行構建 Docker 鏡像
   
   **構建單一架構映像檔：**
   ```bash
   docker build -t file-indexer .
   ```
   
   **構建多架構映像檔 (需要 Docker BuildX)：**
   ```bash
   # 建立並使用 buildx 構建器
   docker buildx create --name multiarch-builder --use
   
   # 構建並推送多架構映像檔
   docker buildx build --platform linux/amd64,linux/arm64 -t your-username/file-indexer:latest --push .
   ```

## 配置選項

| 選項 | 說明 |
|------|------|
| `device_id` | 設備識別碼，用於識別上傳來源，預設使用電腦名稱 |
| `scan_paths` | 要掃描的目錄路徑列表，支援多個路徑 |
| `upload_url` | 索引上傳的目標 URL |
| `exclude_dirs` | 要排除的目錄名稱列表 |
| `exclude_extensions` | 要排除的檔案副檔名列表 |

## 資料庫結構

索引資料保存在 `file_index.db` SQLite 資料庫中，包含以下欄位：

- `id`: 自動遞增的主鍵
- `path`: 檔案的完整路徑
- `name`: 檔案名稱
- `size`: 檔案大小 (位元組)
- `modified_time`: 最後修改時間 (Unix 時間戳)

## CI/CD 配置

本專案使用 GitHub Actions 自動構建和部署：

1. 每次推送到 `main` 分支時自動運行測試
2. 發布新版本時自動構建 Docker 鏡像並推送到 Docker Hub

### 設置 GitHub Secrets

若要啟用 Docker Hub 自動推送，需在 GitHub 倉庫設置中添加以下密鑰：

1. 在 Docker Hub 獲取訪問令牌：
   - 登錄 [Docker Hub](https://hub.docker.com/)
   - 點擊右上角頭像 -> Account Settings -> Security
   - 點擊 "New Access Token"，提供描述並選擇適當權限
   - 生成並複製令牌（這是唯一能看到令牌的機會）

2. 在 GitHub 倉庫設置 Secrets：
   - 訪問倉庫的 Settings -> Secrets and variables -> Actions
   - 點擊 "New repository secret" 並添加：
     * `DOCKERHUB_USERNAME`: 您的 Docker Hub 用戶名
     * `DOCKERHUB_TOKEN`: 您的 Docker Hub 訪問令牌

完成後，GitHub Actions 工作流程將能夠自動構建並推送 Docker 鏡像。

## 提示

- 程式自動偵測並排除所有隱藏檔案和目錄 (Windows系統使用文件屬性判斷，Unix-like系統包含以 `.` 開頭的檔案)
- 若要啟用上傳功能，請取消程式碼最後兩行的註解
- 程式會自動檢查指定的路徑是否存在，若不存在會顯示警告並跳過

## 注意事項

- 若要掃描的目錄中有大量檔案，掃描過程可能需要較長時間
- 請確保您有足夠的權限存取要掃描的目錄

## 版本更新

- 2025/04/29: 新增跨平台支援、多路徑掃描功能和智能檔案過濾
- 2025/04/30: 添加 Docker 支援及 CI/CD 自動部署功能
- 2025/04/30: 增加多架構 Docker 映像支援 (x86/amd64, ARM64)，確保在不同作業系統上的兼容性
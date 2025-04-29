# 檔案索引器 (File Indexer)

![CI/CD Pipeline](https://github.com/haunchen/file_indexer/actions/workflows/ci-cd.yml/badge.svg)
[![codecov](https://codecov.io/gh/haunchen/file_indexer/branch/main/graph/badge.svg)](https://codecov.io/gh/haunchen/file_indexer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
2. 測試通過後自動部署到目標伺服器

### 部署設定

要啟用自動部署功能，需在 GitHub 專案設定中新增以下 Secrets：

- `SSH_PRIVATE_KEY`: 用於連接到部署伺服器的 SSH 私鑰
- `DEPLOY_HOST`: 部署伺服器的主機名稱或 IP 地址
- `DEPLOY_USER`: SSH 登入用戶名
- `DEPLOY_PATH`: 伺服器上的部署路徑 (例如: `/opt/file_indexer`)

### 手動部署指南

如不使用 GitHub Actions，也可以按照以下步驟手動部署：

1. 使用 `rsync` 將程式碼傳輸到伺服器
   ```bash
   rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.db' . user@your-server:/path/to/destination
   ```

2. 在伺服器上安裝相依套件
   ```bash
   cd /path/to/destination
   pip install -r requirements.txt
   ```

3. 設定配置文件並運行
   ```bash
   python indexer.py
   ```

## 提示

- 程式自動偵測並排除所有隱藏檔案和目錄 (Windows系統使用文件屬性判斷，Unix-like系統包含以 `.` 開頭的檔案)
- 若要啟用上傳功能，請取消程式碼最後兩行的註解
- 程式會自動檢查指定的路徑是否存在，若不存在會顯示警告並跳過

## 注意事項

- 若要掃描的目錄中有大量檔案，掃描過程可能需要較長時間
- 請確保您有足夠的權限存取要掃描的目錄

## 版本更新

- 2025/04/29: 新增跨平台支援、多路徑掃描功能和智能檔案過濾
- 2025/04/29: 新增自動部署功能
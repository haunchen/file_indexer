import os
import sqlite3
import json
import requests
import platform
import sys
from pathlib import Path

CONFIG_FILE = "config.json"
DB_FILE = "file_index.db"

def is_hidden_file(path):
    """跨平台判斷是否為隱藏文件"""
    # Windows 用文件屬性判斷
    if sys.platform == 'win32':
        import ctypes
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            return attrs != -1 and bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN
        except (AttributeError, OSError):
            return False
    # Unix-like 系統（包含 macOS 和 Linux）
    else:
        return os.path.basename(path).startswith('.')

def is_hidden_dir(path):
    """跨平台判斷是否為隱藏目錄"""
    return is_hidden_file(path)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "device_id": platform.node(),
            "scan_paths": [str(Path.home())],  # 修改為 scan_paths 而非 scan_path
            "upload_url": "http://yourserver.com/upload",
            "exclude_dirs": [],
            "exclude_extensions": []
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=2)
        print(f"請編輯 {CONFIG_FILE} 設定後再執行")
        sys.exit(0)
    with open(CONFIG_FILE) as f:
        return json.load(f)

def init_db(conn):
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS files")
    c.execute("""
        CREATE TABLE files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            name TEXT,
            size INTEGER,
            modified_time REAL
        )
    """)
    conn.commit()

def scan_files(scan_path, conn, exclude_dirs, exclude_extensions):
    c = conn.cursor()
    scan_path = Path(scan_path)  # 使用 Path 對象處理路徑
    
    for root, dirs, files in os.walk(scan_path):
        root_path = Path(root)
        
        # 過濾目錄：排除隱藏目錄 + config 排除的
        dirs[:] = [d for d in dirs if not is_hidden_dir(root_path / d) and d not in exclude_dirs]
        
        for fname in files:
            try:
                file_path = root_path / fname
                
                # 排除隱藏檔案
                if is_hidden_file(file_path):
                    continue
                    
                # 過濾副檔名
                ext = os.path.splitext(fname)[1].lower()
                if ext in exclude_extensions:
                    continue
                
                # 使用 Path 對象獲取完整路徑，然後轉為字符串存儲
                full_path = str(file_path)
                stat = os.stat(full_path)
                c.execute("INSERT INTO files (path, name, size, modified_time) VALUES (?, ?, ?, ?)", (
                    full_path, fname, stat.st_size, stat.st_mtime
                ))
            except Exception as e:
                print(f"錯誤讀取檔案：{fname} - {e}")
    conn.commit()

def upload_db(upload_url, device_id):
    with open(DB_FILE, "rb") as f:
        files = {
            "file": (f"{device_id}_file_index.db", f, "application/octet-stream"),
        }
        data = {"device_id": device_id}
        try:
            response = requests.post(upload_url, files=files, data=data)
            print(f"[上傳成功] {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[上傳失敗] {e}")

if __name__ == "__main__":
    config = load_config()
    
    conn = sqlite3.connect(DB_FILE)
    init_db(conn)
    scan_paths = config.get("scan_paths", [])
    exclude_dirs = config.get("exclude_dirs", [])
    exclude_extensions = [ext.lower() for ext in config.get("exclude_extensions", [])]
    
    if not scan_paths:
        print("警告：沒有設定掃描路徑，請在 config.json 中配置 scan_paths")
        sys.exit(1)
    
    for path in scan_paths:
        path_obj = Path(path)
        if not path_obj.exists():
            print(f"⚠️  路徑不存在：{path}，跳過")
            continue
            
        print(f"🔍 掃描：{path}")
        scan_files(path, conn, exclude_dirs, exclude_extensions)
    conn.close()
    
    # print("掃描完成，開始上傳...")
    # upload_db(config["upload_url"], config["device_id"])

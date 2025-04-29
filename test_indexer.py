import unittest
import os
import sqlite3
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from indexer import load_config, init_db, scan_files, is_hidden_file, is_hidden_dir


class TestFileIndexer(unittest.TestCase):
    def setUp(self):
        # 创建临时测试目录和文件
        self.test_dir = tempfile.mkdtemp()
        self.config_file = "config.json"
        self.db_file = "file_index.db"
        
        # 备份现有配置文件
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.original_config = f.read()
        else:
            self.original_config = None
            
        # 创建测试配置
        self.test_config = {
            "device_id": "test-device",
            "scan_paths": [self.test_dir],
            "upload_url": "http://test-server.com/upload",
            "exclude_dirs": ["excluded_dir"],
            "exclude_extensions": [".tmp"]
        }
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
            
        # 创建测试文件结构
        os.makedirs(os.path.join(self.test_dir, "normal_dir"))
        os.makedirs(os.path.join(self.test_dir, "excluded_dir"))
        
        # 创建几个测试文件
        with open(os.path.join(self.test_dir, "test_file.txt"), 'w') as f:
            f.write("test content")
        with open(os.path.join(self.test_dir, "normal_dir", "nested_file.txt"), 'w') as f:
            f.write("nested content")
        with open(os.path.join(self.test_dir, "excluded_dir", "excluded_file.txt"), 'w') as f:
            f.write("should not be indexed")
        with open(os.path.join(self.test_dir, "test_file.tmp"), 'w') as f:
            f.write("should not be indexed")
        
        # 初始化测试数据库
        self.conn = sqlite3.connect(self.db_file)
    
    def tearDown(self):
        # 清理测试资源
        self.conn.close()
        shutil.rmtree(self.test_dir)
        
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
            
        # 恢复原始配置
        if self.original_config is not None:
            with open(self.config_file, 'w') as f:
                f.write(self.original_config)
        elif os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    def test_load_config(self):
        config = load_config()
        self.assertEqual(config["device_id"], "test-device")
        self.assertEqual(config["scan_paths"], [self.test_dir])
    
    def test_init_db(self):
        init_db(self.conn)
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
        self.assertIsNotNone(cursor.fetchone())
    
    def test_scan_files(self):
        init_db(self.conn)
        exclude_dirs = self.test_config["exclude_dirs"]
        exclude_extensions = self.test_config["exclude_extensions"]
        
        scan_files(self.test_dir, self.conn, exclude_dirs, exclude_extensions)
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        
        # 期望找到2个文件：test_file.txt和normal_dir/nested_file.txt
        self.assertEqual(file_count, 2)
        
        # 检查是否排除了指定文件
        cursor.execute("SELECT COUNT(*) FROM files WHERE name = 'excluded_file.txt'")
        self.assertEqual(cursor.fetchone()[0], 0)
        
        # 检查是否排除了指定扩展名
        cursor.execute("SELECT COUNT(*) FROM files WHERE path LIKE '%.tmp'")
        self.assertEqual(cursor.fetchone()[0], 0)
    
    def test_is_hidden_file(self):
        # 创建一个隐藏文件用于测试
        hidden_file = os.path.join(self.test_dir, ".hidden_file")
        with open(hidden_file, 'w') as f:
            f.write("hidden content")
            
        self.assertTrue(is_hidden_file(hidden_file))
        self.assertFalse(is_hidden_file(os.path.join(self.test_dir, "test_file.txt")))
    
    def test_is_hidden_dir(self):
        # 创建一个隐藏目录用于测试
        hidden_dir = os.path.join(self.test_dir, ".hidden_dir")
        os.makedirs(hidden_dir)
            
        self.assertTrue(is_hidden_dir(hidden_dir))
        self.assertFalse(is_hidden_dir(os.path.join(self.test_dir, "normal_dir")))


if __name__ == '__main__':
    unittest.main()
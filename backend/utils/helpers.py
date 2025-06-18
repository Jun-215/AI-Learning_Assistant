"""
工具函数模块
"""
import os
import logging

def setup_logging():
    """设置日志配置"""
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)

def ensure_directories(directories):
    """确保目录存在"""
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_file_extension(filename):
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def is_supported_file(filename):
    """检查是否为支持的文件类型"""
    supported_extensions = ['.pdf', '.txt', '.md', '.doc', '.docx']
    return get_file_extension(filename) in supported_extensions

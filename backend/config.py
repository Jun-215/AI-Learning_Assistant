import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 阿里千问API配置
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', 'your-api-key-here')
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # 知识库配置
    KNOWLEDGE_BASE_PATH = 'knowledge_base'

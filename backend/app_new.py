"""
重构后的Flask应用主文件
模块化设计，将原有的大型app.py拆分为多个独立模块
"""
from flask import Flask
from flask_cors import CORS
import dashscope
from config import Config

# 导入模型
from models.knowledge_base import KnowledgeBase

# 导入路由初始化函数
from routes.chat import init_chat_routes
from routes.document import init_document_routes  
from routes.search import init_search_routes
from routes.health import init_health_routes

# 导入工具函数
from utils.helpers import setup_logging, ensure_directories

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app)
    
    # 设置日志
    setup_logging()
    
    # 配置阿里千问API
    dashscope.api_key = app.config['DASHSCOPE_API_KEY']
    
    # 确保必要的目录存在
    ensure_directories([
        app.config['UPLOAD_FOLDER'],
        app.config['KNOWLEDGE_BASE_PATH']
    ])
    
    # 初始化知识库（作为应用上下文的一部分）
    kb = KnowledgeBase(
        knowledge_base_path=app.config['KNOWLEDGE_BASE_PATH'],
        upload_folder=app.config['UPLOAD_FOLDER']
    )
    
    # 注册路由
    with app.app_context():
        # 初始化并注册各个路由蓝图
        chat_blueprint = init_chat_routes(kb)
        document_blueprint = init_document_routes(kb)
        search_blueprint = init_search_routes(kb)
        health_blueprint = init_health_routes(kb)
        
        app.register_blueprint(chat_blueprint)
        app.register_blueprint(document_blueprint)
        app.register_blueprint(search_blueprint)
        app.register_blueprint(health_blueprint)
    
    return app, kb

# 创建应用实例
app, kb = create_app()

if __name__ == '__main__':
    print("🚀 启动 RAG 系统服务器 - 重构优化版本")
    print(f"📚 知识库文档数量: {len(kb.documents)}")
    
    # 检查语义搜索功能
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        embedding_status = '✓ 已启用' if kb.embedding_model else '✗ 模型加载失败'
    except ImportError:
        embedding_status = '✗ 未安装依赖'
    
    print(f"🔍 语义搜索功能: {embedding_status}")
    print(f"🤖 提示词优化: ✓ 第二阶段优化已启用")
    print(f"🏗️ 架构优化: ✓ 模块化重构完成")
    print("=" * 50)
    print("📁 项目结构:")
    print("├── models/         # 数据模型层")
    print("├── routes/         # 路由控制层")  
    print("├── services/       # 服务业务层")
    print("└── utils/          # 工具函数层")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

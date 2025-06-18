"""
系统健康检查路由
"""
from flask import Blueprint, jsonify

# 创建Blueprint
health_bp = Blueprint('health', __name__)

def init_health_routes(kb):
    """初始化健康检查路由"""
    
    @health_bp.route('/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        # 检查嵌入模型是否可用
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            EMBEDDING_AVAILABLE = True
        except ImportError:
            EMBEDDING_AVAILABLE = False
        
        return jsonify({
            'status': 'healthy',
            'knowledge_base_documents': len(kb.documents),
            'embedding_available': EMBEDDING_AVAILABLE,
            'embedding_model_loaded': kb.embedding_model is not None,
            'optimization_stage': 'stage2_prompt_optimization'
        })
    
    return health_bp

"""
搜索相关路由
"""
from flask import Blueprint, request, jsonify

# 创建Blueprint
search_bp = Blueprint('search', __name__)

def init_search_routes(kb):
    """初始化搜索路由，传入知识库实例"""
    
    @search_bp.route('/api/search', methods=['POST'])
    def search_knowledge_base():
        """知识库搜索接口"""
        data = request.json
        query = data.get('query', '')
        max_results = data.get('max_results', 5)
        
        if not query:
            return jsonify({'error': '查询不能为空'}), 400
        
        results = kb.search(query, max_results=max_results)
        
        return jsonify({
            'results': results,
            'query': query,
            'total_documents': len(kb.documents)
        })
    
    @search_bp.route('/api/search_comparison', methods=['POST'])
    def search_comparison():
        """搜索方法对比接口"""
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': '查询不能为空'}), 400
        
        # 使用不同方法搜索
        keyword_results = kb._keyword_search(query)
        semantic_results = []
        
        # 检查是否支持语义搜索
        if hasattr(kb, 'embedding_model') and kb.embedding_model:
            semantic_results = kb._semantic_search(query)
        
        return jsonify({
            'keyword_results': keyword_results,
            'semantic_results': semantic_results,
            'query': query
        })
    
    return search_bp

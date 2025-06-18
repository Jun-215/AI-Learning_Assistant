"""
聊天相关路由
"""
from flask import Blueprint, request, jsonify
from services.qianwen_service import call_qianwen_api
from stage2_config import quality_assessor

# 创建Blueprint
chat_bp = Blueprint('chat', __name__)

def init_chat_routes(kb):
    """初始化聊天路由，传入知识库实例"""
    
    @chat_bp.route('/api/chat', methods=['POST'])
    def chat():
        """聊天接口 - 支持智能文档检索 - 第二阶段RAG优化版本"""
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 先在知识库中搜索（会自动检测是否针对特定文档）
        search_results = kb.search(user_message)
        
        if search_results:
            # 使用增强的上下文质量优化
            enhanced_context, source_files = kb._enhance_context_quality(search_results, user_message)
            search_mode = search_results[0].get('search_info', {}).get('search_mode', 'global')
            
            # 根据搜索模式调整系统提示词 - 使用优化的提示词框架
            if search_mode == 'targeted':
                target_files = search_results[0].get('search_info', {}).get('target_files', [])
                system_prompt = kb._build_targeted_prompt(enhanced_context, target_files, user_message)
            else:
                system_prompt = kb._build_general_prompt(enhanced_context, user_message)
            
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ]
            
            response = call_qianwen_api(messages)
            
            # 评估回答质量
            quality_assessment = quality_assessor.assess_response_quality(response)
            
            return jsonify({
                'response': response,
                'source': 'knowledge_base',
                'search_results': search_results,
                'search_mode': search_mode,
                'source_files': source_files,
                'optimization_stage': 'stage2_prompt_optimization',  # 标识使用了第二阶段优化
                'quality_assessment': quality_assessment,
                'prompt_version': 'v2.0'
            })
        else:
            # 如果知识库中没有找到，使用标准回复模板
            fallback_prompt = """你是一个智能助手。用户询问的问题在当前知识库中没有找到相关信息。

请回答：对不起，我在当前知识库中没有找到与您问题相关的信息。您可以：
1. 尝试重新描述您的问题
2. 上传相关文档到知识库
3. 使用不同的关键词进行询问

如果您希望我基于通用知识回答，请明确告知。"""
            
            messages = [
                {'role': 'system', 'content': fallback_prompt},
                {'role': 'user', 'content': user_message}
            ]
            
            response = call_qianwen_api(messages)
            
            # 为无匹配情况也进行质量评估
            quality_assessment = quality_assessor.assess_response_quality(response)
            
            return jsonify({
                'response': response,
                'source': 'no_knowledge_base_match',
                'search_results': [],
                'search_mode': 'none',
                'source_files': [],
                'optimization_stage': 'stage2_prompt_optimization',
                'quality_assessment': quality_assessment,
                'prompt_version': 'v2.0'
            })
    
    return chat_bp

# -*- coding: utf-8 -*-
"""
本地Hugging Face模型配置
支持离线使用sentence-transformers/all-MiniLM-L6-v2模型
"""

import os

# 本地模型配置
LOCAL_EMBEDDING_CONFIG = {
    # 模型基本信息
    'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
    'snapshot_id': 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf',
    
    # 缓存路径配置
    'cache_dir': os.path.expanduser("~/.cache/huggingface/hub"),
    
    # 离线模式设置
    'force_offline': True,
    'use_local_only': True,
}

def setup_offline_mode():
    """设置离线模式环境变量"""
    if LOCAL_EMBEDDING_CONFIG['force_offline']:
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        print("✓ 已启用Hugging Face离线模式")

def get_local_model_path():
    """获取本地模型完整路径"""
    model_name = LOCAL_EMBEDDING_CONFIG['model_name']
    snapshot_id = LOCAL_EMBEDDING_CONFIG['snapshot_id']
    cache_dir = LOCAL_EMBEDDING_CONFIG['cache_dir']
    
    # 构建标准Hugging Face缓存路径
    model_cache_name = model_name.replace('/', '--')
    local_path = os.path.join(
        cache_dir,
        f"models--{model_cache_name}",
        "snapshots",
        snapshot_id
    )
    
    return local_path

def load_local_embedding_model():
    """加载本地嵌入模型"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # 设置离线模式
        setup_offline_mode()
        
        model_name = LOCAL_EMBEDDING_CONFIG['model_name']
        cache_dir = LOCAL_EMBEDDING_CONFIG['cache_dir']
        local_path = get_local_model_path()
        
        print(f"正在加载本地嵌入模型: {model_name}")
        
        # 尝试多种加载方式
        loading_methods = [
            # 方法1: 直接使用本地路径
            ('直接路径', lambda: SentenceTransformer(local_path)),
            
            # 方法2: 使用模型名称 + 缓存目录
            ('模型名称+缓存', lambda: SentenceTransformer(model_name, cache_folder=cache_dir)),
            
            # 方法3: 仅使用模型名称（依赖环境变量）
            ('模型名称', lambda: SentenceTransformer(model_name)),
        ]
        
        for method_name, loader in loading_methods:
            try:
                print(f"尝试加载方法: {method_name}")
                
                # 对于直接路径方法，先检查路径是否存在
                if method_name == '直接路径' and not os.path.exists(local_path):
                    print(f"  × 路径不存在: {local_path}")
                    continue
                
                model = loader()
                print(f"  ✓ 成功使用 {method_name} 加载模型")
                
                # 简单测试
                test_embedding = model.encode("测试文本")
                print(f"  ✓ 模型测试通过，向量维度: {len(test_embedding)}")
                
                return model
                
            except Exception as e:
                print(f"  × {method_name} 加载失败: {e}")
                continue
        
        print("× 所有加载方法都失败了")
        return None
        
    except ImportError:
        print("× sentence_transformers未安装")
        return None
    except Exception as e:
        print(f"× 模型加载异常: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    print("=== 本地嵌入模型加载测试 ===")
    model = load_local_embedding_model()
    
    if model:
        print("\n🎉 模型加载成功！")
        
        # 进行一些测试
        test_texts = [
            "这是第一个测试句子",
            "这是第二个测试句子",
            "完全不同的内容"
        ]
        
        print("\n=== 嵌入测试 ===")
        embeddings = model.encode(test_texts)
        print(f"成功生成 {len(embeddings)} 个嵌入向量")
        print(f"每个向量维度: {len(embeddings[0])}")
        
        # 计算相似度
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        similarity_matrix = cosine_similarity(embeddings)
        print(f"\n相似度矩阵:")
        for i, text in enumerate(test_texts):
            print(f"{i+1}. {text}")
        print(f"\n{similarity_matrix}")
        
    else:
        print("\n❌ 模型加载失败")
        print("\n排查建议:")
        print("1. 检查模型是否已下载到本地缓存")
        print("2. 验证快照ID是否正确")
        print("3. 确认sentence-transformers已安装")
        print(f"4. 手动检查路径: {get_local_model_path()}")

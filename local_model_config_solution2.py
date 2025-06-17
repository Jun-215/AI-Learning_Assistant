# 方案二：直接指定本地路径的app.py修改版本
# 
# 这个文件展示了如何通过直接指定本地缓存路径来加载Hugging Face模型
# 您可以将这些修改应用到您的app.py文件中

"""
方案二的修改内容：

1. 在文件顶部添加以下导入和配置：
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
from datetime import datetime
import PyPDF2
import dashscope
from config import Config
import jieba
import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from difflib import SequenceMatcher
import math
import logging

# 第二阶段优化相关导入
from stage2_config import stage2_config, prompt_builder, quality_assessor

# 语义嵌入相关导入
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    EMBEDDING_AVAILABLE = True
except ImportError:
    print("警告: sentence-transformers或faiss未安装，语义搜索功能将被禁用")
    EMBEDDING_AVAILABLE = False

# 方案二：配置本地模型路径
LOCAL_MODEL_CONFIG = {
    'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
    'snapshot_id': 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf',
    'cache_dir': os.path.expanduser("~/.cache/huggingface/transformers"),
    'use_local_only': True  # 强制只使用本地模型
}

"""
2. 替换_init_embedding_model方法：
"""

def _init_embedding_model_method_2(self):
    """初始化语义嵌入模型 - 方案二：直接指定本地路径"""
    try:
        print("正在加载本地缓存的语义嵌入模型...")
        
        # 构建本地模型完整路径
        model_name = LOCAL_MODEL_CONFIG['model_name']
        snapshot_id = LOCAL_MODEL_CONFIG['snapshot_id']
        cache_dir = LOCAL_MODEL_CONFIG['cache_dir']
        
        # 构建Hugging Face缓存的标准路径结构
        model_cache_name = model_name.replace('/', '--')
        local_model_path = os.path.join(
            cache_dir,
            f"models--{model_cache_name}",
            "snapshots",
            snapshot_id
        )
        
        print(f"尝试从本地路径加载模型: {local_model_path}")
        
        # 检查本地模型是否存在
        if os.path.exists(local_model_path):
            try:
                # 方法1: 直接使用本地路径
                self.embedding_model = SentenceTransformer(local_model_path, device='cpu')
                print(f"✓ 成功从本地路径加载模型: {local_model_path}")
            except Exception as e:
                print(f"× 从本地路径加载失败: {e}")
                
                # 方法2: 使用模型名称但指定本地缓存目录
                try:
                    # 临时设置环境变量强制离线模式
                    original_offline = os.environ.get('HF_HUB_OFFLINE', '0')
                    os.environ['HF_HUB_OFFLINE'] = '1'
                    
                    self.embedding_model = SentenceTransformer(
                        model_name, 
                        cache_folder=cache_dir,
                        device='cpu'
                    )
                    print(f"✓ 成功使用模型名称从本地缓存加载: {model_name}")
                    
                    # 恢复原始环境变量
                    os.environ['HF_HUB_OFFLINE'] = original_offline
                    
                except Exception as e2:
                    print(f"× 使用模型名称从本地缓存加载失败: {e2}")
                    raise e2
        else:
            print(f"× 本地模型路径不存在: {local_model_path}")
            print("请确认以下路径是否正确：")
            print(f"  缓存目录: {cache_dir}")
            print(f"  模型目录: models--{model_cache_name}")
            print(f"  快照ID: {snapshot_id}")
            
            # 尝试查找可用的快照ID
            model_dir = os.path.join(cache_dir, f"models--{model_cache_name}", "snapshots")
            if os.path.exists(model_dir):
                available_snapshots = os.listdir(model_dir)
                print(f"  可用的快照ID: {available_snapshots}")
                
                # 尝试使用第一个可用的快照
                if available_snapshots:
                    fallback_path = os.path.join(model_dir, available_snapshots[0])
                    print(f"尝试使用备选快照: {fallback_path}")
                    self.embedding_model = SentenceTransformer(fallback_path, device='cpu')
                    print(f"✓ 成功使用备选快照加载模型")
                else:
                    raise FileNotFoundError("没有找到可用的模型快照")
            else:
                raise FileNotFoundError(f"模型目录不存在: {model_dir}")
        
        if self.embedding_model is None:
            print("× 模型加载失败，将使用TF-IDF作为备选")
            return
        
        # 重建语义索引
        self._build_semantic_index()
        print("✓ 语义索引重建完成")
        
    except Exception as e:
        print(f"× 嵌入模型初始化失败: {e}")
        print("将使用TF-IDF作为备选搜索方法")
        self.embedding_model = None

"""
使用说明：

方案二的优势：
1. 更精确地控制模型路径
2. 提供了详细的错误诊断信息
3. 支持自动查找可用的快照ID作为备选
4. 可以在运行时动态切换离线/在线模式

要应用方案二，请将上面的_init_embedding_model_method_2函数内容
替换到您的app.py文件中的_init_embedding_model方法。

同时在文件开头添加LOCAL_MODEL_CONFIG配置。
"""

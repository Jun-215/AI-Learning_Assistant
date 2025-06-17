#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速状态检查脚本
"""

import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("RAG系统状态检查")
print("=" * 30)

try:
    print("1. 检查依赖库...")
    
    # 检查基础依赖
    try:
        import flask
        print("   ✓ Flask已安装")
    except ImportError:
        print("   ✗ Flask未安装")
    
    try:
        import jieba
        print("   ✓ jieba已安装")
    except ImportError:
        print("   ✗ jieba未安装")
    
    try:
        import sklearn
        print("   ✓ scikit-learn已安装")
    except ImportError:
        print("   ✗ scikit-learn未安装")
    
    # 检查语义搜索依赖
    try:
        import sentence_transformers
        print("   ✓ sentence-transformers已安装")
    except ImportError:
        print("   ✗ sentence-transformers未安装")
    
    try:
        import faiss
        print("   ✓ faiss已安装")
    except ImportError:
        print("   ✗ faiss未安装")
    
    print("\n2. 检查应用模块...")
    from app import KnowledgeBase, EMBEDDING_AVAILABLE
    print(f"   嵌入功能可用: {EMBEDDING_AVAILABLE}")
    
    print("\n3. 创建知识库实例...")
    kb = KnowledgeBase()
    print(f"   文档数量: {len(kb.documents)}")
    print(f"   嵌入模型: {'已加载' if kb.embedding_model else '未加载'}")
    print(f"   语义索引: {'已构建' if kb.embedding_index else '未构建'}")
    
    if hasattr(kb, 'document_chunks'):
        print(f"   文档块数量: {len(kb.document_chunks)}")
    
    print("\n4. 测试基础搜索...")
    test_query = "人工智能"
    results = kb.search(test_query, max_results=2)
    print(f"   查询 '{test_query}' 返回 {len(results)} 个结果")
    
    if results:
        print(f"   第一个结果: {results[0]['filename']}")
    
    print("\n✓ 系统状态检查完成")
    
except Exception as e:
    print(f"✗ 检查失败: {e}")
    import traceback
    traceback.print_exc()

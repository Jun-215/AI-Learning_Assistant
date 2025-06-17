#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控RAG系统初始化状态
"""

import time
import os
import sys

print("RAG系统状态监控")
print("=" * 30)

# 监控知识库初始化
print("正在监控系统初始化...")
print("提示: 首次加载语义模型可能需要几分钟时间下载模型文件")

# 添加backend路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

start_time = time.time()
print(f"开始时间: {time.strftime('%H:%M:%S')}")

try:
    print("\n1. 导入基础模块...")
    import flask
    import jieba
    import sklearn
    import numpy as np
    print("   ✓ 基础模块导入完成")
    
    print("\n2. 检查语义搜索依赖...")
    try:
        import sentence_transformers
        import faiss
        import torch
        print("   ✓ 语义搜索依赖可用")
        SEMANTIC_DEPS_OK = True
    except ImportError as e:
        print(f"   ✗ 语义搜索依赖缺失: {e}")
        SEMANTIC_DEPS_OK = False
    
    print("\n3. 导入应用模块...")
    from app import EMBEDDING_AVAILABLE
    print(f"   ✓ 应用模块导入成功")
    print(f"   嵌入功能状态: {EMBEDDING_AVAILABLE}")
    
    if EMBEDDING_AVAILABLE:
        print("\n4. 初始化知识库 (可能需要下载模型)...")
        print("   注意: 首次运行会下载嵌入模型，请耐心等待...")
        
        from app import KnowledgeBase
        kb = KnowledgeBase()
        
        elapsed = time.time() - start_time
        print(f"\n✓ 系统初始化完成!")
        print(f"总耗时: {elapsed:.2f} 秒")
        
        print(f"\n系统状态:")
        print(f"- 文档数量: {len(kb.documents)}")
        print(f"- 嵌入模型: {'✓ 已加载' if kb.embedding_model else '✗ 未加载'}")
        print(f"- 语义索引: {'✓ 已构建' if kb.embedding_index else '✗ 未构建'}")
        if hasattr(kb, 'document_chunks'):
            print(f"- 文档块数量: {len(kb.document_chunks)}")
        
        # 快速测试
        print(f"\n5. 快速功能测试...")
        test_query = "人工智能"
        results = kb.search(test_query, max_results=1)
        print(f"   查询 '{test_query}' 返回 {len(results)} 个结果")
        
        if results and kb.embedding_model:
            result = results[0]
            print(f"   结果文件: {result['filename']}")
            print(f"   相关度分数: {result['score']:.3f}")
            if 'semantic_score' in result:
                print(f"   语义分数: {result['semantic_score']:.3f}")
        
        print(f"\n🎉 RAG系统完全就绪!")
        
    else:
        print(f"\n⚠ 语义搜索功能不可用，系统将使用基础搜索功能")
        from app import KnowledgeBase
        kb = KnowledgeBase()
        print(f"基础搜索功能正常，文档数量: {len(kb.documents)}")

except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n✗ 系统初始化失败 (耗时: {elapsed:.2f}s)")
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print(f"\n结束时间: {time.strftime('%H:%M:%S')}")
print("监控结束")

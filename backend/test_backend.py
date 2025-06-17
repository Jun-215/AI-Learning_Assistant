#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端语义搜索功能测试
"""

import os
import sys

print("后端语义搜索功能测试")
print("=" * 40)

# 检查依赖
print("1. 检查依赖库...")
try:
    import sentence_transformers
    print(f"   ✓ sentence-transformers: {sentence_transformers.__version__}")
    SENTENCE_TRANSFORMERS_OK = True
except ImportError as e:
    print(f"   ✗ sentence-transformers: {e}")
    SENTENCE_TRANSFORMERS_OK = False

try:
    import faiss
    print("   ✓ faiss已安装")
    FAISS_OK = True
except ImportError as e:
    print(f"   ✗ faiss: {e}")
    FAISS_OK = False

try:
    import torch
    print(f"   ✓ torch: {torch.__version__}")
    TORCH_OK = True
except ImportError as e:
    print(f"   ✗ torch: {e}")
    TORCH_OK = False

# 导入应用模块
print("\n2. 导入应用模块...")
try:
    from app import KnowledgeBase, EMBEDDING_AVAILABLE
    print(f"   ✓ app模块导入成功")
    print(f"   嵌入功能状态: {EMBEDDING_AVAILABLE}")
except Exception as e:
    print(f"   ✗ app模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 创建知识库实例
print("\n3. 创建知识库实例...")
try:
    kb = KnowledgeBase()
    print(f"   ✓ 知识库创建成功")
    print(f"   文档数量: {len(kb.documents)}")
    print(f"   嵌入模型: {'已加载' if kb.embedding_model else '未加载'}")
    print(f"   语义索引: {'已构建' if kb.embedding_index else '未构建'}")
    
    if hasattr(kb, 'document_chunks'):
        print(f"   文档块数量: {len(kb.document_chunks)}")
    else:
        print("   文档块: 未初始化")
        
except Exception as e:
    print(f"   ✗ 知识库创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试搜索功能
print("\n4. 测试搜索功能...")
test_queries = [
    "人工智能发展",
    "机器学习算法",
    "深度学习应用"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n   测试 {i}: '{query}'")
    
    try:
        # 基础搜索
        results = kb.search(query, max_results=2)
        print(f"   基础搜索: {len(results)} 个结果")
        
        if results:
            first_result = results[0]
            print(f"   第一个结果: {first_result['filename']}")
            print(f"   相关度分数: {first_result['score']:.3f}")
            
            # 检查是否有语义分数
            if 'semantic_score' in first_result:
                print(f"   语义分数: {first_result['semantic_score']:.3f}")
            if 'keyword_score' in first_result:
                print(f"   关键词分数: {first_result['keyword_score']:.3f}")
        
        # 如果支持语义搜索，单独测试
        if kb.embedding_model and hasattr(kb, '_semantic_search'):
            try:
                semantic_results = kb._semantic_search(query, k=2)
                print(f"   纯语义搜索: {len(semantic_results)} 个结果")
                if semantic_results:
                    print(f"   语义搜索分数: {semantic_results[0]['semantic_score']:.3f}")
            except Exception as e:
                print(f"   语义搜索错误: {e}")
        
    except Exception as e:
        print(f"   ✗ 查询失败: {e}")

# 总结
print(f"\n" + "=" * 40)
print("测试完成!")

print(f"\n功能状态:")
print(f"- 依赖库: {'✓' if SENTENCE_TRANSFORMERS_OK and FAISS_OK else '✗'}")
print(f"- 嵌入功能: {'✓' if EMBEDDING_AVAILABLE else '✗'}")
print(f"- 知识库: {'✓' if kb else '✗'}")
print(f"- 语义模型: {'✓' if kb and kb.embedding_model else '✗'}")
print(f"- 语义索引: {'✓' if kb and kb.embedding_index else '✗'}")

if kb and kb.embedding_model and kb.embedding_index:
    print(f"\n🎉 语义搜索功能完全可用!")
    print(f"特性:")
    print(f"- 高质量中文语义理解")
    print(f"- 智能文档分块 ({len(kb.document_chunks)} 个块)")
    print(f"- 语义相似度检索")
    print(f"- 融合重排序算法")
elif kb:
    print(f"\n⚠ 基础搜索功能可用，语义搜索功能需要完善")
else:
    print(f"\n❌ 系统存在问题，需要修复")

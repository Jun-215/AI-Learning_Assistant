#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import traceback

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("=" * 50)
print("RAG系统完整检查")
print("=" * 50)

def check_dependencies():
    """检查依赖库"""
    print("1. 检查依赖库...")
    
    deps = [
        ('Flask', 'flask'),
        ('jieba', 'jieba'),
        ('scikit-learn', 'sklearn'),
        ('numpy', 'numpy'),
        ('sentence-transformers', 'sentence_transformers'),
        ('faiss', 'faiss'),
        ('torch', 'torch')
    ]
    
    available_deps = []
    for name, module in deps:
        try:
            __import__(module)
            print(f"   ✓ {name}")
            available_deps.append(name)
        except ImportError:
            print(f"   ✗ {name} - 未安装")
    
    return available_deps

def check_system():
    """检查系统功能"""
    print("\n2. 检查系统模块...")
    
    try:
        from app import KnowledgeBase, EMBEDDING_AVAILABLE
        print(f"   ✓ app模块导入成功")
        print(f"   ✓ 嵌入功能状态: {EMBEDDING_AVAILABLE}")
        
        print("\n3. 初始化知识库...")
        kb = KnowledgeBase()
        print(f"   ✓ 知识库创建成功")
        print(f"   - 文档数量: {len(kb.documents)}")
        print(f"   - 嵌入模型: {'已加载' if kb.embedding_model else '未加载'}")
        print(f"   - 语义索引: {'已构建' if kb.embedding_index else '未构建'}")
        
        if hasattr(kb, 'document_chunks'):
            print(f"   - 文档块数量: {len(kb.document_chunks)}")
        
        return kb
        
    except Exception as e:
        print(f"   ✗ 系统检查失败: {e}")
        traceback.print_exc()
        return None

def test_search_functions(kb):
    """测试搜索功能"""
    if not kb:
        return
    
    print("\n4. 测试搜索功能...")
    
    test_queries = [
        "人工智能",
        "机器学习",
        "深度学习"
    ]
    
    for query in test_queries:
        try:
            print(f"\n   测试查询: '{query}'")
            
            # 测试基础搜索
            results = kb.search(query, max_results=2)
            print(f"   - 基础搜索: {len(results)} 个结果")
            
            if results:
                print(f"     第一个结果: {results[0]['filename']}")
                print(f"     分数: {results[0]['score']:.3f}")
            
            # 测试语义搜索（如果可用）
            if kb.embedding_model and hasattr(kb, '_semantic_search'):
                semantic_results = kb._semantic_search(query, k=2)
                print(f"   - 语义搜索: {len(semantic_results)} 个结果")
                
                if semantic_results:
                    print(f"     语义分数: {semantic_results[0]['semantic_score']:.3f}")
            
        except Exception as e:
            print(f"   ✗ 查询 '{query}' 失败: {e}")

def main():
    available_deps = check_dependencies()
    kb = check_system()
    test_search_functions(kb)
    
    print("\n" + "=" * 50)
    print("检查完成!")
    
    # 总结状态
    print("\n系统状态总结:")
    print(f"- 基础依赖: {'✓' if 'Flask' in available_deps else '✗'}")
    print(f"- 分词功能: {'✓' if 'jieba' in available_deps else '✗'}")
    print(f"- 机器学习: {'✓' if 'scikit-learn' in available_deps else '✗'}")
    print(f"- 语义搜索: {'✓' if 'sentence-transformers' in available_deps and 'faiss' in available_deps else '✗'}")
    print(f"- 知识库: {'✓' if kb else '✗'}")
    
    if kb and kb.embedding_model:
        print("\n✓ 系统完全就绪，支持高级语义搜索!")
    elif kb:
        print("\n⚠ 系统基本就绪，但语义搜索功能不可用")
    else:
        print("\n✗ 系统存在问题，需要修复")

if __name__ == "__main__":
    main()

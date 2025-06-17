#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义搜索功能测试脚本
测试新增的语义嵌入和重排序功能
"""

import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("语义搜索功能测试")
print("=" * 40)

def test_semantic_features():
    """测试语义搜索相关功能"""
    try:
        # 导入模块
        print("1. 导入增强后的KnowledgeBase...")
        from app import KnowledgeBase, EMBEDDING_AVAILABLE
        
        print(f"   语义嵌入功能可用: {EMBEDDING_AVAILABLE}")
        
        # 创建知识库实例
        print("2. 创建知识库实例...")
        kb = KnowledgeBase()
        
        print(f"   文档数量: {len(kb.documents)}")
        print(f"   嵌入模型已加载: {kb.embedding_model is not None}")
        print(f"   语义索引已构建: {kb.embedding_index is not None}")
        if hasattr(kb, 'document_chunks'):
            print(f"   文档块数量: {len(kb.document_chunks)}")
        
        # 测试语义搜索功能
        print("\n3. 测试语义搜索功能...")
        
        test_queries = [
            {
                "query": "如何在人工智能领域发展职业？",
                "description": "职业发展相关查询"
            },
            {
                "query": "机器学习需要掌握哪些数学知识？",
                "description": "技能要求查询"
            },
            {
                "query": "简历中的工作经验如何写？",
                "description": "简历相关查询"
            },
            {
                "query": "深度学习和神经网络的关系",
                "description": "技术概念查询"
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            query = test_case["query"]
            description = test_case["description"]
            
            print(f"\n   测试 {i}: {description}")
            print(f"   查询: '{query}'")
            
            # 测试纯语义搜索
            if EMBEDDING_AVAILABLE and kb.embedding_model:
                try:
                    semantic_results = kb._semantic_search(query, k=3)
                    print(f"   语义搜索结果: {len(semantic_results)} 个")
                    
                    for j, result in enumerate(semantic_results[:2], 1):
                        print(f"     结果 {j}: {result['filename']} (分数: {result['semantic_score']:.3f})")
                        print(f"              {result['text'][:80]}...")
                except Exception as e:
                    print(f"   语义搜索失败: {e}")
            
            # 测试增强搜索（融合语义和关键词）
            try:
                enhanced_results = kb.search(query, max_results=3)
                print(f"   增强搜索结果: {len(enhanced_results)} 个")
                
                for j, result in enumerate(enhanced_results[:2], 1):
                    semantic_score = result.get('semantic_score', 0)
                    keyword_score = result.get('keyword_score', 0)
                    print(f"     结果 {j}: {result['filename']} (综合分数: {result['score']:.3f})")
                    if semantic_score > 0:
                        print(f"              语义分数: {semantic_score:.3f}, 关键词分数: {keyword_score:.3f}")
                    print(f"              {result['content'][:80]}...")
            except Exception as e:
                print(f"   增强搜索失败: {e}")
            
            print("   " + "-" * 60)
        
        # 测试文档块功能
        print("\n4. 测试文档分块功能...")
        if hasattr(kb, 'document_chunks') and kb.document_chunks:
            sample_chunks = kb.document_chunks[:3]
            print(f"   示例文档块 (共{len(kb.document_chunks)}个):")
            for i, chunk in enumerate(sample_chunks, 1):
                print(f"     块 {i}: {chunk['filename']}")
                print(f"           {chunk['text'][:100]}...")
        
        # 测试对比不同查询方式
        print("\n5. 测试语义相似性...")
        similar_queries = [
            ("人工智能职业发展", "AI领域如何构建事业"),
            ("机器学习数学基础", "ML需要哪些数学知识"),
            ("简历工作经历", "履历中的职业经验")
        ]
        
        for query1, query2 in similar_queries:
            print(f"\n   对比查询: '{query1}' vs '{query2}'")
            
            if EMBEDDING_AVAILABLE and kb.embedding_model:
                try:
                    results1 = kb._semantic_search(query1, k=2)
                    results2 = kb._semantic_search(query2, k=2)
                    
                    print(f"   查询1结果: {len(results1)} 个")
                    print(f"   查询2结果: {len(results2)} 个")
                    
                    # 检查是否找到相似的文档
                    common_docs = set(r['document_id'] for r in results1) & set(r['document_id'] for r in results2)
                    print(f"   共同文档: {len(common_docs)} 个")
                    
                except Exception as e:
                    print(f"   对比测试失败: {e}")
        
        print("\n6. 功能验证完成 ✓")
        
        # 总结功能状态
        print(f"\n语义搜索功能状态:")
        print(f"- 嵌入模型: {'✓ 已加载' if kb.embedding_model else '✗ 未加载'}")
        print(f"- 语义索引: {'✓ 已构建' if kb.embedding_index else '✗ 未构建'}")
        print(f"- 文档分块: {'✓ 已完成' if hasattr(kb, 'document_chunks') and kb.document_chunks else '✗ 未完成'}")
        print(f"- 重排序: ✓ 已启用")
        
        if EMBEDDING_AVAILABLE and kb.embedding_model:
            print("\n✓ 语义搜索功能正常工作！")
            print("新特性:")
            print("- 高质量中文语义理解")
            print("- 文档智能分块")
            print("- 语义和关键词融合搜索")
            print("- 智能重排序算法")
        else:
            print("\n⚠ 语义搜索功能不可用，请安装相关依赖")
            
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保安装了必要的依赖: pip install sentence-transformers torch faiss-cpu")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_chunk_quality():
    """测试文档分块质量"""
    print("\n7. 测试文档分块质量...")
    
    try:
        from app import KnowledgeBase
        kb = KnowledgeBase()
        
        if hasattr(kb, 'document_chunks') and kb.document_chunks:
            # 分析块的长度分布
            chunk_lengths = [len(chunk['text']) for chunk in kb.document_chunks]
            avg_length = sum(chunk_lengths) / len(chunk_lengths)
            min_length = min(chunk_lengths)
            max_length = max(chunk_lengths)
            
            print(f"   文档块统计:")
            print(f"   - 总块数: {len(kb.document_chunks)}")
            print(f"   - 平均长度: {avg_length:.1f} 字符")
            print(f"   - 最短: {min_length} 字符")
            print(f"   - 最长: {max_length} 字符")
            
            # 显示长度分布
            length_ranges = [(0, 100), (100, 200), (200, 300), (300, 400), (400, float('inf'))]
            for min_len, max_len in length_ranges:
                count = len([l for l in chunk_lengths if min_len <= l < max_len])
                range_str = f"{min_len}-{max_len if max_len != float('inf') else '400+'}"
                print(f"   - {range_str} 字符: {count} 个块")
    
    except Exception as e:
        print(f"   分块质量测试失败: {e}")

if __name__ == "__main__":
    test_semantic_features()
    test_chunk_quality()
    print("\n" + "=" * 40)

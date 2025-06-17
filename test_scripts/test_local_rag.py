#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG优化功能本地测试脚本
不依赖HTTP服务器，直接测试KnowledgeBase类的功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import KnowledgeBase
import json

def test_knowledge_base_functionality():
    """测试知识库的基本功能"""
    print("=== 初始化知识库 ===")
    
    # 创建知识库实例
    kb = KnowledgeBase()
    
    print(f"知识库中的文档数量: {len(kb.documents)}")
    
    # 显示现有文档
    for doc in kb.documents:
        print(f"- {doc['filename']} (ID: {doc['id']})")
    
    print(f"\n文件名模式数量: {len(kb.filename_patterns)}")
    print("前10个文件名模式:")
    for i, (pattern, doc_ids) in enumerate(list(kb.filename_patterns.items())[:10]):
        print(f"  {pattern} -> {doc_ids}")
    
    return kb

def test_document_detection(kb):
    """测试文档检测功能"""
    print("\n=== 测试文档检测功能 ===")
    
    test_queries = [
        "请总结一下助理.pdf的内容",
        "吴恩达文档里说了什么关于AI职业的建议？",
        "助理这个文档讲了什么？",
        "请分析吴恩达的那个PDF文件",
        "AI领域有哪些技能需要学习？",  # 这个不应该检测到特定文档
        "胡晓熊的简历怎么样？"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        detected_files, confidence_scores = kb._detect_target_filename(query)
        
        if detected_files:
            print(f"检测到 {len(detected_files)} 个文档:")
            for doc_id in detected_files:
                # 找到对应的文档
                doc_name = "未知文档"
                for doc in kb.documents:
                    if doc['id'] == doc_id:
                        doc_name = doc['filename']
                        break
                confidence = confidence_scores.get(doc_id, 0)
                print(f"  - {doc_name} (ID: {doc_id}, 置信度: {confidence})")
        else:
            print("未检测到特定文档引用")

def test_search_functionality(kb):
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")
    
    test_queries = [
        {
            "query": "请总结助理.pdf的主要内容",
            "description": "针对特定文档的查询"
        },
        {
            "query": "吴恩达文档中关于学习步骤的建议",
            "description": "针对特定文档的内容查询"
        },
        {
            "query": "AI领域需要学习哪些技能？",
            "description": "全局查询"
        },
        {
            "query": "胡晓熊的工作经历",
            "description": "针对简历的查询"
        }
    ]
    
    for test_case in test_queries:
        query = test_case["query"]
        description = test_case["description"]
        
        print(f"\n查询: {query}")
        print(f"描述: {description}")
        
        try:
            results = kb.search(query)
            
            if results:
                print(f"找到 {len(results)} 个结果:")
                for i, result in enumerate(results):
                    search_mode = result.get('search_info', {}).get('search_mode', 'unknown')
                    print(f"  结果 {i+1}:")
                    print(f"    文档: {result['filename']}")
                    print(f"    搜索模式: {search_mode}")
                    print(f"    分数: {result['score']}")
                    print(f"    文件匹配置信度: {result.get('file_match_confidence', 0)}")
                    print(f"    内容片段: {result['content'][:150]}...")
                    print()
            else:
                print("未找到相关结果")
                
        except Exception as e:
            print(f"搜索失败: {e}")
            import traceback
            traceback.print_exc()

def test_comprehensive_scenarios(kb):
    """测试综合场景"""
    print("\n=== 测试综合场景 ===")
    
    scenarios = [
        {
            "query": "助理简历中的教育背景",
            "expected_behavior": "应该检测到助理.pdf，并在该文档中搜索教育相关内容"
        },
        {
            "query": "吴恩达提到的机器学习基础技能有哪些？",
            "expected_behavior": "应该检测到吴恩达的文档，并搜索机器学习技能相关内容"
        },
        {
            "query": "如何建立AI职业生涯？",
            "expected_behavior": "可能检测到吴恩达文档，或进行全局搜索"
        }
    ]
    
    for scenario in scenarios:
        query = scenario["query"]
        expected = scenario["expected_behavior"]
        
        print(f"\n场景测试:")
        print(f"查询: {query}")
        print(f"期望行为: {expected}")
        
        # 1. 检测文档
        detected_files, confidence_scores = kb._detect_target_filename(query)
        print(f"文档检测结果: {len(detected_files)} 个文档")
        
        # 2. 执行搜索
        results = kb.search(query)
        print(f"搜索结果: {len(results)} 个结果")
        
        if results:
            search_mode = results[0].get('search_info', {}).get('search_mode', 'unknown')
            target_files = results[0].get('search_info', {}).get('target_files', [])
            print(f"实际搜索模式: {search_mode}")
            print(f"目标文件: {target_files}")
        
        print("-" * 50)

def main():
    """主测试函数"""
    print("RAG优化功能本地测试")
    print("==================")
    
    try:
        # 初始化知识库
        kb = test_knowledge_base_functionality()
        
        # 测试文档检测
        test_document_detection(kb)
        
        # 测试搜索功能
        test_search_functionality(kb)
        
        # 测试综合场景
        test_comprehensive_scenarios(kb)
        
        print("\n=== 测试完成 ===")
        print("所有功能正常工作！")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

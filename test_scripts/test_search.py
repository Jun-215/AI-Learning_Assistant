#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的知识库搜索功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import KnowledgeBase

def test_search_functionality():
    """测试搜索功能"""
    print("=== 知识库搜索功能测试 ===\n")
    
    # 创建知识库实例
    kb = KnowledgeBase()
    
    # 添加测试文档
    test_documents = [
        {
            "filename": "人工智能基础.pdf",
            "content": """
            人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
            致力于创建能够执行通常需要人类智能的任务的系统。机器学习是人工智能的一个重要子领域，
            它使计算机能够从数据中学习，而无需明确编程。深度学习是机器学习的一个分支，
            使用神经网络来模拟人脑的工作方式。自然语言处理（NLP）是人工智能的另一个重要领域，
            专注于使计算机能够理解、解释和生成人类语言。
            """
        },
        {
            "filename": "机器学习算法.pdf", 
            "content": """
            机器学习算法可以分为三大类：监督学习、无监督学习和强化学习。
            监督学习使用标记的训练数据来学习输入和输出之间的映射关系，
            常见的监督学习算法包括线性回归、决策树、随机森林和支持向量机。
            无监督学习处理没有标签的数据，目标是发现数据中的隐藏模式，
            聚类算法如K-means是无监督学习的典型例子。强化学习通过与环境交互来学习，
            通过试错来优化决策策略。
            """
        },
        {
            "filename": "数据科学实践.pdf",
            "content": """
            数据科学是一个跨学科领域，结合了统计学、计算机科学和领域专业知识。
            数据科学的典型工作流程包括数据收集、数据清洗、探索性数据分析、
            特征工程、模型构建、模型评估和部署。Python和R是数据科学中最常用的编程语言。
            常用的Python库包括pandas用于数据处理、matplotlib和seaborn用于数据可视化、
            scikit-learn用于机器学习。数据可视化是数据科学中的重要环节，
            能够帮助我们更好地理解数据和模型结果。
            """
        }
    ]
    
    # 清空现有文档并添加测试文档
    kb.documents = []
    for i, doc_data in enumerate(test_documents):
        kb.add_document(doc_data["filename"], doc_data["content"])
    
    print(f"已添加 {len(test_documents)} 个测试文档到知识库\n")
    
    # 测试查询
    test_queries = [
        "什么是人工智能？",
        "机器学习有哪些类型？", 
        "Python在数据科学中的应用",
        "深度学习和神经网络",
        "数据可视化工具",
        "监督学习算法",
        "如何进行数据清洗？",
        "强化学习原理"
    ]
    
    print("开始测试搜索功能：\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"测试 {i}: {query}")
        print("-" * 50)
        
        try:
            results = kb.search(query, threshold=0.1, max_results=3)
            
            if results:
                print(f"找到 {len(results)} 个相关结果：\n")
                for j, result in enumerate(results, 1):
                    print(f"结果 {j}:")
                    print(f"  文档: {result['filename']}")
                    print(f"  总分: {result['score']}")
                    print(f"  TF-IDF分数: {result['tfidf_score']}")
                    print(f"  关键词分数: {result['keyword_score']}")
                    print(f"  匹配关键词: {result['matched_keywords']}")
                    print(f"  相关内容: {result['content'][:100]}...")
                    print()
            else:
                print("未找到相关结果")
            
        except Exception as e:
            print(f"搜索出错: {str(e)}")
        
        print("=" * 80)
        print()

def test_keyword_extraction():
    """测试关键词提取功能"""
    print("\n=== 关键词提取测试 ===\n")
    
    kb = KnowledgeBase()
    
    test_texts = [
        "人工智能在医疗领域的应用越来越广泛，包括疾病诊断和药物研发",
        "机器学习算法可以帮助企业进行数据分析和预测建模",
        "自然语言处理技术使得计算机能够理解和生成人类语言"
    ]
    
    for text in test_texts:
        keywords = kb._extract_keywords(text)
        print(f"原文: {text}")
        print(f"关键词: {keywords}")
        print()

if __name__ == "__main__":
    try:
        test_search_functionality()
        test_keyword_extraction()
        print("所有测试完成！")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

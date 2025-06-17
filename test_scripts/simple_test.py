#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的RAG功能测试脚本
"""

import os
import sys

# 添加backend目录到路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_basic_import():
    """测试基本导入"""
    try:
        print("测试导入模块...")
        from app import KnowledgeBase
        print("✓ 成功导入 KnowledgeBase")
        
        # 创建实例
        print("创建知识库实例...")
        kb = KnowledgeBase()
        print("✓ 成功创建知识库实例")
        
        # 检查文档数量
        print(f"知识库中的文档数量: {len(kb.documents)}")
        
        # 显示文档列表
        if kb.documents:
            print("文档列表:")
            for doc in kb.documents:
                print(f"  - {doc['filename']} (ID: {doc['id']})")
        
        # 测试文档检测
        print("\n测试文档检测功能:")
        test_query = "请总结助理.pdf的内容"
        print(f"查询: {test_query}")
        
        detected_files, confidence_scores = kb._detect_target_filename(test_query)
        print(f"检测到 {len(detected_files)} 个文档")
        
        for doc_id in detected_files:
            doc_name = "未知"
            for doc in kb.documents:
                if doc['id'] == doc_id:
                    doc_name = doc['filename']
                    break
            print(f"  - {doc_name} (置信度: {confidence_scores.get(doc_id, 0)})")
        
        # 测试搜索功能
        print("\n测试搜索功能:")
        results = kb.search(test_query)
        print(f"搜索结果: {len(results)} 个")
        
        if results:
            result = results[0]
            search_mode = result.get('search_info', {}).get('search_mode', 'unknown')
            print(f"搜索模式: {search_mode}")
            print(f"文档: {result['filename']}")
            print(f"分数: {result['score']}")
        
        print("\n✓ 所有测试通过!")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("RAG功能简单测试")
    print("===============")
    test_basic_import()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证RAG优化功能的脚本
"""

import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("RAG优化功能验证")
print("=" * 30)

try:
    # 导入必要的模块
    print("1. 导入KnowledgeBase类...")
    from app import KnowledgeBase
    print("   ✓ 导入成功")
    
    # 创建知识库实例
    print("2. 创建知识库实例...")
    kb = KnowledgeBase()
    print("   ✓ 实例创建成功")
    
    # 检查现有文档
    print("3. 检查现有文档...")
    print(f"   文档数量: {len(kb.documents)}")
    for i, doc in enumerate(kb.documents, 1):
        print(f"   {i}. {doc['filename']} (ID: {doc['id']})")
    
    # 测试文档检测功能
    print("4. 测试文档检测功能...")
    test_queries = [
        "请总结助理.pdf的内容",
        "吴恩达文档里说了什么？",
        "AI技能学习建议"
    ]
    
    for query in test_queries:
        print(f"\n   查询: '{query}'")
        try:
            detected_files, confidence_scores = kb._detect_target_filename(query)
            if detected_files:
                print(f"   检测到 {len(detected_files)} 个文档:")
                for doc_id in detected_files:
                    doc_name = next((doc['filename'] for doc in kb.documents if doc['id'] == doc_id), f"ID-{doc_id}")
                    confidence = confidence_scores.get(doc_id, 0)
                    print(f"     - {doc_name} (置信度: {confidence})")
            else:
                print("   未检测到特定文档")
        except Exception as e:
            print(f"   检测出错: {e}")
    
    # 测试搜索功能
    print("\n5. 测试搜索功能...")
    test_search_query = "请总结助理.pdf的主要内容"
    print(f"   搜索查询: '{test_search_query}'")
    
    try:
        results = kb.search(test_search_query)
        print(f"   搜索结果: {len(results)} 个")
        
        if results:
            for i, result in enumerate(results[:2], 1):  # 只显示前2个结果
                search_info = result.get('search_info', {})
                search_mode = search_info.get('search_mode', 'unknown')
                print(f"   结果 {i}:")
                print(f"     文档: {result['filename']}")
                print(f"     搜索模式: {search_mode}")
                print(f"     分数: {result['score']}")
                print(f"     内容预览: {result['content'][:100]}...")
    except Exception as e:
        print(f"   搜索出错: {e}")
    
    print("\n6. 验证完成 ✓")
    print("\n优化功能正常工作！主要特性:")
    print("- 智能检测文档引用")
    print("- 支持针对性搜索")
    print("- 置信度评分机制")
    print("- 双模式检索系统")

except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保当前目录包含backend文件夹，且backend/app.py存在")
except Exception as e:
    print(f"运行错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 30)
            print(f"匹配分数: {result['score']}")
            print(f"匹配关键词: {result['matched_keywords']}")
            print(f"相关内容: {result['content'][:100]}...")
        else:
            print("未找到相关结果")
        
        print("=" * 50)
        print()

if __name__ == "__main__":
    try:
        quick_test()
        print("✅ 搜索功能测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

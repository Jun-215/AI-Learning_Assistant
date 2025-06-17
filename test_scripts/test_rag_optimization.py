#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG优化功能测试脚本
测试针对特定文档的智能检索功能
"""

import requests
import json
import time

# 后端服务地址
BASE_URL = "http://localhost:5000"

def test_document_detection():
    """测试文档检测功能"""
    print("=== 测试文档检测功能 ===")
    
    test_queries = [
        "请总结一下助理.pdf的内容",
        "吴恩达文档里说了什么关于AI职业的建议？",
        "助理这个文档讲了什么？",
        "career ai pdf 有什么内容？",
        "请分析吴恩达的那个PDF文件",
        "AI career guide 文档的要点是什么？"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        try:
            response = requests.post(f"{BASE_URL}/api/detect-document", 
                                   json={"query": query})
            if response.status_code == 200:
                result = response.json()
                print(f"检测到的文档: {len(result['detected_documents'])} 个")
                for doc in result['detected_documents']:
                    print(f"  - {doc['filename']} (置信度: {doc['confidence']})")
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
        
        time.sleep(0.5)

def test_targeted_search():
    """测试针对特定文档的搜索"""
    print("\n=== 测试针对特定文档的搜索 ===")
    
    test_queries = [
        {
            "query": "请总结一下助理.pdf的主要内容",
            "expected_mode": "targeted"
        },
        {
            "query": "吴恩达：如何在人工智能领域打造你的职业生涯？.pdf 这个文档讲了什么关于学习的建议？",
            "expected_mode": "targeted"  
        },
        {
            "query": "AI领域有哪些技能需要学习？",
            "expected_mode": "global"
        }
    ]
    
    for test_case in test_queries:
        query = test_case["query"]
        expected_mode = test_case["expected_mode"]
        
        print(f"\n查询: {query}")
        print(f"期望模式: {expected_mode}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/search", 
                                   json={"query": query})
            if response.status_code == 200:
                result = response.json()
                results = result['results']
                
                if results:
                    search_mode = results[0].get('search_info', {}).get('search_mode', 'unknown')
                    print(f"实际搜索模式: {search_mode}")
                    print(f"找到结果: {len(results)} 个")
                    
                    for i, res in enumerate(results[:2]):  # 只显示前2个结果
                        print(f"  结果 {i+1}:")
                        print(f"    文档: {res['filename']}")
                        print(f"    分数: {res['score']}")
                        print(f"    内容预览: {res['content'][:100]}...")
                        if 'file_match_confidence' in res:
                            print(f"    文件匹配置信度: {res['file_match_confidence']}")
                else:
                    print("未找到相关结果")
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
        
        time.sleep(0.5)

def test_chat_with_targeted_documents():
    """测试聊天接口的针对性文档功能"""
    print("\n=== 测试聊天接口的针对性文档功能 ===")
    
    test_queries = [
        "请总结助理.pdf的主要内容，包括技能和经历",
        "吴恩达的文档中提到了哪些学习AI的步骤？",
        "胡晓熊的简历中有什么工作经历？",
        "人工智能职业发展有什么建议？"  # 这个应该触发全局搜索
    ]
    
    for query in test_queries:
        print(f"\n问题: {query}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat", 
                                   json={"message": query})
            if response.status_code == 200:
                result = response.json()
                
                print(f"回答来源: {result.get('source', 'unknown')}")
                print(f"搜索模式: {result.get('search_mode', 'unknown')}")
                print(f"源文件: {result.get('source_files', [])}")
                print(f"回答: {result['response'][:300]}...")
                print("-" * 50)
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
        
        time.sleep(1)

def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✓ 后端服务运行正常")
            return True
        else:
            print("✗ 后端服务状态异常")
            return False
    except Exception as e:
        print(f"✗ 无法连接到后端服务: {e}")
        return False

def main():
    """主测试函数"""
    print("RAG优化功能测试")
    print("================")
    
    # 检查服务器状态
    if not check_server_status():
        print("请先启动后端服务 (python backend/app.py)")
        return
    
    print("\n开始测试...")
    
    # 测试文档检测
    test_document_detection()
    
    # 测试针对性搜索
    test_targeted_search()
    
    # 测试聊天接口
    test_chat_with_targeted_documents()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()

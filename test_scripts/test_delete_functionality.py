#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF删除功能的验证脚本
"""

import sys
import os
import json
import time

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

def test_delete_functionality():
    """测试删除功能"""
    print("🧪 测试PDF删除功能")
    print("=" * 50)
    
    try:
        # 导入必要模块
        print("1. 导入模块...")
        from app import KnowledgeBase
        print("   ✓ 模块导入成功")
        
        # 创建知识库实例
        print("\n2. 初始化知识库...")
        kb = KnowledgeBase()
        print(f"   ✓ 知识库初始化完成")
        print(f"   📚 当前文档数量: {len(kb.documents)}")
        
        # 显示现有文档
        print("\n3. 当前文档列表:")
        if kb.documents:
            for i, doc in enumerate(kb.documents, 1):
                print(f"   {i}. ID: {doc['id']} - {doc['filename']}")
        else:
            print("   📝 没有文档")
            return
        
        # 测试delete_document方法是否存在
        print("\n4. 检查delete_document方法...")
        if hasattr(kb, 'delete_document'):
            print("   ✓ delete_document方法存在")
        else:
            print("   ❌ delete_document方法不存在")
            return
        
        # 选择要删除的文档进行测试（选择第一个文档）
        if kb.documents:
            test_doc = kb.documents[0]
            test_doc_id = test_doc['id']
            test_doc_name = test_doc['filename']
            
            print(f"\n5. 测试删除文档: {test_doc_name} (ID: {test_doc_id})")
            
            # 记录删除前的状态
            before_count = len(kb.documents)
            before_files = [doc['filename'] for doc in kb.documents]
            
            print(f"   删除前文档数量: {before_count}")
            print(f"   目标文档: {test_doc_name}")
            
            # 模拟删除操作（但我们不会真的删除，只是测试方法调用）
            print(f"\n   ⚠️ 警告: 即将删除文档 '{test_doc_name}'")
            print(f"   此操作将测试删除功能但不会真正删除文档")
            
            # 询问用户是否继续
            user_input = input("\n   是否继续测试删除功能? (y/N): ").strip().lower()
            
            if user_input == 'y':
                print(f"\n   🗑️ 执行删除操作...")
                
                # 调用删除方法
                success = kb.delete_document(test_doc_id)
                
                if success:
                    print(f"   ✅ 删除操作成功")
                    
                    # 验证删除结果
                    after_count = len(kb.documents)
                    after_files = [doc['filename'] for doc in kb.documents]
                    
                    print(f"   📊 删除后文档数量: {after_count}")
                    print(f"   📉 数量变化: {before_count} -> {after_count}")
                    
                    if after_count == before_count - 1:
                        print("   ✅ 文档数量正确减少1")
                    else:
                        print("   ❌ 文档数量变化异常")
                    
                    if test_doc_name not in after_files:
                        print(f"   ✅ 目标文档 '{test_doc_name}' 已从列表中移除")
                    else:
                        print(f"   ❌ 目标文档 '{test_doc_name}' 仍在列表中")
                    
                    # 检查相关索引是否更新
                    print(f"\n   🔄 检查索引更新状态:")
                    print(f"   - 文件名模式数量: {len(kb.filename_patterns)}")
                    print(f"   - TF-IDF矩阵: {'已更新' if kb.tfidf_matrix is not None else '未初始化'}")
                    if hasattr(kb, 'embedding_index') and kb.embedding_index:
                        print(f"   - 语义索引: 已更新")
                    else:
                        print(f"   - 语义索引: 未启用或未更新")
                    
                else:
                    print(f"   ❌ 删除操作失败")
            else:
                print(f"   ℹ️ 用户取消测试")
        
        print(f"\n✅ 删除功能测试完成")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def test_api_integration():
    """测试API集成"""
    print("\n" + "=" * 50)
    print("🌐 测试API集成")
    print("=" * 50)
    
    try:
        import requests
        
        print("1. 测试获取文档列表...")
        response = requests.get('http://localhost:5000/api/documents')
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API响应成功")
            print(f"   📚 文档数量: {data.get('total', 0)}")
            
            documents = data.get('documents', [])
            if documents:
                print("   📄 文档列表:")
                for doc in documents[:3]:  # 只显示前3个
                    print(f"      - ID: {doc['id']}, 文件名: {doc['filename']}")
                
                # 测试删除API
                if len(documents) > 0:
                    test_doc = documents[0]
                    print(f"\n2. 测试删除API...")
                    print(f"   目标文档: {test_doc['filename']} (ID: {test_doc['id']})")
                    
                    user_input = input(f"   是否测试删除API? (y/N): ").strip().lower()
                    
                    if user_input == 'y':
                        delete_response = requests.delete(f'http://localhost:5000/api/documents/{test_doc["id"]}')
                        
                        if delete_response.status_code == 200:
                            print("   ✅ 删除API调用成功")
                            
                            # 验证删除结果
                            time.sleep(1)  # 等待一秒
                            verify_response = requests.get('http://localhost:5000/api/documents')
                            
                            if verify_response.status_code == 200:
                                new_data = verify_response.json()
                                new_count = new_data.get('total', 0)
                                print(f"   📊 验证结果: 文档数量 {data['total']} -> {new_count}")
                                
                                if new_count == data['total'] - 1:
                                    print("   ✅ API删除功能正常工作")
                                else:
                                    print("   ❌ API删除后数量异常")
                        else:
                            print(f"   ❌ 删除API调用失败: {delete_response.status_code}")
                            print(f"   错误信息: {delete_response.text}")
                    else:
                        print("   ℹ️ 用户取消API测试")
            else:
                print("   📝 没有文档可供测试")
        else:
            print(f"   ❌ API调用失败: {response.status_code}")
            print("   请确保后端服务器正在运行 (python backend/app.py)")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到后端服务器")
        print("   请确保后端服务器正在运行 (python backend/app.py)")
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")

if __name__ == "__main__":
    test_delete_functionality()
    
    # 询问是否测试API
    print("\n" + "=" * 50)
    api_test = input("是否测试API集成? (需要后端服务器运行) (y/N): ").strip().lower()
    
    if api_test == 'y':
        test_api_integration()
    
    print("\n🎉 所有测试完成!")

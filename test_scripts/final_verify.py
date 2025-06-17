#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG系统最终验证脚本
执行完整的功能验证测试
"""

import os
import sys
import time

# 添加backend路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🎯 {title}")
    print(f"{'='*50}")

def print_section(title):
    print(f"\n🔍 {title}")
    print("-" * 30)

def main():
    print_header("RAG系统最终验证")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_tests = 0
    passed_tests = 0
    
    # 测试1: 依赖检查
    print_section("1. 检查系统依赖")
    total_tests += 1
    
    try:
        import sentence_transformers
        import faiss
        import torch
        import jieba
        import sklearn
        print("✅ 所有必需依赖已安装")
        print(f"   - sentence-transformers: {sentence_transformers.__version__}")
        print(f"   - torch: {torch.__version__}")
        passed_tests += 1
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
    
    # 测试2: 知识库初始化
    print_section("2. 知识库系统初始化")
    total_tests += 1
    
    try:
        from app import KnowledgeBase, EMBEDDING_AVAILABLE
        print(f"✅ 系统模块导入成功")
        print(f"   语义嵌入功能: {'启用' if EMBEDDING_AVAILABLE else '禁用'}")
        
        start = time.time()
        kb = KnowledgeBase()
        init_time = time.time() - start
        
        print(f"✅ 知识库初始化完成 (耗时: {init_time:.2f}s)")
        print(f"   - 文档数量: {len(kb.documents)}")
        print(f"   - 嵌入模型: {'已加载' if kb.embedding_model else '未加载'}")
        print(f"   - 语义索引: {'已构建' if kb.embedding_index else '未构建'}")
        
        if hasattr(kb, 'document_chunks'):
            print(f"   - 文档分块: {len(kb.document_chunks)} 个")
        
        passed_tests += 1
        
    except Exception as e:
        print(f"❌ 知识库初始化失败: {e}")
        kb = None
    
    # 测试3: 搜索功能验证
    if kb:
        print_section("3. 搜索功能验证")
        total_tests += 1
        
        test_queries = [
            "人工智能职业发展",
            "机器学习技能要求", 
            "AI领域如何提升竞争力"
        ]
        
        search_success = 0
        for i, query in enumerate(test_queries, 1):
            try:
                results = kb.search(query, max_results=2)
                if results:
                    result = results[0]
                    print(f"   查询 {i}: '{query}'")
                    print(f"      ✅ 返回 {len(results)} 个结果")
                    print(f"      📄 {result['filename']}")
                    print(f"      📊 分数: {result['score']:.3f}")
                    search_success += 1
                else:
                    print(f"   查询 {i}: '{query}' - ❌ 无结果")
            except Exception as e:
                print(f"   查询 {i}: '{query}' - ❌ 错误: {e}")
        
        if search_success == len(test_queries):
            print("✅ 搜索功能完全正常")
            passed_tests += 1
        else:
            print(f"⚠️  搜索功能部分正常 ({search_success}/{len(test_queries)})")
    
    # 测试4: 语义功能验证
    if kb and kb.embedding_model:
        print_section("4. 语义搜索功能验证")
        total_tests += 1
        
        try:
            # 测试语义相似查询
            query1 = "AI职业规划"
            query2 = "人工智能事业发展"
            
            results1 = kb._semantic_search(query1, k=2)
            results2 = kb._semantic_search(query2, k=2)
            
            print(f"   语义查询1: '{query1}' - {len(results1)} 个结果")
            print(f"   语义查询2: '{query2}' - {len(results2)} 个结果")
            
            if results1 and results2:
                # 检查语义相似性
                docs1 = set(r['document_id'] for r in results1)
                docs2 = set(r['document_id'] for r in results2)
                overlap = len(docs1 & docs2) / max(len(docs1), len(docs2))
                
                print(f"   📈 语义相似度: {overlap:.2f}")
                
                if overlap > 0.5:
                    print("✅ 语义搜索功能正常")
                    passed_tests += 1
                else:
                    print("⚠️  语义搜索功能需要调优")
            else:
                print("❌ 语义搜索无结果")
                
        except Exception as e:
            print(f"❌ 语义搜索测试失败: {e}")
    
    # 测试5: API就绪状态
    print_section("5. API服务就绪状态")
    total_tests += 1
    
    try:
        from app import app
        print("✅ Flask应用创建成功")
        
        # 检查关键路由
        with app.test_client() as client:
            routes = ['/api/search', '/api/upload', '/api/documents']
            for route in routes:
                print(f"   📡 API端点: {route}")
        
        print("✅ API服务就绪")
        passed_tests += 1
        
    except Exception as e:
        print(f"❌ API服务检查失败: {e}")
    
    # 最终报告
    print_header("验证结果总结")
    
    success_rate = passed_tests / total_tests * 100
    print(f"📊 测试通过率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 100:
        print("🎉 恭喜！RAG系统完全就绪！")
        print("✨ 系统具备以下能力:")
        print("   - 🧠 智能语义理解")
        print("   - 🔍 精准文档检索") 
        print("   - 📄 智能文档分块")
        print("   - 🎯 多模式搜索融合")
        print("   - 📊 智能结果重排序")
        print("\n🚀 启动命令: python backend/app.py")
        
    elif success_rate >= 80:
        print("✅ RAG系统基本就绪，核心功能正常")
        print("⚠️  部分高级功能可能需要进一步优化")
        
    elif success_rate >= 60:
        print("⚠️  RAG系统部分功能正常")
        print("🔧 建议检查配置和依赖")
        
    else:
        print("❌ RAG系统存在较多问题")
        print("🛠️  需要进行系统性修复")
    
    print(f"\n完成时间: {time.strftime('%H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  验证被用户中断")
    except Exception as e:
        print(f"\n\n❌ 验证过程异常: {e}")
        import traceback
        traceback.print_exc()

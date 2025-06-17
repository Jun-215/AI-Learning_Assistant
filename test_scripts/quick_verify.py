#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证当前RAG系统功能
"""

import os
import sys
import time

# 添加backend路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("RAG系统快速验证")
print("=" * 25)

def quick_test():
    """快速测试系统功能"""
    
    # 检查文档数据
    print("1. 检查知识库数据...")
    kb_file = os.path.join(backend_dir, 'knowledge_base', 'documents.json')
    
    if os.path.exists(kb_file):
        try:
            import json
            with open(kb_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            print(f"   ✓ 发现 {len(documents)} 个文档")
            
            # 显示文档信息
            for i, doc in enumerate(documents[:3], 1):
                print(f"   文档 {i}: {doc['filename']} ({len(doc['content'])} 字符)")
        except Exception as e:
            print(f"   ✗ 读取文档失败: {e}")
            return False
    else:
        print(f"   ✗ 知识库文件不存在: {kb_file}")
        return False
    
    # 检查依赖
    print("\n2. 检查关键依赖...")
    deps_status = {}
    
    try:
        import jieba
        deps_status['jieba'] = True
        print("   ✓ jieba (中文分词)")
    except ImportError:
        deps_status['jieba'] = False
        print("   ✗ jieba")
    
    try:
        import sklearn
        deps_status['sklearn'] = True
        print("   ✓ scikit-learn (TF-IDF)")
    except ImportError:
        deps_status['sklearn'] = False
        print("   ✗ scikit-learn")
    
    try:
        import sentence_transformers
        deps_status['sentence_transformers'] = True
        print("   ✓ sentence-transformers (语义嵌入)")
    except ImportError:
        deps_status['sentence_transformers'] = False
        print("   ✗ sentence-transformers")
    
    try:
        import faiss
        deps_status['faiss'] = True
        print("   ✓ faiss (向量索引)")
    except ImportError:
        deps_status['faiss'] = False
        print("   ✗ faiss")
    
    # 基础功能测试
    print("\n3. 测试基础功能...")
    
    if not deps_status.get('jieba', False) or not deps_status.get('sklearn', False):
        print("   ✗ 缺少基础依赖，无法继续测试")
        return False
    
    try:
        # 不导入完整的KnowledgeBase，先测试基础组件
        import jieba
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # 测试分词
        test_text = "人工智能和机器学习技术"
        words = list(jieba.cut(test_text))
        print(f"   ✓ 分词测试: {' '.join(words)}")
        
        # 测试TF-IDF
        texts = ["人工智能技术发展", "机器学习算法研究", "深度学习应用"]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        print(f"   ✓ TF-IDF测试: {tfidf_matrix.shape}")
        
        print("   ✓ 基础功能正常")
        
    except Exception as e:
        print(f"   ✗ 基础功能测试失败: {e}")
        return False
    
    # 语义功能测试
    print("\n4. 测试语义功能...")
    
    if deps_status.get('sentence_transformers', False) and deps_status.get('faiss', False):
        try:
            from sentence_transformers import SentenceTransformer
            
            print("   正在加载轻量级模型进行测试...")
            # 使用较小的模型进行快速测试
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # 测试编码
            test_sentences = ["这是一个测试", "人工智能发展"]
            embeddings = model.encode(test_sentences)
            print(f"   ✓ 语义编码测试: {embeddings.shape}")
            
            # 测试faiss
            import faiss
            import numpy as np
            
            # 创建简单索引
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings.astype('float32'))
            
            # 测试搜索
            scores, indices = index.search(embeddings[:1].astype('float32'), 2)
            print(f"   ✓ 向量搜索测试: 找到 {len(indices[0])} 个结果")
            
            print("   ✓ 语义功能正常")
            
        except Exception as e:
            print(f"   ⚠ 语义功能测试失败 (可能是首次下载): {e}")
    else:
        print("   ⚠ 语义功能依赖缺失，跳过测试")
    
    return True

def main():
    start_time = time.time()
    
    try:
        success = quick_test()
        elapsed = time.time() - start_time
        
        print(f"\n" + "=" * 25)
        print(f"验证完成! 耗时: {elapsed:.2f}秒")
        
        if success:
            print("✓ 系统基础功能正常")
            print("\n后续步骤:")
            print("1. 如果语义功能测试失败，请等待模型下载完成")
            print("2. 运行完整测试: python test_semantic.py")
            print("3. 启动服务器: python backend/app.py")
        else:
            print("✗ 系统存在问题，请检查依赖安装")
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n✗ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

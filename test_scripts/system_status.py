#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG系统状态总结
"""

import os
import sys
import json

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("=" * 50)
print("RAG系统状态总结")
print("=" * 50)

# 1. 检查项目结构
print("📁 项目结构:")
key_files = [
    'backend/app.py',
    'backend/config.py', 
    'backend/requirements.txt',
    'backend/knowledge_base/documents.json',
    'frontend/package.json'
]

for file_path in key_files:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    status = "✓" if os.path.exists(full_path) else "✗"
    print(f"   {status} {file_path}")

# 2. 检查知识库数据
print(f"\n📚 知识库状态:")
kb_file = os.path.join(backend_dir, 'knowledge_base', 'documents.json')
if os.path.exists(kb_file):
    try:
        with open(kb_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        print(f"   ✓ 文档数量: {len(documents)}")
        
        for i, doc in enumerate(documents, 1):
            print(f"   {i}. {doc['filename']} ({len(doc['content'])} 字符)")
    except Exception as e:
        print(f"   ✗ 读取失败: {e}")
else:
    print("   ✗ 知识库文件不存在")

# 3. 检查依赖状态
print(f"\n🔧 依赖库状态:")
dependencies = [
    ('Flask', 'flask'),
    ('中文分词', 'jieba'),
    ('机器学习', 'sklearn'),
    ('数值计算', 'numpy'),
    ('语义嵌入', 'sentence_transformers'),
    ('向量索引', 'faiss'),
    ('深度学习', 'torch')
]

available_deps = []
for name, module in dependencies:
    try:
        __import__(module)
        print(f"   ✓ {name}")
        available_deps.append(module)
    except ImportError:
        print(f"   ✗ {name}")

# 4. 功能评估
print(f"\n🎯 功能评估:")

basic_ready = all(dep in available_deps for dep in ['flask', 'jieba', 'sklearn', 'numpy'])
semantic_ready = all(dep in available_deps for dep in ['sentence_transformers', 'faiss', 'torch'])

print(f"   基础搜索功能: {'✓ 就绪' if basic_ready else '✗ 依赖缺失'}")
print(f"   语义搜索功能: {'✓ 就绪' if semantic_ready else '✗ 依赖缺失'}")
print(f"   智能文档检测: {'✓ 就绪' if basic_ready else '✗ 依赖缺失'}")
print(f"   重排序算法: {'✓ 就绪' if semantic_ready else '✗ 依赖缺失'}")

# 5. 下一步建议
print(f"\n🚀 下一步建议:")

if not basic_ready:
    print("   1. 安装基础依赖: pip install flask jieba scikit-learn numpy")
    
if not semantic_ready:
    print("   2. 安装语义搜索依赖: pip install sentence-transformers faiss-cpu torch")

if basic_ready and semantic_ready:
    print("   ✅ 所有依赖已就绪，可以运行完整测试:")
    print("      - python verify_rag.py (验证RAG功能)")
    print("      - python test_semantic.py (测试语义搜索)")
    print("      - python backend/app.py (启动服务器)")
    
    print(f"\n   📋 当前实现的功能:")
    print("      - 基于TF-IDF的关键词搜索")
    print("      - 中文分词和语义理解")
    print("      - 智能文档检测和针对性搜索")
    print("      - 多语言语义嵌入模型")
    print("      - FAISS向量索引")
    print("      - 融合重排序算法")
    print("      - RESTful API接口")

# 6. 系统总体评分
total_deps = len(dependencies)
available_count = len(available_deps)
readiness_score = (available_count / total_deps) * 100

print(f"\n📊 系统就绪度: {readiness_score:.1f}% ({available_count}/{total_deps})")

if readiness_score >= 80:
    print("🎉 系统基本就绪，可以开始使用！")
elif readiness_score >= 50:
    print("⚠️  系统部分就绪，建议安装缺失依赖")
else:
    print("❌ 系统需要安装更多依赖才能正常使用")

print("=" * 50)

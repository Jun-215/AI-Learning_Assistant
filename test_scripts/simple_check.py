import sys
import os

print("Python版本:", sys.version)
print("当前目录:", os.getcwd())

# 测试依赖导入
try:
    import sentence_transformers
    print("✓ sentence-transformers已安装，版本:", sentence_transformers.__version__)
except ImportError as e:
    print("✗ sentence-transformers未安装:", e)

try:
    import faiss
    print("✓ faiss已安装")
except ImportError as e:
    print("✗ faiss未安装:", e)

try:
    import torch
    print("✓ torch已安装，版本:", torch.__version__)
except ImportError as e:
    print("✗ torch未安装:", e)

print("\n测试后端模块...")
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

try:
    from app import EMBEDDING_AVAILABLE, KnowledgeBase
    print("✓ 后端模块导入成功")
    print("语义嵌入功能:", "可用" if EMBEDDING_AVAILABLE else "不可用")
    
    kb = KnowledgeBase()
    print("知识库文档数量:", len(kb.documents))
    
except Exception as e:
    print("✗ 后端模块导入失败:", e)
    import traceback
    traceback.print_exc()

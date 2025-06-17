#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试本地Sentence Transformer模型
"""

import os

# 设置离线模式
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

print("=== 快速本地模型测试 ===")

try:
    print("1. 导入sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    print("   ✓ 导入成功")
    
    print("2. 加载本地模型...")
    model_path = r"C:\Users\Jun\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2\snapshots\c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
    
    if os.path.exists(model_path):
        print(f"   ✓ 模型路径存在: {model_path}")
        
        # 尝试加载模型
        model = SentenceTransformer(model_path)
        print("   ✓ 模型加载成功")
        
        # 测试编码
        test_text = "这是一个测试句子"
        embedding = model.encode(test_text)
        print(f"   ✓ 编码测试成功，向量维度: {len(embedding)}")
        
        print("\n🎉 所有测试通过！")
        
    else:
        print(f"   × 模型路径不存在: {model_path}")
        
except Exception as e:
    print(f"   × 测试失败: {e}")

print("\n完成测试")

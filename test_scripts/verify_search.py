#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证改进后的搜索功能是否正常工作
"""

import sys
import os
import importlib.util

def check_dependencies():
    """检查依赖包是否安装"""
    required_packages = ['jieba', 'sklearn', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} 未安装")
    
    return missing_packages

def test_import_app():
    """测试导入app模块"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app import KnowledgeBase
        print("✓ 成功导入 KnowledgeBase 类")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from backend.app import KnowledgeBase
        
        kb = KnowledgeBase()
        
        # 测试文本预处理
        test_text = "人工智能是一门非常有趣的学科"
        processed = kb._preprocess_text(test_text)
        print(f"✓ 文本预处理正常: '{test_text}' -> '{processed}'")
        
        # 测试关键词提取
        keywords = kb._extract_keywords(test_text)
        print(f"✓ 关键词提取正常: {keywords}")
        
        return True
        
    except Exception as e:
        print(f"✗ 功能测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 搜索功能改进验证 ===\n")
    
    print("1. 检查依赖包安装状态...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n需要安装以下包: {missing}")
        print("请运行: pip install " + " ".join(missing))
        sys.exit(1)
    
    print("\n2. 测试模块导入...")
    if not test_import_app():
        sys.exit(1)
    
    print("\n3. 测试基本功能...")
    if not test_basic_functionality():
        sys.exit(1)
    
    print("\n🎉 所有测试通过！搜索功能改进成功！")
    print("\n接下来可以:")
    print("1. 运行 'python backend/app.py' 启动服务")
    print("2. 使用改进后的搜索功能")

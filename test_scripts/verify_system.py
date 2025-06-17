#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent 系统快速验证脚本
"""

def test_imports():
    """测试Python依赖导入"""
    try:
        import flask
        import flask_cors
        import PyPDF2
        import dashscope
        print("✅ Python依赖导入成功")
        return True
    except ImportError as e:
        print(f"❌ 依赖导入失败: {e}")
        return False

def test_config():
    """测试配置文件"""
    try:
        from config import Config
        config = Config()
        api_key = config.DASHSCOPE_API_KEY
        if api_key and api_key != 'your-api-key-here':
            print("✅ API密钥已配置")
            return True
        else:
            print("⚠️  API密钥未配置或使用默认值")
            return False
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return False

def test_directories():
    """测试目录结构"""
    import os
    
    required_dirs = [
        'backend',
        'frontend',
        'backend/uploads',
        'backend/knowledge_base'
    ]
    
    required_files = [
        'backend/app.py',
        'backend/config.py',
        'frontend/src/App.tsx',
        'frontend/package.json'
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"❌ 目录缺失: {dir_path}")
            all_good = False
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ 文件存在: {file_path}")
        else:
            print(f"❌ 文件缺失: {file_path}")
            all_good = False
    
    return all_good

def main():
    print("🔍 AI Agent 系统验证")
    print("=" * 40)
    
    print("\n1. 检查Python依赖...")
    deps_ok = test_imports()
    
    print("\n2. 检查配置...")
    config_ok = test_config()
    
    print("\n3. 检查文件结构...")
    files_ok = test_directories()
    
    print("\n" + "=" * 40)
    if deps_ok and files_ok:
        print("✅ 系统基础验证通过！")
        if config_ok:
            print("🚀 系统完全就绪，可以启动了")
        else:
            print("⚠️  请配置API密钥后再启动")
    else:
        print("❌ 系统验证失败，请检查上述问题")

if __name__ == '__main__':
    main()

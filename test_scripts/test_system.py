#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent 系统测试脚本
用于验证系统基础功能是否正常
"""

import requests
import json
import os
import sys

def test_backend_health():
    """测试后端健康状态"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接后端服务: {e}")
        return False

def test_chat_api():
    """测试聊天API"""
    try:
        response = requests.post(
            'http://localhost:5000/api/chat',
            json={'message': 'Hello, 这是一个测试消息'},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ 聊天API正常")
            print(f"   回复: {data.get('response', 'N/A')[:50]}...")
            print(f"   来源: {data.get('source', 'N/A')}")
            return True
        else:
            print(f"❌ 聊天API异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 聊天API调用失败: {e}")
        return False

def main():
    print("🚀 AI Agent 系统测试")
    print("=" * 40)
    
    # 检查后端是否启动
    if not test_backend_health():
        print("\n⚠️  请先启动后端服务:")
        print("   cd backend && python app.py")
        return
    
    # 测试聊天功能
    print("\n🔍 测试聊天功能...")
    test_chat_api()
    
    print("\n=" * 40)
    print("测试完成")

if __name__ == '__main__':
    main()

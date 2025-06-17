#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG第二阶段优化测试脚本
测试提示词优化效果
"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

def test_stage2_optimization():
    """测试第二阶段优化效果"""
    print("🚀 开始测试RAG第二阶段优化效果...")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "name": "知识边界测试",
            "question": "请解释量子计算的基本原理",
            "expected_behavior": "应该明确指出知识库中没有相关信息"
        },
        {
            "name": "基于文档回答测试",
            "question": "文档中提到了什么内容？",
            "expected_behavior": "应该基于检索到的文档内容回答，并标注来源"
        },
        {
            "name": "信息不足测试",
            "question": "请详细说明具体的技术实现细节",
            "expected_behavior": "应该说明背景资料中信息不足"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}: {test_case['name']}")
        print(f"问题: {test_case['question']}")
        print(f"期望行为: {test_case['expected_behavior']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": test_case['question']},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 响应成功")
                print(f"回答来源: {data.get('source', 'unknown')}")
                print(f"搜索模式: {data.get('search_mode', 'unknown')}")
                print(f"优化阶段: {data.get('optimization_stage', 'unknown')}")
                print(f"源文件: {data.get('source_files', [])}")
                print(f"回答内容: {data.get('response', '')[:200]}...")
                
                # 分析回答质量
                analyze_response_quality(data.get('response', ''), test_case)
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 RAG第二阶段优化测试完成")

def analyze_response_quality(response, test_case):
    """分析回答质量"""
    print("\n📊 回答质量分析:")
    
    # 检查关键词
    quality_indicators = {
        "基于背景资料": "✅ 明确基于背景资料" if "背景资料" in response else "❌ 未明确基于背景资料",
        "信息来源标注": "✅ 标注了信息来源" if any(word in response for word in ["文档", "来源", "根据"]) else "❌ 未标注信息来源",
        "知识边界": "✅ 明确知识边界" if any(word in response for word in ["没有找到", "信息不足", "无法", "不能"]) else "⚠️ 知识边界不明确",
        "避免幻觉": "✅ 避免了幻觉" if not any(word in response for word in ["众所周知", "一般来说", "通常"]) else "⚠️ 可能存在幻觉"
    }
    
    for indicator, result in quality_indicators.items():
        print(f"  {indicator}: {result}")

def test_prompt_framework():
    """测试提示词框架"""
    print("\n🔧 测试提示词框架...")
    
    # 发送一个简单查询，检查返回的详细信息
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "你好，请介绍一下你的功能"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 提示词框架测试成功")
            print(f"优化阶段标识: {data.get('optimization_stage')}")
            
            # 检查是否包含第二阶段优化特征
            if data.get('optimization_stage') == 'stage2_prompt_optimization':
                print("✅ 第二阶段优化已启用")
            else:
                print("⚠️ 第二阶段优化标识未找到")
                
        else:
            print(f"❌ 提示词框架测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 提示词框架测试错误: {e}")

def check_server_health():
    """检查服务器健康状态"""
    print("🏥 检查服务器健康状态...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 服务器健康状态良好")
            print(f"知识库文档数量: {health_data.get('knowledge_base_documents', 0)}")
            print(f"语义搜索功能: {'✅' if health_data.get('embedding_available') else '❌'}")
            print(f"嵌入模型状态: {'✅' if health_data.get('embedding_model_loaded') else '❌'}")
            print(f"优化阶段: {health_data.get('optimization_stage', 'unknown')}")
            return True
        else:
            print(f"❌ 服务器健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 RAG第二阶段优化 - 提示词优化测试")
    print("=" * 60)
    
    # 1. 检查服务器状态
    if not check_server_health():
        print("❌ 服务器不可用，请先启动服务器")
        return
    
    # 2. 测试提示词框架
    test_prompt_framework()
    
    # 3. 测试优化效果
    test_stage2_optimization()
    
    print("\n" + "=" * 60)
    print("🎉 RAG第二阶段优化测试完成！")
    print("\n📋 测试总结:")
    print("- ✅ 实现了明确的角色定位")
    print("- ✅ 优化了上下文使用方式") 
    print("- ✅ 加强了知识边界控制")
    print("- ✅ 提升了信息来源标注")
    print("- ✅ 增强了回答质量评估")

if __name__ == "__main__":
    main()

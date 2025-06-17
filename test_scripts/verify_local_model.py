#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地Hugging Face模型验证脚本
用于验证sentence-transformers/all-MiniLM-L6-v2模型的本地缓存是否可用
"""

import os
import sys

def check_local_model():
    """检查本地模型缓存"""
    print("=== 本地Hugging Face模型缓存检查 ===\n")
    
    # 配置信息
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    snapshot_id = 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf'
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    
    print(f"模型名称: {model_name}")
    print(f"快照ID: {snapshot_id}")
    print(f"缓存目录: {cache_dir}")
    
    # 构建路径
    model_cache_name = model_name.replace('/', '--')
    model_base_dir = os.path.join(cache_dir, f"models--{model_cache_name}")
    snapshots_dir = os.path.join(model_base_dir, "snapshots")
    target_snapshot_dir = os.path.join(snapshots_dir, snapshot_id)
    
    print(f"\n=== 路径检查 ===")
    print(f"模型基础目录: {model_base_dir}")
    print(f"快照目录: {snapshots_dir}")
    print(f"目标快照: {target_snapshot_dir}")
    
    # 检查路径是否存在
    paths_to_check = [
        ("缓存根目录", cache_dir),
        ("模型基础目录", model_base_dir),
        ("快照目录", snapshots_dir),
        ("目标快照目录", target_snapshot_dir)
    ]
    
    print(f"\n=== 目录存在性检查 ===")
    all_exists = True
    for name, path in paths_to_check:
        exists = os.path.exists(path)
        status = "✓" if exists else "×"
        print(f"{status} {name}: {exists}")
        if not exists:
            all_exists = False
    
    # 如果目标快照不存在，列出可用的快照
    if not os.path.exists(target_snapshot_dir) and os.path.exists(snapshots_dir):
        print(f"\n=== 可用快照列表 ===")
        try:
            available_snapshots = os.listdir(snapshots_dir)
            if available_snapshots:
                print("发现以下可用快照:")
                for snapshot in available_snapshots:
                    snapshot_path = os.path.join(snapshots_dir, snapshot)
                    if os.path.isdir(snapshot_path):
                        print(f"  - {snapshot}")
            else:
                print("没有找到任何快照")
        except Exception as e:
            print(f"无法列出快照: {e}")
    
    # 检查关键文件
    if os.path.exists(target_snapshot_dir):
        print(f"\n=== 模型文件检查 ===")
        key_files = [
            "config.json",
            "pytorch_model.bin",
            "tokenizer.json",
            "tokenizer_config.json"
        ]
        
        for file_name in key_files:
            file_path = os.path.join(target_snapshot_dir, file_name)
            exists = os.path.exists(file_path)
            status = "✓" if exists else "×"
            print(f"{status} {file_name}: {exists}")
    
    return all_exists

def test_model_loading():
    """测试模型加载"""
    print(f"\n=== 模型加载测试 ===")
    
    # 设置离线模式
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    
    try:
        print("正在导入sentence_transformers...")
        from sentence_transformers import SentenceTransformer
        print("✓ sentence_transformers导入成功")
        
        # 配置
        model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        snapshot_id = 'c9745ed1d9f207416be6d2e6f8de32d1f16199bf'
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        
        # 方法1: 使用模型名称
        print(f"\n方法1: 使用模型名称加载...")
        try:
            model = SentenceTransformer(model_name, cache_folder=cache_dir)
            print("✓ 方法1成功")
            
            # 测试编码
            test_text = "这是一个测试句子"
            embedding = model.encode(test_text)
            print(f"✓ 测试编码成功，向量维度: {len(embedding)}")
            
            return True
            
        except Exception as e:
            print(f"× 方法1失败: {e}")
        
        # 方法2: 使用直接路径
        print(f"\n方法2: 使用直接路径加载...")
        try:
            model_cache_name = model_name.replace('/', '--')
            local_path = os.path.join(cache_dir, f"models--{model_cache_name}", "snapshots", snapshot_id)
            
            if os.path.exists(local_path):
                model = SentenceTransformer(local_path)
                print("✓ 方法2成功")
                
                # 测试编码
                test_text = "这是一个测试句子"
                embedding = model.encode(test_text)
                print(f"✓ 测试编码成功，向量维度: {len(embedding)}")
                
                return True
            else:
                print(f"× 方法2失败: 路径不存在 {local_path}")
                
        except Exception as e:
            print(f"× 方法2失败: {e}")
            
        return False
        
    except ImportError as e:
        print(f"× 无法导入sentence_transformers: {e}")
        print("请确保已安装: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"× 模型加载测试失败: {e}")
        return False

def main():
    """主函数"""
    print("本地Hugging Face Sentence Transformer模型验证")
    print("=" * 60)
    
    # 检查本地缓存
    cache_ok = check_local_model()
    
    if cache_ok:
        print(f"\n✓ 本地模型缓存检查通过")
        # 测试加载
        load_ok = test_model_loading()
        if load_ok:
            print(f"\n🎉 所有测试通过！本地模型可以正常使用")
            print(f"\n建议使用的配置:")
            print(f"模型名称: sentence-transformers/all-MiniLM-L6-v2")
            print(f"离线模式: HF_HUB_OFFLINE=1")
        else:
            print(f"\n❌ 模型加载测试失败")
    else:
        print(f"\n❌ 本地模型缓存检查失败")
        print(f"\n解决方案:")
        print(f"1. 确认模型已下载到正确位置")
        print(f"2. 检查快照ID是否正确")
        print(f"3. 尝试重新下载模型")

if __name__ == "__main__":
    main()

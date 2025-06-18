"""
嵌入模型服务模块
"""
import os
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

def check_local_model_cache(model_name):
    """检查本地是否有模型缓存"""
    try:
        # Hugging Face模型缓存的可能位置
        cache_locations = [
            os.path.expanduser("~/.cache/huggingface/hub"),
            os.path.expanduser("~/.cache/huggingface/transformers"),
            os.path.expanduser("~/AppData/Local/huggingface/hub"),  # Windows
        ]
        
        model_cache_name = model_name.replace('/', '--')
        
        for cache_dir in cache_locations:
            if not os.path.exists(cache_dir):
                continue
                
            model_dir = os.path.join(cache_dir, f"models--{model_cache_name}")
            if os.path.exists(model_dir):
                snapshots_dir = os.path.join(model_dir, "snapshots")
                if os.path.exists(snapshots_dir):
                    snapshots = os.listdir(snapshots_dir)
                    if snapshots:
                        # 找到最新的快照
                        latest_snapshot = max(snapshots, key=lambda x: os.path.getctime(os.path.join(snapshots_dir, x)))
                        snapshot_path = os.path.join(snapshots_dir, latest_snapshot)
                        
                        # 检查关键文件是否存在
                        key_files = ['config.json', 'tokenizer_config.json']
                        if all(os.path.exists(os.path.join(snapshot_path, f)) for f in key_files):
                            print(f"✓ 发现本地模型缓存: {snapshot_path}")
                            return snapshot_path
        
        print(f"× 未发现本地模型缓存: {model_name}")
        return None
        
    except Exception as e:
        print(f"× 检查本地缓存时出错: {e}")
        return None

def load_embedding_model_smart(model_name, fallback_models=None):
    """智能加载嵌入模型：优先本地缓存，无缓存时在线加载"""
    if not EMBEDDING_AVAILABLE:
        return None
        
    if fallback_models is None:
        fallback_models = []
    
    all_models = [model_name] + fallback_models
    
    for current_model in all_models:
        try:
            print(f"尝试加载模型: {current_model}")
            
            # 1. 检查本地缓存
            local_path = check_local_model_cache(current_model)
            
            if local_path:
                # 使用本地缓存（离线模式）
                print(f"使用本地缓存加载: {current_model}")
                original_offline = os.environ.get('HF_HUB_OFFLINE', '0')
                os.environ['HF_HUB_OFFLINE'] = '1'
                
                try:
                    model = SentenceTransformer(local_path)
                    print(f"✓ 成功从本地缓存加载: {current_model}")
                    return model
                except Exception as e:
                    print(f"× 本地缓存加载失败: {e}")
                    # 尝试使用模型名称从缓存加载
                    try:
                        model = SentenceTransformer(current_model)
                        print(f"✓ 成功使用模型名称从缓存加载: {current_model}")
                        return model
                    except Exception as e2:
                        print(f"× 缓存模型名称加载也失败: {e2}")
                finally:
                    # 恢复原始离线设置
                    os.environ['HF_HUB_OFFLINE'] = original_offline
            else:
                # 没有本地缓存，尝试在线下载
                print(f"本地无缓存，尝试在线下载: {current_model}")
                
                # 确保在线模式
                original_offline = os.environ.get('HF_HUB_OFFLINE', '0')
                if 'HF_HUB_OFFLINE' in os.environ:
                    del os.environ['HF_HUB_OFFLINE']
                if 'TRANSFORMERS_OFFLINE' in os.environ:
                    del os.environ['TRANSFORMERS_OFFLINE']
                
                try:
                    model = SentenceTransformer(current_model)
                    print(f"✓ 成功在线下载并加载: {current_model}")
                    return model
                except Exception as e:
                    print(f"× 在线下载失败: {e}")
                finally:
                    # 恢复原始设置
                    if original_offline != '0':
                        os.environ['HF_HUB_OFFLINE'] = original_offline
        
        except Exception as e:
            print(f"× 模型 {current_model} 加载完全失败: {e}")
            continue
    
    print("× 所有模型都加载失败")
    return None

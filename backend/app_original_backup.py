from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
from datetime import datetime
import PyPDF2
import dashscope
from config import Config
import jieba
import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from difflib import SequenceMatcher
import math
import logging

# 第二阶段优化相关导入
from stage2_config import stage2_config, prompt_builder, quality_assessor

# 语义嵌入相关导入
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    EMBEDDING_AVAILABLE = True
except ImportError:
    print("警告: sentence-transformers或faiss未安装，语义搜索功能将被禁用")
    EMBEDDING_AVAILABLE = False

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# 设置日志级别
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)

# 配置阿里千问API
dashscope.api_key = app.config['DASHSCOPE_API_KEY']

# 确保必要的目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['KNOWLEDGE_BASE_PATH'], exist_ok=True)

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

class KnowledgeBase:
    def __init__(self):
        self.documents = []
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.processed_contents = []
        self.filename_patterns = {}  # 存储文件名模式，用于智能匹配
        
        # 语义嵌入相关
        self.embedding_model = None
        self.document_embeddings = None
        self.embedding_index = None
        self.document_chunks = []  # 存储文档分块信息
        
        self.load_knowledge_base()
        # 初始化jieba分词
        jieba.setLogLevel(jieba.logging.INFO)
        self._build_filename_patterns()
        
        # 初始化语义嵌入模型
        if EMBEDDING_AVAILABLE:
            self._init_embedding_model()
        else:
            print("跳过语义嵌入模型初始化")
    
    def load_knowledge_base(self):
        """加载知识库"""
        kb_file = os.path.join(app.config['KNOWLEDGE_BASE_PATH'], 'documents.json')
        if os.path.exists(kb_file):
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                self._rebuild_search_index()
            except:
                self.documents = []
        else:
            self.documents = []
    
    def _init_embedding_model(self):
        """初始化语义嵌入模型 - 智能加载：优先本地缓存，无缓存时在线加载"""
        try:
            print("正在智能加载语义嵌入模型...")
            
            # 优先使用的模型列表
            preferred_models = [
                'sentence-transformers/all-MiniLM-L6-v2',
                'paraphrase-multilingual-MiniLM-L12-v2',
                'distiluse-base-multilingual-cased'
            ]
            
            # 使用智能加载函数
            self.embedding_model = load_embedding_model_smart(
                model_name=preferred_models[0],
                fallback_models=preferred_models[1:]
            )
            
            if self.embedding_model is None:
                print("× 所有嵌入模型加载失败，将使用TF-IDF作为备选")
                return
            
            print("✓ 嵌入模型初始化成功")
            
            # 重建语义索引
            self._build_semantic_index()
            
        except Exception as e:
            print(f"× 嵌入模型初始化失败: {e}")
            self.embedding_model = None
    
    def _split_document_into_chunks(self, content, chunk_size=300, overlap=50):
        """将文档分割成语义块"""
        # 按句子分割
        sentences = re.split(r'[。！？\n]', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 如果当前块加上新句子不会超过限制，就添加
            if len(current_chunk) + len(sentence) <= chunk_size:
                if current_chunk:
                    current_chunk += "。" + sentence
                else:
                    current_chunk = sentence
            else:
                # 如果当前块不为空，保存它
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 开始新的块
                current_chunk = sentence
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)
        
        # 处理重叠
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            overlapped_chunks.append(chunk)
            
            # 如果不是最后一个块，创建重叠块
            if i < len(chunks) - 1 and overlap > 0:
                # 取当前块的后半部分和下一块的前半部分
                chunk_words = list(chunk)
                next_chunk_words = list(chunks[i + 1])
                
                if len(chunk_words) > overlap and len(next_chunk_words) > overlap:
                    overlap_chunk = ''.join(chunk_words[-overlap:]) + ''.join(next_chunk_words[:overlap])
                    if len(overlap_chunk) >= 20:  # 只保留有意义的重叠块
                        overlapped_chunks.append(overlap_chunk)
        
        return overlapped_chunks
    
    def _build_semantic_index(self):
        """构建语义向量索引"""
        if not self.embedding_model or not self.documents:
            return
        
        print("正在构建语义向量索引...")
        
        # 清空现有的块数据
        self.document_chunks = []
        
        # 为每个文档创建语义块
        all_chunks = []
        for doc in self.documents:
            chunks = self._split_document_into_chunks(doc['content'])
            for chunk in chunks:
                chunk_info = {
                    'text': chunk,
                    'document_id': doc['id'],
                    'filename': doc['filename'],
                    'chunk_index': len(all_chunks)
                }
                self.document_chunks.append(chunk_info)
                all_chunks.append(chunk)
        
        if not all_chunks:
            return
        
        try:
            # 生成嵌入向量
            print(f"正在为 {len(all_chunks)} 个文档块生成嵌入向量...")
            self.document_embeddings = self.embedding_model.encode(all_chunks, 
                                                                  show_progress_bar=True,
                                                                  normalize_embeddings=True)
            
            # 构建FAISS索引
            dimension = self.document_embeddings.shape[1]
            self.embedding_index = faiss.IndexFlatIP(dimension)  # 使用内积相似度
            self.embedding_index.add(self.document_embeddings.astype('float32'))
            
            print(f"✓ 语义索引构建完成，维度: {dimension}")
            
        except Exception as e:
            print(f"× 语义索引构建失败: {e}")
            self.embedding_index = None
            self.document_embeddings = None
    
    def _semantic_search(self, query, k=10):
        """执行语义搜索"""
        if not self.embedding_model or not self.embedding_index:
            return []
        
        try:
            # 生成查询嵌入
            query_embedding = self.embedding_model.encode([query], normalize_embeddings=True)
            
            # 在索引中搜索
            scores, indices = self.embedding_index.search(query_embedding.astype('float32'), k)
            
            # 构建结果
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.document_chunks):
                    chunk_info = self.document_chunks[idx]
                    results.append({
                        'chunk_index': idx,
                        'document_id': chunk_info['document_id'],
                        'filename': chunk_info['filename'],
                        'text': chunk_info['text'],
                        'semantic_score': float(score),
                        'rank': i + 1
                    })
            
            return results
            
        except Exception as e:
            print(f"语义搜索失败: {e}")
            return []
    
    def _rerank_results(self, query, semantic_results, keyword_results):
        """重排序结果，融合语义搜索和关键词搜索的结果"""
        # 创建结果字典，以文档ID为键
        combined_results = {}
        
        # 处理语义搜索结果
        for result in semantic_results:
            doc_id = result['document_id']
            if doc_id not in combined_results:
                combined_results[doc_id] = {
                    'document_id': doc_id,
                    'filename': result['filename'],
                    'semantic_score': 0,
                    'keyword_score': 0,
                    'semantic_chunks': [],
                    'keyword_content': '',
                    'combined_score': 0
                }
            
            # 累积语义分数（取前3个块的平均分）
            if len(combined_results[doc_id]['semantic_chunks']) < 3:
                combined_results[doc_id]['semantic_chunks'].append({
                    'text': result['text'],
                    'score': result['semantic_score']
                })
                combined_results[doc_id]['semantic_score'] += result['semantic_score']
        
        # 处理关键词搜索结果
        for result in keyword_results:
            doc_id = result['document_id']
            if doc_id not in combined_results:
                combined_results[doc_id] = {
                    'document_id': doc_id,
                    'filename': result['filename'],
                    'semantic_score': 0,
                    'keyword_score': 0,
                    'semantic_chunks': [],
                    'keyword_content': '',
                    'combined_score': 0
                }
            
            combined_results[doc_id]['keyword_score'] = result['score']
            combined_results[doc_id]['keyword_content'] = result['content']
        
        # 计算综合分数并构建最终结果
        final_results = []
        for doc_id, data in combined_results.items():
            # 语义分数归一化
            semantic_score = data['semantic_score'] / max(len(data['semantic_chunks']), 1)
            keyword_score = data['keyword_score']
            
            # 综合评分：语义搜索权重0.6，关键词搜索权重0.4
            combined_score = semantic_score * 0.6 + keyword_score * 0.4
            
            # 构建内容
            content_parts = []
            if data['semantic_chunks']:
                # 选择分数最高的语义块
                best_chunks = sorted(data['semantic_chunks'], 
                                   key=lambda x: x['score'], reverse=True)[:2]
                for chunk in best_chunks:
                    content_parts.append(chunk['text'])
            
            if data['keyword_content']:
                content_parts.append(data['keyword_content'])
            
            final_content = '\n\n'.join(content_parts)
            
            final_results.append({
                'document_id': doc_id,
                'filename': data['filename'],
                'content': final_content,
                'score': combined_score,
                'semantic_score': semantic_score,
                'keyword_score': keyword_score,
                'reranked': True
            })
        
        # 按综合分数排序
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results
    
    def save_knowledge_base(self):
        """保存知识库"""
        kb_file = os.path.join(app.config['KNOWLEDGE_BASE_PATH'], 'documents.json')
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def _preprocess_text(self, text):
        """文本预处理：清洗、分词、去停用词"""
        # 清理文本
        text = re.sub(r'\s+', ' ', text)  # 规范化空白字符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)  # 只保留中英文数字
        
        # 使用jieba分词
        words = jieba.lcut(text)
        
        # 简单的停用词列表
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '为', '与', '等', '可以', '如何', '什么', '怎么', '为什么', '哪里'}
        
        # 过滤停用词和短词
        filtered_words = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return ' '.join(filtered_words)
    
    def _extract_keywords(self, text, top_k=10):
        """提取关键词"""
        words = pseg.cut(text)
        # 选择名词、动词、形容词作为关键词
        keywords = []
        for word, flag in words:
            if flag.startswith(('n', 'v', 'a')) and len(word) > 1:
                keywords.append(word)
        
        # 去重并返回前top_k个
        return list(set(keywords))[:top_k]
    
    def _rebuild_search_index(self):
        """重建搜索索引"""
        if not self.documents:
            return
        
        # 预处理所有文档内容
        self.processed_contents = []
        for doc in self.documents:
            processed_content = self._preprocess_text(doc['content'])
            self.processed_contents.append(processed_content)
        
        # 构建TF-IDF向量
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # 支持1-2gram
            min_df=1,
            max_df=0.95
        )
        
        try:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.processed_contents)
        except:
            self.tfidf_matrix = None
    
    def _build_filename_patterns(self):
        """构建文件名匹配模式，支持多种文件名识别方式"""
        self.filename_patterns = {}
        for doc in self.documents:
            filename = doc['filename']
            # 存储完整文件名（包含扩展名）
            self.filename_patterns[filename.lower()] = doc['id']
            
            # 存储不含扩展名的文件名
            name_without_ext = os.path.splitext(filename)[0].lower()
            self.filename_patterns[name_without_ext] = doc['id']
            
            # 处理中文文件名的关键词
            keywords = self._extract_filename_keywords(filename)
            for keyword in keywords:
                if keyword not in self.filename_patterns:
                    self.filename_patterns[keyword] = []
                if isinstance(self.filename_patterns[keyword], list):
                    if doc['id'] not in self.filename_patterns[keyword]:
                        self.filename_patterns[keyword].append(doc['id'])
                else:
                    # 转换为列表格式
                    existing_id = self.filename_patterns[keyword]
                    self.filename_patterns[keyword] = [existing_id, doc['id']]
    
    def _extract_filename_keywords(self, filename):
        """从文件名中提取关键词"""
        # 去掉扩展名
        name_without_ext = os.path.splitext(filename)[0]
        
        # 使用jieba分词提取中文关键词
        keywords = []
        words = jieba.lcut(name_without_ext)
        for word in words:
            if len(word) > 1 and word not in {'的', '了', '在', '是', '和', '与', '等'}:
                keywords.append(word.lower())
        
        # 添加英文单词（按空格、下划线、横线分割）
        import re
        english_words = re.findall(r'[a-zA-Z]+', name_without_ext)
        for word in english_words:
            if len(word) > 2:
                keywords.append(word.lower())
        
        return keywords
    
    def _detect_target_filename(self, query):
        """检测查询中是否包含特定的文件名"""
        query_lower = query.lower()
        detected_files = []
        confidence_scores = {}
        
        # 1. 完全匹配检测
        for pattern, doc_ids in self.filename_patterns.items():
            if pattern in query_lower:
                if isinstance(doc_ids, list):
                    for doc_id in doc_ids:
                        if doc_id not in detected_files:
                            detected_files.append(doc_id)
                            confidence_scores[doc_id] = confidence_scores.get(doc_id, 0) + len(pattern) * 2
                else:
                    if doc_ids not in detected_files:
                        detected_files.append(doc_ids)
                        confidence_scores[doc_ids] = confidence_scores.get(doc_ids, 0) + len(pattern) * 2
        
        # 2. 文件扩展名检测（如果用户提到了.pdf, .doc等）
        extensions = ['.pdf', '.doc', '.docx', '.txt', '.xlsx']
        for ext in extensions:
            if ext in query_lower:
                # 寻找扩展名前的文件名部分
                import re
                pattern = r'(\S+)' + re.escape(ext)
                matches = re.finditer(pattern, query_lower)
                for match in matches:
                    potential_filename = match.group(1) + ext
                    for doc in self.documents:
                        if doc['filename'].lower() == potential_filename:
                            if doc['id'] not in detected_files:
                                detected_files.append(doc['id'])
                                confidence_scores[doc['id']] = confidence_scores.get(doc['id'], 0) + 10
        
        # 3. 按置信度排序
        if detected_files and confidence_scores:
            detected_files.sort(key=lambda x: confidence_scores.get(x, 0), reverse=True)
        
        return detected_files, confidence_scores
    
    def _fuzzy_match_score(self, query_word, doc_words):
        """计算模糊匹配分数"""
        max_score = 0
        for word in doc_words:
            # 使用序列匹配计算相似度
            similarity = SequenceMatcher(None, query_word, word).ratio()
            if similarity > max_score:
                max_score = similarity
        return max_score
    
    def _calculate_keyword_match_score(self, query_keywords, doc_content):
        """计算关键词匹配分数"""
        content_lower = doc_content.lower()
        doc_words = jieba.lcut(content_lower)
        
        total_score = 0
        matched_keywords = 0
        
        for keyword in query_keywords:
            keyword_lower = keyword.lower()
            
            # 精确匹配
            if keyword_lower in content_lower:
                total_score += 2.0
                matched_keywords += 1
            else:
                # 模糊匹配
                fuzzy_score = self._fuzzy_match_score(keyword_lower, doc_words)
                if fuzzy_score > 0.7:  # 相似度阈值
                    total_score += fuzzy_score
                    matched_keywords += 1
        
        # 考虑匹配关键词的比例
        if query_keywords:
            match_ratio = matched_keywords / len(query_keywords)
            total_score *= (1 + match_ratio)
        
        return total_score
    
    def _extract_relevant_snippets(self, content, query_keywords, max_snippets=3, snippet_length=200):
        """提取相关文本片段"""
        sentences = re.split(r'[。！？\n]', content)
        scored_sentences = []
        
        for sentence in sentences:
            if len(sentence.strip()) < 10:  # 跳过过短的句子
                continue
                
            score = 0
            sentence_lower = sentence.lower()
            
            # 计算句子与查询关键词的相关性
            for keyword in query_keywords:
                if keyword.lower() in sentence_lower:
                    score += 1
                    # 如果关键词在句子开头，给予额外分数
                    if sentence_lower.strip().startswith(keyword.lower()):
                        score += 0.5
            
            if score > 0:
                scored_sentences.append((sentence.strip(), score))
        
        # 按分数排序并选择最相关的片段
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        snippets = []
        for sentence, _ in scored_sentences[:max_snippets]:
            # 确保片段不超过指定长度
            if len(sentence) > snippet_length:
                sentence = sentence[:snippet_length] + "..."
            snippets.append(sentence)
        
        return snippets
    
    def add_document(self, filename, content):
        """添加文档到知识库"""
        doc = {
            'id': len(self.documents) + 1,
            'filename': filename,
            'content': content,
            'created_at': datetime.now().isoformat()
        }
        self.documents.append(doc)
        self.save_knowledge_base()
        # 重建搜索索引和文件名模式
        self._rebuild_search_index()
        self._build_filename_patterns()
        
        # 重建语义索引
        if EMBEDDING_AVAILABLE and self.embedding_model:
            self._build_semantic_index()
        
        return doc['id']
    
    def delete_document(self, doc_id):
        """删除知识库中的文档"""
        try:
            # 1. 查找要删除的文档
            doc_to_delete = None
            for i, doc in enumerate(self.documents):
                if doc['id'] == doc_id:
                    doc_to_delete = doc
                    break
            
            if not doc_to_delete:
                print(f"文档 ID {doc_id} 不存在")
                return False
            
            # 2. 从文档列表中移除
            self.documents = [doc for doc in self.documents if doc['id'] != doc_id]
            
            # 3. 删除相应的物理文件（如果存在）
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_to_delete['filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"已删除物理文件: {file_path}")
            except Exception as e:
                print(f"删除物理文件失败: {e}")
                # 即使物理文件删除失败，也继续删除数据库记录
            
            # 4. 保存更新后的知识库
            self.save_knowledge_base()
            
            # 5. 重建搜索索引
            self._rebuild_search_index()
            
            # 6. 重建文件名模式
            self._build_filename_patterns()
            
            # 7. 重建语义索引（如果启用）
            if EMBEDDING_AVAILABLE and self.embedding_model:
                try:
                    self._build_semantic_index()
                    print("语义索引已重建")
                except Exception as e:
                    print(f"重建语义索引失败: {e}")
            
            print(f"文档 '{doc_to_delete['filename']}' (ID: {doc_id}) 已成功删除")
            return True
            
        except Exception as e:
            print(f"删除文档时发生错误: {e}")
            return False

    def search(self, query, threshold=0.1, max_results=5, target_documents=None):
        """增强的智能搜索功能，支持语义搜索和重排序"""
        if not self.documents:
            return []
        
        # 1. 检测查询中是否指向特定文档
        detected_files, confidence_scores = self._detect_target_filename(query)
        
        # 如果检测到特定文档引用，限制搜索范围
        search_scope = target_documents or detected_files
        
        results = []
        
        # 2. 预处理查询
        processed_query = self._preprocess_text(query)
        query_keywords = self._extract_keywords(query)
        
        # 3. 确定要搜索的文档范围
        documents_to_search = []
        if search_scope:
            # 只在指定的文档中搜索
            for doc in self.documents:
                if doc['id'] in search_scope:
                    documents_to_search.append(doc)
            search_info = {
                'search_mode': 'targeted',
                'target_files': [doc['filename'] for doc in documents_to_search],
                'detection_confidence': confidence_scores,
                'semantic_enabled': EMBEDDING_AVAILABLE and self.embedding_model is not None
            }
        else:
            # 在所有文档中搜索
            documents_to_search = self.documents
            search_info = {
                'search_mode': 'global',
                'target_files': [],
                'detection_confidence': {},
                'semantic_enabled': EMBEDDING_AVAILABLE and self.embedding_model is not None
            }
        
        if not documents_to_search:
            return []
        
        # 4. 语义搜索（如果可用）
        semantic_results = []
        if EMBEDDING_AVAILABLE and self.embedding_model and self.embedding_index:
            try:
                semantic_results = self._semantic_search(query, k=max_results * 2)
                
                # 如果是针对特定文档的搜索，过滤语义结果
                if search_scope:
                    semantic_results = [r for r in semantic_results 
                                      if r['document_id'] in search_scope]
                
                print(f"语义搜索找到 {len(semantic_results)} 个结果")
            except Exception as e:
                print(f"语义搜索失败: {e}")
                semantic_results = []
        
        # 5. 传统关键词搜索（作为备选和补充）
        keyword_results = []
        
        # TF-IDF向量搜索（如果可用且在全局搜索模式）
        tfidf_scores = {}
        if self.tfidf_matrix is not None and processed_query and not search_scope:
            try:
                query_vector = self.tfidf_vectorizer.transform([processed_query])
                similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
                
                for i, score in enumerate(similarities):
                    if score > threshold and i < len(self.documents):
                        tfidf_scores[self.documents[i]['id']] = score
            except:
                pass
        
        # 计算关键词匹配分数
        for doc in documents_to_search:
            total_score = 0
            
            # TF-IDF分数（只在全局搜索时使用）
            tfidf_score = tfidf_scores.get(doc['id'], 0) if not search_scope else 0
            total_score += tfidf_score * 2  # 降低TF-IDF权重
            
            # 关键词匹配分数
            keyword_score = self._calculate_keyword_match_score(query_keywords, doc['content'])
            total_score += keyword_score * 1.5  # 调整关键词匹配权重
            
            # 简单文本匹配分数（兜底方案）
            query_lower = query.lower()
            content_lower = doc['content'].lower()
            if query_lower in content_lower:
                total_score += len(re.findall(re.escape(query_lower), content_lower)) * 0.3
            
            # 如果是针对特定文档的搜索，降低阈值并给予额外分数
            if search_scope and doc['id'] in search_scope:
                total_score += confidence_scores.get(doc['id'], 0) * 0.1
                effective_threshold = threshold * 0.3
            else:
                effective_threshold = threshold
            
            # 如果总分数超过阈值，添加到关键词结果
            if total_score > effective_threshold:
                relevant_snippets = self._extract_relevant_snippets(
                    doc['content'], 
                    query_keywords + [query],
                    max_snippets=2
                )
                
                if relevant_snippets:
                    keyword_results.append({
                        'document_id': doc['id'],
                        'filename': doc['filename'],
                        'content': '\n'.join(relevant_snippets),
                        'score': total_score,
                        'tfidf_score': tfidf_score,
                        'keyword_score': keyword_score,
                        'matched_keywords': query_keywords,
                        'search_info': search_info,
                        'file_match_confidence': confidence_scores.get(doc['id'], 0)
                    })
        
        # 6. 结果融合和重排序
        if semantic_results and keyword_results:
            # 使用重排序算法融合结果
            try:
                results = self._rerank_results(query, semantic_results, keyword_results)
                for result in results:
                    result['search_info'] = search_info
                print(f"重排序后得到 {len(results)} 个结果")
            except Exception as e:
                print(f"重排序失败，使用关键词结果: {e}")
                results = keyword_results
                
        elif semantic_results:
            # 只有语义搜索结果
            print("只使用语义搜索结果")
            doc_results = {}
            for sem_result in semantic_results:
                doc_id = sem_result['document_id']
                if doc_id not in doc_results:
                    doc_results[doc_id] = {
                        'document_id': doc_id,
                        'filename': sem_result['filename'],
                        'content': sem_result['text'],
                        'score': sem_result['semantic_score'],
                        'semantic_score': sem_result['semantic_score'],
                        'keyword_score': 0,
                        'search_info': search_info,
                        'file_match_confidence': confidence_scores.get(doc_id, 0)
                    }
                else:
                    # 合并多个语义块
                    doc_results[doc_id]['content'] += '\n\n' + sem_result['text']
                    doc_results[doc_id]['score'] = max(doc_results[doc_id]['score'], 
                                                     sem_result['semantic_score'])
            
            results = list(doc_results.values())
            results.sort(key=lambda x: x['score'], reverse=True)
            
        else:
            # 只有关键词搜索结果
            print("只使用关键词搜索结果")
            results = keyword_results
        
        # 7. 如果没有找到结果且不是针对特定文档的搜索，降低阈值重新搜索
        if not results and not search_scope and threshold > 0.05:
            print("降低阈值重新搜索...")
            return self.search(query, threshold=threshold * 0.5, max_results=max_results)
        
        # 8. 按综合分数排序并返回结果
        if not any('reranked' in result for result in results):
            results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def _build_general_prompt(self, context, user_question):
        """构建通用RAG提示词框架 - 使用配置化的第二阶段优化版本"""
        return prompt_builder.build_system_prompt(
            prompt_type="general",
            context=context,
            user_question=user_question
        )
    
    def _build_targeted_prompt(self, context, target_files, user_question):
        """构建针对特定文档的RAG提示词框架 - 使用配置化的第二阶段优化版本"""
        return prompt_builder.build_system_prompt(
            prompt_type="targeted",
            context=context,
            user_question=user_question,
            target_files=target_files
        )
    
    def _enhance_context_quality(self, search_results, user_question):
        """增强上下文质量 - 第二阶段优化"""
        if not search_results:
            return "", []
        
        # 1. 按相关性重新排序
        enhanced_results = []
        for result in search_results:
            # 计算内容与问题的相关性
            content_relevance = self._calculate_content_relevance(result['content'], user_question)
            result['enhanced_score'] = result.get('score', 0) + content_relevance * 0.3
            enhanced_results.append(result)
        
        # 2. 重新排序
        enhanced_results.sort(key=lambda x: x['enhanced_score'], reverse=True)
        
        # 3. 构建高质量上下文
        context_parts = []
        source_files = []
        
        for i, result in enumerate(enhanced_results):
            source_files.append(result['filename'])
            
            # 为每个内容片段添加更清晰的标识
            content_snippet = f"""
**文档来源：{result['filename']}**
**相关性评分：{result['enhanced_score']:.3f}**
**内容：**
{result['content'].strip()}
---"""
            context_parts.append(content_snippet)
        
        enhanced_context = "\n".join(context_parts)
        
        return enhanced_context, list(set(source_files))
    
    def _calculate_content_relevance(self, content, question):
        """计算内容与问题的相关性"""
        # 简单的关键词匹配相关性计算
        question_words = set(jieba.lcut(question.lower()))
        content_words = set(jieba.lcut(content.lower()))
        
        if not question_words:
            return 0
        
        # 计算交集比例
        intersection = len(question_words.intersection(content_words))
        relevance = intersection / len(question_words)
        
        return relevance

# 初始化知识库
kb = KnowledgeBase()

def extract_text_from_pdf(file_path):
    """从PDF文件提取文本"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"PDF提取错误: {e}")
    return text

def call_qianwen_api(messages):
    """调用阿里千问API"""
    try:
        from dashscope import Generation
        
        response = Generation.call(
            model='qwen-turbo',
            messages=messages,
            result_format='message'
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            return f"API调用失败: {response.message}"
    except Exception as e:
        return f"API调用错误: {str(e)}"

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口 - 支持智能文档检索 - 第二阶段RAG优化版本"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400
    
    # 先在知识库中搜索（会自动检测是否针对特定文档）
    search_results = kb.search(user_message)
    
    if search_results:
        # 使用增强的上下文质量优化
        enhanced_context, source_files = kb._enhance_context_quality(search_results, user_message)
        search_mode = search_results[0].get('search_info', {}).get('search_mode', 'global')
        
        # 根据搜索模式调整系统提示词 - 使用优化的提示词框架
        if search_mode == 'targeted':
            target_files = search_results[0].get('search_info', {}).get('target_files', [])
            system_prompt = kb._build_targeted_prompt(enhanced_context, target_files, user_message)
        else:
            system_prompt = kb._build_general_prompt(enhanced_context, user_message)
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        response = call_qianwen_api(messages)
        
        # 评估回答质量
        quality_assessment = quality_assessor.assess_response_quality(response)
        
        return jsonify({
            'response': response,
            'source': 'knowledge_base',
            'search_results': search_results,
            'search_mode': search_mode,
            'source_files': source_files,
            'optimization_stage': 'stage2_prompt_optimization',  # 标识使用了第二阶段优化
            'quality_assessment': quality_assessment,
            'prompt_version': 'v2.0'
        })
    else:
        # 如果知识库中没有找到，使用标准回复模板
        fallback_prompt = """你是一个智能助手。用户询问的问题在当前知识库中没有找到相关信息。

请回答：对不起，我在当前知识库中没有找到与您问题相关的信息。您可以：
1. 尝试重新描述您的问题
2. 上传相关文档到知识库
3. 使用不同的关键词进行询问

如果您希望我基于通用知识回答，请明确告知。"""
        
        messages = [
            {'role': 'system', 'content': fallback_prompt},
            {'role': 'user', 'content': user_message}
        ]
        
        response = call_qianwen_api(messages)
        
        # 为无匹配情况也进行质量评估
        quality_assessment = quality_assessor.assess_response_quality(response)
        
        return jsonify({
            'response': response,
            'source': 'no_knowledge_base_match',
            'search_results': [],
            'search_mode': 'none',
            'source_files': [],
            'optimization_stage': 'stage2_prompt_optimization',
            'quality_assessment': quality_assessment,
            'prompt_version': 'v2.0'
        })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 提取文本内容
        content = ""
        if filename.lower().endswith('.pdf'):
            content = extract_text_from_pdf(file_path)
        elif filename.lower().endswith(('.txt', '.md')):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        if content:
            # 添加到知识库
            kb.add_document(filename, content)
            return jsonify({'message': f'文件 {filename} 上传并处理成功'})
        else:
            return jsonify({'error': '无法提取文件内容'}), 400

@app.route('/api/search', methods=['POST'])
def search_knowledge_base():
    """知识库搜索接口"""
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 5)
    
    if not query:
        return jsonify({'error': '查询不能为空'}), 400
    
    results = kb.search(query, max_results=max_results)
    
    return jsonify({
        'results': results,
        'query': query,
        'total_documents': len(kb.documents)
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """获取知识库中的所有文档"""
    documents = [
        {
            'id': doc['id'],
            'filename': doc['filename'],
            'upload_time': doc.get('upload_time', ''),
            'content_length': len(doc['content'])
        }
        for doc in kb.documents
    ]
    
    return jsonify({
        'documents': documents,
        'total': len(documents)
    })

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """删除知识库中的文档"""
    if kb.delete_document(doc_id):
        return jsonify({'message': '文档删除成功'})
    else:
        return jsonify({'error': '文档不存在'}), 404

@app.route('/api/search_comparison', methods=['POST'])
def search_comparison():
    """搜索方法对比接口"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': '查询不能为空'}), 400
    
    # 使用不同方法搜索
    keyword_results = kb._keyword_search(query)
    semantic_results = []
    
    if EMBEDDING_AVAILABLE and kb.embedding_model:
        semantic_results = kb._semantic_search(query)
    
    return jsonify({
        'keyword_results': keyword_results,
        'semantic_results': semantic_results,
        'query': query
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'knowledge_base_documents': len(kb.documents),
        'embedding_available': EMBEDDING_AVAILABLE,
        'embedding_model_loaded': kb.embedding_model is not None,
        'optimization_stage': 'stage2_prompt_optimization'
    })

if __name__ == '__main__':
    print("🚀 启动 RAG 系统服务器 - 第二阶段优化版本")
    print(f"📚 知识库文档数量: {len(kb.documents)}")
    print(f"🔍 语义搜索功能: {'✓ 已启用' if EMBEDDING_AVAILABLE else '✗ 未启用'}")
    print(f"🤖 提示词优化: ✓ 第二阶段优化已启用")
    app.run(debug=True, host='0.0.0.0', port=5000)

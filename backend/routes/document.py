"""
文档管理相关路由
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.pdf_service import extract_text_from_pdf
import os

# 创建Blueprint
document_bp = Blueprint('document', __name__)

def init_document_routes(kb):
    """初始化文档路由，传入知识库实例"""
    
    def allowed_file(filename):
        """
        检查文件是否为允许的类型 - 健壮版本
        处理大小写、中文文件名和复杂文件名格式
        """
        if not filename or not isinstance(filename, str):
            return False
        
        # 支持的文件扩展名（小写）
        ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.doc'}
        
        # 将文件名转为小写进行比较
        filename_lower = filename.lower().strip()
        
        # 方法1: 使用 endswith 检查（处理多点文件名）
        for ext in ALLOWED_EXTENSIONS:
            if filename_lower.endswith(ext):
                return True
        
        # 方法2: 提取最后一个点之后的扩展名（备用方法）
        if '.' in filename_lower:
            # 获取最后一个点之后的内容作为扩展名
            last_ext = '.' + filename_lower.split('.')[-1]
            if last_ext in ALLOWED_EXTENSIONS:
                return True
        
        return False
    
    def get_safe_filename(original_filename):
        """
        获取安全的文件名，保留原始扩展名
        """
        if not original_filename:
            return None
        
        # 首先验证原始文件名的扩展名
        if not allowed_file(original_filename):
            return None
        
        # 提取扩展名（保持原始大小写用于显示）
        if '.' in original_filename:
            name_part = original_filename.rsplit('.', 1)[0]
            ext_part = '.' + original_filename.rsplit('.', 1)[1]
        else:
            name_part = original_filename
            ext_part = ''
        
        # 对文件名主体应用secure_filename
        safe_name_part = secure_filename(name_part)
        
        # 如果secure_filename清空了文件名，使用时间戳
        if not safe_name_part:
            import time
            safe_name_part = f'document_{int(time.time())}'
        
        # 组合安全的文件名和原始扩展名
        safe_filename = safe_name_part + ext_part.lower()
        
        return safe_filename
    
    @document_bp.route('/api/upload', methods=['POST'])
    def upload_file():
        """文件上传接口 - 修复版本"""
        try:
            # 1. 检查是否有文件
            if 'file' not in request.files:
                return jsonify({'error': '没有文件'}), 400
            
            file = request.files['file']
            if file.filename == '' or file.filename is None:
                return jsonify({'error': '没有选择文件'}), 400
            
            # 2. 原始文件名验证
            original_filename = file.filename
            print(f"原始文件名: {original_filename}")
            
            # 3. 文件类型验证（基于原始文件名）
            if not allowed_file(original_filename):
                return jsonify({
                    'error': f'不支持的文件类型。支持的格式：PDF, TXT, MD, DOCX, DOC',
                    'filename': original_filename,
                    'suggestion': '请确保文件扩展名正确（如 .pdf, .txt, .md, .docx）'
                }), 400
            
            # 4. 获取安全的文件名
            safe_filename = get_safe_filename(original_filename)
            if not safe_filename:
                return jsonify({
                    'error': '文件名处理失败',
                    'filename': original_filename,
                    'suggestion': '请检查文件名是否包含有效的扩展名'
                }), 400
            
            print(f"安全文件名: {safe_filename}")
            
            # 5. 保存文件
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
            file.save(file_path)
            print(f"文件已保存到: {file_path}")
            
            # 6. 提取文本内容
            content = ""
            error_msg = ""
            
            try:
                # 使用小写扩展名判断文件类型
                file_ext = safe_filename.lower().split('.')[-1]
                
                if file_ext == 'pdf':
                    print("处理PDF文件...")
                    content = extract_text_from_pdf(file_path)
                    if not content.strip():
                        error_msg = "PDF文件可能是扫描版或无法读取文本内容"
                elif file_ext in ['txt', 'md']:
                    print(f"处理{file_ext.upper()}文件...")
                    # 尝试多种编码
                    encodings = ['utf-8', 'gbk', 'gb2312', 'ascii', 'utf-16']
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                            print(f"成功使用{encoding}编码读取文件")
                            break
                        except UnicodeDecodeError:
                            continue
                    if not content:
                        error_msg = "无法读取文本文件，尝试了多种编码格式都失败"
                elif file_ext in ['docx', 'doc']:
                    print("处理Word文档...")
                    try:
                        import docx
                        doc = docx.Document(file_path)
                        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                    except ImportError:
                        error_msg = "Word文档处理需要安装python-docx库: pip install python-docx"
                    except Exception as e:
                        error_msg = f"Word文档读取失败: {str(e)}"
                else:
                    error_msg = f"不支持的文件扩展名: {file_ext}"
                    
            except Exception as e:
                error_msg = f"文件处理失败: {str(e)}"
                print(f"文件处理异常: {e}")
            
            # 7. 验证内容
            if content and content.strip():
                # 添加到知识库（使用原始文件名用于显示）
                doc_id = kb.add_document(original_filename, content)
                print(f"文档已添加到知识库，ID: {doc_id}")
                
                return jsonify({
                    'message': f'文件 {original_filename} 上传并处理成功',
                    'filename': original_filename,
                    'safe_filename': safe_filename,
                    'document_id': doc_id,
                    'content_length': len(content)
                })
            else:
                # 删除已保存的文件（如果内容提取失败）
                try:
                    os.remove(file_path)
                    print(f"已删除失败的文件: {file_path}")
                except:
                    pass
                
                return jsonify({
                    'error': error_msg or '文件内容为空或无法提取文本内容',
                    'filename': original_filename,
                    'suggestion': '请确保文件包含可读取的文本内容，或尝试另存为其他格式'
                }), 400
                
        except Exception as e:
            print(f"文件上传异常: {e}")
            return jsonify({
                'error': f'文件上传过程中发生错误: {str(e)}',
                'suggestion': '请检查文件是否完整且格式正确'
            }), 500
    
    @document_bp.route('/api/documents', methods=['GET'])
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
    
    @document_bp.route('/api/documents/<int:doc_id>', methods=['DELETE'])
    def delete_document(doc_id):
        """删除知识库中的文档"""
        if kb.delete_document(doc_id):
            return jsonify({'message': '文档删除成功'})
        else:
            return jsonify({'error': '文档不存在'}), 404
    
    return document_bp

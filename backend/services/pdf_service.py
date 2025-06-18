"""
PDF文件处理服务模块
"""
import PyPDF2
import os

def extract_text_from_pdf(file_path):
    """从PDF文件提取文本 - 增强版本"""
    text = ""
    
    if not os.path.exists(file_path):
        print(f"PDF文件不存在: {file_path}")
        return ""
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # 检查PDF是否已加密
            if pdf_reader.is_encrypted:
                print(f"PDF文件已加密，无法读取: {file_path}")
                return ""
            
            # 检查页数
            page_count = len(pdf_reader.pages)
            if page_count == 0:
                print(f"PDF文件没有页数: {file_path}")
                return ""
            
            print(f"正在处理PDF文件: {file_path} (共{page_count}页)")
            
            # 提取每页文本
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        print(f"第{i+1}页无法提取文本")
                except Exception as e:
                    print(f"提取第{i+1}页时出错: {e}")
                    continue
            
            # 清理文本
            text = text.strip()
            
            if not text:
                print(f"PDF文件可能是扫描版或纯图片文件: {file_path}")
                return ""
            
            print(f"成功提取PDF文本，长度: {len(text)} 字符")
            return text
            
    except Exception as e:
        print(f"PDF提取错误: {e}")
        return ""

def validate_pdf_file(file_path):
    """验证PDF文件是否有效"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages) > 0
    except Exception as e:
        print(f"PDF验证失败: {e}")
        return False

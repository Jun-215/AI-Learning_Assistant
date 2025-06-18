"""
千问API服务模块
"""
import dashscope
from dashscope import Generation

def call_qianwen_api(messages):
    """调用阿里千问API"""
    try:
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

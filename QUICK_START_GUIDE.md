# 项目快速使用指南

## 🚀 一键启动

### Windows 用户

1. **PowerShell 启动（推荐）**

   ```powershell
   .\run.ps1
   ```

2. **批处理启动**

   ```cmd
   run.bat
   ```

## 📋 使用前准备

1. **获取 API 密钥**
   - 访问 [阿里云DashScope](https://dashscope.aliyun.com/)
   - 注册账号并获取 API 密钥

2. **配置环境变量**
   - 在项目根目录创建 `.env` 文件
   - 添加内容：`DASHSCOPE_API_KEY=你的API密钥`

## 💡 主要功能

- 🤖 **智能问答**: 直接对话，获得AI回答
- 📄 **文档上传**: 上传PDF文档构建知识库
- 🔍 **智能检索**: 优先从知识库中找答案
- 📊 **多种搜索**: 关键词、语义、向量检索

## 🌐 访问地址

启动后访问：<http://localhost:3000>

## ❓ 遇到问题？

1. 检查 Python 3.8+ 和 Node.js 16+ 是否安装
2. 确保 API 密钥配置正确
3. 查看终端输出的错误信息
4. 参考完整的 README.md 文档

祝您使用愉快！ 🎉

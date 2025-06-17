# 🚀 AI Agent 对话系统 - 配置指南

## 📋 系统要求

- Python 3.13.2 (已安装)
- Node.js (建议 16.0+)
- 阿里千问API密钥

## ⚙️ 配置步骤

### 1. 获取阿里千问API密钥

1. 访问 [阿里云控制台](https://dashscope.console.aliyun.com/)
2. 登录您的阿里云账号
3. 开通通义千问服务
4. 获取API Key

### 2. 配置API密钥

编辑 `backend/.env` 文件：

```bash
# 将 your-dashscope-api-key-here 替换为您的实际API密钥
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=your-secret-key-here
```

### 3. 安装依赖（如果还未安装）

#### 后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖

```bash
cd frontend
npm install
```

## 🔧 手动启动

### 启动后端

```bash
cd backend
python app.py
```

后端将运行在: <http://localhost:5000>

### 启动前端

```bash
cd frontend
npm start
```

前端将运行在: <http://localhost:3000>

## 🚀 快速启动

双击 `start.bat` 文件一键启动前后端服务。

## 🔍 功能特性

1. **智能对话**: 基于阿里千问API的对话功能
2. **知识库管理**: 上传PDF文件构建个人知识库
3. **智能检索**: 优先从知识库检索，未找到时调用API
4. **现代UI**: 类似ChatGPT的对话界面

## 📝 使用说明

1. 首次使用建议先上传一些PDF文档到知识库
2. 对话时系统会自动判断是否需要从知识库检索
3. 可以在右侧面板管理已上传的文档

## 🐛 常见问题

### Q: 后端启动失败

A: 请检查：

- Python版本是否为3.13.2
- 是否正确安装了所有依赖
- 是否配置了正确的API密钥

### Q: 前端无法访问后端

A: 请检查：

- 后端是否正常启动（端口5000）
- 防火墙是否阻止了连接

### Q: API调用失败

A: 请检查：

- API密钥是否正确配置
- 阿里云账户是否有足够的额度
- 网络连接是否正常

## 📞 支持

如有问题，请检查：

1. 控制台错误信息
2. 后端日志输出
3. 网络连接状态

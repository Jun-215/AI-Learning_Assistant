# 🤖 AI Agent 对话系统

基于 React + Flask + 阿里千问API 的智能对话系统，支持PDF知识库构建和智能检索。

## ✨ 功能特性

- 🎯 **智能对话**: 基于阿里千问API的自然语言对话
- 📚 **知识库管理**: 上传PDF文件自动构建个人知识库
- 🔍 **智能检索**: 优先从知识库检索答案，提高回答准确性
- 💬 **现代界面**: 类似ChatGPT的直观对话界面
- 🚀 **一键启动**: 双击启动脚本即可运行

## 🛠 技术栈

- **前端**: React 18 + TypeScript + Axios
- **后端**: Python Flask + CORS支持
- **AI服务**: 阿里千问API (DashScope)
- **文档处理**: PyPDF2
- **UI组件**: Lucide React图标库

## 📦 项目结构

```
demo7/
├── backend/                 # Python Flask 后端
│   ├── app.py              # 主应用文件
│   ├── config.py           # 配置管理
│   ├── requirements.txt    # Python依赖
│   └── .env               # 环境变量配置
├── frontend/               # React 前端
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # Node.js依赖
├── start.bat              # 一键启动脚本
├── CONFIG.md              # 详细配置指南
└── test_system.py         # 系统测试脚本
```

## 🚀 快速开始

### 方法一：一键启动（推荐）

1. 双击 `start.bat` 文件
2. 按照提示配置API密钥
3. 访问 <http://localhost:3000>

### 方法二：手动启动

#### 1. 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### 2. 前端启动

```bash
cd frontend
npm install
npm start
```

## ⚙️ 配置说明

### 1. 获取阿里千问API密钥

- 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
- 开通通义千问服务
- 获取API Key

### 2. 配置密钥

编辑 `backend/.env` 文件：

```env
DASHSCOPE_API_KEY=sk-你的实际API密钥
SECRET_KEY=随机密钥字符串
```

## 📖 使用指南

1. **上传文档**: 在右侧面板拖拽或点击上传PDF文件
2. **开始对话**: 在输入框中输入问题，支持回车发送
3. **智能回答**: 系统会自动判断从知识库还是API获取答案
4. **管理文档**: 在文档列表中可以删除不需要的文档

## 🧪 测试系统

运行测试脚本验证系统功能：

```bash
python test_system.py
```

## 📝 接口说明

- `GET /api/health` - 健康检查
- `POST /api/chat` - 聊天对话
- `POST /api/upload` - 文件上传
- `GET /api/documents` - 获取文档列表
- `DELETE /api/documents/{id}` - 删除文档

## 🐛 常见问题

详细的配置和问题解决方案请查看 [CONFIG.md](CONFIG.md)

## 📄 许可证

MIT License

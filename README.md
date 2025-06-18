# AI-Learning Assistant 🤖

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18.2.0-61dafb.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-4.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个基于大语言模型和 RAG（检索增强生成）技术的智能学习助手系统，支持知识库构建、文档上传和智能问答。

## ✨ 特性

- 🧠 **智能问答**: 基于阿里千问大模型的智能对话系统
- 📚 **知识库管理**: 支持PDF文档上传和知识库构建
- 🔍 **RAG检索**: 多阶段优化的检索增强生成，包括关键词搜索、语义搜索和质量评估
- 🎨 **现代UI**: 基于React + TypeScript的现代化前端界面
- 🔧 **灵活配置**: 支持本地模型和云端API两种模式
- 📊 **多种搜索**: TF-IDF、语义嵌入、FAISS向量检索等多种搜索算法
- 🛠️ **测试覆盖**: 完整的测试脚本和验证工具

## 🏗️ 系统架构

```text
AI-Learning Assistant
├── 前端 (React + TypeScript)
│   ├── 智能对话界面
│   ├── 文档管理系统
│   └── 实时状态反馈
├── 后端 (Flask + Python)
│   ├── RAG 检索引擎
│   ├── 知识库管理
│   ├── 文档处理
│   └── API 接口服务
└── 智能模块
    ├── 多阶段检索优化
    ├── 语义搜索引擎
    └── 质量评估系统
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装步骤

1. **克隆项目**

   ```bash
   git clone https://github.com/yourusername/AI-Learning_Assistant.git
   cd AI-Learning_Assistant
   ```

2. **配置环境变量**

   在项目根目录创建 `.env` 文件：

   ```env
   DASHSCOPE_API_KEY=your_qianwen_api_key_here
   ```

3. **安装后端依赖**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **安装前端依赖**

   ```bash
   cd frontend
   npm install
   ```

### 🎯 运行项目

#### 方式一：一键启动（推荐）

**Windows PowerShell:**

```powershell
.\run.ps1
```

**Windows 批处理:**

```batch
run.bat
```

#### 方式二：分别启动

**启动后端:**

```bash
cd backend
python app.py
```

**启动前端:**

```bash
cd frontend
npm start
```

访问 `http://localhost:3000` 即可使用系统！

## 📖 使用指南

### 基本功能

1. **智能对话**: 直接在聊天框中输入问题，系统会智能回答
2. **上传文档**: 点击上传按钮，上传PDF文档到知识库
3. **知识库查询**: 系统会优先从知识库中检索相关信息
4. **文档管理**: 查看和删除已上传的文档

### 高级特性

- **多阶段检索**: 系统采用关键词提取 → TF-IDF搜索 → 语义搜索的多阶段检索策略
- **智能融合**: 结合知识库内容和大模型能力，生成更准确的答案
- **实时反馈**: 显示答案来源（知识库 or 大模型）

## 🛠️ 技术栈

### 后端技术

- **Flask**: Web框架
- **PyPDF2**: PDF文档解析
- **jieba**: 中文分词
- **scikit-learn**: TF-IDF向量化
- **sentence-transformers**: 语义嵌入
- **FAISS**: 向量检索
- **DashScope**: 阿里千问API

### 前端技术

- **React 18**: 用户界面框架
- **TypeScript**: 类型安全
- **Axios**: HTTP客户端
- **Lucide React**: 图标库
- **CSS3**: 现代样式

## 📁 项目结构

```text
AI-Learning_Assistant/
├── backend/                 # 后端服务
│   ├── app.py              # 主应用文件
│   ├── config.py           # 配置文件
│   ├── stage2_config.py    # 第二阶段优化配置
│   ├── requirements.txt    # Python依赖
│   └── knowledge_base/     # 知识库存储
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── App.tsx        # 主应用组件
│   │   ├── index.tsx      # 入口文件
│   │   └── index.css      # 样式文件
│   ├── public/            # 静态资源
│   └── package.json       # Node.js依赖
├── test_scripts/          # 测试脚本集合
├── report_md/            # 项目文档和报告
├── run.ps1               # PowerShell启动脚本
├── run.bat               # 批处理启动脚本
└── README.md             # 项目说明
```

## 🧪 测试

项目包含完整的测试套件：

```bash
# 运行系统测试
python test_scripts/test_system.py

# 运行RAG功能测试
python test_scripts/test_rag_optimization.py

# 运行搜索功能测试
python test_scripts/test_search.py

# 快速验证
python test_scripts/quick_verify.py
```

## ⚙️ 配置说明

### API配置

在 `backend/config.py` 中配置：

- DashScope API密钥
- 模型参数
- 文件上传路径

### 搜索优化

在 `backend/stage2_config.py` 中调整：

- 检索策略
- 相似度阈值
- 质量评估参数

## 🔧 部署

### 开发环境

使用提供的启动脚本即可快速部署开发环境。

### 生产环境

1. 配置反向代理（Nginx推荐）
2. 使用WSGI服务器（如Gunicorn）
3. 配置HTTPS证书
4. 优化前端构建

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 常见问题

### Q: 如何获取阿里千问API密钥？

A: 访问 [阿里云DashScope](https://dashscope.aliyun.com/) 注册并获取API密钥。

### Q: 支持哪些文档格式？

A: 目前支持PDF格式，未来将支持更多格式。

### Q: 可以使用本地模型吗？

A: 是的，项目支持本地模型配置，详见配置文件。

### Q: 遇到依赖安装问题怎么办？

A: 建议使用虚拟环境，并确保Python和Node.js版本符合要求。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/yourusername/AI-Learning_Assistant/issues)

---

⭐ 如果这个项目对您有帮助，请给个星标支持！

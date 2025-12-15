# 企业知识图谱智能助手系统

基于 RAG（检索增强生成）技术的企业知识助手系统，支持用户认证、知识库管理和智能问答。

## 核心功能

- 🔐 **用户认证**：注册、登录，JWT Token 认证（Access Token + Refresh Token）
- 📚 **知识库管理**：支持多种格式文件上传（txt, pdf, md, doc, docx, csv），文件管理
- 💬 **智能问答**：RAG 模式和非 RAG 模式的流式聊天，显示参考来源
- 🎨 **现代化 UI**：基于 Vuetify 3 的 Material Design 界面，响应式布局

## 技术栈

**后端**
- Flask 3.0+ / SQLAlchemy / SQLite
- Flask-JWT-Extended（JWT 认证）
- ChromaDB（向量数据库）
- Flask-CORS

**前端**
- Vue 3 + TypeScript
- Vuetify 3
- Vue Router 4
- Vite 7+

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- pnpm（推荐）或 npm/yarn

### 后端启动

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
cd backend
python run.py
```

后端服务运行在 `http://localhost:5000`

### 前端启动

```bash
cd frontend
pnpm install
pnpm dev
```

前端应用运行在 `http://localhost:5173`

### 环境变量（可选）

在项目根目录创建 `.env` 文件：

```env
# JWT 密钥（生产环境必须设置）
JWT_SECRET_KEY=your-secret-key-here

# CORS 配置（多个域名用逗号分隔）
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Token 过期时间（可选）
JWT_ACCESS_TOKEN_EXPIRES_HOURS=24
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30
```

> 开发环境可使用默认配置，生产环境必须设置 `JWT_SECRET_KEY`

## 项目结构

```
demo1/
├── backend/              # 后端服务目录
│   ├── app/             # 应用核心代码
│   │   ├── api/         # API路由模块
│   │   │   ├── auth     # 用户认证相关接口
│   │   │   ├── core     # 核心功能接口
│   │   │   ├── kb       # 知识库管理接口
│   │   │   └── chat     # 聊天相关接口
│   │   ├── models/      # 数据模型定义
│   │   ├── config.py    # 系统配置文件
│   │   └── utils/       # 工具函数集合
│   ├── instance/        # 数据存储目录
│   │   ├── demo.db      # SQLite数据库文件
│   │   └── chroma_db/   # Chroma向量数据库
│   ├── uploads/         # 用户上传文件存储目录
│   └── run.py           # 后端服务启动入口
│
├── frontend/            # 前端应用目录
│   ├── src/             # 前端源代码
│   │   ├── components/  # 可复用UI组件
│   │   ├── composables/ # Vue组合式函数
│   │   ├── pages/       # 页面组件
│   │   ├── utils/       # 前端工具函数
│   │   └── main.ts      # 前端应用入口
│   ├── public/          # 静态资源目录
│   ├── package.json     # 前端依赖配置
│   └── vite.config.ts   # Vite构建配置
│
└── requirements.txt     # Python后端依赖列表

```

## 主要 API

### 认证
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/refresh` - 刷新 Token
- `POST /api/logout` - 用户登出

### 知识库
- `GET /api/kb-info` - 获取知识库信息
- `POST /api/upload` - 上传文件
- `POST /api/delete` - 删除文件

### 聊天
- `POST /api/chat` - 发送消息（SSE 流式响应）

## 配置说明

### 文件上传
- 最大文件大小：10MB
- 支持格式：txt, pdf, md, doc, docx, csv
- 存储位置：`backend/uploads/`

### 数据库
- SQLite 数据库：`backend/instance/demo.db`
- ChromaDB 向量库：`backend/instance/chroma_db/`

## 构建部署

### 前端构建
```bash
cd frontend
pnpm build
```

### 生产环境部署

**后端**：使用 Gunicorn
```bash
pip install gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**前端**：将 `frontend/dist/` 部署到静态服务器

> 生产环境必须设置 `JWT_SECRET_KEY` 环境变量，建议使用 HTTPS

## 常见问题

- **端口被占用**：修改 `backend/run.py` 中的端口号
- **CORS 错误**：检查 `CORS_ORIGINS` 配置是否包含前端地址
- **Token 过期**：系统会自动刷新，失败需重新登录
- **文件上传失败**：检查文件大小（≤10MB）和格式是否支持

## 许可证

MIT License

# 前后端分离改造完成指南

恭喜！你的校友管理系统已经成功改造为前后端分离架构。

## 📁 项目结构

### 后端项目（当前目录）
```
flask-alumni-with-AI/
├── app_api.py              # 新的 API 版本（前后端分离）
├── app.py                  # 原版本（服务端渲染，保留）
├── Dockerfile.api          # API 版本的 Dockerfile
├── docker-compose.api.yml  # API 版本的 docker-compose
├── requirements.txt        # 已添加 flask-cors
└── frontend-template/      # 前端项目模板
```

### 前端项目（frontend-template/）
```
frontend-template/
├── src/
│   ├── api/               # API 接口封装
│   ├── router/            # 路由配置
│   ├── stores/            # 状态管理
│   ├── utils/             # 工具函数
│   ├── views/             # 页面组件
│   │   ├── Login.vue      # 登录页
│   │   ├── Home.vue       # 首页（列表）
│   │   ├── Add.vue        # 新增页
│   │   └── Edit.vue       # 编辑页
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── Dockerfile             # 前端 Dockerfile
├── docker-compose.yml     # 前端 docker-compose（包含后端）
├── nginx.conf             # Nginx 配置
└── package.json           # 依赖配置
```

## 🚀 快速开始

### 方式一：本地开发（推荐初学者）

#### 1. 启动后端

```bash
# 在后端目录
cd D:\wll\flask-alumni-with-AI

# 安装依赖
pip install -r requirements.txt

# 启动 API 服务
python app_api.py
```

后端将运行在 `http://localhost:8001`

#### 2. 启动前端

```bash
# 复制前端模板到新目录（或直接在 frontend-template 目录工作）
cd D:\wll\flask-alumni-with-AI\frontend-template

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 `http://localhost:5173`

#### 3. 访问应用

打开浏览器访问 `http://localhost:5173`

**登录信息**：任何非空用户名和密码都可以登录（演示模式）

---

### 方式二：Docker 部署（推荐生产环境）

#### 1. 仅部署后端 API

```bash
# 在后端目录
cd D:\wll\flask-alumni-with-AI

# 使用 docker-compose 启动
docker-compose -f docker-compose.api.yml up -d
```

访问 `http://localhost:8001/api/auth/current` 测试 API

#### 2. 部署完整应用（前端 + 后端 + 数据库）

```bash
# 在前端目录
cd D:\wll\flask-alumni-with-AI\frontend-template

# 复制环境变量配置
cp .env.example .env

# 编辑 .env 文件，配置数据库和 LLM 信息
# vim .env

# 启动所有服务
docker-compose up -d
```

访问 `http://localhost` 查看完整应用

---

## 📝 主要改动说明

### 后端改动（app_api.py）

1. **所有路由改为返回 JSON**
   - 不再使用 `render_template()`
   - 统一使用 `jsonify()` 返回数据
   - 路由前缀统一为 `/api`

2. **添加 CORS 支持**
   - 使用 `flask-cors` 允许跨域请求
   - 配置 `supports_credentials=True` 支持 Session

3. **统一响应格式**
   ```json
   {
     "code": 200,
     "message": "操作成功",
     "data": { ... }
   }
   ```

4. **API 端点**
   - `POST /api/auth/login` - 登录
   - `POST /api/auth/logout` - 登出
   - `GET /api/auth/current` - 获取当前用户
   - `GET /api/users` - 获取校友列表
   - `POST /api/users` - 新增校友
   - `PUT /api/users/:id` - 更新校友
   - `DELETE /api/users/:id` - 删除校友
   - `POST /api/ai/summary` - AI 摘要
   - `POST /api/ai/draft_email` - AI 邮件

### 前端改动

1. **使用 Vue 3 + Element Plus**
   - 组件化开发
   - 响应式数据绑定
   - 路由管理（Vue Router）
   - 状态管理（Pinia）

2. **Axios 封装**
   - 统一的请求拦截器
   - 统一的响应处理
   - 自动处理错误

3. **页面组件**
   - Login.vue - 登录页面
   - Home.vue - 校友列表（含搜索、AI 功能）
   - Add.vue - 新增校友
   - Edit.vue - 编辑校友

---

## 🔧 配置说明

### 后端配置

在 `.env` 文件中配置：

```env
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=alumni_user
DB_PASSWORD=alumni_password
DB_NAME=alumni_mgmt

# LLM
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_API_KEY=your-api-key
LLM_MODEL=deepseek-v3-1-250821

# Flask
FLASK_SECRET_KEY=your-secret-key
```

### 前端配置

在 `vite.config.js` 中配置代理：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true
    }
  }
}
```

生产环境在 `nginx.conf` 中配置反向代理。

---

## 📊 架构对比

### 改造前（服务端渲染）
```
浏览器 → Flask → 渲染 HTML → 返回完整页面
```

### 改造后（前后端分离）
```
浏览器（Vue） ←→ API（Flask） ←→ 数据库（MySQL）
```

---

## 🎯 学习建议

### 1. 理解前后端分离
- 前端负责：页面展示、用户交互、数据渲染
- 后端负责：数据处理、业务逻辑、API 提供
- 通信方式：HTTP/HTTPS + JSON

### 2. 学习 Vue 3 基础
- 组件（Component）
- 响应式（Reactive）
- 路由（Router）
- 状态管理（Pinia）

### 3. 学习 RESTful API
- GET - 获取数据
- POST - 创建数据
- PUT - 更新数据
- DELETE - 删除数据

### 4. 练习任务
1. 修改页面样式
2. 添加新的字段（如"公司"、"职位"）
3. 实现数据导出功能
4. 优化 AI 提示词

---

## ❓ 常见问题

### 1. 跨域问题
开发环境使用 Vite 代理解决，生产环境配置 Nginx 反向代理。

### 2. Session 问题
确保后端 CORS 配置 `supports_credentials: true`，前端 Axios 配置 `withCredentials: true`。

### 3. 部署问题
- 前端：构建后部署到 Nginx
- 后端：使用 Gunicorn + Docker
- 数据库：使用 MySQL 容器

---

## 📚 参考资源

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Element Plus 文档](https://element-plus.org/zh-CN/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [RESTful API 设计指南](https://restfulapi.net/)

---

## 🎉 总结

你已经成功完成前后端分离改造！

**下一步建议：**
1. 在本地运行项目，熟悉前后端交互
2. 尝试修改代码，理解工作原理
3. 学习 Vue 3 和 Flask 的高级特性
4. 部署到服务器，体验完整流程

祝你学习愉快！🚀
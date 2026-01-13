# API 测试指南

## 问题解决

之前访问 `http://localhost:8001/` 返回 404 错误，现在已经修复！

## 可用的 API 端点

### 1. 根路径
```
GET http://localhost:8001/
```

**响应示例：**
```json
{
  "code": 200,
  "message": "欢迎使用校友管理系统 API",
  "data": {
    "name": "校友管理系统 API",
    "version": "1.0.0",
    "status": "running",
    "endpoints": {
      "auth": "/api/auth/*",
      "users": "/api/users",
      "ai": "/api/ai/*"
    }
  }
}
```

### 2. 健康检查
```
GET http://localhost:8001/api/health
```

**响应示例：**
```json
{
  "code": 200,
  "message": "服务正常",
  "data": {
    "status": "healthy",
    "service": "alumni-api"
  }
}
```

### 3. 用户认证

#### 登录
```
POST http://localhost:8001/api/auth/login
Content-Type: application/json

{
  "username": "test",
  "password": "123456"
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "username": "test"
  }
}
```

#### 登出
```
POST http://localhost:8001/api/auth/logout
```

#### 获取当前用户
```
GET http://localhost:8001/api/auth/current
```

### 4. 校友管理

#### 获取校友列表
```
GET http://localhost:8001/api/users
```

**带搜索参数：**
```
GET http://localhost:8001/api/users?keyword=张三
```

#### 获取单个校友详情
```
GET http://localhost:8001/api/users/1
```

#### 新增校友
```
POST http://localhost:8001/api/users
Content-Type: application/json

{
  "name": "李四",
  "gender": "女",
  "age": 25,
  "phone": "13800000002",
  "email": "lisi@example.com",
  "grad_year": 2020,
  "degree": "本科",
  "major": "计算机科学",
  "city": "北京",
  "country": "中国",
  "bio": "软件工程师"
}
```

#### 更新校友
```
PUT http://localhost:8001/api/users/1
Content-Type: application/json

{
  "name": "李四",
  "gender": "女",
  "age": 26,
  "phone": "13800000002",
  "email": "lisi@example.com",
  "grad_year": 2020,
  "degree": "硕士",
  "major": "计算机科学",
  "city": "上海",
  "country": "中国",
  "bio": "高级软件工程师"
}
```

#### 删除校友
```
DELETE http://localhost:8001/api/users/1
```

### 5. AI 功能

#### 生成校友摘要
```
POST http://localhost:8001/api/ai/summary
Content-Type: application/json

{
  "name": "张三",
  "major": "计算机科学",
  "work": "软件工程师",
  "bio": "后端开发，擅长 Python 和 Flask"
}
```

**响应示例：**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "summary": "张三，计算机专业校友，现任软件工程师，专注于后端开发，精通 Python 和 Flask 框架。"
  }
}
```

#### 生成邮件草稿
```
POST http://localhost:8001/api/ai/draft_email
Content-Type: application/json

{
  "topic": "校友返校日邀请",
  "audience": "2020届计算机科学校友张三",
  "style": "正式友好",
  "points": [
    "时间：2024年9月20日",
    "地点：学校主楼礼堂",
    "活动：校友分享会 + 校园参观"
  ]
}
```

#### AI 智能搜索
```
GET http://localhost:8001/api/ai/search?q=张三
```

---

## 如何测试

### 方法一：使用浏览器

直接在浏览器中访问以下地址：

- 根路径：http://localhost:8001/
- 健康检查：http://localhost:8001/api/health
- 获取列表：http://localhost:8001/api/users

**注意：** POST、PUT、DELETE 请求需要使用工具（如 Postman、curl）

### 方法二：使用 curl

```bash
# 测试根路径
curl http://localhost:8001/

# 测试健康检查
curl http://localhost:8001/api/health

# 测试登录
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 获取校友列表
curl http://localhost:8001/api/users
```

### 方法三：使用 Postman

1. 下载并安装 Postman
2. 创建新请求
3. 选择请求方法（GET、POST、PUT、DELETE）
4. 输入 URL
5. 如果是 POST/PUT，在 Body 中选择 JSON 并输入数据
6. 点击 Send

---

## 常见问题

### 1. 返回 404 错误
**原因：** 访问的路径不存在

**解决：**
- 检查 URL 是否正确
- 确认使用的是 `/api` 开头的路径（除了根路径）

### 2. 返回 401 错误
**原因：** 未登录或 Session 过期

**解决：**
- 先调用 `/api/auth/login` 登录
- 确保浏览器允许 Cookie

### 3. 返回 500 错误
**原因：** 服务器内部错误

**解决：**
- 检查数据库是否正常
- 查看后端控制台的错误日志
- 确保 `.env` 配置正确

### 4. CORS 错误
**原因：** 跨域请求被阻止

**解决：**
- 确保后端已配置 CORS
- 前端使用代理（开发环境）或 Nginx 反向代理（生产环境）

---

## 启动后端

```bash
# 在项目根目录
cd D:\wll\flask-alumni-with-AI

# 安装依赖（如果还没安装）
pip install -r requirements.txt

# 启动 API 服务
python app_api.py
```

服务将在 `http://localhost:8001` 启动

---

## 下一步

1. ✅ 测试根路径：http://localhost:8001/
2. ✅ 测试健康检查：http://localhost:8001/api/health
3. ✅ 测试登录接口
4. ✅ 启动前端项目
5. ✅ 测试前后端联调

现在你可以正常访问 API 了！🎉
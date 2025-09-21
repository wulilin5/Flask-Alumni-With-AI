校友管理系统 (Alumni Management System)
一个基于 Flask + MySQL 开发的校友信息管理平台，结合 AI 功能提升管理效率。
✨ 核心功能
完整的 CRUD 操作：对校友信息（姓名、专业、毕业年份等 12 个字段）进行规范化管理。
AI 智能增强：
AI 摘要：一键生成校友的个人简介，效率提升 80%。
AI 邮件草稿：根据主题和受众自动生成邮件正文，告别重复劳动。
用户认证：基于 Flask 蓝图（Blueprint）实现登录、注册和权限控制。
响应式设计：使用 Bootstrap 框架，在电脑和手机上都有良好的显示效果。
🛠️ 技术栈
后端: Python 3.x, Flask
数据库: MySQL
前端: Bootstrap, JavaScript (Fetch API)
AI 集成: 兼容 OpenAI 接口规范的大模型客户端
🚀 快速开始
1. 环境准备
Python: 建议 3.8 或更高版本
MySQL: 本地或远程的 MySQL 服务
大模型 API: 一个兼容 OpenAI 接口的 API Key (如火山方舟、豆包、通义千问等)
2. 克隆项目
bash
git clone [你的项目仓库地址]
cd [项目文件夹]
3. 安装依赖
bash
pip install -r requirements.txt
requirements.txt 文件内容建议如下：
txt
Flask==2.3.3
PyMySQL==1.1.0
python-dotenv==1.0.0
Werkzeug==2.3.7
requests==2.31.0
4. 配置环境变量
在项目根目录创建 .env 文件，并填入以下信息：
env
# Flask 配置
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-db-password
DB_NAME=alumni_mgmt
DB_PORT=3306

# LLM 配置
LLM_BASE_URL=https://your-llm-api-base-url.com/v1
LLM_API_KEY=your-llm-api-key-here
LLM_MODEL=your-model-name
5. 初始化数据库
创建数据库:
sql
CREATE DATABASE IF NOT EXISTS alumni_mgmt DEFAULT CHARSET utf8mb4;
执行 SQL 脚本: 运行 alumni_schema.sql 文件中的脚本，创建 tb_user (校友表) 和 auth_user (用户表)。
bash
# 可以使用命令行工具执行
mysql -u root -p alumni_mgmt < alumni_schema.sql
6. 启动应用
bash
flask run --host=0.0.0.0 --port=8001
或
bash
python app.py
启动后，访问 http://127.0.0.1:8001/ 即可进入系统。
📂 项目结构
plaintext
/
├── app.py             # 应用主入口，定义核心路由
├── auth.py            # 用户认证蓝图 (登录/注册/退出)
├── alumni_schema.sql  # 数据库表结构定义
├── requirements.txt   # 项目依赖
├── .env               # 环境变量配置 (不纳入版本控制)
├── services/
│   └── llm_client.py  # 大模型客户端，封装API调用
└── templates/         # 前端模板文件夹
    ├── index.html     # 校友列表首页
    ├── add.html       # 新增校友信息
    ├── edit.html      # 编辑校友信息
    ├── login.html     # 用户登录页
    └── register.html  # 用户注册页
🎯 主要路由
路由	方法	功能描述
/	GET	校友列表首页
/search	GET	搜索校友
/add	GET/POST	新增校友信息
/edit/<id>	GET	展示编辑表单
/update/<id>	POST	更新校友信息
/delete/<id>	GET	删除校友信息
/ai/summary	POST	生成 AI 摘要
/ai/draft_email	POST	生成邮件草稿
/auth/login	GET/POST	用户登录
/auth/logout	GET	用户退出
/auth/register	GET/POST	用户注册
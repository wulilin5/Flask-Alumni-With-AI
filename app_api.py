# -*- coding: utf-8 -*-
# Flask API：校友/毕业生管理系统（前后端分离版本）
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pymysql.cursors
from services.ai_query import ai_expand_query
from dotenv import load_dotenv
import os
import init_db
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()  # 让 .env 生效

from services.llm_client import LLMClient
llm = LLMClient()

# =========================
# 数据库连接
# =========================
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        db=os.getenv('DB_NAME', 'alumni_mgmt'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# =========================
# Flask 基本配置
# =========================
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "a-very-secret-key")

# =========================
# 自动初始化数据库
# =========================
try:
    init_db.init_database()
except Exception as e:
    print(f"警告: 数据库初始化失败 - {e}")

# 启用 CORS，允许前端跨域访问
CORS(app, supports_credentials=True)

# =========================
# 根路径和健康检查
# =========================
@app.route('/')
def index():
    """API 根路径，返回 API 信息"""
    return success_response({
        "name": "校友管理系统 API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth/*",
            "users": "/api/users",
            "ai": "/api/ai/*"
        }
    }, "欢迎使用校友管理系统 API")

@app.route('/api/health')
def health():
    """健康检查接口"""
    return success_response({
        "status": "healthy",
        "service": "alumni-api"
    }, "服务正常")

# =========================
# 统一响应格式
# =========================
def success_response(data=None, message="操作成功"):
    return jsonify({
        "code": 200,
        "message": message,
        "data": data
    })

def error_response(message="操作失败", code=500):
    return jsonify({
        "code": code,
        "message": message,
        "data": None
    }), code

# =========================
# 登录拦截中间件（可选）
# =========================
@app.before_request
def _require_login():
    # 允许的路径（不需要登录）
    allowed_paths = ['/', '/api/health', '/api/auth/login', '/api/auth/register', '/static']
    if request.path in allowed_paths or request.path.startswith('/static'):
        return

    # 检查登录状态
    if not session.get('user'):
        return error_response("未登录，请先登录", 401)

# =========================
# 权限检查装饰器
# =========================
from functools import wraps

def require_admin(f):
    """管理员权限检查装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'admin':
            return error_response("需要管理员权限", 403)
        return f(*args, **kwargs)
    return decorated_function

# =========================
# 认证相关 API
# =========================
@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return error_response("用户名和密码不能为空", 400)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 查询用户
            cursor.execute("SELECT id, username, password_hash, role, is_active FROM auth_user WHERE username=%s", (username,))
            user = cursor.fetchone()

            if not user:
                return error_response("用户名或密码错误", 401)

            if not user['is_active']:
                return error_response("账户已被禁用", 403)

            # 验证密码
            if not check_password_hash(user['password_hash'], password):
                return error_response("用户名或密码错误", 401)

            # 更新最后登录时间
            cursor.execute("UPDATE auth_user SET last_login=NOW() WHERE id=%s", (user['id'],))

            # 保存用户信息到 Session
            session['user'] = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }

            conn.commit()
            conn.close()

            return success_response({
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }, "登录成功")

    except Exception as e:
        print("Login error:", e)
        return error_response(f"登录失败: {str(e)}", 500)

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return error_response("用户名和密码不能为空", 400)

    if len(username) < 3:
        return error_response("用户名至少 3 个字符", 400)

    if len(password) < 6:
        return error_response("密码至少 6 个字符", 400)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM auth_user WHERE username=%s", (username,))
            if cursor.fetchone():
                return error_response("用户名已存在", 400)

            # 加密密码
            password_hash = generate_password_hash(password)

            # 插入新用户
            cursor.execute(
                "INSERT INTO auth_user (username, password_hash, role, is_active) VALUES (%s, %s, 'user', TRUE)",
                (username, password_hash)
            )

            new_user_id = cursor.lastrowid

            # 保存用户信息到 Session
            session['user'] = {
                'id': new_user_id,
                'username': username,
                'role': 'user'
            }

            conn.commit()
            conn.close()

            return success_response({
                'id': new_user_id,
                'username': username,
                'role': 'user'
            }, "注册成功，已自动登录")

    except Exception as e:
        print("Register error:", e)
        return error_response(f"注册失败: {str(e)}", 500)

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.pop('user', None)
    return success_response(None, "登出成功")

@app.route('/api/auth/current', methods=['GET'])
def get_current_user():
    """获取当前登录用户"""
    user = session.get('user')
    if user:
        return success_response(user)
    return error_response("未登录", 401)

# =========================
# 用户管理 API（仅管理员）
# =========================

@app.route('/api/admin/users', methods=['GET'])
@require_admin
def get_users():
    """获取所有用户列表（仅管理员）"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, role, is_active, created_at, last_login
                FROM auth_user
                ORDER BY id
            """)
            users = cursor.fetchall()
        conn.close()
        return success_response(users, "获取用户列表成功")
    except Exception as e:
        print("Get users error:", e)
        return error_response(f"获取用户列表失败: {str(e)}", 500)

@app.route('/api/admin/users/<int:user_id>/toggle', methods=['POST'])
@require_admin
def toggle_user_status(user_id):
    """启用/禁用用户（仅管理员）"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 查询当前状态
            cursor.execute("SELECT is_active FROM auth_user WHERE id=%s", (user_id,))
            result = cursor.fetchone()

            if not result:
                return error_response("用户不存在", 404)

            # 切换状态
            new_status = not result['is_active']
            cursor.execute("UPDATE auth_user SET is_active=%s WHERE id=%s", (new_status, user_id))

            conn.commit()
            conn.close()

            status_text = "启用" if new_status else "禁用"
            return success_response({'user_id': user_id, 'is_active': new_status}, f"用户已{status_text}")
    except Exception as e:
        print("Toggle user error:", e)
        return error_response(f"操作失败: {str(e)}", 500)

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """删除用户（仅管理员）"""
    user = session.get('user')
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 不允许删除自己
            if user_id == user['id']:
                return error_response("不能删除自己", 400)

            # 检查用户是否存在
            cursor.execute("SELECT id FROM auth_user WHERE id=%s", (user_id,))
            if not cursor.fetchone():
                return error_response("用户不存在", 404)

            # 删除用户
            cursor.execute("DELETE FROM auth_user WHERE id=%s", (user_id,))
            conn.commit()
            conn.close()

            return success_response(None, "用户删除成功")
    except Exception as e:
        print("Delete user error:", e)
        return error_response(f"删除失败: {str(e)}", 500)

# =========================
# 校友管理 API
# =========================
@app.route('/api/users', methods=['GET'])
def get_users():
    """获取校友列表（支持搜索）"""
    keyword = request.args.get('keyword', '').strip()

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if keyword:
                sql = """
                SELECT id, name, gender, age, phone, email, grad_year, degree, major, city, country, bio
                FROM tb_user
                WHERE name    LIKE CONCAT('%%', %s, '%%')
                   OR phone   LIKE CONCAT('%%', %s, '%%')
                   OR email   LIKE CONCAT('%%', %s, '%%')
                   OR major   LIKE CONCAT('%%', %s, '%%')
                   OR city    LIKE CONCAT('%%', %s, '%%')
                   OR country LIKE CONCAT('%%', %s, '%%')
                   OR bio     LIKE CONCAT('%%', %s, '%%')
                ORDER BY id
                """
                params = (keyword,) * 7
                cursor.execute(sql, params)
            else:
                sql = """
                SELECT id, name, gender, age, phone, email, grad_year, degree, major, city, country, bio
                FROM tb_user
                ORDER BY id
                """
                cursor.execute(sql)

            users = cursor.fetchall()
        conn.close()
        return success_response(users, "获取列表成功")
    except Exception as e:
        print("Get users error:", e)
        return error_response(f"获取列表失败: {str(e)}", 500)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个校友详情"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_user WHERE id=%s", (user_id,))
            user = cursor.fetchone()
        conn.close()

        if not user:
            return error_response("校友不存在", 404)
        return success_response(user)
    except Exception as e:
        print("Get user error:", e)
        return error_response(f"获取详情失败: {str(e)}", 500)

@app.route('/api/users', methods=['POST'])
def create_user():
    """新增校友"""
    data = request.get_json()

    name = data.get('name', '').strip()
    gender = data.get('gender', '').strip()
    age = data.get('age')
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    grad_year = data.get('grad_year')
    degree = data.get('degree', '').strip()
    major = data.get('major', '').strip()
    city = data.get('city', '').strip()
    country = data.get('country', '').strip()
    bio = data.get('bio', '').strip()

    if not name:
        return error_response("姓名不能为空", 400)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO tb_user
            (name, gender, age, phone, email, grad_year, degree, major, city, country, bio)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql, (name, gender, age, phone, email, grad_year, degree, major, city, country, bio))
            conn.commit()
            new_id = cursor.lastrowid
        conn.close()
        return success_response({'id': new_id}, "新增成功")
    except Exception as e:
        print("Create user error:", e)
        return error_response(f"新增失败: {str(e)}", 500)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新校友信息"""
    data = request.get_json()

    name = data.get('name', '').strip()
    gender = data.get('gender', '').strip()
    age = data.get('age')
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    grad_year = data.get('grad_year')
    degree = data.get('degree', '').strip()
    major = data.get('major', '').strip()
    city = data.get('city', '').strip()
    country = data.get('country', '').strip()
    bio = data.get('bio', '').strip()

    if not name:
        return error_response("姓名不能为空", 400)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            UPDATE tb_user SET
                name=%s, gender=%s, age=%s, phone=%s,
                email=%s, grad_year=%s, degree=%s, major=%s,
                city=%s, country=%s, bio=%s
            WHERE id=%s
            """
            cursor.execute(sql, (name, gender, age, phone, email, grad_year, degree, major, city, country, bio, user_id))
            conn.commit()
        conn.close()
        return success_response(None, "更新成功")
    except Exception as e:
        print("Update user error:", e)
        return error_response(f"更新失败: {str(e)}", 500)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除校友"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tb_user WHERE id=%s", (user_id,))
            conn.commit()
        conn.close()
        return success_response(None, "删除成功")
    except Exception as e:
        print("Delete user error:", e)
        return error_response(f"删除失败: {str(e)}", 500)

# =========================
# AI 功能 API
# =========================
@app.route('/api/ai/summary', methods=['POST'])
def ai_summary():
    """生成校友摘要"""
    if not llm:
        return error_response("LLM 未配置", 500)

    data = request.get_json() or {}
    prompt = f"""为以下校友生成一段简短"名片摘要"，50~120字，客观、可读性强：
                姓名：{data.get('name','')}
                专业：{data.get('major','')}
                工作/公司：{data.get('work','')}
                简介/说明：{data.get('bio','')}
                输出不要多余引言，直接给摘要文本。"""
    try:
        text = llm.ask(prompt)
        return success_response({'summary': text})
    except Exception as e:
        print("AI summary error:", e)
        return error_response(f"生成失败: {str(e)}", 500)

@app.route('/api/ai/draft_email', methods=['POST'])
def ai_draft_email():
    """生成邮件草稿"""
    if not llm:
        return error_response("LLM 未配置", 500)

    data = request.get_json() or {}
    topic = data.get("topic", "校友活动通知")
    audience = data.get("audience", "本校校友")
    style = data.get("style", "正式友好")
    points = "; ".join(data.get("points", []))
    prompt = f"""请写一封面向{audience}的邮件草稿，主题为"{topic}"，风格：{style}。
                    要点：{points}
                    要求：包含邮件主题建议、称呼、正文（简洁、有行动号召）、落款。"""
    try:
        text = llm.ask(prompt)
        return success_response({'draft': text})
    except Exception as e:
        print("AI draft email error:", e)
        return error_response(f"生成失败: {str(e)}", 500)

@app.route('/api/ai/search', methods=['GET'])
def ai_search():
    """AI 智能搜索"""
    if not llm:
        return error_response("LLM 未配置", 500)

    q = (request.args.get("q") or "").strip()
    if not q:
        return success_response([])

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            like = f"%{q}%"
            cursor.execute("""
                SELECT id, name, gender, age, phone, email, grad_year, degree, major, city, country,
                       LEFT(COALESCE(bio,''), 120) AS snippet
                FROM tb_user
                WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s
                   OR major LIKE %s OR city LIKE %s OR country LIKE %s OR bio LIKE %s
                LIMIT 20
            """, (like, like, like, like, like, like, like))
            rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        return error_response(f"DB 查询失败: {str(e)}", 500)

    items_text = "\n".join([
        f"- id={r['id']}, 姓名={r['name']}, 性别={r.get('gender')}, 年龄={r.get('age')}, 电话={r.get('phone')}, "
        f"邮箱={r.get('email')}, 专业={r.get('major')}, 城市={r.get('city')}, 国家={r.get('country')}, 摘要={r.get('snippet')}"
        for r in rows
    ]) or "（无）"

    prompt = f"""用户搜索：{q}
    以下是候选（最多20条）：
{items_text}

    请挑选最相关的前 5 名，并按相关度排序输出，每条给出一句话理由（简短）。
    输出 JSON 数组，字段：id, reason。不要多余文本。"""
    try:
        ranked_json = llm.ask(prompt)
        return success_response({'ranked': ranked_json, 'candidates': rows})
    except Exception as e:
        print("AI search error:", e)
        return error_response(f"搜索失败: {str(e)}", 500)

# =========================
# 错误处理
# =========================
@app.errorhandler(404)
def page_not_found(error):
    return error_response("接口不存在", 404)

@app.errorhandler(500)
def system_error(error):
    return error_response("服务器内部错误", 500)

# =========================
# 启动
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
# -*- coding: utf-8 -*-
# Flask 应用：校友/毕业生管理
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,session
from flask_login import LoginManager
import pymysql.cursors
from services.ai_query import ai_expand_query

# === 登录蓝图 & 拦截配置 ===
from auth import auth_bp
from dotenv import load_dotenv

load_dotenv()  # 让 .env 生效

from services.llm_client import LLMClient
llm = LLMClient()


# =========================
# 数据库连接
# =========================
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='alumni_mgmt',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def getconnection():
    return connection

# =========================
# Flask 基本配置
# =========================
app = Flask(__name__)

app.secret_key = "a-very-secret-key"  # 用于 flash 提示



# 注册蓝图
app.register_blueprint(auth_bp, url_prefix="/auth")
# 把当前登录用户注入所有模板
@app.context_processor
def inject_current_user():
    return dict(current_user=session.get("user"))


# 登录拦截：未登录的访问一律跳转到 /auth/login
@app.before_request
def _require_login():
    if request.endpoint in ("static",) or (request.endpoint or "").startswith("auth."):
        return
    if session.get("user"):
        return
    return redirect(url_for("auth.login"))


# =========================
# 列表页：展示扩展字段
# =========================
@app.route('/')
def index():
    try:
        with getconnection().cursor() as cursor:
            sql = """
            SELECT id, name, gender, age, phone, email, grad_year, degree, major, city, country, bio
            FROM tb_user
            ORDER BY id
            """
            cursor.execute(sql)
            users = cursor.fetchall()
        # 传入模板渲染
        return render_template('index.html', users=users)
    except Exception as e:
        print("Index error:", e)
        return render_template('500.html')


# =========================
# 搜索：按多字段模糊匹配
# =========================
@app.route('/search')
def search():
    keyword = (request.args.get('keyword') or '').strip()
    try:
        with getconnection().cursor() as cursor:
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
            params = (keyword,)*7
            cursor.execute(sql, params)
            users = cursor.fetchall()
        return render_template('index.html', users=users, keyword=keyword)
    except Exception as e:
        print("Search error:", e)
        return render_template('500.html')

# =========================
# 新增
# =========================
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # 原有字段 + 扩展字段（表单没这些项也没关系）
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        age = request.form.get('age') or None
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        grad_year = request.form.get('grad_year') or None
        degree = request.form.get('degree', '').strip()
        major = request.form.get('major', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', '').strip()
        bio = request.form.get('bio', '').strip()

        if not name:
            flash('姓名不能为空')
            return redirect(url_for('add'))

        try:
            with getconnection().cursor() as cursor:
                sql = """
                INSERT INTO tb_user
                (name, gender, age, phone, email, grad_year, degree, major, city, country, bio)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
                cursor.execute(sql, (name, gender, age, phone, email, grad_year, degree, major, city, country, bio))
                getconnection().commit()
            flash('新增成功')
            return redirect(url_for('index'))
        except Exception as e:
            print("Add error:", e)
            flash('新增失败')
            return redirect(url_for('add'))
    # GET
    return render_template('add.html')

# =========================
# 编辑
# =========================
@app.route('/edit/<int:id>', methods=['GET'])
def edit(id):
    try:
        with getconnection().cursor() as cursor:
            cursor.execute("SELECT * FROM tb_user WHERE id=%s", (id,))
            user = cursor.fetchone()
        if not user:
            flash('该记录不存在')
            return redirect(url_for('index'))
        return render_template('edit.html', user=user)
    except Exception as e:
        print("Edit error:", e)
        return render_template('500.html')

# =========================
# 更新
# =========================
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    name = request.form.get('name', '').strip()
    gender = request.form.get('gender', '').strip()
    age = request.form.get('age') or None
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    grad_year = request.form.get('grad_year') or None
    degree = request.form.get('degree', '').strip()
    major = request.form.get('major', '').strip()
    city = request.form.get('city', '').strip()
    country = request.form.get('country', '').strip()
    bio = request.form.get('bio', '').strip()

    try:
        with getconnection().cursor() as cursor:
            sql = """
            UPDATE tb_user SET
                name=%s, gender=%s, age=%s, phone=%s,
                email=%s, grad_year=%s, degree=%s, major=%s,
                city=%s, country=%s, bio=%s
            WHERE id=%s
            """
            cursor.execute(sql, (name, gender, age, phone, email, grad_year, degree, major, city, country, bio, id))
            getconnection().commit()
        flash('更新成功')
        return redirect(url_for('index'))
    except Exception as e:
        print("Update error:", e)
        flash('更新失败')
        return redirect(url_for('edit', id=id))

# =========================
# 删除
# =========================
@app.route('/delete/<int:id>')
def delete(id):
    try:
        with getconnection().cursor() as cursor:
            cursor.execute("DELETE FROM tb_user WHERE id=%s", (id,))
            getconnection().commit()
        flash('删除成功')
    except Exception as e:
        print("Delete error:", e)
        flash('删除失败')
    return redirect(url_for('index'))

# =========================
# —— AI 路由（没配置 .env 不会影响其他页）——
# =========================
# 兼容 OpenAI 风格大模型网关（豆包/通义等）
try:
    from services.llm_client import LLMClient
    llm = LLMClient()
except Exception:
    llm = None

@app.post("/ai/summary")
def ai_summary():
    if not llm:
        return jsonify({"error": "LLM 未配置"}), 500
    data = request.get_json() or {}
    prompt = f"""为以下校友生成一段简短“名片摘要”，50~120字，客观、可读性强：
                姓名：{data.get('name','')}
                专业：{data.get('major','')}
                工作/公司：{data.get('work','')}
                简介/说明：{data.get('bio','')}
                输出不要多余引言，直接给摘要文本。"""
    try:
        text = llm.ask(prompt)
        return jsonify({"summary": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/ai/draft_email")
def ai_draft_email():
    if not llm:
        return jsonify({"error": "LLM 未配置"}), 500
    data = request.get_json() or {}
    topic = data.get("topic", "校友活动通知")
    audience = data.get("audience", "本校校友")
    style = data.get("style", "正式友好")
    points = "; ".join(data.get("points", []))
    prompt = f"""请写一封面向{audience}的邮件草稿，主题为“{topic}”，风格：{style}。
                    要点：{points}
                    要求：包含邮件主题建议、称呼、正文（简洁、有行动号召）、落款。"""
    try:
        text = llm.ask(prompt)
        return jsonify({"draft": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/ai/search_lite")
def ai_search_lite():
    if not llm:
        return jsonify({"error": "LLM 未配置"}), 500
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])
    try:
        with getconnection().cursor() as cursor:
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
    except Exception as e:
        return jsonify({"error": f"DB 查询失败: {e}"}), 500

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
        return jsonify({"ranked": ranked_json, "candidates": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# 错误页
# =========================
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.errorhandler(500)
def system_error(error):
    return render_template('500.html'), 500

# =========================
# 启动
# =========================
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(host='127.0.0.1', port=8001, debug=True)


# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pymysql
import os
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="templates")

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "alumni_mgmt"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def fetch_user(username: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM auth_user WHERE username=%s", (username,))
            return cur.fetchone()
    finally:
        conn.close()

def create_user(username: str, raw_password: str, role: str = "member"):
    pwd_hash = generate_password_hash(raw_password)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO auth_user (username, password_hash, role) VALUES (%s,%s,%s)",
                (username, pwd_hash, role),
            )
    finally:
        conn.close()


@auth_bp.get("/login")
def login():
    if session.get("user"):
        return redirect(url_for("index"))
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("请输入账号和密码", "danger")
        return redirect(url_for("auth.login"))

    row = fetch_user(username)
    if not row or not check_password_hash(row["password_hash"], password):
        flash("账号或密码错误", "danger")
        return redirect(url_for("auth.login"))

    session["user"] = {"id": row["id"], "username": row["username"], "role": row["role"]}
    flash("登录成功", "success")
    return redirect(url_for("index"))

@auth_bp.get("/logout")
def logout():
    session.pop("user", None)
    flash("已退出", "info")
    return redirect(url_for("auth.login"))

# 简易注册页：仅管理员可创建用户
@auth_bp.get("/register")
def register():
    return render_template("register.html")

@auth_bp.post("/register")
def register_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm  = request.form.get("confirm", "")

    if not username or not password:
        flash("请完整填写", "danger")
        return redirect(url_for("auth.register"))
    if password != confirm:
        flash("两次密码不一致", "danger")
        return redirect(url_for("auth.register"))

    if fetch_user(username):
        flash("用户名已存在", "danger")
        return redirect(url_for("auth.register"))

    create_user(username, password, "member")
    flash("创建成功，请登录", "success")
    return redirect(url_for("auth.login"))

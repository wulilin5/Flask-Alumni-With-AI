# -*- coding: utf-8 -*-
"""
数据库初始化脚本
自动创建数据库和校友信息表
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """初始化数据库和表结构"""
    
    # 连接到 MySQL 服务器（不指定数据库）
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            db_name = os.getenv('DB_NAME', 'alumni_mgmt')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
            print(f"✓ 数据库 {db_name} 已存在或创建成功")
            
            # 切换到目标数据库
            cursor.execute(f"USE {db_name}")

            # 删除旧表（如果存在）
            cursor.execute("DROP TABLE IF EXISTS tb_user")

            # 创建校友用户表
            create_table_sql = """
            CREATE TABLE tb_user (
              id INT PRIMARY KEY AUTO_INCREMENT,
              name VARCHAR(100) NOT NULL,
              gender VARCHAR(10) DEFAULT NULL,
              age INT DEFAULT NULL,
              phone VARCHAR(30) DEFAULT NULL,
              email VARCHAR(120) DEFAULT NULL,
              grad_year INT DEFAULT NULL,
              degree VARCHAR(64) DEFAULT NULL,
              major VARCHAR(128) DEFAULT NULL,
              city VARCHAR(64) DEFAULT NULL,
              country VARCHAR(64) DEFAULT NULL,
              bio TEXT DEFAULT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              KEY idx_name (name),
              KEY idx_phone (phone),
              KEY idx_major (major),
              KEY idx_city (city),
              KEY idx_grad_year (grad_year)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            cursor.execute(create_table_sql)
            print("✓ 表 tb_user 创建成功")

            # 创建用户认证表
            cursor.execute("DROP TABLE IF EXISTS auth_user")
            create_auth_user_sql = """
            CREATE TABLE auth_user (
              id INT PRIMARY KEY AUTO_INCREMENT,
              username VARCHAR(50) UNIQUE NOT NULL,
              password_hash VARCHAR(255) NOT NULL,
              role ENUM('admin', 'user') DEFAULT 'user',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              last_login TIMESTAMP NULL,
              is_active BOOLEAN DEFAULT TRUE,
              KEY idx_username (username),
              KEY idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
            cursor.execute(create_auth_user_sql)
            print("✓ 表 auth_user 创建成功")

            # 检查校友表中是否有数据
            cursor.execute("SELECT COUNT(*) as count FROM tb_user")
            result = cursor.fetchone()

            if result['count'] == 0:
                # 插入示例数据
                insert_data_sql = """
                INSERT INTO tb_user (name, gender, age, phone, email, grad_year, degree, major, city, country, bio) VALUES
                ('张三', '男', 30, '13800000001', 'zhangsan@example.com', 2017, '硕士', '计算机科学', '北京', '中国', '后端工程师，分布式存储方向'),
                ('李四', '女', 29, '13800000002', 'lisi@example.com', 2018, '本科', '通信工程', '上海', '中国', '运营商网络优化，5G 项目'),
                ('王五', '男', 28, '13800000003', 'wangwu@example.com', 2019, '硕士', '人工智能', '深圳', '中国', '算法工程师，NLP/LLM'),
                ('Lucy', '女', 31, '13800000004', 'lucy@example.com', 2016, '硕士', '软件工程', 'New York', 'USA', '全栈开发，React/Flask');
                """
                cursor.execute(insert_data_sql)
                print("✓ 示例数据插入成功")
            else:
                print(f"✓ 表中已有 {result['count']} 条数据，跳过示例数据插入")

            # 检查用户表中是否有管理员账户
            cursor.execute("SELECT COUNT(*) as count FROM auth_user WHERE role='admin'")
            result = cursor.fetchone()

            if result['count'] == 0:
                # 插入默认管理员账户（用户名: admin, 密码: admin123）
                from werkzeug.security import generate_password_hash
                default_password_hash = generate_password_hash('admin123')
                insert_admin_sql = """
                INSERT INTO auth_user (username, password_hash, role, is_active) VALUES
                ('admin', %s, 'admin', TRUE)
                """
                cursor.execute(insert_admin_sql, (default_password_hash,))
                print("✓ 默认管理员账户创建成功 (用户名: admin, 密码: admin123)")
            else:
                print(f"✓ 已有 {result['count']} 个管理员账户，跳过默认管理员创建")
            
        connection.commit()
        print("\n✅ 数据库初始化完成！")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()

if __name__ == "__main__":
    print("开始初始化数据库...")
    init_database()
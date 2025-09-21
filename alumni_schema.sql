
-- Create a new database for the alumni system
CREATE DATABASE IF NOT EXISTS alumni_mgmt DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE alumni_mgmt;

-- Alumni-oriented user table (keeps legacy fields for compatibility)
DROP TABLE IF EXISTS tb_user;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed sample data
INSERT INTO tb_user (name, gender, age, phone, email, grad_year, degree, major, city, country, bio) VALUES
('张三', '男', 30, '13800000001', 'zhangsan@example.com', 2017, '硕士', '计算机科学', '北京', '中国', '后端工程师，分布式存储方向'),
('李四', '女', 29, '13800000002', 'lisi@example.com', 2018, '本科', '通信工程', '上海', '中国', '运营商网络优化，5G 项目'),
('王五', '男', 28, '13800000003', 'wangwu@example.com', 2019, '硕士', '人工智能', '深圳', '中国', '算法工程师，NLP/LLM'),
('Lucy', '女', 31, '13800000004', 'lucy@example.com', 2016, '硕士', '软件工程', 'New York', 'USA', '全栈开发，React/Flask');

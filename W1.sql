-- 1. 查看目前有哪些資料庫
SHOW DATABASES;

-- 2. 如果沒有 testdb，先建立資料庫（可選）
CREATE DATABASE IF NOT EXISTS test_db;

-- 3. 切換到測試資料庫
USE test_db;

-- 4. 建立一個測試資料表，如果已經存在就不再建立
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. 查詢所有資料
SELECT * FROM users;
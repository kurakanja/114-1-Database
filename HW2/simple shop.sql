-- 建立一個新的資料庫 (如果不存在)
CREATE DATABASE IF NOT EXISTS simple_shop;

-- 使用該資料庫
USE simple_shop;

-- 1. 建立顧客資料表 (Customers)
-- 儲存客戶基本資訊
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. 建立產品資料表 (Products)
-- 儲存商品資訊，價格使用 DECIMAL 以確保精確度
CREATE TABLE IF NOT EXISTS Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- 3. 建立訂單資料表 (Orders)
-- 記錄訂單的總體資訊，並透過 customer_id 與 Customers 表關聯
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
) ENGINE=InnoDB;

-- 4. 建立訂單明細資料表 (Order_Details)
-- 這是連結 Orders 和 Products 的關聯表 (Junction Table)
CREATE TABLE IF NOT EXISTS Order_Details (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price_at_purchase DECIMAL(10, 2) NOT NULL, -- 記錄購買當下的價格，避免未來商品調價影響歷史訂單
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
) ENGINE=InnoDB;

-- 顯示所有建立的資料表
SHOW TABLES;

from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
# 設定一個 secret_key 才能使用 flash 訊息
app.secret_key = 'your_very_secret_key' 

# --- 資料庫連線設定 ---
# !!! 請務必修改成你自己的設定 !!!
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '0000',
    'database': 'simple_shop' 
}

# --- 資料庫輔助函數 ---
def get_db_connection():
    """建立並回傳資料庫連線"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def setup_database():
    """初始化資料庫和資料表"""
    print("正在設定資料庫...")
    # 建立一個不指定資料庫的連線來建立資料庫
    temp_config = db_config.copy()
    temp_config.pop('database', None)
    conn = mysql.connector.connect(**temp_config)
    cursor = conn.cursor()
    
    db_name = db_config['database']
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute(f"USE {db_name};")
    print(f"資料庫 '{db_name}' 已準備就緒。")

    # 刪除舊表以便重新開始
    cursor.execute("DROP TABLE IF EXISTS Order_Details, Orders, Products, Customers;")
    
    # 建立資料表
    cursor.execute("""
    CREATE TABLE Customers (
        customer_id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL, email VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB;""")
    cursor.execute("""
    CREATE TABLE Products (
        product_id INT AUTO_INCREMENT PRIMARY KEY, product_name VARCHAR(100) NOT NULL,
        price DECIMAL(10, 2) NOT NULL, stock_quantity INT NOT NULL DEFAULT 0
    ) ENGINE=InnoDB;""")
    cursor.execute("""
    CREATE TABLE Orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY, customer_id INT,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, total_amount DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE SET NULL
    ) ENGINE=InnoDB;""")
    cursor.execute("""
    CREATE TABLE Order_Details (
        order_detail_id INT AUTO_INCREMENT PRIMARY KEY, order_id INT, product_id INT,
        quantity INT NOT NULL, price_at_purchase DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE SET NULL
    ) ENGINE=InnoDB;""")

    

# --- Flask 路由 (Routes) ---

@app.route('/')
def index():
    """主頁面，顯示所有資料"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # 使用 dictionary=True 讓結果更易於使用
    
    cursor.execute("SELECT * FROM Customers ORDER BY customer_id")
    customers = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Products ORDER BY product_id")
    products = cursor.fetchall()

    # 查詢訂單摘要 (包含顧客姓名)
    cursor.execute("""
        SELECT o.order_id, o.order_date, o.total_amount, c.first_name, c.last_name
        FROM Orders o
        LEFT JOIN Customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_id DESC
    """)
    orders = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('index.html', customers=customers, products=products, orders=orders)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Customers (first_name, last_name, email) VALUES (%s, %s, %s)",
                       (first_name, last_name, email))
        conn.commit()
        flash('顧客新增成功!', 'success')
    except Error as e:
        flash(f'新增顧客失敗: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('index'))

@app.route('/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    price = request.form['price']
    stock_quantity = request.form['stock_quantity']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Products (product_name, price, stock_quantity) VALUES (%s, %s, %s)",
                   (product_name, price, stock_quantity))
    conn.commit()
    cursor.close()
    conn.close()
    flash('產品新增成功!', 'success')
    return redirect(url_for('index'))

@app.route('/create_order', methods=['POST'])
def create_order():
    customer_id = request.form['customer_id']
    
    # 找出所有被勾選並填寫數量的產品
    product_details = []
    total_amount = 0
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    for key, quantity_str in request.form.items():
        if key.startswith('quantity_') and quantity_str.isdigit() and int(quantity_str) > 0:
            product_id = key.split('_')[1]
            quantity = int(quantity_str)
            
            # 取得產品目前價格
            cursor.execute("SELECT price FROM Products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if product:
                price = product['price']
                total_amount += price * quantity
                product_details.append({'product_id': product_id, 'quantity': quantity, 'price': price})
    
    if not product_details:
        flash('您沒有選擇任何商品或數量!', 'error')
        return redirect(url_for('index'))

    # 寫入資料庫 (交易)
    try:
        cursor.execute("INSERT INTO Orders (customer_id, total_amount) VALUES (%s, %s)",
                       (customer_id, total_amount))
        order_id = cursor.lastrowid
        
        for item in product_details:
            cursor.execute("""
                INSERT INTO Order_Details (order_id, product_id, quantity, price_at_purchase)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], item['price']))
        
        conn.commit()
        flash(f'訂單 #{order_id} 建立成功!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'建立訂單失敗: {e}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/order/<int:order_id>')
def order_details(order_id):
    """顯示訂單詳情 (JOIN 查詢)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT o.order_id, o.order_date, o.total_amount,
           c.first_name, c.last_name, c.email,
           p.product_name, od.quantity, od.price_at_purchase
    FROM Orders AS o
    JOIN Customers AS c ON o.customer_id = c.customer_id
    JOIN Order_Details AS od ON o.order_id = od.order_id
    JOIN Products AS p ON od.product_id = p.product_id
    WHERE o.order_id = %s;
    """
    cursor.execute(query, (order_id,))
    details = cursor.fetchall()
    
    cursor.close()
    conn.close()

    if not details:
        flash(f"找不到訂單 ID {order_id}", "error")
        return redirect(url_for('index'))

    return render_template('order_details.html', details=details)

@app.route('/delete/<string:entity>/<int:entity_id>', methods=['POST'])
def delete_entity(entity, entity_id):
    """通用刪除函數"""
    table_map = {
        'customer': 'Customers',
        'product': 'Products',
        'order': 'Orders'
    }
    id_map = {
        'customer': 'customer_id',
        'product': 'product_id',
        'order': 'order_id'
    }
    
    if entity not in table_map:
        flash('無效的實體類型!', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 如果刪除訂單，會因為 ON DELETE CASCADE 自動刪除 Order_Details
        query = f"DELETE FROM {table_map[entity]} WHERE {id_map[entity]} = %s"
        cursor.execute(query, (entity_id,))
        conn.commit()
        flash(f'{entity.capitalize()} #{entity_id} 刪除成功!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'刪除失敗: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 第一次執行時，初始化資料庫
    setup_database()
    # 啟動 Flask 伺服器
    # debug=True 會在程式碼變更時自動重啟伺服器，但生產環境中應設為 False
    app.run(debug=True)
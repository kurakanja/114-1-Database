from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# 建立資料庫連線
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",        # 改成你的 MySQL 使用者
        password="0000", # 改成你的密碼
        database="test_db"
    )
    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")  # 查詢現在時間
        result = cursor.fetchone()
        conn.close()
        return jsonify({"status": "成功連線！", "time": str(result[0])})
    except Exception as e:
        return jsonify({"status": "連線失敗", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
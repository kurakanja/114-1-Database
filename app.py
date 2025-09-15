from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL 連線設定
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "0000",
    "database": "test_db"
}

@app.route("/")
def home():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)
    except mysql.connector.Error as err:
        return {"error": str(err)}

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, redirect, render_template_string
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# MySQL 連線設定 (加上 autocommit=True)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "0000",
    "database": "test_db",
    "autocommit": True   # ✅ 自動提交
}

# HTML 模板
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>使用者列表</title>
</head>
<body>
    <h1>使用者列表</h1>
    <table border="1" cellpadding="5">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Created At</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.created_at }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>新增使用者</h2>
    <form method="POST" action="/add_user">
        Name: <input type="text" name="name" required>
        Email: <input type="email" name="email" required>
        <button type="submit">新增使用者</button>
    </form>
</body>
</html>
"""

@app.route("/")
def home():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template_string(HOME_HTML, users=users)

@app.route("/add_user", methods=["POST"])
def add_user():
    name = request.form["name"]
    email = request.form["email"]
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, created_at) VALUES (%s, %s, %s)",
        (name, email, created_at)
    )
    # 不需要 conn.commit()，因為 autocommit=True
    cursor.close()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

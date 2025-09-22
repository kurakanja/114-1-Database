from flask import Flask, request, redirect, url_for, render_template_string
import mysql.connector

app = Flask(__name__)

# MySQL 連線設定
db = mysql.connector.connect(
    host="localhost",
    user="root",       # 改成你的 MySQL 帳號
    password="0000",   # 改成你的 MySQL 密碼
    database="addd_db"
)
cursor = db.cursor(dictionary=True)

# 🔹 HTML 模板（用簡單的 inline template）
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>使用者管理</title>
</head>
<body>
    <h2>使用者列表</h2>

    <!-- 新增使用者 -->
    <form method="POST" action="/add">
        <input type="text" name="name" placeholder="輸入名字" required>
        <button type="submit">新增</button>
    </form>

    <hr>

    <!-- 顯示所有使用者 -->
    <table border="1" cellpadding="5">
        <tr>
            <th>ID</th>
            <th>名字</th>
            <th>建立時間</th>
            <th>操作</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.created_at }}</td>
            <td>
                <a href="/edit/{{ user.id }}">修改</a> | 
                <a href="/delete/{{ user.id }}">刪除</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# 🔹 編輯頁面模板
EDIT_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>修改使用者</title></head>
<body>
    <h2>修改使用者</h2>
    <form method="POST">
        <input type="text" name="name" value="{{ user.name }}" required>
        <button type="submit">儲存</button>
    </form>
    <a href="/">回首頁</a>
</body>
</html>
"""

# 首頁：顯示所有資料
@app.route("/")
def index():
    cursor.execute("SELECT * FROM users ORDER BY id DESC")
    users = cursor.fetchall()
    return render_template_string(HTML, users=users)

# 新增資料
@app.route("/add", methods=["POST"])
def add_user():
    name = request.form["name"]
    cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
    db.commit()
    return redirect(url_for("index"))

# 刪除資料
@app.route("/delete/<int:user_id>")
def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return redirect(url_for("index"))

# 修改資料（顯示表單）
@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if request.method == "POST":
        new_name = request.form["name"]
        cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
        db.commit()
        return redirect(url_for("index"))
    
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return render_template_string(EDIT_HTML, user=user)

if __name__ == "__main__":
    app.run(debug=True)
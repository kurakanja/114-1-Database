from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")
db = client["hw3"]
users = db["users"]
contacts = db["contacts"]


# 登入頁面
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="帳號或密碼錯誤")

    return render_template("login.html")


# 註冊頁面
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 檢查是否重複
        if users.find_one({"username": username}):
            return render_template("register.html", error="帳號已存在")

        hashed_pw = generate_password_hash(password)
        users.insert_one({"username": username, "password": hashed_pw})
        return redirect(url_for("login"))

    return render_template("register.html")


# 登出
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# 主頁（需登入）
@app.route("/index")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    # 只取出自己的資料
    records = list(
        contacts.find({"username": username}).sort([("date", 1), ("importance", 1)])
    )

    # 分日期分組
    grouped_records = {}
    for r in records:
        date = r.get("date", "")
        if date not in grouped_records:
            grouped_records[date] = []
        grouped_records[date].append(r)

    return render_template("index.html", grouped_records=grouped_records, user=username)


# 新增資料
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    date = request.form["date"]
    title = request.form["title"]
    details = request.form["details"]
    importance = int(request.form["importance"])

    contacts.insert_one({
        "username": username,
        "date": date,
        "title": title,
        "details": details,
        "importance": importance
    })
    return redirect(url_for("index"))


# 刪除資料
@app.route("/delete/<id>")
def delete(id):
    if "user" not in session:
        return redirect(url_for("login"))
    username = session["user"]
    contacts.delete_one({"_id": ObjectId(id), "username": username})
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
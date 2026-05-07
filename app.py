from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import unquote
import sqlite3


app = Flask(__name__)

areas = ["العتبة", "المطرية", "الزاوية", "شبرا"]

# 🔥 إنشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            area TEXT,
            debt TEXT,
            status TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# 🏠 الرئيسية (عرض من SQLite)
@app.route("/")
def home():

    conn = sqlite3.connect("/tmp/customers.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    conn.close()

    return render_template("index.html", customers=customers, areas=areas)


# ➕ صفحة إضافة
@app.route("/add")
def add_page():
    return render_template("add.html", areas=areas)


# 💾 حفظ عميل (SQLite)
@app.route("/save", methods=["POST"])
def save():

    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers
        (name, phone, address, area, debt, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["name"],
        request.form["phone"],
        request.form["address"],
        request.form["area"],
        request.form["debt"],
        request.form["status"],
        request.form["notes"]
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# 🔍 بحث
@app.route("/search")
def search():

    text = request.args.get("search", "").strip().lower()

    conn = sqlite3.connect("customers.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE LOWER(name) LIKE ?", ('%' + text + '%',))
    customers = cursor.fetchall()

    conn.close()

    return render_template("index.html", customers=customers, areas=areas)


# 📍 منطقة
@app.route("/area/<path:area_name>")
def area_view(area_name):

    area_name = unquote(area_name)

    conn = sqlite3.connect("customers.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE area = ?", (area_name,))
    customers = cursor.fetchall()

    conn.close()

    return render_template("area.html", customers=customers, area=area_name)


# ✏️ تعديل
@app.route("/edit/<int:customer_id>", methods=["GET", "POST"])
def edit(customer_id):

    conn = sqlite3.connect("customers.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        cursor.execute("""
            UPDATE customers
            SET name=?, phone=?, address=?, area=?, debt=?, status=?, notes=?
            WHERE id=?
        """, (
            request.form["name"],
            request.form["phone"],
            request.form["address"],
            request.form["area"],
            request.form["debt"],
            request.form["status"],
            request.form["notes"],
            customer_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    customer = cursor.fetchone()

    conn.close()

    return render_template("edit.html", customer=customer, areas=areas)


# 🗑 حذف
@app.route("/delete/<int:customer_id>")
def delete(customer_id):

    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
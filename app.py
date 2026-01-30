from flask import Flask, render_template, request, redirect, session
import json

app = Flask(__name__)
app.secret_key = "сложный_случайный ключ_ключ"

PRODUCTS_FILE = "products.json"
ADMIN_PASSWORD = "andre0502"


def load_products():
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    products = load_products()
    return render_template("index.html", products=products)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
        else:
            return "Неверный пароль"

    if not session.get("admin"):
        return render_template("login.html")

    products = load_products()
    return render_template("admin.html", products=products)


@app.route("/add", methods=["POST"])
def add():
    if not session.get("admin"):
        return redirect("/admin")

    name = request.form["name"]
    price = int(request.form["price"])

    products = load_products()
    products.append({"name": name, "price": price})
    save_products(products)

    return redirect("/admin")


@app.route("/delete/<int:index>")
def delete(index):
    if not session.get("admin"):
        return redirect("/admin")

    products = load_products()
    products.pop(index)
    save_products(products)

    return redirect("/admin")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/admin")


@app.route("/edit/<int:index>", methods=["POST"])
def edit(index):
    if not session.get("admin"):
        return redirect("/admin")

    name = request.form["name"]
    price = int(request.form["price"])

    products = load_products()
    products[index]["name"] = name
    products[index]["price"] = price
    save_products(products)

    return redirect("/admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


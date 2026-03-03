import json
import logging
import os

from flask import Flask, jsonify, redirect, render_template, request, session

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "simple_random_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
LEGACY_PRODUCTS_FILE = os.path.join(DATA_DIR, "\u043f\u0440\u043e\u0434\u0443\u043a\u0442\u044b.json")
ADMIN_PASSWORD = "andre0502"


def load_products():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(PRODUCTS_FILE) and os.path.exists(LEGACY_PRODUCTS_FILE):
        try:
            with open(LEGACY_PRODUCTS_FILE, "r", encoding="utf-8") as f:
                legacy_data = json.load(f)
                legacy_data = legacy_data if isinstance(legacy_data, list) else []
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(legacy_data, f, ensure_ascii=False, indent=2)
            return legacy_data
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.exception("Failed to parse legacy products file")

    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.exception("Failed to parse products.json, reset file")
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []


def save_products(products):
    os.makedirs(DATA_DIR, exist_ok=True)
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
            return "Wrong password"

    if not session.get("admin"):
        return render_template("login.html")

    products = load_products()
    return render_template("admin.html", products=products)


@app.route("/add", methods=["POST"])
def add():
    if not session.get("admin"):
        return redirect("/admin")

    name = request.form["name"]
    price = request.form.get("price", "")
    if price.isdigit():
        price = int(price)

    products = load_products()
    products.append({"name": name, "price": price})
    save_products(products)

    return redirect("/admin")


@app.route("/delete/<int:index>")
def delete(index):
    if not session.get("admin"):
        return redirect("/admin")

    products = load_products()
    if 0 <= index < len(products):
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
    price = request.form.get("price", "")
    if price.isdigit():
        price = int(price)

    products = load_products()
    if 0 <= index < len(products):
        products[index]["name"] = name
        products[index]["price"] = price
        save_products(products)

    return redirect("/admin")


@app.route("/team", methods=["POST"])
def team():
    return redirect("/")


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Server error: {e}", exc_info=True)
    return jsonify({"error": "Internal server error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

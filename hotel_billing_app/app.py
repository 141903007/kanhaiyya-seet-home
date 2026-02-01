from flask import Flask, render_template, request, jsonify, session, redirect
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hotel_secret"

DATA_PATH = "data/"

def load_excel(file, columns):
    path = DATA_PATH + file
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columns)
        df.to_excel(path, index=False)
    return pd.read_excel(path)

def save_excel(df, file):
    df.to_excel(DATA_PATH + file, index=False)

# ---------------- AUTH ----------------
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    users = load_excel("users.xlsx", ["username", "password"])
    user = request.form["username"]
    pwd = request.form["password"]
    if ((users.username == user) & (users.password == pwd)).any():
        session["user"] = user
        return "success"
    return "fail"

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/")
    return render_template("dashboard.html")

@app.route("/billing")
def billing():
    if "user" not in session: return redirect("/")
    return render_template("billing.html")

# ---------------- ITEMS ----------------
@app.route("/items", methods=["GET", "POST"])
def items():
    df = load_excel("items.xlsx", ["id", "name", "price"])

    if request.method == "POST":
        data = request.json
        new_id = int(df["id"].max()) + 1 if len(df) else 1
        df.loc[len(df)] = [new_id, data["name"], float(data["price"])]
        save_excel(df, "items.xlsx")
        return "added"

    return df.to_json(orient="records")


# ---------------- CART (FIXED) ----------------
@app.route("/cart", methods=["POST"])
def cart():
    data = request.get_json()

    table = str(data["table"])
    item  = str(data["item"])
    qty   = float(data["qty"])

    cart = session.get("cart", {})

    if table not in cart:
        cart[table] = {}

    # remove item if qty is 0
    if qty <= 0:
        cart[table].pop(item, None)
    else:
        cart[table][item] = qty

    session["cart"] = cart   # important
    session.modified = True

    return jsonify(cart[table])



# ---------------- BILL GENERATION (FIXED) ----------------
@app.route("/generate_bill", methods=["POST"])
def generate_bill():
    data = request.get_json()
    table = str(data["table"])
    mobile = data["mobile"]

    cart_all = session.get("cart", {})
    cart = cart_all.get(table, {})

    items_df = load_excel("items.xlsx", ["id", "name", "price"])
    bills = load_excel("bills.xlsx", ["bill_no", "table", "mobile", "date", "total"])
    bill_items = load_excel("bill_items.xlsx", ["bill_no", "item", "qty", "price", "line_total"])

    bill_no = f"BILL{int(datetime.now().timestamp())}"
    total = 0

    for item_id, qty in cart.items():
        price = float(items_df[items_df.id == int(item_id)]["price"].values[0])
        line = price * qty
        total += line
        bill_items.loc[len(bill_items)] = [bill_no, item_id, qty, price, line]

    bills.loc[len(bills)] = [bill_no, table, mobile, datetime.now(), total]

    save_excel(bills, "bills.xlsx")
    save_excel(bill_items, "bill_items.xlsx")

    # clear only that table cart
    cart_all[table] = {}
    session["cart"] = cart_all
    session.modified = True

    return bill_no


# ---------------- BILL SEARCH ----------------
@app.route("/search_bill", methods=["POST"])
def search_bill():
    df = load_excel("bills.xlsx", ["bill_no", "table", "mobile", "date", "total"])
    data = request.json

    if data.get("bill_no"):
        df = df[df.bill_no == data["bill_no"]]
    if data.get("mobile"):
        df = df[df.mobile == data["mobile"]]

    return df.to_json(orient="records")


if __name__ == "__main__":
    app.run(debug=True)

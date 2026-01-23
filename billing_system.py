import tkinter as tk
from tkinter import messagebox
import pandas as pd
from datetime import datetime
import os

# ---------------- LOAD DATA ----------------
PRICE_FILE = "prices.xlsx"
df_prices = pd.read_excel(PRICE_FILE)

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Snack Billing System")
root.geometry("1250x700")
root.config(bg="#f4f6f7")

cart = {}
filtered_df = df_prices.copy()
qty_vars = {}

# ---------------- FUNCTIONS ----------------
def search_items(*args):
    global filtered_df
    q = search_var.get().lower()
    filtered_df = df_prices if q == "" else df_prices[df_prices["Item"].str.lower().str.startswith(q)]
    draw_items()

def add_or_update_item(item, qty_var):
    try:
        qty = int(qty_var.get())
        if qty < 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Quantity must be 0 or positive")
        return

    if qty == 0:
        cart.pop(item, None)
    else:
        cart[item] = qty

    # ❌ no redraw / no refresh
    refresh_cart()

def refresh_cart():
    txt_cart.config(state="normal")
    txt_cart.delete(1.0, tk.END)
    subtotal = 0

    for item, qty in cart.items():
        price = df_prices.loc[df_prices["Item"] == item, "Price"].values[0]
        amt = price * qty
        txt_cart.insert(tk.END, f"{item}  ₹{price} x {qty} = ₹{amt}\n")
        subtotal += amt

    discount = float(entry_discount.get() or 0)
    net = subtotal - (subtotal * discount / 100)
    lbl_total.config(text=f"Subtotal: ₹{subtotal} | Discount: {discount}% | Net Total: ₹{net}")
    txt_cart.config(state="disabled")

def get_bill_data():
    subtotal = 0
    lines = []

    for item, qty in cart.items():
        price = df_prices.loc[df_prices["Item"] == item, "Price"].values[0]
        amt = price * qty
        lines.append(f"{item}  ₹{price} x {qty} = ₹{amt}")
        subtotal += amt

    discount = float(entry_discount.get() or 0)
    net = subtotal - (subtotal * discount / 100)
    return lines, subtotal, discount, net

# ---------------- BILL PREVIEW ----------------
def preview_bill():
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return

    preview = tk.Toplevel(root)
    preview.title("Bill Preview")
    preview.geometry("420x550")

    txt = tk.Text(preview, font=("Courier", 10))
    txt.pack(fill="both", expand=True, padx=10, pady=10)

    lines, subtotal, discount, net = get_bill_data()
    now = datetime.now()

    table = entry_table.get().strip()
    mobile = entry_mobile.get().strip()

    txt.insert("end", "Kanhaiyya Snack Center\n")
    txt.insert("end", "-" * 35 + "\n")
    txt.insert("end", f"Date   : {now.strftime('%d-%m-%Y %H:%M:%S')}\n")
    txt.insert("end", f"Table  : {table}\n")
    txt.insert("end", f"Mobile : {mobile}\n")
    txt.insert("end", "-" * 35 + "\n\n")

    txt.insert("end", "\n".join(lines) + "\n\n")
    txt.insert("end", "-" * 35 + "\n")
    txt.insert("end", f"Subtotal : ₹{subtotal}\n")
    txt.insert("end", f"Discount : {discount}%\n")
    txt.insert("end", f"Net Total: ₹{net}\n")
    txt.insert("end", "-" * 35 + "\n")
    txt.insert("end", "Thank You! Visit Again 🙏")

    txt.config(state="disabled")

    tk.Button(
        preview,
        text="Confirm & Save",
        bg="#27ae60",
        fg="white",
        height=2,
        command=lambda: [preview.destroy(), save_bill()]
    ).pack(fill="x", padx=10, pady=5)

    tk.Button(preview, text="Cancel", height=2,
              command=preview.destroy).pack(fill="x", padx=10)

# ---------------- SAVE BILL ----------------
def save_bill():
    table = entry_table.get().strip()
    mobile = entry_mobile.get().strip()

    now = datetime.now()
    year_folder = f"bills/{now.year}"
    os.makedirs(year_folder, exist_ok=True)

    file_name = f"{now.strftime('%H-%M-%S')}_T-{table}_{mobile}.txt"
    file_path = os.path.join(year_folder, file_name)

    lines, subtotal, discount, net = get_bill_data()

    with open(file_path, "w") as f:
        f.write("Kanhaiyya Snack Center\n")
        f.write("-----------------------\n")
        f.write(f"Date   : {now.strftime('%d-%m-%Y %H:%M:%S')}\n")
        f.write(f"Table  : {table}\n")
        f.write(f"Mobile : {mobile}\n")
        f.write("-----------------------\n")
        f.write("\n".join(lines) + "\n")
        f.write("-----------------------\n")
        f.write(f"Subtotal : ₹{subtotal}\n")
        f.write(f"Discount : {discount}%\n")
        f.write(f"Net Total: ₹{net}\n")
        f.write("\nThank You! Visit Again\n")

    cart.clear()
    for var in qty_vars.values():
        var.set("0")

    entry_table.delete(0, tk.END)
    entry_mobile.delete(0, tk.END)
    entry_discount.delete(0, tk.END)
    entry_discount.insert(0, "0")

    refresh_cart()
    messagebox.showinfo("Saved", f"Bill saved:\n{file_path}")

# ---------------- DRAW ITEMS ----------------
def draw_items():
    for w in frame_items_list.winfo_children():
        w.destroy()

    col = row = 0
    for _, r in filtered_df.iterrows():
        item = r["Item"]
        price = r["Price"]

        qty_var = qty_vars.setdefault(item, tk.StringVar(value="0"))

        block = tk.Frame(frame_items_list, bg="#ecf0f1", bd=1, relief="solid")
        block.grid(row=row, column=col, padx=6, pady=6, sticky="w")

        tk.Label(block, text=item, width=18, anchor="w").grid(row=0, column=0)
        tk.Label(block, text=f"₹{price}", width=6).grid(row=0, column=1)

        qty_entry = tk.Entry(block, textvariable=qty_var, width=4)
        qty_entry.grid(row=0, column=2)
        qty_entry.bind("<Return>", lambda e, i=item, q=qty_var: add_or_update_item(i, q))

        tk.Button(
            block,
            text="Add",
            bg="#27ae60",
            fg="white",
            command=lambda i=item, q=qty_var: add_or_update_item(i, q)
        ).grid(row=0, column=3, padx=4)

        col += 1
        if col == 2:
            col = 0
            row += 1

# ---------------- TOP INFO ----------------
frame_info = tk.Frame(root, bg="white", pady=8)
frame_info.pack(fill="x")

tk.Label(frame_info, text="Table").pack(side="left", padx=5)
entry_table = tk.Entry(frame_info, width=5)
entry_table.pack(side="left")

tk.Label(frame_info, text="Mobile").pack(side="left", padx=10)
entry_mobile = tk.Entry(frame_info, width=12)
entry_mobile.pack(side="left")

tk.Label(frame_info, text="Discount %").pack(side="left", padx=10)
entry_discount = tk.Entry(frame_info, width=5)
entry_discount.insert(0, "0")
entry_discount.pack(side="left")

# ---------------- ITEMS ----------------
frame_items = tk.LabelFrame(root, text="Items")
frame_items.place(x=10, y=60, width=780, height=520)

search_var = tk.StringVar()
search_var.trace("w", search_items)
tk.Entry(frame_items, textvariable=search_var).pack(fill="x", padx=6, pady=4)

canvas = tk.Canvas(frame_items)
scroll = tk.Scrollbar(frame_items, command=canvas.yview)
canvas.configure(yscrollcommand=scroll.set)

scroll.pack(side="right", fill="y")
canvas.pack(fill="both", expand=True)

frame_items_list = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame_items_list, anchor="nw")

# ---------------- CART ----------------
frame_cart = tk.LabelFrame(root, text="Cart")
frame_cart.place(x=800, y=60, width=440, height=420)

txt_cart = tk.Text(frame_cart, state="disabled")
txt_cart.pack(fill="both", expand=True, padx=5)

lbl_total = tk.Label(root, font=("Arial", 13), bg="#f4f6f7")
lbl_total.place(x=800, y=490)

# ---------------- BILL PANEL ----------------
frame_bill = tk.LabelFrame(root, text="Bill")
frame_bill.place(x=10, y=590, width=1230, height=90)

tk.Button(
    frame_bill,
    text="Preview Bill",
    height=2,
    bg="#34495e",
    fg="white",
    command=preview_bill
).pack(fill="x", padx=30, pady=15)

draw_items()
root.mainloop()


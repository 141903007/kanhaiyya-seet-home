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
root.geometry("1250x650")
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

    search_var.set("")
    refresh_cart()
    draw_items()

def refresh_cart():
    txt_cart.config(state="normal")
    txt_cart.delete(1.0, tk.END)
    subtotal = 0

    for item, qty in cart.items():
        price = df_prices.loc[df_prices["Item"] == item, "Price"].values[0]
        amt = price * qty
        txt_cart.insert(tk.END, f"{item}  ₹{price} x {qty}  =  ₹{amt}\n")
        subtotal += amt

    discount = float(entry_discount.get() or 0)
    net = subtotal - (subtotal * discount / 100)
    lbl_total.config(text=f"Subtotal: ₹{subtotal} | Discount: {discount}% | Net Total: ₹{net}")
    txt_cart.config(state="disabled")

def save_bill():
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return

    table = entry_table.get().strip()
    mobile = entry_mobile.get().strip()

    try:
        discount = float(entry_discount.get())
    except:
        discount = 0

    now = datetime.now()
    year_folder = f"bills/{now.year}"
    os.makedirs(year_folder, exist_ok=True)

    file_name = f"{now.strftime('%H-%M-%S')}_T-{table}_{mobile}.txt"
    file_path = os.path.join(year_folder, file_name)

    subtotal = 0
    with open(file_path, "w") as f:
        f.write("Kanhaiyya Snack Center\n")
        f.write("-----------------------\n")
        f.write(f"Date: {now.strftime('%d-%m-%Y %H:%M:%S')}\n")
        f.write(f"Table: {table}\n")
        f.write(f"Mobile: {mobile}\n\n")

        for item, qty in cart.items():
            price = df_prices.loc[df_prices["Item"] == item, "Price"].values[0]
            amt = price * qty
            f.write(f"{item}  ₹{price} x {qty}  =  ₹{amt}\n")
            subtotal += amt

        net = subtotal - (subtotal * discount / 100)

        f.write("\n-----------------------\n")
        f.write(f"Subtotal: ₹{subtotal}\n")
        f.write(f"Discount: {discount}%\n")
        f.write(f"Net Total: ₹{net}\n\n")
        f.write("Thank You! Visit Again")

    # ---------- RESET EVERYTHING ----------
    cart.clear()

    for var in qty_vars.values():
        var.set("0")

    entry_table.delete(0, tk.END)
    entry_mobile.delete(0, tk.END)
    entry_discount.delete(0, tk.END)
    entry_discount.insert(0, "0")

    refresh_cart()

    messagebox.showinfo("Saved", f"Bill saved successfully:\n{file_path}")


# ---------------- DRAW ITEMS (2 COLUMNS) ----------------
def draw_items():
    for w in frame_items_list.winfo_children():
        w.destroy()

    col = 0
    row = 0

    for _, r in filtered_df.iterrows():
        item = r["Item"]
        price = r["Price"]

        qty_var = qty_vars.setdefault(item, tk.StringVar(value="0"))

        block = tk.Frame(frame_items_list, bg="#ecf0f1")
        block.grid(row=row, column=col, padx=6, pady=4, sticky="w")

        tk.Label(block, text=item, width=18, anchor="w", bg="#ecf0f1").grid(row=0, column=0)
        tk.Label(block, text=f"₹{price}", width=6, bg="#ecf0f1").grid(row=0, column=1)
        tk.Entry(block, textvariable=qty_var, width=4).grid(row=0, column=2)
        tk.Button(block, text="Add", width=6, bg="#27ae60", fg="white",
                  command=lambda i=item, q=qty_var: add_or_update_item(i, q)).grid(row=0, column=3)

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

# ---------------- ITEMS (LEFT) ----------------
frame_items = tk.LabelFrame(root, text="Items", bg="#ecf0f1")
frame_items.place(x=10, y=60, width=800, height=560)

search_var = tk.StringVar()
search_var.trace("w", search_items)

tk.Entry(frame_items, textvariable=search_var).pack(fill="x", padx=6, pady=4)

canvas_items = tk.Canvas(frame_items, bg="#ecf0f1")
scroll_items = tk.Scrollbar(frame_items, command=canvas_items.yview)
canvas_items.configure(yscrollcommand=scroll_items.set)

scroll_items.pack(side="right", fill="y")
canvas_items.pack(side="left", fill="both", expand=True)

frame_items_list = tk.Frame(canvas_items, bg="#ecf0f1")
canvas_items.create_window((0, 0), window=frame_items_list, anchor="nw")

frame_items_list.bind("<Configure>",
    lambda e: canvas_items.configure(scrollregion=canvas_items.bbox("all")))

# ---------------- CART (RIGHT SIDE) ----------------
frame_cart = tk.LabelFrame(root, text="Cart", bg="white")
frame_cart.place(x=820, y=60, width=420, height=560)

txt_cart = tk.Text(frame_cart, height=24, state="disabled")
txt_cart.pack(fill="both", expand=True, padx=5)

lbl_total = tk.Label(root, text="Subtotal: ₹0 | Discount: 0% | Net Total: ₹0",
                     font=("Arial", 13), bg="#f4f6f7")
lbl_total.place(x=820, y=630)

tk.Button(root, text="Save Bill", width=12, height=2,
          bg="#2980b9", fg="white", command=save_bill)\
    .place(x=1080, y=625)

draw_items()
root.mainloop()


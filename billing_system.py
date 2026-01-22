import tkinter as tk
from tkinter import messagebox
import pandas as pd
from datetime import datetime
import os

# ---------------- LOAD DATA ----------------
PRICE_FILE = "prices.xlsx"

try:
    df_prices = pd.read_excel(PRICE_FILE)
except Exception as e:
    messagebox.showerror("Error", f"Cannot read prices.xlsx\n{e}")
    exit()

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Snack Hotel Billing System")
root.geometry("1000x600")
root.config(bg="#f4f6f7")

# ---------------- DATA ----------------
cart = {}  # {item: qty}
filtered_df = df_prices.copy()
qty_vars = {}  # store StringVar for each item to reset later

# ---------------- FUNCTIONS ----------------
def search_items(*args):
    global filtered_df
    q = search_var.get().lower()
    if q == "":
        filtered_df = df_prices.copy()
    else:
        filtered_df = df_prices[df_prices["Item"].str.lower().str.startswith(q)]
    draw_items()

def add_or_update_item(item, qty_var):
    try:
        qty = int(qty_var.get())
        if qty < 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Quantity must be 0 or a positive number")
        return

    if qty == 0:
        cart.pop(item, None)
    else:
        cart[item] = qty
    refresh_cart()

    # Clear search box and reset filtered items
    search_var.set("")
    filtered_df[:] = df_prices[:]
    draw_items()

def refresh_cart():
    txt_cart.config(state="normal")
    txt_cart.delete(1.0, tk.END)
    subtotal = 0

    for item, qty in cart.items():
        price = df_prices.loc[df_prices["Item"] == item, "Price"].values[0]
        amount = price * qty
        txt_cart.insert(tk.END, f"{item}  ₹{price} x {qty}  =  ₹{amount}\n")
        subtotal += amount

    try:
        discount = float(entry_discount.get())
    except:
        discount = 0

    net_total = subtotal - (subtotal * discount / 100)
    lbl_total.config(text=f"Subtotal: ₹{subtotal} | Discount: {discount}% | Net Total: ₹{net_total}")
    txt_cart.config(state="disabled")

def save_bill():
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return

    table_no = entry_table.get()
    mobile = entry_mobile.get()
    try:
        discount = float(entry_discount.get())
    except:
        discount = 0

    now = datetime.now()
    year_str = now.strftime("%Y")
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H-%M-%S")

    # Folder: bills/YYYY/DD-MM-YYYY/
    folder_path = os.path.join("bills", year_str, date_str)
    os.makedirs(folder_path, exist_ok=True)

    # Filename: HH-MM-SS_T-TableNumber_MobileNumber.txt
    filename = os.path.join(folder_path, f"{time_str}_T-{table_no}_{mobile}.txt")

    subtotal = 0
    with open(filename, "w") as f:
        f.write("Kanhaiyya Snack Center\n")
        f.write("-----------------------\n")
        f.write(f"Date: {now.strftime('%d-%m-%Y %H:%M:%S')}\n")
        f.write(f"Table: {table_no}\n")
        f.write(f"Mobile: {mobile}\n\n")

        for item, qty in cart.items():
            price = df_prices.loc[df_prices["Item"] == item, "Price"].values[0]
            amount = price * qty
            f.write(f"{item}  ₹{price} x {qty}  =  ₹{amount}\n")
            subtotal += amount

        net_total = subtotal - (subtotal * discount / 100)
        f.write("\n-----------------------\n")
        f.write(f"Subtotal: ₹{subtotal}\n")
        f.write(f"Discount: {discount}%\n")
        f.write(f"Net Total: ₹{net_total}\n")
        f.write("\nThank You! Visit Again\n")

    messagebox.showinfo("Saved", f"Bill saved:\n{filename}")

    # Clear cart and reset quantities
    cart.clear()
    for var in qty_vars.values():
        var.set("0")
    refresh_cart()

def draw_items():
    for w in frame_items_list.winfo_children():
        w.destroy()

    for i, row in filtered_df.iterrows():
        item = row["Item"]
        price = row["Price"]

        if item in qty_vars:
            qty_var = qty_vars[item]
        else:
            qty_var = tk.StringVar(value="0")
            qty_vars[item] = qty_var

        tk.Label(frame_items_list, text=item, width=20, anchor="w", bg="#ecf0f1")\
            .grid(row=i, column=0, padx=5, pady=2)

        tk.Label(frame_items_list, text=f"₹{price}", width=8, bg="#ecf0f1")\
            .grid(row=i, column=1)

        tk.Entry(frame_items_list, textvariable=qty_var, width=5)\
            .grid(row=i, column=2)

        tk.Button(
            frame_items_list,
            text="Add / Update",
            bg="#27ae60",
            fg="white",
            command=lambda it=item, q=qty_var: add_or_update_item(it, q)
        ).grid(row=i, column=3, padx=5)

# ---------------- UI ----------------

frame_info = tk.Frame(root, bg="#ffffff", pady=10)
frame_info.pack(fill="x")

tk.Label(frame_info, text="Table No:", bg="white").pack(side="left", padx=5)
entry_table = tk.Entry(frame_info, width=5)
entry_table.pack(side="left")

tk.Label(frame_info, text="Mobile:", bg="white").pack(side="left", padx=10)
entry_mobile = tk.Entry(frame_info, width=12)
entry_mobile.pack(side="left")

tk.Label(frame_info, text="Discount %:", bg="white").pack(side="left", padx=10)
entry_discount = tk.Entry(frame_info, width=5)
entry_discount.insert(0, "0")
entry_discount.pack(side="left")

# Items Section with scrollbar
frame_items = tk.LabelFrame(root, text="Items", bg="#ecf0f1", padx=10, pady=10)
frame_items.place(x=10, y=70, width=520, height=520)

search_var = tk.StringVar()
search_var.trace("w", search_items)

tk.Label(frame_items, text="Search Item:", bg="#ecf0f1").pack(anchor="w")
tk.Entry(frame_items, textvariable=search_var).pack(fill="x", pady=5)

canvas_items = tk.Canvas(frame_items, bg="#ecf0f1")
frame_items_list = tk.Frame(canvas_items, bg="#ecf0f1")
scrollbar_items = tk.Scrollbar(frame_items, orient="vertical", command=canvas_items.yview)
canvas_items.configure(yscrollcommand=scrollbar_items.set)

scrollbar_items.pack(side="right", fill="y")
canvas_items.pack(side="left", fill="both", expand=True)
canvas_items.create_window((0,0), window=frame_items_list, anchor="nw")

def configure_items_scroll(event):
    canvas_items.configure(scrollregion=canvas_items.bbox("all"))
frame_items_list.bind("<Configure>", configure_items_scroll)

# Cart Section with scrollbar
frame_cart = tk.LabelFrame(root, text="Cart", bg="white", padx=10, pady=10)
frame_cart.place(x=550, y=70, width=430, height=420)

canvas_cart = tk.Canvas(frame_cart, bg="white")
frame_cart_inner = tk.Frame(canvas_cart, bg="white")
scrollbar_cart = tk.Scrollbar(frame_cart, orient="vertical", command=canvas_cart.yview)
canvas_cart.configure(yscrollcommand=scrollbar_cart.set)

scrollbar_cart.pack(side="right", fill="y")
canvas_cart.pack(side="left", fill="both", expand=True)
canvas_cart.create_window((0,0), window=frame_cart_inner, anchor="nw")

txt_cart = tk.Text(frame_cart_inner, height=18, width=45, state="disabled")
txt_cart.pack()

def configure_cart_scroll(event):
    canvas_cart.configure(scrollregion=canvas_cart.bbox("all"))
frame_cart_inner.bind("<Configure>", configure_cart_scroll)

# Final payable amount below cart
lbl_total = tk.Label(root, text="Subtotal: ₹0 | Discount: 0% | Net Total: ₹0",
                     font=("Arial", 14), bg="#f4f6f7")
lbl_total.place(x=550, y=500)

tk.Button(root, text="Save Bill", bg="#2980b9", fg="white",
          command=save_bill, width=12, height=2)\
    .place(x=750, y=530)

draw_items()
root.mainloop()


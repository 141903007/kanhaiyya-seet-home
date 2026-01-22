import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pandas as pd
from datetime import datetime
import os

# Load prices
price_file = "prices.xlsx"
df_prices = pd.read_excel(price_file)

# Main Window
root = tk.Tk()
root.title("Snack Hotel Billing Software")
root.geometry("900x600")
root.config(bg="#f8f8f8")

# ------------------ FUNCTIONALITY ------------------

cart = []

def refresh_cart_display():
    txt_cart.delete(1.0, tk.END)
    total = 0
    for item, qty in cart:
        price = df_prices.loc[df_prices["Item"]==item, "Price"].values[0]
        txt_cart.insert(tk.END, f"{item} x {qty} = {price*qty}\n")
        total += price * qty

    lbl_total.config(text=f"Total: ₹{total}")

def add_to_cart(item):
    qty = simple_qty.get()
    try:
        qty = int(qty)
        if qty <= 0:
            raise ValueError
    except:
        messagebox.showerror("Invalid Qty", "Enter a valid quantity!")
        return

    cart.append((item, qty))
    refresh_cart_display()

def save_bill():
    if not cart:
        messagebox.showerror("Empty Cart", "Add items first!")
        return

    table_no = entry_table.get().strip()
    mobile_no = entry_mobile.get().strip()
    discount = 0

    try:
        discount = float(entry_discount.get())
    except:
        messagebox.showerror("Invalid Discount", "Enter valid discount!")
        return

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    filename = f"Bill_{table_no}_{now.replace(':','-').replace(' ','_')}.txt"
    with open(filename, "w") as f:
        f.write("SNACK HOTEL BILL\n")
        f.write(f"Date/Time: {now}\nTable: {table_no}\nMobile: {mobile_no}\n\n")
        f.write("Items:\n")

        total = 0
        for item, qty in cart:
            price = df_prices.loc[df_prices["Item"]==item, "Price"].values[0]
            f.write(f"{item} x {qty} = {price*qty}\n")
            total += price*qty

        f.write(f"\nSubtotal: ₹{total}\n")
        f.write(f"Discount: {discount}%\n")
        net = total - (total * discount / 100)
        f.write(f"Net Total: ₹{net}\n\n")
        f.write("--- THANK YOU ---")

    messagebox.showinfo("Saved", f"Bill saved as:\n{filename}")

def print_bill():
    save_bill()
    messagebox.showinfo("Print", "Send file to printer manually")

# ------------------ UI ------------------

# Info Frame
frame_info = tk.Frame(root, bg="#fff", padx=10, pady=10)
frame_info.place(x=10, y=10)

tk.Label(frame_info, text="Table No:", bg="#fff").grid(row=0, column=0)
entry_table = tk.Entry(frame_info)
entry_table.grid(row=0, column=1)

tk.Label(frame_info, text="Mobile No:", bg="#fff").grid(row=1, column=0)
entry_mobile = tk.Entry(frame_info)
entry_mobile.grid(row=1, column=1)

tk.Label(frame_info, text="Discount %:", bg="#fff").grid(row=2, column=0)
entry_discount = tk.Entry(frame_info)
entry_discount.insert(0, "0")
entry_discount.grid(row=2, column=1)

# Items Frame
frame_items = tk.LabelFrame(root, text="Items", bg="#e8e8e8", padx=10, pady=10)
frame_items.place(x=10, y=130, width=400, height=450)

row = 0
simple_qty = tk.StringVar(value="1")

for idx, row_data in df_prices.iterrows():
    item = row_data["Item"]
    img_path = row_data["ImagePath"]

    try:
        pil_img = Image.open(img_path).resize((50,50))
        photo = ImageTk.PhotoImage(pil_img)
    except:
        photo = None

    btn = tk.Button(frame_items, text=item, image=photo, compound="left",
                    command=lambda item=item: add_to_cart(item))
    btn.image = photo
    btn.grid(row=row, column=0, sticky="w", pady=5)

    tk.Label(frame_items, text=f"₹{row_data['Price']}", bg="#e8e8e8").grid(row=row, column=1)
    row+=1

tk.Label(frame_items, text="Qty:", bg="#e8e8e8").grid(row=row, column=0)
tk.Entry(frame_items, textvariable=simple_qty, width=5).grid(row=row, column=1)

# Cart Display
frame_cart = tk.LabelFrame(root, text="Cart", bg="#fff", padx=10, pady=10)
frame_cart.place(x=420, y=130, width=450, height=350)

txt_cart = tk.Text(frame_cart, height=15, width=40)
txt_cart.pack()

lbl_total = tk.Label(root, text="Total: ₹0", font=("Arial", 14), bg="#f8f8f8")
lbl_total.place(x=420, y=490)

# Buttons
tk.Button(root, text="Save Bill", bg="#4caf50", fg="#fff", command=save_bill).place(x=420, y=530, width=100, height=40)
tk.Button(root, text="Print Bill", bg="#2196f3", fg="#fff", command=print_bill).place(x=550, y=530, width=100, height=40)
tk.Button(root, text="Clear Cart", bg="#f44336", fg="#fff", command=lambda: (cart.clear(), refresh_cart_display())).place(x=680, y=530, width=100, height=40)

root.mainloop()


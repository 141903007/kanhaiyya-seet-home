let itemsData = {};
let currentCart = {};

window.onload = function () {
    loadItems();
};

function loadItems() {
    fetch("/items")
        .then(r => r.json())
        .then(data => {
            let html = "";
            data.forEach(item => {
                itemsData[item.id] = item;   // store item details
                html += `
                    <div class="item-box" onclick="addToCart(${item.id})">
                        ${item.name} - ₹${item.price}
                    </div>`;
            });
            document.getElementById("items").innerHTML = html;
        });
}

function addToCart(itemId) {
    let table = document.getElementById("table").value;
    if (!table) return alert("Enter table number");

    let qty = prompt("Enter Qty (0.5, 1, 1.5)");
    if (!qty) return;

    fetch("/cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item: itemId, table: table, qty: qty })
    })
    .then(r => r.json())
    .then(cart => {
        currentCart = cart;
        renderCart();
    });
}

function renderCart() {
    let html = "";
    let total = 0;

    for (let id in currentCart) {
        let item = itemsData[id];
        let qty = currentCart[id];
        let line = item.price * qty;
        total += line;

        html += `
            <div class="cart-row">
                ${item.name} x 
                <input type="number" step="0.5" value="${qty}" onchange="updateQty(${id}, this.value)">
                = ₹${line}
                <button onclick="removeItem(${id})">❌</button>
            </div>`;
    }

    document.getElementById("cart").innerHTML = html;
    document.getElementById("total").innerText = total.toFixed(2);
}

function updateQty(itemId, qty) {
    let table = document.getElementById("table").value;
    fetch("/cart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item: itemId, table: table, qty: qty })
    })
    .then(r => r.json())
    .then(cart => {
        currentCart = cart;
        renderCart();
    });
}

function removeItem(itemId) {
    updateQty(itemId, 0);
}

function generateBill() {
    let table = document.getElementById("table").value;
    let mobile = document.getElementById("mobile").value;

    fetch("/generate_bill", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ table: table, mobile: mobile })
    })
    .then(r => r.text())
    .then(billNo => {
        alert("Bill Generated: " + billNo);
        currentCart = {};
        renderCart();
    });
}

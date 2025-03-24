document.addEventListener("DOMContentLoaded", async function () {
    let token = localStorage.getItem("access_token");

    if (!token) {
        alert("You must be logged in to update products.");
        window.location.href = "/loginPage";
        return;
    }

        // Logout functionality
    document.getElementById("logout-btn").addEventListener("click", function () {
        localStorage.removeItem("access_token");
        window.location.href = "/loginPage";
    });
    
    let response = await fetch("/products/user", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    let products = await response.json();
    let container = document.getElementById("user-products-container");
    container.innerHTML = "";

    products.forEach(product => {
        let div = document.createElement("div");
        div.classList.add("product-card");
        div.innerHTML = `
            <h3>${product.name}</h3>
            <p><strong>Price:</strong> $${product.price}</p>
            <p>${product.description}</p>
            <button onclick="selectProduct(${product.id}, '${product.name}', ${product.price}, '${product.description}')">Edit</button>
        `;
        container.appendChild(div);
    });
});

function selectProduct(id, name, price, description) {
    document.getElementById("product-id").value = id;
    document.getElementById("update-name").value = name;
    document.getElementById("update-price").value = price;
    document.getElementById("update-description").value = description;
}

document.getElementById("update-product-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    let token = localStorage.getItem("access_token");
    if (!token) {
        alert("You must be logged in to update products.");
        return;
    }


    let productId = document.getElementById("product-id").value;
    let name = document.getElementById("update-name").value;
    let price = document.getElementById("update-price").value;
    let description = document.getElementById("update-description").value;

    let updateData = {};
    if (name) updateData.name = name;
    if (price) updateData.price = price;
    if (description) updateData.description = description;

    let method = Object.keys(updateData).length === 3 ? "PUT" : "PATCH"; // Use PUT if all fields are filled

    let response = await fetch(`/products/${productId}`, {
        method: method,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
    });

    let result = await response.json();

    if (response.ok) {
        alert("Product updated successfully!");
        window.location.reload();
    } else {
        alert("Error updating product: " + result.error);
    }
});

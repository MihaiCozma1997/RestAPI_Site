document.addEventListener("DOMContentLoaded", function () {
    let token = localStorage.getItem("access_token");

    // Check if user is logged in (token exists)
    if (!token) {
        alert("You must be logged in to add a product.");
        window.location.href = "/loginPage"; // Redirect to login
        return;
    }

    // Logout functionality
    document.getElementById("logout-btn").addEventListener("click", function () {
        localStorage.removeItem("access_token");
        window.location.href = "/loginPage";
    });

    // Handle product submission
    document.getElementById("product-form").addEventListener("submit", async function (event) {
        event.preventDefault();

        let name = document.getElementById("name").value;
        let price = document.getElementById("price").value;
        let description = document.getElementById("description").value;

        let productData = {
            name: name,
            price: parseFloat(price), // Ensure it's a number
            description: description
        };

        try {
            let response = await fetch("/products", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token  // ✅ Send token in the header
                },
                body: JSON.stringify(productData)
            });

            let result = await response.json();

            if (response.ok) {
                alert("Product added successfully!");
                window.location.href = "/"; // Redirect to home page
            } else {
                alert("Failed to add product: " + result.error);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred.");
        }
    });
});

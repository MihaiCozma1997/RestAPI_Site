// Declare globally so it's accessible in all functions
let selectedProductId = null;

document.addEventListener("DOMContentLoaded", function() {
    fetchProducts();
    checkAuthStatus(); // Check if the user is logged in

    // Check if logout button exists before adding event listener
    let logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", logoutUser);
    }

    // Check if close button exists before adding event listener
    let closeBtn = document.querySelector(".close-btn");
    if (closeBtn) {
        closeBtn.addEventListener("click", function() {
            document.getElementById("review-popup").style.display = "none";
        });
    }

    // Check if submit review button exists before adding event listener
    let submitReviewBtn = document.getElementById("submit-review");
    if (submitReviewBtn) {
        submitReviewBtn.addEventListener("click", submitReview);
    }

    // Check if login form exists before adding event listener
    let loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function(event) {
            event.preventDefault();  // Prevent normal form submission

            let username = document.getElementById("username").value;
            let password = document.getElementById("password").value;

            let loginData = { username: username, password: password };

            try {
                let response = await fetch("/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(loginData)
                });

                let result = await response.json();

                if (response.ok) {
                    alert("Login successful!");
                    console.log("Token:", result.access_token);
                    localStorage.setItem("access_token", result.access_token); // Store token for future use
                    window.location.href = "http://127.0.0.1:5000/"; // Redirect to home page
                } else {
                    alert("Login failed: " + result.error);
                }
            } catch (error) {
                console.error("Error:", error);
            }
        });
    }
    document.querySelectorAll('#star-rating .star').forEach(star => {
    star.addEventListener('click', function() {
        let ratingValue = this.getAttribute('data-value');
        document.getElementById('review-rating').value = ratingValue;

        // Reset all stars
        document.querySelectorAll('#star-rating .star').forEach(s => s.classList.remove('selected'));

        // Highlight selected stars
        for (let i = 0; i < ratingValue; i++) {
            document.querySelectorAll('#star-rating .star')[i].classList.add('selected');
        }
    });
});
});

function fetchProducts() {
    fetch("/products")
        .then(response => response.json())
        .then(data => {
            let container = document.getElementById("products-container");
            let token = localStorage.getItem("access_token");  // Check if user is logged in
            container.innerHTML = "";

            data.forEach(product => {
                let div = document.createElement("div");
                div.classList.add("product-card");

                // --- Calculate Stars ---
                let fullStars = Math.floor(product.average_rating);
                let halfStar = product.average_rating % 1 >= 0.5;
                let starsHTML = '';

                for (let i = 0; i < fullStars; i++) {
                    starsHTML += '<i class="fa-solid fa-star" style="color: gold;  border-radius: 3px;"></i>';
                }
                if (halfStar) {
                    starsHTML += '<i class="fa-solid fa-star-half-stroke" style="color: gold;  border-radius: 3px;"></i>';
                }
                for (let i = fullStars + (halfStar ? 1 : 0); i < 5; i++) {
                    starsHTML += '<i class="fa-regular fa-star" style="color: black; border: border-radius: 3px;"></i>';
                }

                // --- Build Product HTML ---
                let productHTML = `
                    <h3>${product.name}</h3>
                    <p><strong>Price:</strong> $${product.price}</p>
                    <p>${product.description}</p>
                    <div class="rating-display">
                        ${starsHTML}
                        <span class="clickable" onclick="showReviewsPopup(${product.id})">
                        (${product.average_rating.toFixed(2)} from ${product.review_count} reviews)</span>
                    </div>
                `;

                // Show Rate Product button only if logged in
                if (token) {
                    productHTML += `<button class="review-button" onclick="showReviewPopup(${product.id})">Rate Product</button>`;
                }

                div.innerHTML = productHTML;
                container.appendChild(div);
            });

            // Add event listeners to "View Reviews" buttons after all are rendered
            document.querySelectorAll('.view-reviews-btn').forEach(button => {
                button.addEventListener('click', function () {
                    const productId = this.getAttribute('data-product-id');
                    showAllReviewsPopup(productId);  // Define this function to show reviews popup
                });
            });
        })
        .catch(error => console.error("Error fetching products:", error));
}


// Function to show the review popup
function showReviewPopup(productId) {
    selectedProductId = productId;
    document.getElementById("review-popup").style.display = "block";
}

// Function to check if user is logged in
function checkAuthStatus() {
    let token = localStorage.getItem("access_token"); // Get JWT from localStorage

    let addProductBtn = document.getElementById("add-product-btn");
    let logoutBtn = document.getElementById("logout-btn");
    let loginBtn = document.getElementById("login-btn");
    let updateProductBtn = document.getElementById("update-product-btn");

    if (token) {
        if (addProductBtn) addProductBtn.style.display = "inline-block";
        if (logoutBtn) logoutBtn.style.display = "inline-block";
        if (loginBtn) loginBtn.style.display = "none";
        if (updateProductBtn) updateProductBtn.style.display = "inline-block";
    } else {
        if (addProductBtn) addProductBtn.style.display = "none";
        if (logoutBtn) logoutBtn.style.display = "none";
        if (updateProductBtn) updateProductBtn.style.display = "none";
        if (loginBtn) loginBtn.style.display = "inline-block";
    }
}

// Function to log out user
function logoutUser() {
    localStorage.removeItem("access_token"); // Remove token
    checkAuthStatus(); // Refresh UI
    location.reload(); // Reload page
}

// Function to submit a review
function submitReview() {
    let rating = document.getElementById("review-rating");
    let comment = document.getElementById("review-comment");
    const stars = document.querySelectorAll('.star-rating-inner i');

    if (!selectedProductId || !rating.value) {
        alert("Please select a product and enter a rating.");
        return;
    }

    let reviewData = {
        rating: parseInt(rating.value),
        comment: comment.value || "NA"
    };

    try {
    let token = localStorage.getItem("access_token"); // Get JWT Token
    if (token) {
        fetch(`/products/${selectedProductId}/reviews`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}` // Pass JWT Token for authentication
            },
            body: JSON.stringify(reviewData)
        })
        .then(response => response.json())
        .then(result => {
            if (result.message === "Review added") {
                alert("Review added successfully!");
                document.getElementById("review-popup").style.display = "none"; // Close popup
                location.reload(); // Reload page
            } else {
                alert("Failed to add review: " + result.error);
            }
            // Reset form and stars
            rating.value = '';
            comment.value = '';
            stars.forEach(star => star.classList.remove('selected', 'hovered'));
        })
        .catch(error => {
            console.error("Error:", error);
        });
    } else {
        alert("User is not logged in.");
    }
} catch (error) {
    console.error("Error:", error);
}}

function showReviewsPopup(productId) {
    document.getElementById("reviews-popup").style.display = "block"; // Show popup

    fetch(`/products/${productId}/reviews`)
        .then(response => response.json())
        .then(data => {
            const reviewsList = document.getElementById("reviews-list");
            reviewsList.innerHTML = ""; // Clear previous reviews

            if (Array.isArray(data) && data.length > 0) {
                data.forEach(review => {
                    const reviewItem = document.createElement("div");
                    reviewItem.classList.add("review-item");
                    reviewItem.innerHTML = `
                        <p><strong>User:</strong> ${review.user_name || "Anonymous"}</p>
                        <p><strong>Rating:</strong> ${review.rating} ⭐</p>
                        <p>${review.comment}</p>
                    `;
                    reviewsList.appendChild(reviewItem);
                });
            } else {
                reviewsList.innerHTML = "<p>No reviews found for this product.</p>";
            }
        })
        .catch(error => {
            console.error("Error fetching reviews:", error);
            document.getElementById("reviews-list").innerHTML = "<p>Error loading reviews.</p>";
        });
}

function closeReviewsPopup() {
    document.getElementById("reviews-popup").style.display = "none";
}

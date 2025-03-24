document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("register-form").addEventListener("submit", async function(event) {
        event.preventDefault();  // Prevent normal form submission

        // Get values from input fields
        let username = document.getElementById("username").value;
        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;

        // Create JSON data
        let registerData = {
            username: username,
            email: email,
            password: password
        };

        try {
            // Send POST request with JSON body
            let response = await fetch("/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(registerData)
            });

            let result = await response.json(); // Parse JSON response

            if (response.ok) {
                alert("Registration successful! Redirecting to login...");
                window.location.href = "http://127.0.0.1:5000/loginPage"; // Redirect to login page
            } else {
                alert("Registration failed: " + result.error);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    });
});

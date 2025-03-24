import pytest
from app import create_app, db
from flask_jwt_extended import decode_token


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def user_register_login(client):
    client.post("/auth/register", json={
        "username": "Mihai2",
        "email": "Mihai23@yahoo.com",
        "password": "parola123"
    })
    response = client.post("/auth/login", json={
        "username": "Mihai2",
        "password": "parola123"
    })
    return response.get_json()["access_token"]


def post_products(client, prod_nr: int, auth_token):
    token = auth_token
    header = {"Authorization": f"Bearer {token}"}  # Attach JWT token
    for prod in range(0, prod_nr):
        client.post("/products", json={
            "name": f"Test Product {prod}",
            "description": f"product {prod} for testing",
            "price": prod*2+1
        }, headers=header)


def post_review_helper(client, auth_token, json_body, prod_nr):
    token = auth_token
    header = {"Authorization": f"Bearer {token}"}  # Attach JWT token
    response = client.post(f"/products/{prod_nr}/reviews", json=json_body, headers=header)
    return response


# --------------- Post method tests ------------------------------------------------------------------------------------


def test_post_product(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": 5
    }, headers=header)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Product added"


def test_post_product_no_description(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "name": "Test Product",
        "price": 10
    }, headers=header)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Product added"


def test_post_product_no_name(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "description": "A product for testing",
        "price": 10
    }, headers=header)
    assert response.status_code == 400
    assert "name" in response.get_json()["error"]


def test_post_product_no_price(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "name": "Test Product",
        "description": "A product for testing"
    }, headers=header)
    assert response.status_code == 400
    assert "price" in response.get_json()["error"]


def test_post_product_str_price(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": "Ten"
    }, headers=header)
    assert response.status_code == 400


def test_post_product_extra_field(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": "10",
        "extra_fields": "oops"
    }, headers=header)
    assert response.status_code == 400


def test_post_product_negative_price(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "name": "Test Product",
        "description": "A product for testing",
        "price": -10
    }, headers=header)
    assert response.status_code == 400


def test_post_product_empty_strings(client, user_register_login):
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    response = client.post("/products", json={
        "name": "",
        "description": "a product",
        "price": -10
    }, headers=header)
    assert response.status_code == 400


# --------------- Get method tests -------------------------------------------------------------------------------------


def test_get_products(client, user_register_login):
    # First, add 2 products
    post_products(client, 2, user_register_login)
    # Now, get all products
    response = client.get("/products")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Product 0"
    assert data[1]["name"] == "Test Product 1"


def test_get_single_product(client, user_register_login):
    # Add a product first
    post_products(client, 1, user_register_login)
    # Retrieve the product by ID
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Test Product 0"


def test_get_product_invalid_id(client, user_register_login):
    # Add a product first
    post_products(client, 1, user_register_login)
    response = client.get("/products/10")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product 10 not found!"


def test_get_product_str_id(client):
    response = client.get('/products/"invalid_id"')  # Invalid ID format
    assert response.status_code == 404


# --------------- Post Review method tests -----------------------------------------------------------------------------


def test_post_review(client, user_register_login):

    post_products(client, 1, user_register_login)
    review_dict = {
        "rating": 4,
        "comment": "A good product"
    }
    response = post_review_helper(client, user_register_login, review_dict, prod_nr=1)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Review added"


def test_post_review_same_user(client, user_register_login):

    post_products(client, 1, user_register_login)
    review_dict = {
        "rating": 4,
        "comment": "A good product"
    }
    post_review_helper(client, user_register_login, review_dict, prod_nr=1)
    response = post_review_helper(client, user_register_login, review_dict, prod_nr=1)
    assert response.status_code == 400
    assert response.get_json()["error"] == "You have already reviewed this product."


def test_post_review_invalid_rating_6(client, user_register_login):
    post_products(client, 1, user_register_login)
    review_dict = {
        "rating": 6,
        "comment": "A good product"
    }
    response = post_review_helper(client, user_register_login, review_dict, prod_nr=1)

    assert response.status_code == 400
    assert response.get_json()["error"] == "{'rating': ['Rating should be between 1 and 5']}"


def test_post_review_invalid_rating_0(client, user_register_login):
    post_products(client, 1, user_register_login)
    review_dict = {
        "rating": 0,
        "comment": "A good product"
    }
    response = post_review_helper(client, user_register_login, review_dict, prod_nr=1)
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'rating': ['Rating should be between 1 and 5']}"


def test_post_review_invalid_id(client, user_register_login):
    post_products(client, 1, user_register_login)

    review_dict = {
        "rating": 5,
        "comment": "A good product"
    }
    response = post_review_helper(client, user_register_login, review_dict, prod_nr=2)
    assert response.status_code == 404


def test_post_review_str_id(client, user_register_login):
    post_products(client, 1, user_register_login)

    review_dict = {
        "rating": 5,
        "comment": "A good product"
    }
    response = post_review_helper(client, user_register_login, review_dict, prod_nr='two')
    assert response.status_code == 404


def test_post_review_only_rating(client, user_register_login):
    post_products(client, 1, user_register_login)

    review_dict = {
        "rating": 5
    }
    response = post_review_helper(client, user_register_login, review_dict, prod_nr=1)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Review added"


def test_post_review_only_comment(client, user_register_login):
    post_products(client, 1, user_register_login)

    review_dict = {
        "comment": "a good product"
    }
    response = post_review_helper(client, user_register_login, review_dict, prod_nr=1)
    assert response.status_code == 400
    assert "rating" in response.get_json()["error"]


# --------------- Get Review method tests -----------------------------------------------------------------------------


def test_get_review(client, user_register_login):
    post_products(client, 1, user_register_login)

    review_dict = {
        "rating": 5,
        "comment": "A good product"
    }
    post_review_helper(client, user_register_login, review_dict, prod_nr=1)
    response = client.get("/products/1/reviews")
    assert response.status_code == 200
    assert response.get_json()[0]["rating"] == 5
    assert response.get_json()[0]["comment"] == "A good product"


def test_get_review_invalid_id(client, user_register_login):
    post_products(client, 1, user_register_login)
    client.post("/products/1/reviews", json=({
        "rating": 5,
        "comment": "A good product"
    }))
    response = client.get("/products/2/reviews")
    assert response.status_code == 404


def test_get_review_no_review(client, user_register_login):
    post_products(client, 1, user_register_login)
    response = client.get("/products/1/reviews")
    assert response.status_code == 404


# --------------- Patch method tests -----------------------------------------------------------------------------------


def test_patch_product_price(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/1", json={
        "price": 5
    }, headers=header)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Product partially updated!"
    updated_product = client.get("/products/1").get_json()
    assert updated_product["price"] == 5


def test_patch_product_name(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/1", json={
        "name": "New product"
    }, headers=header)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Product partially updated!"
    updated_product = client.get("/products/1").get_json()
    assert updated_product["name"] == "New product"


def test_patch_product_description(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/1", json={
        "description": "New description"
    }, headers=header)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Product partially updated!"
    updated_product = client.get("/products/1").get_json()
    assert updated_product["description"] == "New description"


def test_patch_product_all(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/1", json={
        "name": "New Product",
        "description": "New description",
        "price": 5
    }, headers=header)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Product partially updated!"
    updated_product = client.get("/products/1").get_json()
    assert updated_product["name"] == "New Product"
    assert updated_product["description"] == "New description"
    assert updated_product["price"] == 5


def test_patch_product_invalid_id(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/2", json={
        "name": "New Product"
    }, headers=header)
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found!"


def test_patch_product_str_id(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/two", json={
        "name": "New Product"
    }, headers=header)
    assert response.status_code == 404


def test_patch_product_invalid_field(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/1", json={
        "new_price": "New Product"
    }, headers=header)
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'new_price': ['Unknown field.']}"


def test_patch_product_invalid_value(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/1", json={
        "price": "two"
    }, headers=header)
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'price': ['Not a valid number.']}"


def test_patch_product_empty(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.patch("/products/1", json={

    }, headers=header)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Product partially updated!"
    updated_product = client.get("/products/1").get_json()
    assert updated_product["name"] == "Test Product 0"
    assert updated_product["description"] == "product 0 for testing"
    assert updated_product["price"] == 1


# --------------- Put method tests -------------------------------------------------------------------------------------


def test_put_product(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.put("/products/1", json={
        "name": "put Product",
        "description": "New description",
        "price": 5
    }, headers=header)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Product fully updated!"
    # Verify the update
    updated_product = client.get("/products/1").get_json()
    assert updated_product["price"] == 5


def test_put_product_1_field(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.put("/products/1", json={
        "name": "put Product"
    }, headers=header)
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'price': ['Missing data for required field.']}"


def test_put_product_invalid_id(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.put("/products/2", json={
        "name": "put Product",
        "description": "New description",
        "price": 5
    }, headers=header)
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found!"


def test_put_product_invalid_value(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Update the product with Patch
    response = client.put("/products/1", json={
        "name": "put Product",
        "description": "New description",
        "price": "five"
    }, headers=header)
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'price': ['Not a valid number.']}"


# --------------- Delete method tests ----------------------------------------------------------------------------------


def test_delete_product(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Delete the product
    response = client.delete("/products/1", headers=header)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Product 1 deleted successfully"
    # Verify deletion
    get_response = client.get("/products/1")
    assert get_response.status_code == 404


def test_delete_product_invalid_id(client, user_register_login):
    # Add a product
    post_products(client, 1, user_register_login)
    header = {"Authorization": f"Bearer {user_register_login}"}  # Attach JWT token
    # Delete the product
    response = client.delete("/products/2", headers=header)
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


# --------------- Options method tests ---------------------------------------------------------------------------------


def test_options_request(client):
    # Send an OPTIONS request
    response = client.options("/products/1")
    assert response.status_code == 200
    allowed_methods = response.headers["Allow"].split(", ")  # Get the allowed methods
    assert sorted(allowed_methods) == sorted(["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "PUT"])
    response = client.options("/products")
    assert response.status_code == 200
    allowed_methods = response.headers["Allow"].split(", ")  # Get the allowed methods
    assert sorted(allowed_methods) == sorted(["GET", "HEAD", "OPTIONS", "POST"])


def test_options_request_invalid_id(client):
    # Send an OPTIONS request
    response = client.options("/products/10")
    assert response.status_code == 200


# --------------- register method tests --------------------------------------------------------------------------------


def test_register_request(client):
    # send register request
    response = client.post("/auth/register", json={
        "username": "User1",
        "email": "user1@gmail.com",
        "password": "parola122"
    })
    # verify registration
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"


def test_register_request_same_name(client):
    # send register request
    client.post("/auth/register", json={
        "username": "User1",
        "email": "user1@gmail.com",
        "password": "parola122"
    })
    # send register with the same name
    response2 = client.post("/auth/register", json={
        "username": "User1",
        "email": "user2@gmail.com",
        "password": "parola222"
    })
    # verify registration
    assert response2.status_code == 400
    assert response2.get_json()["error"] == "User name already taken"


def test_register_request_same_email(client):
    # send register request
    client.post("/auth/register", json={
        "username": "User1",
        "email": "user1@gmail.com",
        "password": "parola133"
    })
    # send register with the same name
    response2 = client.post("/auth/register", json={
        "username": "User2",
        "email": "user1@gmail.com",
        "password": "parola233"
    })
    # verify registration
    assert response2.status_code == 400
    assert response2.get_json()["error"] == "email already used for another account"


def test_register_request_email_format(client):
    # send register request
    response = client.post("/auth/register", json={
        "username": "User1",
        "email": "newemail.com",
        "password": "parola123"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'email': ['Not a valid email address.']}"


def test_register_request_short_pw(client):
    # send register request
    response = client.post("/auth/register", json={
        "username": "User1",
        "email": "user@yahoo.com",
        "password": "parola1"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'password': ['Password should have at least 8 char']}"


def test_register_request_missing_fields(client):
    # send register request
    response = client.post("/auth/register", json={
        "username": "User1",
        "email": "user@yahoo.com"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'password': ['Missing data for required field.']}"

    # send register request
    response = client.post("/auth/register", json={
        "username": "User1",
        "password": "parola123"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'email': ['Missing data for required field.']}"

    # send register request
    response = client.post("/auth/register", json={
        "email": "user@yahoo.com",
        "password": "parola123"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'username': ['Missing data for required field.']}"


def test_register_request_empty_fields(client):
    # send register request
    response = client.post("/auth/register", json={
        "username": "User1",
        "email": "user@yahoo.com",
        "password": ""
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'password': ['Password should have at least 8 char']}"

    # send register request
    response = client.post("/auth/register", json={
        "username": "User1",
        "email": "",
        "password": "parola122"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'email': ['Not a valid email address.']}"

    # send register request
    response = client.post("/auth/register", json={
        "username": "",
        "email": "user@yahoo.com",
        "password": "parola122"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'username': ['Username must be at least 3 characters long.']}"


def test_register_request_invalid_username(client):
    # send register request
    response = client.post("/auth/register", json={
        "username": "User1_",
        "email": "user@yahoo.com",
        "password": "parola1234"
    })
    # verify registration
    assert response.status_code == 400
    assert response.get_json()["error"] == "{'username': ['Username must only contain letters and numbers.']}"


# --------------- login method tests -----------------------------------------------------------------------------------


def test_login_request(client):
    # send register request
    client.post("/auth/register", json={
        "username": "Mihai2",
        "email": "Mihai23@yahoo.com",
        "password": "parola123"
    })
    response = client.post("/auth/login", json={
        "username": "Mihai2",
        "password": "parola123"
    })
    # verify registration
    assert response.status_code == 200

    # Check if the token is present
    assert "access_token" in response.get_json()

    token = response.get_json()["access_token"]
    decoded_data = decode_token(token)

    assert decoded_data["sub"] == 1  # Assuming user ID is 1


def test_login_request_invalid_user(client):
    # send register request
    client.post("/auth/register", json={
        "username": "Mihai2",
        "email": "Mihai23@yahoo.com",
        "password": "parola123"
    })
    response = client.post("/auth/login", json={
        "username": "Mihai23",
        "password": "parola123"
    })
    # verify registration
    assert response.status_code == 401
    assert response.get_json()["error"] == 'Invalid username or password'


def test_login_request_invalid_pw(client):
    # send register request
    client.post("/auth/register", json={
        "username": "Mihai2",
        "email": "Mihai23@yahoo.com",
        "password": "parola123"
    })
    response = client.post("/auth/login", json={
        "username": "Mihai2",
        "password": "parola12345"
    })
    # verify registration
    assert response.status_code == 401
    assert response.get_json()["error"] == 'Invalid username or password'


@pytest.mark.parametrize("payload", [
    {"username": "testuser"},  # Missing password
    {"password": "testpassword"},  # Missing username
    {}  # Empty request
])
def test_login_missing_fields(client, payload):
    response = client.post('/auth/login', json=payload)
    assert response.status_code == 400  # Validation should fail
    assert "error" in response.get_json()


def test_login_invalid_json(client):
    response = client.post('/auth/login', json="invalid json")
    assert response.status_code == 400
    assert "error" in response.get_json()




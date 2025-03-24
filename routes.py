# routes.py
def register_routes(app):
    from flask import jsonify, request, render_template, send_from_directory
    from flask_jwt_extended import jwt_required, get_jwt_identity
    from models import db, Product, Review, User
    from app import product_schema, review_schema, reviews_schema

    # API routes
    @app.route('/')
    def home():
        return send_from_directory('static', 'index.html')

    @app.route('/updateProduct')
    def update_product():
        return render_template('updateProduct.html')

    @app.route('/addProduct', methods=['GET'])
    def add_product_page():
        return render_template('addProduct.html')

    @app.route('/loginPage', methods=['GET'])
    def login_page():
        return render_template('loginPage.html')

    @app.route('/registerPage', methods=['GET'])
    def register_page():
        return render_template('register.html')

    # Get all products
    @app.route('/products', methods=['GET'])
    def get_products():
        products = Product.query.all()
        product_list = []
        if products:
            try:
                for product in products:
                    reviews = Review.query.filter_by(product_id=product.id).all()
                    if reviews:
                        review_count = len(reviews)
                        average_rating = round(sum([r.rating for r in reviews]) / review_count,
                                               2) if review_count > 0 else 0
                    else:
                        review_count = 0
                        average_rating = 0

                    product_data = {
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "description": product.description,
                        "average_rating": average_rating,
                        "review_count": review_count
                    }

                    product_list.append(product_data)
                return jsonify(product_list), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400  # Return error message if validation fails

        else:
            return jsonify({"error": "No products in database!"}), 404

    # Get product by ID
    @app.route('/products/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        if isinstance(product_id, int):
            product = Product.query.get(product_id)
            if product:
                product_data = product_schema.dump(product)
                return jsonify(product_data), 200
            else:
                return jsonify({"error": f"Product {product_id} not found!"}), 404
        else:
            return jsonify({"error": "Product ID not integer"}), 400

    @app.route("/products/user", methods=["GET"])
    @jwt_required()
    def get_user_products():
        user_id = get_jwt_identity()  # Get logged-in user's ID
        user_products = Product.query.filter_by(user_id=user_id).all()
        if user_products:
            return jsonify([{
                "id": p.id, "name": p.name, "price": p.price, "description": p.description
            } for p in user_products]), 200
        else:
            return jsonify({"error": f"No products posted by user: {user_id}"}), 400

    # Add a new product
    @app.route('/products', methods=['POST'])
    @jwt_required()
    def add_product():
        current_user = get_jwt_identity()  # Get the logged-in user
        data = request.get_json()

        # Use the schema to validate and deserialize input data
        # `load` method will validate and return a Python object
        try:
            product_data = product_schema.load(data)  # Validates and deserializes input
        except Exception as e:
            return jsonify({"error": str(e)}), 400  # Return error message if validation fails

        new_product = Product(
            name=product_data['name'],
            description=product_data.get('description', 'NA'),
            price=product_data['price'],
            user_id=current_user
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added'}), 201

    # Add a review to a product
    @app.route('/products/<int:product_id>/reviews', methods=['POST'])
    @jwt_required()
    def add_review(product_id):
        current_user = get_jwt_identity()  # Get the logged-in user

        # Fetch user from the database
        user = User.query.get(current_user)
        if not user:
            return jsonify({"error": "User not found"}), 404

        Product.query.get_or_404(product_id)
        data = request.get_json()
        existing_review = Review.query.filter_by(product_id=product_id, user_name=user.username).first()
        if existing_review:
            return jsonify({"error": "You have already reviewed this product."}), 400

        # Use the schema to validate and deserialize input data
        # `load` method will validate and return a Python object
        try:
            review_data = review_schema.load(data, partial=("comment",))  # Validates and deserializes input
        except Exception as e:
            return jsonify({"error": str(e)}), 400  # Return error message if validation fails

        new_review = Review(
            rating=review_data['rating'],
            comment=review_data.get('comment', "NA"),
            product_id=product_id,
            user_name=user.username
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({'message': 'Review added'}), 201

    # Get reviews for a product
    @app.route('/products/<int:product_id>/reviews', methods=['GET'])
    def get_reviews(product_id):
        reviews = Review.query.filter_by(product_id=product_id).all()
        reviews_data = reviews_schema.dump(reviews)
        if reviews_data:
            return jsonify(reviews_data), 200
        else:
            return jsonify({"error": "no review found"}), 404

    # PATCH - Partially Update a Product
    @app.route('/products/<int:product_id>', methods=['PATCH'])
    @jwt_required()
    def patch_product(product_id):
        user_id = get_jwt_identity()
        data = request.get_json()
        product = Product.query.get(product_id)
        if product:
            if product.user_id != user_id:
                return jsonify({"error": "Unauthorized to update this product"}), 403
            try:
                product_data = product_schema.load(data, partial=True)
            except Exception as e:
                return jsonify({"error": str(e)}), 400  # Return error message if validation fails

            # Only update fields that are provided
            if 'name' in product_data:
                product.name = product_data['name']
            if 'description' in product_data:
                product.description = product_data['description']
            if 'price' in product_data:
                product.price = product_data['price']

            db.session.commit()
            return jsonify({"message": "Product partially updated!"}), 200
        return jsonify({"error": "Product not found!"}), 404

    @app.route('/products/<int:product_id>', methods=['PUT'])
    @jwt_required()
    def put_product(product_id):
        data = request.get_json()
        product = Product.query.get(product_id)
        try:
            product_data = product_schema.load(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        if product:
            product.name = product_data['name']
            product.description = product_data['description']
            product.price = product_data['price']
            db.session.commit()
            return jsonify({"message": "Product fully updated!"}), 200
        return jsonify({"error": "Product not found!"}), 404

    # OPTIONS - Get Supported Methods
    @app.route('/products', methods=['OPTIONS'])
    def options_products():
        return jsonify({
            "methods": ["GET", "POST"]
        }), 200

    @app.route('/products/<int:product_id>', methods=['OPTIONS'])
    def options_product(product_id):
        return jsonify(200)

    # HEAD - Get Headers Only (No body)
    @app.route('/products/<int:product_id>', methods=['HEAD'])
    def head_product(product_id):
        product = Product.query.get(product_id)
        if product:
            return '', 200  # Empty response body, just headers
        return '', 404  # No content, just headers

    # delete method
    @app.route('/products/<int:product_id>', methods=['DELETE'])
    @jwt_required()
    def delete_product(product_id):
        # Query the product by ID
        product = Product.query.get(product_id)
        if not product:
            # If product not found, return 404
            return jsonify({"error": "Product not found"}), 404

        # Delete the product from the database
        db.session.delete(product)
        db.session.commit()

        # Return success message
        return jsonify({"message": f"Product {product_id} deleted successfully"}), 200



from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from datetime import datetime
from models import User, Product, db, Order, OrderItem, Customer
import random
import string

app = Flask(__name__)

# Config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)

# Initialize db + migrate
db.init_app(app) 
migrate = Migrate(app, db)


# Helper function to generate SKU
def generate_sku():
    """Generate a random 6-character SKU"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ROUTES
@app.route('/')
def index():
    return render_template('signup.html')


# --- USER ROUTES ---
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    new_user = User(name=data['name'], email=data.get('email', ''), pin=data.get('pin', '0000'))
    if 'password' in data:
        new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created', 'user': {'id': new_user.id, 'name': new_user.name}}), 201


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role} for u in users]
    return jsonify(users_list)


@app.route('/oneusers/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role})


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        pin = request.form.get('pin')
        role = request.form.get('role', 'admin')

        if not all([name, email, password, pin]):
            flash('All fields are required!')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('signup'))

        new_user = User(name=name, email=email, pin=pin, role=role)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}'

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([email, password]):
            flash('Email and password are required!')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!')
            return redirect(url_for('order'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))

    return render_template('login.html')


# --- PRODUCT ROUTES ---
@app.route('/order')
def order():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    
    products = Product.query.all()
    return render_template('order.html', name=session['user_name'], products=products)


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id, 
            "name": p.name, 
            "price": p.price, 
            "stock": p.stock, 
            "category": p.category, 
            "sku": p.sku,
            "image_url": p.image_url
        }
        for p in products
    ])


@app.route('/add_multiple_products')
def add_multiple_products():
    try:
        products = [
            Product(
                name="Espresso",
                category="Drink",
                sku=generate_sku(),
                stock=10,
                price=2.50,
                image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuAj8EpLVI56YxMycwpZRJvLxvVzpE-QfVwjqdzdrMIEUX2qczthx5VbMy_LpjwzIsWQvGV3GyFSpq2Wl4LRXZ5Rs2HAwqtobp6WYCIhTqDMgV-Y8f6xq4aSXTPf8PJSMhzm-OvHZsgxMkzm0n7SpXYQI8RvgLaoeDWN3fCaPsPt1xe4k3utvkpqxvT6D1N0DAfQbCDLYps_k8a3e6R7SpNAM0GNfIibFw0WRQZvwpzhryAEWjVMPc1P01N0yWPlET0TdSRiUpwvL1M"
            ),
            Product(
                name="Cappuccino",
                category="Drink",
                sku=generate_sku(),
                stock=15,
                price=3.50,
                image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuDHnAxhppAEV661r6lI8-XGoLCcsyVfQdg12Q1U2TDFLfY0QN7nYzEREHQbR8D8PwfEMawGds2yxd7GvWwShQPhHLEcUUNqWcnH7EDL8wNitIo2ccKg1YPqh6uyOYL4Ks57PUZ8JYFi_XZQm40jwJzu4j4vlHC0T7b0XjoNTStI3lgvlVIoOJ2lmgNNFnZKO0P1eyEwYSYXIm4s7BpF7V5OPXNdy1Drv_aQOY5nI09G492by4ZTP4VmtWpP7pxZcwYNqD4_vwZQ2fI"
            ),
            Product(
                name="Latte",
                category="Drink",
                sku=generate_sku(),
                stock=20,
                price=4.00,
                image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuDLD_S6LvEpZF9j_ER8EfiStDf3DFPwpFU2ulokzowa5A4gMHM2E2i2yXWiblv5hL6Xx8Dn6k0bJ_Do7V33qGNRpVvDz1OsTE4Sqw_jUIM-KoeVEF-qRggqsLjycTd2C3yQmb3htXY5cGeoIs-c0RgdfCOQILa9Gxb-8k1Z1gOKUzvKFTrbUuFM-BO1ao0cG2Hkf_J_4Q_fSKh1FgyCfpBWooTRTbAGUhIclBsSoze218tpVl1rvxx6Ip2vatEVXCZQtJOiroH3pvY"
            ),
            Product(
                name="Iced Coffee",
                category="Drink",
                sku=generate_sku(),
                stock=10,
                price=3.00,
                image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuAj8EpLVI56YxMycwpZRJvLxvVzpE-QfVwjqdzdrMIEUX2qczthx5VbMy_LpjwzIsWQvGV3GyFSpq2Wl4LRXZ5Rs2HAwqtobp6WYCIhTqDMgV-Y8f6xq4aSXTPf8PJSMhzm-OvHZsgxMkzm0n7SpXYQI8RvgLaoeDWN3fCaPsPt1xe4k3utvkpqxvT6D1N0DAfQbCDLYps_k8a3e6R7SpNAM0GNfIibFw0WRQZvwpzhryAEWjVMPc1P01N0yWPlET0TdSRiUpwvL1M"
            ),
            Product(
                name="Pastry",
                category="Food",
                sku=generate_sku(),
                stock=30,
                price=2.00,
                image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuDHnAxhppAEV661r6lI8-XGoLCcsyVfQdg12Q1U2TDFLfY0QN7nYzEREHQbR8D8PwfEMawGds2yxd7GvWwShQPhHLEcUUNqWcnH7EDL8wNitIo2ccKg1YPqh6uyOYL4Ks57PUZ8JYFi_XZQm40jwJzu4j4vlHC0T7b0XjoNTStI3lgvlVIoOJ2lmgNNFnZKO0P1eyEwYSYXIm4s7BpF7V5OPXNdy1Drv_aQOY5nI09G492by4ZTP4VmtWpP7pxZcwYNqD4_vwZQ2fI"
            ),
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        return "Products added!"
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"


# --- INVENTORY PAGE ---
@app.route('/inventory')
def inventory():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    category_filter = request.args.get('category')
    search_query = request.args.get('search', '').strip()
    
    # Start with base query
    query = Product.query
    
    # Apply search filter
    if search_query:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search_query}%'),
                Product.sku.ilike(f'%{search_query}%'),
                Product.category.ilike(f'%{search_query}%')
            )
        )
    
    # Apply category filter
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    products = query.all()
    categories = sorted({product.category for product in Product.query.all()})
    
    return render_template(
        'inventory.html', 
        name=session['user_name'], 
        products=products, 
        categories=categories,
        current_category=category_filter or "All"
    )


# --- PRODUCT ROUTES ---
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session or session['user_role'] not in ['admin', 'employee']:
        flash('You are not authorized to add products.')
        return redirect(url_for('inventory'))

    name = request.form['name']
    category = request.form['category']
    sku = request.form.get('sku', generate_sku())  # Use provided SKU or generate one
    stock = int(request.form['stock'])
    last_restocked = datetime.strptime(request.form['last_restocked'], '%Y-%m-%dT%H:%M')
    price = float(request.form['price'])
    image_url = request.form['image_url']

    new_product = Product(
        name=name,
        category=category,
        sku=sku,
        stock=stock,
        last_restocked=last_restocked,
        price=price,
        image_url=image_url
    )
    db.session.add(new_product)
    db.session.commit()
    flash(f'Product "{name}" (SKU: {sku}) added successfully!', 'success')
    return redirect(url_for('inventory'))


# Edit product form
@app.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    if 'user_id' not in session or session['user_role'] not in ['admin', 'employee']:
        flash('You are not authorized to edit products.')
        return redirect(url_for('inventory'))
        
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form["name"]
        product.category = request.form.get("category", product.category)
        product.sku = request.form.get("sku", product.sku)
        product.stock = int(request.form["stock"])
        product.price = float(request.form["price"])

        # Convert the string 'YYYY-MM-DD' into a Python date object
        product.last_restocked = datetime.strptime(
            request.form["last_restocked"], "%Y-%m-%d"
        ).date()

        db.session.commit()
        flash(f'Product "{product.name}" (SKU: {product.sku}) updated successfully!', 'success')
        return redirect(url_for("inventory"))

    return render_template("product_edit.html", product=product)


@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    if 'user_id' not in session or session['user_role'] not in ['admin', 'employee']:
        flash('You are not authorized to delete products.', 'error')
        return redirect(url_for('inventory'))
    
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    product_sku = product.sku
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{product_name}" (SKU: {product_sku}) has been deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('inventory'))


@app.route('/customers')
def customers_page():
    customers = Customer.query.all()
    return render_template('customer.html', customers=customers)




# --- CUSTOMER ROUTES ---
@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')

    if not name or not phone:
        flash("Name and phone are required")
        return redirect(url_for('order'))

    customer = Customer(name=name, email=email, phone=phone, address=address)
    db.session.add(customer)
    db.session.commit()
    flash("Customer created successfully!")
    return redirect(url_for('order'))


@app.route('/customersPage', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "points": c.loyalty_points
        } for c in customers
    ])


# --- ORDER ROUTES ---
@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    customer_id = data.get('customer_id')
    items = data.get('items', [])  # list of {product_id, quantity}

    if not customer_id or not items:
        return jsonify({"error": "Customer and items are required"}), 400

    order = Order(customer_id=customer_id, status="pending")
    total_price = 0.0

    for item in items:
        product = Product.query.get(item['product_id'])
        if not product or product.stock < item['quantity']:
            return jsonify({"error": f"Product {item['product_id']} unavailable"}), 400

        # Deduct stock
        product.stock -= item['quantity']

        # Add to order
        order_item = OrderItem(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=product.price
        )
        total_price += product.price * item['quantity']
        db.session.add(order_item)

    order.total_price = total_price

    # Add loyalty points (1 point per $1 spent for example)
    customer = Customer.query.get(customer_id)
    if customer:
        customer.add_points(int(total_price))

    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "Order created", "order_id": order.id})


@app.route('/orders/<int:customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id).all()
    return jsonify([
        {
            "id": o.id,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at,
            "items": [
                {"product": item.product.name, "qty": item.quantity, "price": item.price}
                for item in o.items
            ]
        } for o in orders
    ])


if __name__ == '__main__':
    app.run(debug=True)
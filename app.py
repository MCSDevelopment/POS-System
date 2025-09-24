from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from datetime import datetime
from models import User, Product, db
app = Flask(__name__)

# Config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)

# Initialize db + migrate

db.init_app(app) 
migrate = Migrate(app, db)





# ROUTES
@app.route('/')
def index():
    return "Welcome to the POS System!"


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
        {"id": p.id, "name": p.name, "price": p.price, "stock": p.stock, "category": p.category, "image_url": p.image_url}
        for p in products
    ])


# @app.route('/add_products')
# def add_products():
#     try:
#         products = [
#             Product(name="Espresso", category="Drink", stock=10, price=2.50, image_url="https://...espresso-image-url..."),
#             Product(name="Cappuccino", category="Drink", stock=15, price=3.50, image_url="https://...cappuccino-image-url..."),
#             Product(name="Latte", category="Drink", stock=20, price=4.00, image_url="https://...latte-image-url..."),
#             Product(name="Iced Coffee", category="Drink", stock=10, price=3.00, image_url="https://...icedcoffee-url..."),
#             Product(name="Pastry", category="Food", stock=30, price=2.00, image_url="https://...pastry-url..."),
#         ]
#         db.session.bulk_save_objects(products)
#         db.session.commit()
#         return "Products added!"
#     except Exception as e:
#         db.session.rollback()
#         return f"Error: {str(e)}"




# --- INVENTORY PAGE ---
@app.route('/inventory')
def inventory():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    category_filter = request.args.get('category')
    
    if category_filter:
        products = Product.query.filter_by(category=category_filter).all()
    else:
        products = Product.query.all()
        category_filter = "Category"  # default text when no filter

    categories = sorted({product.category for product in Product.query.all()})
    
    return render_template(
        'inventory.html', 
        name=session['user_name'], 
        products=products, 
        categories=categories,
        current_category=category_filter
    )





if __name__ == '__main__':
    app.run(debug=True)

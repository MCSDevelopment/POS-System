from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
import os
from models import db, User  # import shared db and User model

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


import secrets
app.secret_key = secrets.token_hex(16)  # generates a random 32-character hex string

# Initialize db and migrate
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return "Welcome to the User CRUD API!"

# CREATE - add a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    new_user = User(name=data['name'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created', 'user': {'id': new_user.id, 'name': new_user.name}}), 201

# READ - get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{ 'email': user.email,'id': user.id, 'name': user.name} for user in users]
    return jsonify(users_list)

# READ - get a single user by ID
@app.route('/oneusers/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name})


@app.route('/add_test')
def add_test():
    with app.app_context():
        test_user = User(name='Test User')
        db.session.add(test_user)
        db.session.commit()
    return 'Test user added!'

from flask import request, redirect, url_for, flash

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        pin = request.form.get('pin')

        # Basic validation
        if not all([name, email, password, pin]):
            flash('All fields are required!')
            return redirect(url_for('signup'))

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('signup'))

        # Create user
        new_user = User(
            name=name,
            email=email,
            pin=pin
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!')
            return redirect(url_for('login'))  # or wherever you want
        except Exception as e:
            db.session.rollback()
            return f'Error: {str(e)}'

    # GET request renders the signup form
    return render_template('signup.html')

from flask import request, render_template, redirect, url_for, flash, session
from models import User, db

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic validation
        if not all([email, password]):
            flash('Email and password are required!')
            return redirect(url_for('login'))

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Store session
            session['user_id'] = user.id
            session['user_name'] = user.name

            flash(f'Welcome back, {user.name}!')
            return redirect(url_for('order'))  # change to your dashboard/home
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))

    # GET request → show login page
    return render_template('login.html')


@app.route('/order')
def order():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    return render_template('order.html', name=session['user_name'])



# UPDATE AND DELETE ARE NOT USEABLE IN BROWSER 
# BROWSER ONLY SUPPORTS GET AND POST METHODS


# # UPDATE - update a user by ID
# @app.route('/updateusers/<int:user_id>', methods=['PUT'])
# def update_user(user_id):
#     user = User.query.get_or_404(user_id)
#     data = request.get_json()
#     if not data or 'name' not in data:
#         return jsonify({'error': 'Name is required'}), 400
    
#     user.name = data['name']
#     db.session.commit()
#     return jsonify({'message': 'User updated', 'user': {'id': user.id, 'name': user.name}})

# # DELETE - delete a user by ID
# @app.route('/deleteusers/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = User.query.get_or_404(user_id)
#     db.session.delete(user)
#     db.session.commit()
#     return jsonify({'message': f'User {user_id} deleted'})

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, User

def register_routes(app):
    @app.route('/')
    def index():
        with app.app_context():
            users = User.query.all()
        # List users with email instead of name
        user_list = ''.join(f'<li>{user.email}</li>' for user in users)
        return f'<h1>Users</h1><ul>{user_list}</ul>'



    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        users_list = [{'id': u.id, 'email': u.email, 'pint': u.pint} for u in users]
        return jsonify(users_list)
    

    @app.route('/add_test')
    def add_test():
        try:
            # Make sure app context is active
            with app.app_context():
                # Create a test user with all required fields
                test_user = User(
                    name='Test User',
                    email='test@example.com',
                    pin='1234'
                )
                test_user.set_password('password')  # hash the password

                db.session.add(test_user)
                db.session.commit()

            return 'Test user added successfully!'
        except Exception as e:
            return f'Error: {str(e)}'




    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            pin = request.form.get('pin')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm-password')

            # Basic validation
            if not name or not email or not pin or not password or not confirm_password:
                flash('All fields are required!', 'error')
                return redirect(url_for('signup'))

            if len(pin) != 4 or not pin.isdigit():
                flash('PIN must be exactly 4 digits!', 'error')
                return redirect(url_for('signup'))

            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('signup'))

            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered!', 'error')
                return redirect(url_for('signup'))

            # Create new user
            new_user = User(name=name, email=email, pin=pin)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully!', 'success')
            return redirect(url_for('index'))

        # GET request -> render signup page
        return render_template('signup.html')




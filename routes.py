from flask import render_template, request, redirect, url_for
from models import db, User


def register_routes(app):
    @app.route('/')
    def index():
        with app.app_context():
            users = User.query.all()
        return '<h1>Users</h1><ul>' + ''.join(f'<li>{user.name}</li>' for user in users) + '</ul>'

    @app.route('/add_test')
    def add_test():
        try:
            with app.app_context():
                test_user = User(name='Test User')
                db.session.add(test_user)
                db.session.commit()
            return 'Test user added!'
        except Exception as e:
            return f'Error: {str(e)}'
        


    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name = request.form['username']
            pin = request.form['pin']

            # Validate PIN is 4 digits
            if not (pin.isdigit() and len(pin) == 4):
                return render_template('signup.html', error="PIN must be exactly 4 digits")

            # Check if username already exists
            if User.query.filter_by(name=name).first():
                return render_template('signup.html', error="Username already exists")

            # Create new user
            new_user = User(name=name, pin=pin)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('signup_success'))

        return render_template('signup.html', error=None)




    @app.route('/signup_success')
    def signup_success():
        return "Signup successful! <a href='/signup'>Back to Signup</a>"

    @app.route('/login')
    def login():
        return render_template("login.html")

    @app.route('/orderpage')
    def orderpage():
        return render_template("orderpage.html")

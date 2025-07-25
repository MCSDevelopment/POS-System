from flask import Flask, render_template
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
        
    @app.route('/login')
    def login():

        return  render_template("login.html")
      
        
        
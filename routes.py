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







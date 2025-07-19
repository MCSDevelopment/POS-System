from flask import render_template

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('login.html')
    
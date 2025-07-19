from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes import init_routes

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

init_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
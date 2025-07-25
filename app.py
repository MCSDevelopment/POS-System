from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Example model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# Create database and tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 

@app.route('/add_test')
def add_test():
    with app.app_context():
        test_user = User(name='Test User')
        db.session.add(test_user)
        db.session.commit()
    return 'Test user added!'

if __name__ == '__main__':
    app.run(debug=True)
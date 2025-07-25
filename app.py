from flask import Flask
from flask_migrate import Migrate
from config import Config
from models import db
from routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

# Register routes
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from flask_migrate import Migrate
from config import Config
from models import db
from routes import register_routes



# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# # Create an engine (replace 'sqlite:///your_database.db' with your actual path)
# engine = create_engine('sqlite:///mydatabase.db')

# # Create a session factory with autoflush=True (which is the default)
# Session = sessionmaker(bind=engine, autoflush=True)

# # Create a session instance
# session = Session()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

# Register routes
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)



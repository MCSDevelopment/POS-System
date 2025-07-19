class Config:
    SECRET_KEY = 'your-secret-key'  # Replace with a secure key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pos.db'  # SQLite for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
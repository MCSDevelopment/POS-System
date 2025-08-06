import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mydatabase.db'  # Or use PostgreSQL/MySQL URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)

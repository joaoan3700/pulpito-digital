import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Usando SQLite para simplicidade
    SQLALCHEMY_TRACK_MODIFICATIONS = False

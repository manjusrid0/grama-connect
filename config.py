import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ensure the database folder exists
DB_FOLDER = os.path.join(BASE_DIR, 'database')
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# Full path to the SQLite database file
DB_PATH = os.path.join(DB_FOLDER, 'gramaconnect.db').replace("\\", "/")

class Config:
    SECRET_KEY = 'your_secret_key_here'  # Replace with a strong secret key
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads').replace("\\", "/")

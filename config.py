import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
from settings import DB_NAME, DB_USER, DB_PASSWORD

# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}'

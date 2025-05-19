
import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='static')
app.config.from_object('config')
csrf = CSRFProtect(app)

app.jinja_env.globals.update(getattr=getattr)

# Database connection settings
DB_NAME = app.config['DB_NAME']
DB_USER = app.config['DB_USERNAME']  
DB_PASSWORD = app.config['DB_PASSWORD'] 
DB_HOST = app.config['DB_HOST']

# Function to check if the database exists
def database_exists():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES;")
        databases = [db[0] for db in cursor.fetchall()]
        connection.close()
        return DB_NAME in databases  # Returns True if the database exists
    except Exception as e:
        print("Error connecting to MySQL:", e)
        return False

# Create database if it does not exist
if not database_exists():
    print(f"Database '{DB_NAME}' not found. Creating now...")
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE {DB_NAME};")
        connection.close()
        print(f"Database '{DB_NAME}' created successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")
        exit(1)  # Stop execution if database creation fails

# Set SQLAlchemy to use the newly created database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database AFTER setting config
db = SQLAlchemy(app)

# Import models after db initialization to avoid circular import issues
from models import *

# Create tables if they do not exist
with app.app_context():
    db.create_all()
    print("All tables are ensured to exist.")

# Import routes after database is set up
from routes import *

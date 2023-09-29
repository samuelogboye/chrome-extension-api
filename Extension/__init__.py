from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
import cloudinary
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/videos.db'

db = SQLAlchemy()

migrate = Migrate(app, db)

db.init_app(app)

# Retrieve Cloudinary configuration values
cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

# Configure Cloudinary
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

from Extension import routes

def get_allowed_file():
    return [
        ".mp4",
        ".MP4",
        ".gif",
        ".FLV",
        ".flv",
        ".avi",
        ".AVI",
        ".WebM",
        ".webm",
        ".3gp",
        ".3GP",
    ]
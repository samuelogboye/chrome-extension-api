from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from models import app

load_dotenv()



def get_allowed_file():
    return [
        ".mp4",
        ".mkv",
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
        ".jpg",
    ]


app.config["MAX_CONTENT_LENGTH"] = 50 * (1024 * 1024)
app.config["UPLOAD_EXTENSIONS"] = get_allowed_file()


if __name__ == "__main__":
    app.run(debug=True)


import models
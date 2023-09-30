from flask import Flask, jsonify, url_for, request, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
from uuid import uuid4


app = Flask(__name__)
CORS(app)


@app.route("/upload", methods=["POST"])
def upload_video():
    upload = request.files["file"]
    file_name = upload.filename
    file_name = secure_filename(file_name)
    # Generate a random UUID
    user_id = str(uuid4())
    user_id = user_id[:8]

    # Concatenate the UUID with the file name
    combined_file_name = f"{user_id}_{file_name}"

    if file_name == "":
        return jsonify({"error": "Bad Request", "message": "File has no name"}), 400
    file_ext = os.path.splitext(file_name)[1]

    if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
        return (
            jsonify(
                {"error": "Forbidden", "message": "This file type is not supported"}
            ),
            403,
        )

    if not os.path.exists("static"):
        os.mkdir("static")

    # Save the uploaded file with the combined file name
    upload.save(os.path.join("static", combined_file_name))

    # Construct the URL using the generated UUID and combined file name
    video_url = url_for("view_video", video_name=combined_file_name, _external=True)

    # Return the URL as a JSON response
    return (
        jsonify(
            {
                "message": "success",
                "video_name": combined_file_name,
                "video_url": video_url,
            }
        ),
        201,
    )


@app.route("/videos", methods=["GET"])
def list_videos():
    # Example logic for listing video files:
    video_files = []
    for index, filename in enumerate(os.listdir("static"), start=1):
        video_url = url_for("view_video", video_name=filename, _external=True)
        video_files.append({"video_number": index, "video_name": filename, "video_url": video_url})

    return jsonify({"videos": video_files}), 200


@app.route("/videos/<string:video_name>", methods=["GET"])
def view_video(video_name):
    if not os.path.exists("static"):
        return jsonify({"message": "no uploads yet", "videos_urls": []}), 200

    # Example logic for retrieving the video file:
    video_path = os.path.join("static", f"{video_name}")

    # Check if the video file exists and serve it
    if os.path.exists(video_path):
        # You might want to use Flask's send_file function to serve the video.
        return send_file(video_path, as_attachment=False)
    else:
        return jsonify({"error": "Not Found", "message": "Video not found."}), 404


@app.route("/")
def cron():
    return (
        jsonify({"message": "success", "types": app.config["UPLOAD_EXTENSIONS"]}),
        200,
    )

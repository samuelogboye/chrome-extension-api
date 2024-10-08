from flask import Flask, jsonify, url_for, request, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
from uuid import uuid4
import base64
from video import transcribe, get_size
from datetime import datetime


app = Flask(__name__)
CORS(app)


@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return (
            jsonify({"error": "Bad Request", "message": "File not found in request"}),
            400,
        )
    upload = request.files["file"]
    file_name = upload.filename
    file_name = secure_filename(file_name)
    # Generate a random UUID
    user_id = str(uuid4())
    user_id = user_id[:8]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Concatenate the UUID with the file name
    combined_file_name = f"{created_at}_{user_id}_{file_name}"

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

    file_path = os.path.join("static", combined_file_name)
    # Save the uploaded file temporarily
    upload.save(file_path)

    file_size = get_size(file_path)

    # Construct the URL using the generated UUID and combined file name
    video_url = url_for("view_video", video_name=combined_file_name, _external=True)

    # Return the URL as a JSON response
    return (
        jsonify(
            {
                "message": "success",
                "video_name": combined_file_name,
                "video_url": video_url,
                "video_size": file_size,
                "created_at": created_at,
                # "transcribed_text": recognized_text,
            }
        ),
        201,
    )


@app.route("/upload/base/", methods=["POST"])
def upload_video_base():
    base64_data = request.json.get(
        "file"
    )  # Assuming the base64 content is in a JSON field named "file"
    if not base64_data:
        return jsonify(
            {"error": "Bad Request", "message": "No base64 file provided"}
        ), 400

    # Convert the base64 data to bytes
    try:
        file_data = base64.b64decode(base64_data)
    except Exception as e:
        return jsonify(
            {
                "error": "Bad Request",
                "message": "Invalid base64 encoding",
                "status": str(e),
            }
        ), 400

    # Generate a random UUID
    user_id = str(uuid4())
    user_id = user_id[:8]

    # Define the file name with .mp4 extension
    combined_file_name = f"{user_id}.mp4"

    # Create a file path for the MP4 file
    file_path = os.path.join("static", combined_file_name)

    # Write the base64 data to the MP4 file
    with open(file_path, "wb") as file:
        file.write(file_data)

    file_size = get_size(file_path)

    # Construct the URL using the generated UUID and combined file name
    video_url = url_for("view_video", video_name=combined_file_name, _external=True)

    # Return the URL as a JSON response
    return jsonify(
        {
            "message": "success",
            "video_name": combined_file_name,
            "video_url": video_url,
            "video_size": file_size,  # Include the size in the response
        }
    ), 201


@app.route("/videos", methods=["GET"])
def list_videos():
    # Example logic for listing video files:
    video_files = []

    # Function to get the creation time from the filename
    def get_creation_time(filename):
        created_at = filename.split("_")[0]
        return created_at

    video_directory = "static"
    video_files = os.listdir(video_directory)

    # Sort the files based on creation time
    video_files = sorted(video_files, key=get_creation_time)

    # Now, you have the video files sorted by creation time
    video_files_data = []

    for index, filename in enumerate(video_files, start=1):
        video_path = os.path.join(video_directory, filename)
        size_mb_str = get_size(video_path)

        video_url = url_for("view_video", video_name=filename, _external=True)
        created_at = get_creation_time(filename)

        video_files_data.append(
            {
                "video_number": index,
                "video_name": filename,
                "video_url": video_url,
                "video_size": size_mb_str,
                "created_at": created_at,
            }
        )

    return jsonify({"videos": video_files_data}), 200


# the view a particular video
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


@app.route("/<string:video_name>", methods=["DELETE"])
def delete_video(video_name):
    # Construct the full path to the video file
    video_path = os.path.join("static", video_name)

    # Check if the video file exists
    if os.path.exists(video_path):
        # Attempt to delete the video file
        try:
            os.remove(video_path)
            return jsonify(
                {
                    "message": "success",
                    "info": f"Video '{video_name}' has been deleted.",
                }
            ), 200
        except Exception as e:
            return jsonify(
                {
                    "error": "Internal Server Error",
                    "message": f"Failed to delete video: {str(e)}",
                }
            ), 500
    else:
        return jsonify({"error": "Not Found", "message": "Video not found."}), 404


# To transcribe a video
@app.route("/transcribe/<string:video_name>", methods=["GET"])
def transcribe_video(video_name):
    # Construct the full path to the video file
    video_path = os.path.join("static", video_name)

    # Check if the video file exists
    if os.path.exists(video_path):
        transcribed_text = transcribe(video_path)
        # Return the URL as a JSON response
        return (
            jsonify(
                {
                    "message": "success",
                    "video_name": video_name,
                    "transcribed_text": transcribed_text,
                }
            ),
            201,
        )
    else:
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "Video not found.",
                }
            ),
            404,
        )


@app.route("/")
def cron():
    return (
        jsonify({"message": "success", "types": app.config["UPLOAD_EXTENSIONS"]}),
        200,
    )


# Define a custom error handler for 404 (Not Found) errors
@app.errorhandler(404)
def page_not_found(error):
    return jsonify(
        {
            "error": "Not Found",
            "message": "The requested URL was not found on the server.",
        }
    ), 404


# This is a catch-all route that handles any undefined path
@app.route(
    "/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
def undefined_route(path):
    # Raise a 404 error to trigger the custom error handler
    return page_not_found(404)

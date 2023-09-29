from io import BytesIO
from flask import jsonify, request
from Extension import app, db
from Extension.models import User, Video
from Extension import get_allowed_file


app.config["MAX_CONTENT_LENGTH"] = 100 * 1024  # 100 MB max size for a file
app.config["UPLOAD_EXTENSIONS"] = get_allowed_file()

# Add a new user to the database
@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'message': 'Username is required', 'success': False}), 400

    if len(username) < 3:
        return jsonify({'message': 'Username must be at least 3 characters', 'success': False}), 400
    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists, please pick another username', 'success': False}), 400

    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    response_data = {
        'id': new_user.id,
        'username': new_user.username,
        'created_at': new_user.created_at,
        'message': 'User created successfully',
        'success': True
    }
    return jsonify(response_data), 201  # 201 Created status code




# ----------------- Video ----------------- #
@app.route('/<string:username>', methods=['POST'])
def add_video(username):
    """To add a new video record for a specific user."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found', 'success': False}), 404

    data = request.get_json()
    video_name = data.get('video_name')
    video_data = data.get('data')

    if not video_name or not video_data:
        return jsonify({'message': 'video_name and data are required', 'success': False}), 400

    new_video = Video(video_name=video_name, data=video_data)
    db.session.add(new_video)
    db.session.commit()

    response_data = {
        'id': new_video.id,
        'video_name': new_video.video_name,
        'data': new_video.data,
        'created_at': new_video.created_at,
        'message': 'Video added successfully',
        'success': True
    }

    return jsonify(response_data), 201  # 201 Created status code


# Get all videos of a specific username
@app.route('/<string:username>', methods=['GET'])
def get_videos(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found', 'success': False}), 404

    videos = Video.query.filter_by(user_id=user.id).all()
    video_list = []
    for video in videos:
        video_list.append({
            'id': video.id,
            'video_name': video.video_name,
            'data': video.data,
            'created_at': video.created_at
        })

    return jsonify(video_list)


# Get a specific video of a username by username and video ID
@app.route('/<string:username>/<string:video_id>', methods=['GET'])
def get_video(username, video_id):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found', 'success': False}), 404

    video = Video.query.filter_by(user_id=user.id, id=video_id).first()
    if video is None:
        return jsonify({'message': 'Video not found', 'success': False}), 404

    response_data = {
        'id': video.id,
        'video_name': video.video_name,
        'data': video.data,
        'created_at': video.created_at,
    }

    return jsonify(response_data)

# @app.route('/video/<id>', methods=['GET'])
# def get_video(id):
#     """To get a video by id"""
#     video = Video.query.filter_by(id=id).first()
#     if video is not None:
#         # Assuming video.content_type represents the MIME type of the video (e.g., 'video/mp4')
#         return render_template('video.html', video=video)
#     else:
#         # Handle the case where the video is not found
#         return "Video not found", 404

#     # return send_file(BytesIO(video.data), attachment_filename=video.video, as_attachment=True)
#     # # return jsonify(video)


# DELETE a specific video of a username by username and video ID
@app.route('/<string:username>/<string:video_id>', methods=['DELETE'])
def delete_video(username, video_id):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'message': 'User not found', 'success': False}), 404

    video = Video.query.filter_by(user_id=user.id, id=video_id).first()
    if video is None:
        return jsonify({'message': 'Video not found', 'success': False}), 404

    db.session.delete(video)
    db.session.commit()

    return jsonify({'message': 'Video deleted successfully', 'success': True}), 200  # 200 OK status code

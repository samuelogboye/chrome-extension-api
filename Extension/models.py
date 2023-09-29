from flask_login import UserMixin
from Extension import db
import uuid
from datetime import datetime

# Model for the table ti atore the scren record data
class Video(db.Model):
    """A table model for video"""
    __tablename__ = 'video'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    video_name = db.Column(db.String(100), nullable=True)
    data = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        super(Video, self).__init__(**kwargs)

    def __repr__(self):
        return f"Video('{self.video_name}', '{self.created_at}')"

# Model for the table to store the user data
class User(db.Model, UserMixin):
    """Table model for User"""
    __tablename__ = 'user'

    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    videos = db.relationship('Video', backref='author', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return f"User('{self.username}', '{self.created_at}')"
